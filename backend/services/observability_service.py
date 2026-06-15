import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from settings.paths import AGENT_EVENTS_JSONL


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_observability_file() -> None:
    """
        Garantiza que exista la carpeta y el archivo JSONL de observabilidad.
    """

    AGENT_EVENTS_JSONL.parent.mkdir(parents=True, exist_ok=True)

    if not AGENT_EVENTS_JSONL.exists():
        AGENT_EVENTS_JSONL.write_text("", encoding="utf-8")


def build_agent_event(
    state: Dict[str, Any],
    agent_name: str,
    status: str,
    details: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    latency_ms: Optional[float] = None,
) -> Dict[str, Any]:
    """
        Construye un evento observable por agente.

        Ojo: Este evento no reemplaza agent_trace.
            Es una capa persistente para auditoría técnica / observabilidad.
    """

    transaction_id = state.get("transaction_id", "UNKNOWN")
    evaluation_id = state.get("evaluation_id")

    return {
        "event_id": f"AGENT-EVENT-{uuid4()}",
        "evaluation_id": evaluation_id,
        "transaction_id": transaction_id,
        "agent": agent_name,
        "status": status,
        "message": message,
        "latency_ms": latency_ms,
        "details": details or {},
        "created_at": _utc_now_iso(),
    }


def save_agent_event(
    state: Dict[str, Any],
    agent_name: str,
    status: str,
    details: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    latency_ms: Optional[float] = None,
) -> Dict[str, Any]:
    """
        Guarda un evento de agente en data/observability/agent_events.jsonl.
    """

    _ensure_observability_file()

    event = build_agent_event(
        state=state,
        agent_name=agent_name,
        status=status,
        details=details,
        message=message,
        latency_ms=latency_ms,
    )

    # Abre y escribe sobre el evento de agentes
    with AGENT_EVENTS_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event