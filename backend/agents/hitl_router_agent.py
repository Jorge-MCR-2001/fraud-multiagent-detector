from typing import Dict, Any, Optional

from agents.base_agent import BaseAgent
from services.hitl_queue_service import enqueue_hitl_case


class HITLRouterAgent(BaseAgent):

    """
        Gestor de humano en el bucle: Determina si el caso debe ir a revision humana
    """

    # Asigna nombre al Agente
    name: str = "HITLRouterAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        try:
            # Recuperacion del caso para trazabilidad y veridicacion de intervencion de Humano
            decision = state.get("decision")
            confidence = state.get("confidence", 0.0)
            decision_basis = state.get("decision_basis", {})
            requires_human_review = state.get("requires_human_review", False)

            basis_type = self._extract_basis_type(decision_basis)

            # Construccion ruta de requerimiento de human-in-loop
            hitl_required = self._should_route_to_human(
                decision=decision,
                confidence=confidence,
                decision_basis=decision_basis,
                requires_human_review=requires_human_review
            )

            # Construcción de razonamiento de intervencion human-in-loop
            hitl_reason = self._build_hitl_reason(
                decision=decision,
                confidence=confidence,
                decision_basis=decision_basis,
                requires_human_review=requires_human_review,
                hitl_required=hitl_required
            )

            hitl_queue_item = {}

            if hitl_required:
                state["hitl_required"] = True
                state["hitl_reason"] = hitl_reason

                hitl_queue_item = enqueue_hitl_case(
                    state=state,
                    reason=hitl_reason,
                )

                state["hitl_queue_item"] = hitl_queue_item

            else:
                state["hitl_required"] = False
                state["hitl_reason"] = hitl_reason
                state["hitl_queue_item"] = None

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "hitl_required": state.get("hitl_required"),
                    "hitl_reason": state.get("hitl_reason"),
                    "hitl_queue_id": (state.get("hitl_queue_item", {}) or {}).get("hitl_queue_id"),
                    "priority": (state.get("hitl_queue_item", {}) or {}).get("priority"),
                    "basis_type": basis_type,
                }
            )

            return state
        
        except Exception as exc:

            state["hitl_required"] = False
            state["hitl_reason"] = "HITL routing failed."
            state["hitl_queue_item"] = None

            self.add_error(
                state=state,
                message="Error durante enrutamiento HITL",
                details={"error": str(exc)}
            )
            return state
    
    def _extract_basis_type(self, decision_basis: Any) -> Optional[str]:
        """
            Extrae el tipo de criterio desde decision_basis.
        """

        if isinstance(decision_basis, dict):
            return decision_basis.get("basis_type")

        if isinstance(decision_basis, str):
            return decision_basis

        return None

    def _should_route_to_human(self, decision: str, confidence: float, decision_basis: str, requires_human_review: bool) -> bool:

        # Validacion de revision humana
        if requires_human_review:
            return True

        if decision == "ESCALATE_TO_HUMAN":
            return True

        # Solo analizar para confidence menores a 0.60
        if confidence is not None and confidence < 0.60:
            return True

        if decision_basis == "contradictory_agent_arguments":
            return True

        return False
    
    def _build_hitl_reason(self, decision: str, confidence: float, decision_basis: str, requires_human_review: bool, hitl_required: bool) -> str:

        if not hitl_required:
            return "No requiere revisión humana."

        if requires_human_review:
            return "El árbitro marcó el caso como requerido para revisión humana."

        if decision == "ESCALATE_TO_HUMAN":
            return "La decisión final fue ESCALATE_TO_HUMAN."

        if confidence is not None and confidence < 0.60:
            return "La confianza de la decisión está por debajo del umbral mínimo."

        if decision_basis == "contradictory_agent_arguments":
            return "Se detectaron argumentos contradictorios entre agentes."

        return "El caso requiere revisión humana por criterio de seguridad."