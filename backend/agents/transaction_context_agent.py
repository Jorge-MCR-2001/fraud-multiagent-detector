from datetime import datetime

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

class TransactionContextAgent(BaseAgent):

    # Asignar nombre al agente
    name: str = "TransactionContextAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        
        transaction = state.get("transaction")
        
        # Validación si el orquestador entrego estado del analisis de la transacción
        if not transaction:
            self.add_error(
                state=state,
                message="Información de transacción no encontrada en el estado compartido"
            )
            return state
    
        try:
            # Construir contexto de la transacción
            transaction_context = self._build_transaction_context(transaction)

            # Inyectar informacion recuperada en estado compartido
            state["transaction_context"] = transaction_context

            # Añadir trazabilidad a operacion del agente
            self.add_trace(
                state=state,
                status="completed",
                details={
                    "transaction_id": transaction_context.get("transaction_id"),
                    "customer_id": transaction_context.get("customer_id"),
                    "transaction_hour": transaction_context.get("transaction_hour")
                }
            )

            return state
        
        except Exception as exc:
            self.add_error(
                state=state,
                message="Error al construir contexto de transacción",
                details={
                    "error": str(exc)
                }
            )
            return state


    def _build_transaction_context(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        
        # Extraccion de instante de transaccion
        transaction_timestamp = transaction.get("timestamp")
        # Extracción de hora de la transacción
        transaction_hour = self._extract_hour(transaction_timestamp)

        # Construir 
        return {
            "transaction_id": transaction.get("transaction_id"),
            "customer_id": transaction.get("customer_id"),
            "amount": transaction.get("amount"),
            "currency": transaction.get("currency"),
            "country": self._normalize_text(transaction.get("country")),
            "channel": self._normalize_text(transaction.get("channel")),
            "device_id": self._normalize_text(transaction.get("device_id")),
            "timestamp": transaction.get("timestamp"),
            "transaction_hour": transaction_hour,
            "merchant_id": self._normalize_text(transaction.get("merchant_id"))
        }
    
    def _extract_hour(self, timestamp: Optional[str]) -> Optional[int]:
        
        # Control de informacion referente a instante de transacción
        if not timestamp:
            return None
        
        # Garantizar el valor en STRING y eliminar espacios en blanco al inico y final
        timestamp = str(timestamp).strip()

        # Formato relativo a datos sinteticos 2026-01-01T23:15:00
        try:
            transaction_hour = datetime.fromisoformat(timestamp).hour
            return transaction_hour
        except ValueError:
            pass

        # Fallback para formato corrupto: 2026-01-01 23:15:00
        try:
            transaction_hour = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").hour
            return transaction_hour
        except ValueError:
            pass

        # Fallback para formato corrupto: 01/01/2026 23:15:00
        try:
            transaction_hour = datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S").hour
            return transaction_hour
        except ValueError:
            pass
        
        return None
    
    def _safe_float(self, value: Any) -> Optional[float]:

        # Retorna vacio si no se declaro vacio el valor explicitamente
        if value is None:
            return None
        
        # Garantizar el formato flotante para variables monetarias
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
        

    def _normalize_text(self, value: Any) -> Optional[str]:
        
        # Retorna vacio si no se declaro vacio el valor explicitamente
        if value is None:
            return None
        
        # Garantizar el valor en STRING y eliminar espacios en blanco al inico y final
        text = str(value).strip()

        # Si no se a ingresado un dato de transacción se retornara vacio
        if text == "":
            return None
        
        return text