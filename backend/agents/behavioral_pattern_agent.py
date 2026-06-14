from typing import Dict, Any
from agents.base_agent import BaseAgent
from services.signal_detector import detect_signals


class BehavioralPatternAgent(BaseAgent):
    
    # Asignar nombre al agente
    name: str = "BehavioralPatternAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        # Recuperacion de estados de entrada
        transaction_context = state.get("transaction_context")
        customer = state.get("customer")

        # Validar existencia de transacción contextualizada
        # "TransactionContextAgent" debe haber creado "transaction_context"
        if not transaction_context:
            self.add_error(
                state=state,
                message="Contexto de transacción no encontrado en el estado compartido"
            )
            return state
        
        # Validar existencia de customer en estado
        # "orchestrator" deber haber cargado el comportamiento del cliente
        if not customer:
            self.add_error(
                state=state,
                message="El Orquestador no a cargado los datos del cliente"
            )

        try:
            # Determinar las señales de comportamiento
            result = detect_signals(
                transaction_context=transaction_context,
                customer=customer
            )

            # Cargar metricas y señales en el estado compartido
            state["signal_tags"] = result.get(("signal_tags"), [])
            state["signals"] = result.get(("signals"), [])
            state["signal_metrics"] = result.get(("signal_metrics"), [])
            
            # Añadir trazabilidad post ejecución del agente
            self.add_trace(
                state=state,
                status="completed",
                details={
                    "signal_tags": state["signal_tags"],
                    "signals_count": len(state["signal_tags"])
                }
            )

            return state

        except Exception as exc:
            self.add_error(
                state=state,
                message="Error durante la detección de patrones de comportamiento",
                details={
                    "error": str(exc),
                }
            )
            return state