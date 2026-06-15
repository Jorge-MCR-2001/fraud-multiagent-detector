import json
from typing import List, Dict, Any, Optional

import numpy as np

from rag.embedding_client import EmbeddingClient

from settings.paths import POLICY_CHUNKS_JSON, POLICY_EMBEDDINGS_NPY
from settings.runtime_config import RAG_PROVIDER

from rag.rag_indexer import build_policy_index

def retrieve_policy_context(
                signal_tags: List[str],
                signals: Optional[List[str]] = None,
                transaction_context: Optional[Dict[str, Any]] = None,
                query: Optional[str] = None,
                top_k: int = 2,
            ) -> Dict[str, Any]:
    
    """
        Recupera evidencia interna de politicas usando embeddgins y similitud de cosenos
        - No genera decisiones
        - Solo recupera informacion
    """

    if RAG_PROVIDER == "azure_ai_search":
        from rag.azure_ai_search_retriever import retrieve_policy_context_from_azure_ai_search

        return retrieve_policy_context_from_azure_ai_search(
            signal_tags=signal_tags,
            signals=signals,
            transaction_context=transaction_context,
        )

    # Analiza la existencia del vector store
    chunks, embeddings = _load_or_build_text()

    query_text = _build_query_text(
        signal_tags=signal_tags,
        signals=signals,
        transaction_context=transaction_context,
        query=query
    )

    if not query_text: # No se a construido conrrectamente la consulta
        return {
            "rag_query": "",
            "rag_policy_context": [],
            "citations_internal": []
        }
        
    embedding_client = EmbeddingClient()
    query_embedding = embedding_client.embed_query(query_text) # Generar embeddings de la consulta

    similarities = embeddings @ query_embedding # Producto . ente vectores

    ranked_indices = np.argsort(similarities)[::-1] # Ordenar de manyor a menor similitud

    selected_chunks = []

    for index in ranked_indices:
        chunk = chunks[int(index)] # Recuperar los chunks de mayor a menor
        vector_score = float(similarities[int(index)]) # Obtiene el score de similitud vectorial

        hybrid_score = _calculate_hybrid_score( # Asigna un score hibrido en funcion a similitud semantica y reglas fijas
            chunk=chunk,
            signal_tags=signal_tags,
            vector_score=vector_score,
        )

        if hybrid_score <= 0: # Si no se tiene un score hibrido valido continua con el siguiente
            continue

        selected_chunks.append( # Añade los chunks y metadata asociada
            {
                **chunk,
                "retrieval_score": round(vector_score, 4),
                "hybrid_score": round(hybrid_score, 4),
            }
        )

        if len(selected_chunks) >= top_k: # Limita la cantidad de chunks recuperados
            break

    # Construccion de la respuesta de la busqueda por RAG
    return {
        "rag_query": query_text,
        "rag_policy_context": [
            {
                "policy_id": chunk.get("policy_id"),
                "chunk_id": chunk.get("chunk_id"),
                "version": chunk.get("version"),
                "content": chunk.get("content"),
                "suggested_action": chunk.get("suggested_action"),
                "required_signals": chunk.get("required_signals", []),
                "retrieval_score": chunk.get("retrieval_score"),
                "hybrid_score": chunk.get("hybrid_score"),
            }
            for chunk in selected_chunks
        ],
        "citations_internal": [
            {
                "policy_id": chunk.get("policy_id"),
                "chunk_id": chunk.get("chunk_id"),
                "version": chunk.get("version"),
            }
            for chunk in selected_chunks
        ],
    }



