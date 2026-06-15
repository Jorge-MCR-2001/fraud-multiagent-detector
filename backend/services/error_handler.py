from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


def build_trace_id() -> str:
    return f"ERR-{uuid4()}"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_error_response(error_code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "status": "error",
        "error_code": error_code,
        "message": message,
        "trace_id": build_trace_id(),
        "details": {
            **(details or {}),
            "timestamp": utc_now_iso(),
        },
    }