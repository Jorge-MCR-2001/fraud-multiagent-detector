import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from settings.paths import AUDIT_TRAIL_JSONL

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_audit_event(state: Dict[str, Any]) -> Dict[str, Any]:
    transaction_id = state.get("transaction_id", "UNKNOWN")
    created_at = _utc_now_iso()

    evaluation_id = f"EVAL-{transaction_id}-{created_at}"
    audit_event_id = f"AUDIT-{transaction_id}-{created_at}"

    return {
        "audit_event_id": audit_event_id,
        "evaluation_id": evaluation_id,
        "transaction_id": transaction_id,

        "final_decision": state.get("decision"),
        "confidence": state.get("confidence"),
        "requires_human_review": state.get("requires_human_review", False),
        "hitl_required": state.get("hitl_required", False),

        "decision_basis": state.get("decision_basis", {}),
        "decision_rationale": state.get("decision_rationale", ""),

        "citations_internal": state.get("citations_internal", []),
        "citations_external": state.get("citations_external", []),

        "evidence_bundle": state.get("evidence_bundle", {}),

        "pro_fraud_argument": state.get("pro_fraud_argument", {}),
        "pro_customer_argument": state.get("pro_customer_argument", {}),

        "explanation_customer": state.get("explanation_customer", ""),
        "explanation_audit": state.get("explanation_audit", ""),

        "hitl_reason": state.get("hitl_reason"),
        "hitl_queue_item": state.get("hitl_queue_item"),

        "agent_trace": state.get("agent_trace", []),
        "decision_trace": state.get("decision_trace", []),
        "errors": state.get("errors", []),

        "created_at": created_at,
    }


def save_audit_event(state: Dict[str, Any]) -> Dict[str, Any]:

    # Verificación de existencia de archivo de auditoria          
    AUDIT_TRAIL_JSONL.parent.mkdir(parents=True, exist_ok=True)

    # Escribir auditoria sobre archivo de control
    audit_event = build_audit_event(state)

    with AUDIT_TRAIL_JSONL.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(audit_event, ensure_ascii=False)
            + "\n"
        )

    return {
        "audit_saved": True,
        "audit_event_id": audit_event["audit_event_id"],
        "audit_file": str(AUDIT_TRAIL_JSONL),
        "audit_event": audit_event,
    }