from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from datetime import datetime, timezone

from services.observability_service import save_agent_event

# Clase basica para la trazabilidad de informacion entre grafos
class BaseAgent(ABC):

    name: str = "BaseAgent"

    @abstractmethod
    # Formato de metodo de ejecución de nodos (por cada agente)
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
    
    def _utc_now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()
    
    def add_trace(self, state: Dict[str, Any], status: str = "completed", details: Optional[Dict[str, Any]] = None) -> None:
        
        trace_item = {
            "agent": self.name,
            "status": status,
            "details": details or {},
            "timestamp": self._utc_now_iso(),
        }
        
        if "agent_trace" not in state or state["agent_trace"] is None:
            state["agent_trace"] = []

        # Añadir un rastro al agente
        state["agent_trace"].append(trace_item)

        try:
            save_agent_event(
                state=state,
                agent_name=self.name,
                status=status,
                details=details or {},
                message=None,
                latency_ms=None,
            )

        except Exception as exc:
            # No debe romper el flujo principal si falla la observabilidad.
            if "observability_errors" not in state:
                state["observability_errors"] = []

            state["observability_errors"].append({
                "agent": self.name,
                "error": str(exc),
                "timestamp": self._utc_now_iso(),
            })

    def add_error(self, state: Dict[str, Any], message: str, details: Optional[Dict[str, Any]] = None) -> None:

        # Registra los errores en memoria y tambien en evento observable

        error_item = {
            "agent": self.name,
            "message": message,
            "details": details or {},
            "timestamp": self._utc_now_iso(),
        }

        if "errors" not in state or state["errors"] is None:
            state["errors"] = []

        # Añadir un rastro de error controlado para el agente
        state["errors"].append(error_item)

        try:
            save_agent_event(
                state=state,
                agent_name=self.name,
                status="error",
                details=details or {},
                message=message,
                latency_ms=None,
            )

        except Exception as exc:
            if "observability_errors" not in state:
                state["observability_errors"] = []

            state["observability_errors"].append({
                "agent": self.name,
                "error": str(exc),
                "timestamp": self._utc_now_iso(),
            })