from typing import Dict, Any

def build_response(final_state:Dict[str, Any]) -> Dict[str, Any]: # Constructor de respuesta del agente 

    response = {
        "transaction_id": final_state.get("transaction_id"),
        "decision": final_state.get("decision"),
        "confidence": final_state.get("confidence"),

        "signals": final_state.get("signals", []), # Asegura una lista valida
        "signal_tags": final_state.get("signal_tags", []), # Asegura una lista valida

        "citations_internal": final_state.get("citations_internal", []), # Asegura una lista valida

        "external_signals": final_state.get("matched_policies",[]), # Asegura una lista valida
        "citations_external": final_state.get("citations_external", []), # Asegura una lista valida

        "matched_policies": final_state.get("matched_policies", []), # Asegura una lista valida
        "rag_policy_context": final_state.get("rag_policy_context", []), # Asegura una lista valida
        
        "agent_trace": final_state.get("agent_trace", []), # Asegura una lista valida
        "decision_trace": final_state.get("decision_trace", []) # Asegura una lista valida
    }

    errors = final_state.get("errors",[]) # Asegura una lista valida

    if errors:
        response["errors"] = errors # Agrupar dentro del output los errores dentro del ciclo de vida del Agente

    return response