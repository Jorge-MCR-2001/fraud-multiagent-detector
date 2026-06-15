from typing import Dict, Any, List

from agents.base_agent import BaseAgent


class ExplainabilityAgent(BaseAgent):

    """
        Usa datos finales de la consulta
        - Genera la explicacion para el cliente
        - Genera la explicacion para auditoria
    """

    # Asignar nombre al Agente
    name: str = "ExplainabilityAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        try:
            # Recopila información final del analisis
            decision = state.get("decision")
            confidence = state.get("confidence")
            decision_basis = state.get("decision_basis")
            signals = state.get("signals", [])
            signal_tags = state.get("signal_tags", [])

            citations_internal = state.get("citations_internal", [])
            citations_external = state.get("citations_external", [])

            external_signals = state.get("external_signals", [])
            rag_policy_context = state.get("rag_policy_context", [])

            pro_fraud_argument = state.get("pro_fraud_argument", {})
            pro_customer_argument = state.get("pro_customer_argument", {})

            agent_trace = state.get("agent_trace", [])

            # Construir explicacion para el cliente
            explanation_customer = self._build_customer_explanation(
                decision=decision,
                signals=signals
            )

            # Construir explicacion para auditoria
            explanation_audit = self._build_audit_explanation(
                decision=decision,
                confidence=confidence,
                decision_basis=decision_basis,
                signal_tags=signal_tags,
                signals=signals,
                citations_internal=citations_internal,
                citations_external=citations_external,
                rag_policy_context=rag_policy_context,
                external_signals=external_signals,
                pro_fraud_argument=pro_fraud_argument,
                pro_customer_argument=pro_customer_argument,
                agent_trace=agent_trace
            )

            state["explanation_customer"] = explanation_customer
            state["explanation_audit"] = explanation_audit

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "generated_customer_explanation": True,
                    "generated_audit_explanation": True
                }
            )

            return state


        except Exception as exc:
            self.add_error(
                state=state,
                message="Error durante generación de explicabilidad",
                details={
                    "error": str(exc)
                }
            )
            return state
        
    
    def _build_customer_explanation(self, decision: str, signals: List[str]) -> str:

        if decision == "APPROVE":
            return (
                "La transacción fue aprobada porque no se identificaron señales "
                "relevantes de riesgo frente al comportamiento habitual del cliente."
            )

        if decision == "CHALLENGE":
            relevant_reasons = self._join_reasons(signals) # helper para apilamiento de señales

            if relevant_reasons:
                return (
                    "La transacción requiere validación adicional debido a "
                    f"{relevant_reasons}."
                )

            return (
                "La transacción requiere validación adicional por presentar "
                "condiciones que deben ser confirmadas antes de continuar."
            )

        if decision == "ESCALATE_TO_HUMAN":
            return (
                "La transacción será revisada por un especialista debido a que "
                "presenta señales que requieren una evaluación adicional."
            )

        if decision == "BLOCK":
            return (
                "La transacción fue bloqueada preventivamente porque se identificó "
                "una combinación crítica de señales de riesgo."
            )

        return (
            "La transacción fue evaluada por el sistema de análisis de riesgo."
        )
    
    def _build_audit_explanation(
        self,
        decision: str,
        confidence: float,
        decision_basis: str,
        signal_tags: List[str],
        signals: List[str],
        citations_internal: List[Dict[str, Any]],
        citations_external: List[Dict[str, Any]],
        rag_policy_context: List[Dict[str, Any]],
        external_signals: List[str],
        pro_fraud_argument: Dict[str, Any],
        pro_customer_argument: Dict[str, Any],
        agent_trace: List[Dict[str, Any]]
    ) -> str:

        # Extraer metricas precisas para la auditoria
        policy_ids = self._extract_policy_ids(rag_policy_context) # helper para extraccion de id de politicas 
        internal_citation_ids = self._extract_internal_citation_ids(citations_internal) # helper para extraccion de id de citas de politicas internas
        external_citation_ids = self._extract_external_citation_ids(citations_external) # helper para extraccion de id de citas de busqueda inteligente externa
        route = self._build_agent_route(agent_trace) # helper de contruccion de la ruta de agentes utilizados

        parts = [
            f"Decisión final: {decision}.",
            f"Confianza: {confidence}.",
            f"Criterio aplicado: {decision_basis}."
        ]

        if signals:
            parts.append(
                "Señales internas detectadas: "
                + ", ".join(signals)
                + "."
            )

        if signal_tags:
            parts.append(
                "Tags técnicos asociados: "
                + ", ".join(signal_tags)
                + "."
            )

        if policy_ids:
            parts.append(
                "Políticas recuperadas por RAG: "
                + ", ".join(policy_ids)
                + "."
            )

        if internal_citation_ids:
            parts.append(
                "Citas internas utilizadas: "
                + ", ".join(internal_citation_ids)
                + "."
            )

        if external_signals:
            parts.append(
                "Señales externas consideradas: "
                + ", ".join(external_signals)
                + "."
            )

        if external_citation_ids:
            parts.append(
                "Fuentes externas utilizadas: "
                + ", ".join(external_citation_ids)
                + "."
            )

        if pro_fraud_argument:
            parts.append(
                "Argumento Pro-Fraud: score "
                + str(pro_fraud_argument.get("risk_score"))
                + ", sugerencia "
                + str(pro_fraud_argument.get("suggested_decision"))
                + "."
            )

        if pro_customer_argument:
            parts.append(
                "Argumento Pro-Customer: score "
                + str(pro_customer_argument.get("customer_trust_score"))
                + ", sugerencia "
                + str(pro_customer_argument.get("suggested_decision"))
                + "."
            )

        if route:
            parts.append(
                "Ruta de agentes: "
                + route
                + "."
            )

        return " ".join(parts)

    def _join_reasons(self, reasons: List[str]) -> str:

        if not reasons:
            return ""

        if len(reasons) == 1:
            return reasons[0].lower()

        return ", ".join(reason.lower() for reason in reasons)

    def _extract_policy_ids(self, rag_policy_context: List[Dict[str, Any]]) -> List[str]:

        policy_ids = []

        for item in rag_policy_context or []:
            policy_id = item.get("policy_id")

            if policy_id and policy_id not in policy_ids:
                policy_ids.append(policy_id)

        return policy_ids

    def _extract_internal_citation_ids(self, citations_internal: List[Dict[str, Any]]) -> List[str]:

        citation_ids = []

        for citation in citations_internal or []:
            policy_id = citation.get("policy_id")
            chunk_id = citation.get("chunk_id")

            if policy_id and chunk_id:
                citation_ids.append(f"{policy_id}/{chunk_id}")
            elif policy_id:
                citation_ids.append(policy_id)

        return citation_ids

    def _extract_external_citation_ids(self, citations_external: List[Dict[str, Any]]) -> List[str]:

        citation_ids = []

        for citation in citations_external or []:
            threat_id = citation.get("threat_id")
            url = citation.get("url")

            if threat_id:
                citation_ids.append(threat_id)
            elif url:
                citation_ids.append(url)

        return citation_ids

    def _build_agent_route(self, agent_trace: List[Dict[str, Any]]) -> str:

        route = []

        for item in agent_trace or []:
            agent = item.get("agent")

            if agent and agent not in route:
                route.append(agent)

        return " → ".join(route)
