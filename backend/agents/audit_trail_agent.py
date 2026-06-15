import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from agents.base_agent import BaseAgent
from settings.paths import AUDIT_DIR, AUDIT_TRAIL_JSONL

class AuditTrailAgent(BaseAgent):

    """
        Registra la evaluacion final en JSONL
    """

    # Asigna nombre al Agente
    name: str = "AuditTrailAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        try:
            # Verificación de existencia de archivo de auditoria
            AUDIT_DIR.mkdir(parents=True, exist_ok=True)

            audit_event_id = str(uuid.uuid4())

            # Escribir auditoria sobre archivo de control
            audit_record = {
                "audit_event_id": audit_event_id,
                "created_at": datetime.now(timezone.utc).isoformat(),

                "transaction_id": state.get("transaction_id"),
                "decision": state.get("decision"),
                "confidence": state.get("confidence"),
                "decision_basis": state.get("decision_basis"),
                "requires_human_review": state.get("requires_human_review"),

                "signals": state.get("signals", []),
                "signal_tags": state.get("signal_tags", []),

                "citations_internal": state.get("citations_internal", []),
                "citations_external": state.get("citations_external", []),

                "external_signals": state.get("external_signals", []),

                "explanation_customer": state.get("explanation_customer"),
                "explanation_audit": state.get("explanation_audit"),

                "hitl_required": state.get("hitl_required"),
                "hitl_reason": state.get("hitl_reason"),
                "hitl_queue_item": state.get("hitl_queue_item", {}),

                "pro_fraud_argument": state.get("pro_fraud_argument", {}),
                "pro_customer_argument": state.get("pro_customer_argument", {}),

                "agent_trace": state.get("agent_trace", []),
                "decision_trace": state.get("decision_trace", []),
            }

            with open(AUDIT_TRAIL_JSONL, "a", encoding="utf-8") as file:
                file.write(
                    json.dumps(
                        audit_record,
                        ensure_ascii=False,
                        default=str
                    )
                    + "\n"
                )

            # Guardar parametros en estado compartido del grafo
            state["audit_saved"] = True
            state["audit_event_id"] = audit_event_id
            state["audit_file"] = str(AUDIT_TRAIL_JSONL)

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "audit_saved": True,
                    "audit_event_id": audit_event_id,
                    "audit_file": str(AUDIT_TRAIL_JSONL)
                }
            )

            return state

        except Exception as exc:
            state["audit_saved"] = False

            self.add_error(
                state=state,
                message="Error durante registro de auditoría, conflictos con el archivo de control",
                details={"error": str(exc)}
            )

            return state