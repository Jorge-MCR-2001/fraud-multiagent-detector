from typing import Dict, Any

from agents.base_agent import BaseAgent
from rag.rag_retriever import retrieve_policy_context

class InternalPolicyRagAgent(BaseAgent):

    """
        Recupera evidencia interna de politicas internas por RAG
        - Lee señales detectadas por BehaviorPatternAgent
        - Consulta al vectorstore generado por el archivo fraud_policies.json
        - No toma decisiones finales
    """

    # Asignar nombre al Agente
    name: str = "InternalPolicyRagAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        signal_tags = state.get("signal_tags",[])
        signals = state.get("signals",[])
        transaction_context = state.get("transaction_context",{})

        if signal_tags is None:
            self.add_error(
                state=state,
                message="Signal_tags no han sido encontradas en el estado compartido"
            )
            return state
        
        try:
            
            result = retrieve_policy_context(
                signal_tags=signal_tags,
                signals=signals,
                transaction_context=transaction_context,
                top_k=2 # solo dos recuperaciones
            )

            # Actualizar el estado compartido
            state["rag_query"] = result.get("rag_query","")
            state["rag_policy_context"] = result.get("rag_policy_context",[])
            state["citations_internal"] = result.get("citations_internal", [])

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "retrieved_policies": [
                        item.get("policy_id")
                        for item in state["rag_policy_context"]
                    ],
                    "citations_internal_count": len(state["citations_internal"])
                }
            )

            return state
        
        
        except Exception as exc:
            self.add_error(
                state=state,
                message="error",
                details={
                    "error": str(exc)
                }
            )
            return state
