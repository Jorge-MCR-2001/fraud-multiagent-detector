from typing import Any, Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from rag.embedding_client import EmbeddingClient
from settings.runtime_config  import (
    AZURE_AI_SEARCH_ENDPOINT,
    AZURE_AI_SEARCH_API_KEY,
    AZURE_AI_SEARCH_INDEX_NAME,
)


VECTOR_FIELD_NAME = "content_vector"


def _validate_azure_ai_search_config() -> None:
    missing = []

    if not AZURE_AI_SEARCH_ENDPOINT:
        missing.append("AZURE_AI_SEARCH_ENDPOINT")

    if not AZURE_AI_SEARCH_API_KEY:
        missing.append("AZURE_AI_SEARCH_API_KEY")

    if not AZURE_AI_SEARCH_INDEX_NAME:
        missing.append("AZURE_AI_SEARCH_INDEX_NAME")

    if missing:
        raise ValueError(
            "Faltan variables para Azure AI Search: "
            + ", ".join(missing)
        )


def build_rag_query(
    signal_tags: List[str],
    signals: List[str],
    transaction_context: Dict[str, Any],
) -> str:
    """
    Construye la misma intención semántica que el RAG local.
    """

    amount = transaction_context.get("amount")
    country = transaction_context.get("country")
    channel = transaction_context.get("channel")
    device_id = transaction_context.get("device_id")
    merchant_id = transaction_context.get("merchant_id")

    return (
        "Señales técnicas detectadas: "
        + ", ".join(signal_tags or [])
        + ". Señales de negocio detectadas: "
        + ", ".join(signals or [])
        + f". Contexto transaccional: monto {amount}, país {country}, "
        + f"canal {channel}, dispositivo {device_id}, merchant {merchant_id}"
    )


def retrieve_policy_context_from_azure_ai_search(
    signal_tags: List[str],
    signals: List[str],
    transaction_context: Dict[str, Any],
    top_k: int = 3,
) -> Dict[str, Any]:
    """
    Recupera políticas internas desde Azure AI Search.

    No decide.
    No modifica confidence.
    Solo devuelve evidencia RAG y citas internas.
    """

    _validate_azure_ai_search_config()

    rag_query = build_rag_query(
        signal_tags=signal_tags,
        signals=signals,
        transaction_context=transaction_context,
    )

    embedding_client = EmbeddingClient()
    query_vector = embedding_client.embed_query(rag_query)

    credential = AzureKeyCredential(AZURE_AI_SEARCH_API_KEY)

    search_client = SearchClient(
        endpoint=AZURE_AI_SEARCH_ENDPOINT,
        index_name=AZURE_AI_SEARCH_INDEX_NAME,
        credential=credential,
    )

    vector_query = VectorizedQuery(
        vector=query_vector.tolist(),
        k_nearest_neighbors=top_k,
        fields=VECTOR_FIELD_NAME,
    )

    results = search_client.search(
        search_text=rag_query,
        vector_queries=[vector_query],
        select=[
            "policy_id",
            "chunk_id",
            "version",
            "content",
            "suggested_action",
            "required_signals",
        ],
        top=top_k,
    )

    rag_policy_context = []
    citations_internal = []

    for item in results:
        policy_id = item.get("policy_id")
        chunk_id = item.get("chunk_id")
        version = item.get("version")

        policy_context_item = {
            "policy_id": policy_id,
            "chunk_id": chunk_id,
            "version": version,
            "content": item.get("content"),
            "suggested_action": item.get("suggested_action"),
            "required_signals": item.get("required_signals", []),
            "retrieval_provider": "azure_ai_search",
            "retrieval_score": item.get("@search.score"),
        }

        rag_policy_context.append(policy_context_item)

        citations_internal.append({
            "policy_id": policy_id,
            "chunk_id": chunk_id,
            "version": version,
        })

    return {
        "rag_query": rag_query,
        "rag_policy_context": rag_policy_context,
        "citations_internal": citations_internal,
    }