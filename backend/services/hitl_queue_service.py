import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from settings.paths import HITL_QUEUE_JSONL


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _ensure_hitl_file() -> None:
    HITL_QUEUE_JSONL.parent.mkdir(parents=True, exist_ok=True)

    if not HITL_QUEUE_JSONL.exists():
        HITL_QUEUE_JSONL.write_text("", encoding="utf-8")


def _read_all_items() -> List[Dict[str, Any]]:
    _ensure_hitl_file()

    items: List[Dict[str, Any]] = []

    with HITL_QUEUE_JSONL.open("r", encoding="utf-8") as file:
        for line in file:
            raw_line = line.strip()

            if not raw_line:
                continue

            items.append(json.loads(raw_line))

    return items


def _write_all_items(items: List[Dict[str, Any]]) -> None:
    _ensure_hitl_file()

    with HITL_QUEUE_JSONL.open("w", encoding="utf-8") as file:
        for item in items:
            file.write(json.dumps(item, ensure_ascii=False) + "\n")


def _append_item(item: Dict[str, Any]) -> None:
    _ensure_hitl_file()

    with HITL_QUEUE_JSONL.open("a", encoding="utf-8") as file:
        file.write(json.dumps(item, ensure_ascii=False) + "\n")


def _resolve_priority(state: Dict[str, Any]) -> str:
    confidence = state.get("confidence", 0.0)
    decision = state.get("decision")

    if decision == "ESCALATE_TO_HUMAN" and confidence <= 0.60:
        return "HIGH"

    if state.get("requires_human_review") is True:
        return "MEDIUM"

    return "LOW"


def build_hitl_queue_item(state: Dict[str, Any], reason: Optional[str] = None) -> Dict[str, Any]:
    
    transaction_id = state.get("transaction_id", "UNKNOWN")
    created_at = _utc_now_iso()

    hitl_queue_id = f"HITL-{transaction_id}-{_utc_now_compact()}"

    return {
        "hitl_queue_id": hitl_queue_id,
        "transaction_id": transaction_id,
        "reason": reason or state.get("hitl_reason") or "Human review required.",
        "priority": _resolve_priority(state),
        "status": "PENDING_REVIEW",

        "original_decision": state.get("decision"),
        "original_confidence": state.get("confidence"),
        "requires_human_review": state.get("requires_human_review", True),

        "decision_snapshot": {
            "decision": state.get("decision"),
            "confidence": state.get("confidence"),
            "decision_basis": state.get("decision_basis", {}),
            "decision_rationale": state.get("decision_rationale", ""),
            "citations_internal": state.get("citations_internal", []),
            "citations_external": state.get("citations_external", []),
            "agent_trace": state.get("agent_trace", []),
            "decision_trace": state.get("decision_trace", []),
        },

        "assigned_to": None,
        "reviewer": None,
        "resolution": None,
        "resolution_notes": None,

        "created_at": created_at,
        "resolved_at": None,
    }


def enqueue_hitl_case(state: Dict[str, Any], reason: Optional[str] = None) -> Dict[str, Any]:

    item = build_hitl_queue_item(state=state, reason=reason)
    _append_item(item)
    return item


def list_hitl_queue(status: Optional[str] = None) -> List[Dict[str, Any]]:
    items = _read_all_items()

    if status:
        normalized_status = status.upper()
        items = [
            item for item in items
            if str(item.get("status", "")).upper() == normalized_status
        ]

    return items


def get_hitl_item(hitl_queue_id: str) -> Optional[Dict[str, Any]]:
    items = _read_all_items()

    for item in items:
        if item.get("hitl_queue_id") == hitl_queue_id:
            return item

    return None


def resolve_hitl_item(hitl_queue_id: str, reviewer: str, resolution: str, notes: Optional[str] = None) -> Dict[str, Any]:
    items = _read_all_items()

    for item in items:
        if item.get("hitl_queue_id") == hitl_queue_id:
            item["status"] = "RESOLVED"
            item["reviewer"] = reviewer
            item["resolution"] = resolution
            item["resolution_notes"] = notes
            item["resolved_at"] = _utc_now_iso()

            _write_all_items(items)

            return item

    raise ValueError(f"No se encontró el item HITL: {hitl_queue_id}")