def _load_or_build_text() -> tuple[List[Dict[str, Any]], np.ndarray]: 

    if not POLICY_CHUNKS_JSON.exists() or not POLICY_EMBEDDINGS_NPY.exists(): # No existe ni la fuente ni el vectorstore
        build_policy_index()

    with open(POLICY_CHUNKS_JSON, "r", encoding="utf-8") as json_file:
        chunks = json.load(json_file)

    embeddings = np.load(POLICY_EMBEDDINGS_NPY)

    if not isinstance(chunks, list): # Analiza la naturaleza de la fuente
        raise ValueError("policy_chunks.json debe ser una lista")
    
    if len(chunks) != embeddings.shape[0]: # Control de calidad del vectorstore
        raise ValueError(
            "La cantidad de chunks no coincide con la cantidad de embeddings" 
        )
    
    return chunks, embeddings

def _build_query_text(signal_tags: List[str], signals: List[str], transaction_context: Dict[str, Any], query: Optional[str]) -> str:

    parts = []

    if query:
        parts.append(query)

    if signal_tags: # Artificio generado para control
        parts.append("Señales técnicas detectadas: " + ", ".join(signal_tags))

    if signals: # Señales originales
        parts.append("Señales de negocio detectadas: " + ", ".join(signals))

    context_parts = []

    amount = transaction_context.get("amount")
    country = transaction_context.get("country")
    channel = transaction_context.get("channel")
    device_id = transaction_context.get("device_id")
    transaction_hour = transaction_context.get("transaction_hour")
    merchant_id = transaction_context.get("merchant_id")

    # Contextualizar la pregunta

    if amount is not None:
        context_parts.append(f"monto {amount}")

    if transaction_hour is not None:
        context_parts.append(f"hora de transacción {transaction_hour}")

    if country:
        context_parts.append(f"país {country}")

    if channel:
        context_parts.append(f"canal {channel}")

    if device_id:
        context_parts.append(f"dispositivo {device_id}")

    if merchant_id:
        context_parts.append(f"merchant {merchant_id}")

    if context_parts:
        parts.append("Contexto transaccional: " + ", ".join(context_parts))

    return ". ".join(parts).strip()

def _calculate_hybrid_score(chunk: Dict[str, Any], signal_tags: List[str], vector_score: float) -> float:
    """
        Score híbrido:
        - vector_score: similitud semántica por embeddings.
        - signal overlap: alineación con señales internas detectadas.
    """

    # Recuperacion de señales por chunks
    required_signals = set(chunk.get("required_signals", []))
    # Recuperacion de señales por reglas dentro del query
    detected_signals = set(signal_tags or [])

    # Determina la interseccion entre ambas señales
    signal_overlap = required_signals.intersection(detected_signals)

    # Si la consulta tiene señales detectadas pero el chunk no tiene ninguna --> NO SE ASOCIA A NINGUNA POLITICA
    if detected_signals and not signal_overlap:
        return 0.0

    # Añade un ponderado de 0.1 por cada señal coincidente
    overlap_boost = len(signal_overlap) * 0.10

    # Añade un bonus de 0.2 si todas las señales requeridas por el chunk estan presentes en la consulta
    full_match_boost = 0.20 if (
        required_signals and required_signals.issubset(detected_signals)
    ) else 0.0

    return vector_score + overlap_boost + full_match_boost


if __name__ == "__main__":
    print("Caso FP-01:")

    result_fp01 = retrieve_policy_context(
        signal_tags=["signal_a", "signal_b"],
        signals=["Monto fuera de rango", "Horario no habitual"],
        transaction_context={
            "amount": 9500,
            "transaction_hour": 23,
            "country": "PE",
            "device_id": "D-02",
            "channel": "mobile",
            "merchant_id": "M-002",
        },
    )

    print(json.dumps(result_fp01, ensure_ascii=False, indent=2))

    print("\nCaso FP-02:")

    result_fp02 = retrieve_policy_context(
        signal_tags=["signal_c", "signal_d"],
        signals=["País inusual", "Dispositivo desconocido"],
        transaction_context={
            "amount": 500,
            "transaction_hour": 14,
            "country": "US",
            "device_id": "D-99",
            "channel": "web",
            "merchant_id": "M-001",
        },
    )

    print(json.dumps(result_fp02, ensure_ascii=False, indent=2))