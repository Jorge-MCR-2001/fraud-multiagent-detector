import json
import re

from typing import List, Dict, Any, Optional

from settings.paths import FRAUD_POLICY_DIR, POLICY_INDEX_DIR, POLICY_CHUNKS_JSON
from services.load_resources import load_json_file

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

    POLICY_CHUNKS_JSON.write_text( # Inyecta los chunks en un doc json en texto plano
        json.dumps(chunks, ensure_ascii=False, indent=2), # Convierte la lista en texto json
        encoding="utf-8"
    )

    return chunks

def _load_policies() -> List[Dict[str, Any]]:

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
    
    action = _infer_action(rule)
    required_signals = _infer_required_signals(policy_id=policy_id,rule=rule)

    chunk_id = _build_chunk_id(policy_id)

    content = _build_content(
        policy_id=policy_id,
        rule=rule,
        version=version,
        action=action,
        required_signals=required_signals
    )

    return {
        "policy_id": policy_id,
        "chunk_id": chunk_id,
        "version": version,
        "rule": rule,
        "suggested_action": action,
        "required_signals": required_signals,
        "content": content,
        "keywords": _build_keywords(
            policy_id=policy_id,
            rule=rule,
            action=action,
            required_signals=required_signals
        )
    }


def _infer_action(rule: str) -> Optional[str]:

    # Realiza la estración de la acción de la regla citada

    if not rule: # Garantiza la existencia de la regla
        return None 
    
    if "->" in rule:
        return rule.split("->")[-1].strip()
    
    if "→" in rule:
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

def _infer_required_signals(policy_id: str, rule: str) -> List[str]:

    # Asignación de reglas en la data curada

    normalize_rule = rule.lower()

    if policy_id == "FP-01":
        return ["signal_a", "signal_b"]
    
    if policy_id == "FP-02":
        return ["signal_c", "signal_d"]

    # Fallback por     

    return