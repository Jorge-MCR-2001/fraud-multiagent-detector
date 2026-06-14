from typing import Dict, Any, List, Optional

DECISION_RANGES = {
    "APPROVE": 0,
    "CHALLENGE": 1,
    "ESCALATE_TO_HUMAN": 2,
    "BLOCK": 3
}

DEFAULT_CONFIDENCE_BY_ACTION = {
    "APPROVE": 0.95,
    "CHALLENGE": 0.65,
    "ESCALATE_TO_HUMAN": 0.50,
    "BLOCK": 0.90
}

def evaluate_policies(signal_tags: List[str], policies: List[Dict[str, Any]]) -> Dict[str, Any]:
    
    # Evaluacion de politicas -> Observación: No es una toma de decision / Es una sugerencia

    detected_signals = set(signal_tags or []) # Garantizar una lista valida
    matched_policies: List[Dict[str, Any]] = [] # Declarar lista de politicas con match

    for policy in policies or []:

        if not policy: # Garantiza la presencia de politicas
            continue

        policy_id = policy.get("policy_id")
        rule = policy.get("rule", "")

        # Extraccion de la señal de la politica
        required_signals = _map_policy_to_internal_signals(
            policy_id=policy_id,
            rule=rule
        )

        # Extraccion de accion de la regla
        action = _parse_action_from_rule(rule)
        
        if not required_signals: # Solo aplicar para politicas con señales claras
            continue

        if set(required_signals).issubset(detected_signals): # Todas las señales requeridas por la politica estan dentro de las señales detectadas
            matched_policies.append(
                {
                    "policy_id": policy.get("policy_id"),
                    "rule": policy.get("rule", ""),
                    "required_signals": policy.get("required_signals", []),
                    "action": action,
                    "confidence": DEFAULT_CONFIDENCE_BY_ACTION.get(action, 0.50),
                    "version": policy.get("version", "unknown")
                }
            )

        # Elegir una politica conveniente
        selected_policy = _select_highest_severity_policy(matched_policies)

        return {
            "matched_policies": matched_policies,
            "policy_suggested_decision": selected_policy.get("action") if selected_policy else None, # solo inyectar una sugerencia si existe la politica
            "policy_suggested_confidence": selected_policy.get("confidence") if selected_policy else None # solo inyectar una sugerencia si existe la politica
        }

def _parse_action_from_rule(rule: str) -> Optional[str]:
    
    # Extrae la desicion explicita de la regla

    


def _select_highest_severity_policy(matched_policies:List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:

    # Mantener el orden segun el rango establecido por la politica

    if not matched_policies: # No continuar si no se encontraron matches
        return None
    
    # Escoje la politica con accion mas severa segun el DICCIONARIO DE RANGOS / para evitar ambiguedad
    return max(
        matched_policies,
        key=lambda policy: DECISION_RANGES.get(policy.get("action"), 0)
    )