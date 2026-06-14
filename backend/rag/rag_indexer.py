import json
from datetime import datetime
from typing import List, Dict, Any, Optional

import numpy as np

from rag.embedding_client import EmbeddingClient
from settings.paths import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    FRAUD_POLICY_DIR,
    POLICY_INDEX_DIR,
    POLICY_CHUNKS_JSON,
    POLICY_EMBEDDINGS_NPY,
    EMBEDDING_CONFIG_JSON
)



def build_policy_index() -> List[Dict[str, Any]]:
    
    POLICY_INDEX_DIR.mkdir(parents=True,exist_ok=True) # Crear la carpeta si no existe
    
    if not FRAUD_POLICY_DIR.exists(): # Garantizar la existencia del documento para contruccion del KB
        raise FileExistsError(
            f"No se encontro el archivo de politicas {FRAUD_POLICY_DIR}"
        )
    
    # Cargar archivos de politicas json
    policies = _load_policies()

    chunks = []

    # Fragmentar en chunks cada elemento de la lista > 1 Diccionario de politica x Chunk
    for policy in policies:
        chunk = _build_policy_chunk(policy)
        chunks.append(chunk)

    text_to_embed = []

    # Apliar los textos para crear el vector store
    for chunk in chunks:
        text_to_embed.append(chunk["content"])

    # Crear el objeto
    embedding_client = EmbeddingClient()
    embeddings = embedding_client.embed_texts(text_to_embed)

    # Guardar los chunks generados
    _save_chunks(chunks)
    _save_embeddings(embeddings)

    # Guardar la configuración de los embeddings
    _save_embeddings_config(
        chunk_count = len(chunks),
        embeddings_dimension = int(embeddings.shape[1])
    )

    return chunks

def _load_policies() -> List[Dict[str, Any]]:

    # Garantiza la exitencia de la fuente de recursos para politicas internas
    if not FRAUD_POLICY_DIR.exists():
        raise FileNotFoundError(
            f"No se encontró la fuente oficial de políticas: {FRAUD_POLICY_DIR}"
        )

    # Abrir archivo de politicas y cargar en el sistem
    with open(FRAUD_POLICY_DIR, "r", encoding="utf-8") as json_file:
      data = json.load(json_file)

    # Validar la naturaleza de los datos
    if not isinstance(data, list):
        raise ValueError("fraud_policies.json debe contener una lista de politicas")

    return data


def _build_policy_chunk(policy: List[Dict[str, Any]]) -> Dict[str, Any]:

    policy_id = policy.get("policy_id")
    rule = policy.get("rule", "") # Garantiza una regla (contexto o vacia)
    version = policy.get("version","unknow")

    if not policy_id:
        raise ValueError(f"Politica sin policy_id: {policy_id}")
    
    suggested_action = _parse_action_from_rule(rule)

    required_signals = _map_policy_to_internal_signals(
        policy_id=policy_id,
        rule=rule
    )

    chunk_id = _build_chunk_id(policy_id)

    content = _build_content(
        policy_id=policy_id,
        rule=rule,
        version=version,
        suggested_action=suggested_action,
        required_signals=required_signals
    )

    return {
        "policy_id": policy_id,
        "chunk_id": chunk_id,
        "version": version,
        "rule": rule,
        "suggested_action": suggested_action,
        "required_signals": required_signals,
        "content": content,
        "source": str(FRAUD_POLICY_DIR)
    }


def _parse_action_from_rule(rule: str) -> Optional[str]:

    """
        Extrae una accion explicita de las reglas
        - Se obtienen sugerencia de acciones / decisiones
        - Se parsea la politica
    """

    if not rule: # Garantiza la existencia de la regla
        return None 
    
    if "->" in rule: # Segun la metrica
        return rule.split("->")[-1].strip()
    
    if "→" in rule: # Segun la metrica
        return rule.split("→")[-1].strip()
    
    upper_rule = rule.upper()

    # Trazabilidad de acciónes conocidas
    known_actions = [
        "APPROVE",
        "CHALLENGE",
        "BLOCK",
        "ESCALATE_TO_HUMAN"
    ]

    # Retorno de acción reconocida
    for action in known_actions:
        if action in upper_rule:
            return action

def _map_policy_to_internal_signals(policy_id: str, rule: str) -> List[str]:

    """
        Mapea politicas oficiales a señales internas del sistema
        - No es una decision final
        - Recuperacioon gobernada para recuperacion y trazabilidad
    """

    # Realiza un levantamiento de señales en función a politicas o ratros marcados -> Preparacion de datos

    if policy_id == "FP-01":
        return ["signal_a", "signal_b"]
    
    if policy_id == "FP-02":
        return ["signal_c", "signal_d"]

    normalized_rule = rule.lower()
    signals = []

    if "monto" in normalized_rule:
        signals.append("signal_a")

    if "horario" in normalized_rule:
        signals.append("signal_b")

    if "internacional" in normalized_rule or "país" in normalized_rule or "pais" in normalized_rule:
        signals.append("signal_c")

    if "dispositivo" in normalized_rule:
        signals.append("signal_d")

    return signals

def _build_chunk_id(policy_id: str) -> str:
    normalized = policy_id.lower().replace("-","")
    chunk_id = f"policy-{normalized}-001"
    return chunk_id

def _build_content(policy_id: str, rule: str, version: str, suggested_action: Optional[str], required_signals: List[str]) -> str:
    return (
        f"Politica interna: {policy_id}"
        f"Version: {version}"
        f"Regla oficial: {rule}"
        f"Accion sugerida explicita en la regla: {suggested_action}",
        f"Señales internas asociadas: {', '.join(required_signals)}"
        f"Esta politica se usa como evidencia interna recuperada por RAG, para agentes posteriores. NO REPRESENTA la decision final."
    )

