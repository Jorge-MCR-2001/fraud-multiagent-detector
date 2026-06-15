from typing import Dict, Any

def _normalize_decision_basis(decision_basis: Any) -> Dict[str, Any]:
    if isinstance(decision_basis, dict):
        return decision_basis

    if isinstance(decision_basis, str):
        return {
            "basis_type": decision_basis,
            "summary": f"Decision basis received as legacy string: {decision_basis}"
        }

    if decision_basis is None:
        return {
            "basis_type": "unknown",
            "summary": "No decision basis was provided by DecisionArbiterAgent."
        }

    return {
        "basis_type": "unsupported_format",
        "summary": "Decision basis had an unsupported format.",
        "raw_value": str(decision_basis)
    }

def build_response(final_state:Dict[str, Any]) -> Dict[str, Any]: # Constructor de respuesta del agente 

    response = {
        "transaction_id": final_state.get("transaction_id"),

        "decision": final_state.get("decision"),
        "confidence": final_state.get("confidence"),

        "decision_basis": _normalize_decision_basis(final_state.get("decision_basis")),
        "decision_rationale": final_state.get("decision_rationale"),
        "requires_human_review": final_state.get("requires_human_review", False),

        "signals": final_state.get("signals", []), # Asegura una lista valida
        "signal_tags": final_state.get("signal_tags", []), # Asegura una lista valida

        "citations_internal": final_state.get("citations_internal", []), # Asegura una lista valida
        "external_signals": final_state.get("external_signals",[]), # Asegura una lista valida
        "citations_external": final_state.get("citations_external", []), # Asegura una lista valida

        "rag_policy_context": final_state.get("rag_policy_context", []), # Asegura una lista valida
        "evidence_bundle": final_state.get("evidence_bundle", {}), # Asegura una lista valida

        "pro_fraud_argument": final_state.get("pro_fraud_argument", {}), # Asegura una lista valida
        "pro_customer_argument": final_state.get("pro_customer_argument", {}), # Asegura una lista valida

        "explanation_customer": final_state.get("explanation_customer"), # Asegura una lista valida
        "explanation_audit": final_state.get("explanation_audit"), # Asegura una lista valida
        
        "hitl_required": final_state.get("hitl_required"),
        "hitl_reason": final_state.get("hitl_reason"),
        "hitl_queue_item": final_state.get("hitl_queue_item", {}), # Asegura una lista valida

        "audit_saved": final_state.get("audit_saved", False), # Asegurar que hay una auditoria salvada
        "audit_event_id": final_state.get("audit_event_id"),

        "confidence_level": final_state.get("confidence_level", "LOW"),
        "confidence_factors": final_state.get("confidence_factors", []),

        "agent_trace": final_state.get("agent_trace", []), # Asegura una lista valida
        "decision_trace": final_state.get("decision_trace", []), # Asegura una lista valida

        "errors": final_state.get("errors",[]) # Asegura una lista valida
    }

    return response