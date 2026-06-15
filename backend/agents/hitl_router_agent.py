from typing import Dict, Any

from agents.base_agent import BaseAgent


class HITLRouterAgent(BaseAgent):

    """
        Gestor de humano en el bucle: Determina si el caso debe ir a revision humana
    """

    # Asigna nombre al Agente
    name: str = "HITLRouterAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        try:
            # Recuperacion del caso para trazabilidad y veridicacion de intervencion de Humano
            transaction_id = state.get("transaction_id")
            decision = state.get("decision")
            confidence = state.get("confidence", 0.0)
            decision_basis = state.get("decision_basis")
            requires_human_review = state.get("requires_human_review", False)

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
                hitl_queue_item = {
                    "transaction_id": transaction_id,
                    "decision": decision,
                    "confidence": confidence,
                    "decision_basis": decision_basis,
                    "reason": hitl_reason,
                    "priority": self._calculate_priority( # Calculo de prioridad de llamada a humano
                        decision=decision,
                        confidence=confidence,
                        decision_basis=decision_basis
                    )
                }

            state["hitl_required"] = hitl_required
            state["hitl_reason"] = hitl_reason
            state["hitl_queue_item"] = hitl_queue_item

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "hitl_required": hitl_required,
                    "hitl_reason": hitl_reason,
                    "priority": hitl_queue_item.get("priority") if hitl_queue_item else None
                }
            )

            return state
        
        except Exception as exc:
            self.add_error(
                state=state,
                message="Error durante enrutamiento HITL",
                details={"error": str(exc)}
            )
            return state
        
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
    
    def _calculate_priority(self, decision: str, confidence: float, decision_basis: str) -> str:

        if decision == "ESCALATE_TO_HUMAN" and confidence < 0.55:
            return "HIGH"

        if decision_basis == "contradictory_agent_arguments":
            return "HIGH"

        if decision == "ESCALATE_TO_HUMAN":
            return "MEDIUM"

        if confidence < 0.60:
            return "MEDIUM"

        return "LOW"