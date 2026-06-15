import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from agents.base_agent import BaseAgent
from services.audit_trail_service import save_audit_event

class AuditTrailAgent(BaseAgent):

    """
        Registra la evaluacion final en JSONL
    """

    # Asigna nombre al Agente
    name: str = "AuditTrailAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        try:
            
            # Delegar la auditoria del evento a un helper de servicio
            audit_result = save_audit_event(state)

            # Guardar parametros en estado compartido del grafo
            state["audit_saved"] = audit_result["audit_saved"]
            state["audit_event_id"] = audit_result["audit_event_id"]
            state["audit_file"] = audit_result["audit_file"]
            state["audit_event"] = audit_result["audit_event"]

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "audit_saved": state["audit_saved"],
                    "audit_event_id": state["audit_event_id"],
                    "audit_file": state["audit_file"],
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