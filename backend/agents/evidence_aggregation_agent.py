from typing import Dict, Any, List

from agents.base_agent import BaseAgent

class EvidenceAggregationAgent(BaseAgent):

    """
        Consolida la evidencia para los agentes posteriores
    """

    # Asignar nombra al Agente
    name: str = "EvidenceAggregationAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        try:
            # Agrupacion de data apilada durante el analisis

            # Informacion de recuperacion de data - resources
            transaction_id = state.get("transaction_id")
            transaction_context = state.get("transaction_context", {})
            customer = state.get("customer", {})

            # Informacion relativa a señales identificadas
            signal_tags = state.get("signal_tags", [])
            signals = state.get("signals", [])
            signal_metrics = state.get("signal_metrics", {})

            # Informacion relativa a politicas / citas encontradas por rag 
            rag_policy_context = state.get("rag_policy_context", [])
            citations_internal = state.get("citations_internal", [])

            # Informacion relativa a busqueda inteligente externa
            external_signals = state.get("external_signals", [])
            citations_external = state.get("citations_external", [])
            external_threat_context = state.get("external_threat_context", [])

            retrieved_policy_ids = self._extract_policy_ids(rag_policy_context)
            rag_required_signals = self._extract_required_signals(rag_policy_context)

            # Construccion de evidencias
            evidence_bundle = {
                "transaction_id": transaction_id,

                "transaction_context": transaction_context,
                "customer_behavior": customer,

                "internal_evidence": {
                    "signal_tags": signal_tags,
                    "signals": signals,
                    "signal_metrics": signal_metrics,
                    "signals_count": len(signal_tags or [])
                },

                "rag_evidence": {
                    "rag_policy_context": rag_policy_context,
                    "citations_internal": citations_internal,
                    "retrieved_policy_ids": retrieved_policy_ids,
                    "required_signals_from_rag": rag_required_signals,
                    "internal_citations_count": len(citations_internal or [])
                },

                "external_evidence": {
                    "external_signals": external_signals,
                    "citations_external": citations_external,
                    "external_threat_context": external_threat_context,
                    "external_signals_count": len(external_signals or []),
                    "external_citations_count": len(citations_external or [])
                },

                "risk_summary": {
                    "total_internal_signals": len(signal_tags or []),
                    "total_external_signals": len(external_signals or []),
                    "total_internal_citations": len(citations_internal or []),
                    "total_external_citations": len(citations_external or []),
                    "has_rag_evidence": bool(rag_policy_context),
                    "has_external_evidence": bool(external_signals),
                    "has_fp01": "FP-01" in retrieved_policy_ids,
                    "has_fp02": "FP-02" in retrieved_policy_ids
                }
            }

            state["evidence_bundle"] = evidence_bundle

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "internal_signals_count": len(signal_tags or []),
                    "external_signals_count": len(external_signals or []),
                    "rag_policies": retrieved_policy_ids
                }
            )

            return state
        
        except Exception as exc:
            self.add_error(
                state=state,
                message="Error durante la recopilacion de evidencias",
                details={
                    "error": str(exc)
                }
            )

            return state
        
    def _extract_policy_ids(self, items: List[Dict[str, Any]]) -> List[str]:

        # Recuperacion de id de politicas extraidas por rag
        policy_ids = []

        for item in items or []:
            policy_id = item.get("policy_id")

            if policy_id and policy_id not in policy_ids:
                policy_ids.append(policy_id)

        return policy_ids
    
    def _extract_required_signals(self, items: List[Dict[str, Any]]) -> List[str]:

        # Recuperacion de señales requeridas por politicas
        required_signals = []

        for item in items or []:
            for signal in item.get("required_signals", []):
                if signal not in required_signals:
                    required_signals.append(signal)

        return required_signals