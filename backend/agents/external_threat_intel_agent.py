from typing import Dict, Any

from agents.base_agent import BaseAgent
from services.external_threat_service import search_external_threats

class ExternalThreatIntelAgent(BaseAgent):

    """
        Agente especializado en busquedas de fuentes externas
        - Agrega señales externas
        - Agrega citas externas
    """

    # Asignar nombre al Agente
    name: str = "ExternalThreatIntelAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        # Realiza la carga de la transaccion contextualizada
        transaction_context = state.get("transaction_context", {})

        if not transaction_context:
            self.add_error(
                state=state,
                message="Transaction_context no encontrado para búsqueda externa"
            )
            return state

        try:
            result = search_external_threats(
                transaction_context=transaction_context
            )

            # Actualizacion del estado compartido
            state["external_signals"] = result.get("external_signals", [])
            state["citations_external"] = result.get("citations_external", [])
            state["external_threat_context"] = result.get("external_threat_context",[])
            
            self.add_trace(
                state=state,
                status="completed",
                details={ # Apliar metricas para trazabilidad
                    "external_signals": state["external_signals"],
                    "citations_external_count": len(state["citations_external"])
                }
            )

            return state
        
        except Exception as exc:
            self.add_error(
                state=state,
                message="Error durante busqueda inteligente externa",
                details={
                    "error": str(exc)
                }
            )

