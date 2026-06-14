from typing import Dict, Any, List, Optional

DECISION_RANGES = {
    "APPROVE": 0,
    "CHALLENGE": 1,
    "ESCALATE_TO_HUMAN": 2,
    "BLOCK": 3
}

def evaluate_policies(signal_tags: List[str], policies: List[Dict[str, Any]]) -> Dict[str, Any]:
    
    # Evaluacion de politicas -> Observación: No es una toma de decision / Es una sugerencia

    detected_signals = set(signal_tags or []) # Garantizar una lista valida
    matched_policies: List[Dict[str, Any]] = [] # Declarar lista de politicas con match

    for policy in policies:
        required_signals = set(policy.get("required_signals", [])) # Cargar señales requeridas por politicas en un conjunto

        if not required_signals: # Solo aplicar para politicas con señales claras
            continue

        if required_signals.issubset(detected_signals): # Todas las señales requeridas por la politica estan dentro de las señales detectadas
            matched_policies.append(
                {
                    "policy_id": policy.get("policy_id"),
                    "rule": policy.get("rule"),
                    "required_signals": policy.get("required_signals", []),
                    "action": policy.get("action"),
                    "confidence": policy.get("confidence"),
                    "version": policy.get("version")
                }
            )

        # Elegir una politica conveniente
        selected_policy = _select_highest_severity_policy(matched_policies)

        # Constructor de citas internas
        citations_internal: List[Dict[str, Any]] = []
        for policy in matched_policies:
            citations_internal.append([
                {
                    "policy_id": policy.get("policy_id"),
                    "version": policy.get("version")
                }
            ])

        return {
            "matched_policies": matched_policies,
            "citations_internal": citations_internal,
            "policy_suggested_decision": selected_policy.get("action") if selected_policy else None, # solo inyectar una sugerencia si existe la politica
            "policy_suggested_confidence": selected_policy.get("confidence") if selected_policy else None # solo inyectar una sugerencia si existe la politica
        }


def _select_highest_severity_policy(matched_policies:List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:

    # Mantener el orden segun el rango establecido por la politica

    if not matched_policies: # No continuar si no se encontraron matches
        return None
    
    # Escoje la politica con accion mas severa segun el DICCIONARIO DE RANGOS / para evitar ambiguedad
    return max(
        matched_policies,
        key=lambda policy: DECISION_RANGES.get(policy.get("action"), 0)
    )