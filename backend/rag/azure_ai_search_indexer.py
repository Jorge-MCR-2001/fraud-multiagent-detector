import json
from typing import Any, Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchField,
    SearchableField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

from rag.embedding_client import EmbeddingClient
from settings.runtime_config import (
    AZURE_AI_SEARCH_ENDPOINT,
    AZURE_AI_SEARCH_API_KEY,
    AZURE_AI_SEARCH_INDEX_NAME,
    EMBEDDING_DIMENSIONS,
)
from settings.paths import POLICY_CHUNKS_JSON


VECTOR_FIELD_NAME = "content_vector"
VECTOR_SEARCH_PROFILE_NAME = "policy-vector-profile"
VECTOR_ALGORITHM_NAME = "policy-hnsw"


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


def _load_policy_chunks() -> List[Dict[str, Any]]:
    if not POLICY_CHUNKS_JSON.exists():
        raise FileNotFoundError(
            f"No existe policy_chunks.json en: {POLICY_CHUNKS_JSON}"
        )

    with POLICY_CHUNKS_JSON.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_or_update_policy_index() -> None:
    """
    Crea o actualiza el índice vectorial de políticas internas en Azure AI Search.
    """

    _validate_azure_ai_search_config()

    credential = AzureKeyCredential(AZURE_AI_SEARCH_API_KEY)

    index_client = SearchIndexClient(
        endpoint=AZURE_AI_SEARCH_ENDPOINT,
        credential=credential,
    )

    vector_dimensions = EMBEDDING_DIMENSIONS or 1536

    fields = [
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="policy_id",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="chunk_id",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="version",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
        ),
        SimpleField(
            name="suggested_action",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SearchField(
            name="required_signals",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            filterable=True,
        ),
        SearchField(
            name=VECTOR_FIELD_NAME,
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=vector_dimensions,
            vector_search_profile_name=VECTOR_SEARCH_PROFILE_NAME,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name=VECTOR_ALGORITHM_NAME,
            )
        ],
        profiles=[
            VectorSearchProfile(
                name=VECTOR_SEARCH_PROFILE_NAME,
                algorithm_configuration_name=VECTOR_ALGORITHM_NAME,
            )
        ],
    )

    index = SearchIndex(
        name=AZURE_AI_SEARCH_INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
    )

    index_client.create_or_update_index(index)


def upload_policy_chunks_to_index() -> Dict[str, Any]:
    """
    Genera embeddings para policy_chunks.json y los sube a Azure AI Search.
    """

    _validate_azure_ai_search_config()

    chunks = _load_policy_chunks()

    embedding_client = EmbeddingClient()

    documents = []

    for idx, chunk in enumerate(chunks):
        content = str(chunk.get("content", ""))
        vector = embedding_client.embed_query(content)

        documents.append({
            "id": str(chunk.get("chunk_id") or f"policy-chunk-{idx}"),
            "policy_id": str(chunk.get("policy_id", "")),
            "chunk_id": str(chunk.get("chunk_id", "")),
            "version": str(chunk.get("version", "")),
            "content": content,
            "suggested_action": str(chunk.get("suggested_action", "")),
            "required_signals": chunk.get("required_signals", []),
            VECTOR_FIELD_NAME: vector.tolist(),
        })

    credential = AzureKeyCredential(AZURE_AI_SEARCH_API_KEY)

    search_client = SearchClient(
        endpoint=AZURE_AI_SEARCH_ENDPOINT,
        index_name=AZURE_AI_SEARCH_INDEX_NAME,
        credential=credential,
    )

    result = search_client.upload_documents(documents=documents)

    succeeded = [
        item for item in result
        if item.succeeded
    ]

    failed = [
        item for item in result
        if not item.succeeded
    ]

    return {
        "uploaded": len(succeeded),
        "failed": len(failed),
        "index_name": AZURE_AI_SEARCH_INDEX_NAME,
    }


def build_azure_policy_index() -> Dict[str, Any]:
    """
    Operación completa:
    1. Crea o actualiza índice.
    2. Sube documentos.
    """

    create_or_update_policy_index()
    return upload_policy_chunks_to_index()


if __name__ == "__main__":
    result = build_azure_policy_index()
    print(json.dumps(result, indent=2, ensure_ascii=False))