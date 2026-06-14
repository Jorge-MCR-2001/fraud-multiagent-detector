from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

# Clase basica para la trazabilidad de informacion entre grafos
class BaseAgent(ABC):

    name: str = "BaseAgent"

    @abstractmethod
    # Formato de metodo de ejecución de nodos (por cada agente)
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
    
    def add_trace(self, state: Dict[str, Any], status: str = "completed", details: Optional[Dict[str, Any]] = None) -> None:
        # Añadir un rastro al agente
        state.setdefault("agent_trace", []).append(
            {
                "agent": self.name,
                "status": status,
                "details": details or {}
            }
        )

    def add_error(self, state: Dict[str, Any], message: str, details: Optional[Dict[str, Any]] = None) -> None:

        # Añadir un rastro de error controlado para el agente
        state.setdefault("error", []).append(
            {
                "agent": self.name,
                "message": message,
                "details": details or {}
            }
        )

        # Añadir rastro al agente
        self.add_trace(
            state=state,
            status="error",
            details={
                "message":message
            }
        )