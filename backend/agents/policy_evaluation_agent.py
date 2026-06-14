from typing import Dict, Any
from agents.base_agent import BaseAgent

from services.load_resources import load_json_file
from services.policy_engine import evaluate_policies

class PolicyEvaluationAgent(BaseAgent):

    # Asignar nombre al agente
    name: str = "PolicyEvaluationAgent"

    # Formato de metodo de ejecución de nodos (por cada agente)
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        
        # Recuperar y garantizar el formato de los tags de señales
        signal_tags = state.get("signal_tags", [])

        # Validar existencia de tags de señales
        # "BehaivoralPatternAgent" debe haber creado "signal_tags"
        if signal_tags is None:
            self.add_error(
                state=state,
                message="Las señales de alerta no fueron encontradas en el estado compartido"
            )
            return state

        # Carga de Politicas
        policies = load_json_file()

        # Obtener un resultado de contraste con las politicas actuales
        result = evaluate_policies(
            signal_tags=signal_tags,
            policies=policies
        )

        try:
            # Carga de Politicas
            policies = load_json_file()

            # Obtener un resultado de contraste con las politicas actuales
            result = evaluate_policies(
                signal_tags=signal_tags,
                policies=policies
            )

            state["matched_policies"] = result.get("matched_policies", []) # Guardar y garantizar el valor del estado
            state["citations_internal"] = result.get("citations_internal", []) # Guardar y garantizar el valor del estado
            state["policy_suggested_decision"] = result.get("policy_suggested_decision") # Guardar y garantizar el valor del estado
            state["policy_suggested_confidence"] = result.get("policy_suggested_confidence") # Guardar y garantizar el valor del estado

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "matched_policies_count": len(state["matched_policies"]), # Cantidad de politicas que hicieron match
                    "policy_suggested_decision": state["policy_suggested_decision"] # Politica sugerida por el agente
                }
            )
            
            return state

        except Exception as exc:
            self.add_error(
                state=state,
                message="Error durante la evaluación de politicas internas",
                details={
                    "error": exc,
                }
            )
            return state
