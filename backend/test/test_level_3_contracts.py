import sys
from pathlib import Path
import json

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


EXPECTED_DECISIONS = {
    "T-1003": "APPROVE",
    "T-1004": "BLOCK",
    "T-1005": "ESCALATE_TO_HUMAN",
    "T-1007": "CHALLENGE",
}


def test_root_endpoint_reports_level_3_ready_components():
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"
    assert data["level"] in ["2", "3", "4"]
    assert data["rag_enabled"] is True
    assert data["hitl_enabled"] is True
    assert data["audit_trail_enabled"] is True


def test_expected_decisions_for_core_transactions():
    for transaction_id, expected_decision in EXPECTED_DECISIONS.items():
        response = client.get(f"/evaluate/{transaction_id}")
        assert response.status_code == 200

        data = response.json()

        assert data["transaction_id"] == transaction_id
        assert data["decision"] == expected_decision
        assert 0.0 <= data["confidence"] <= 1.0


def test_response_contains_required_level_3_contract_fields():
    response = client.get("/evaluate/T-1007")
    assert response.status_code == 200

    data = response.json()

    required_fields = [
        "transaction_id",
        "decision",
        "confidence",
        "confidence_level",
        "confidence_factors",
        "decision_basis",
        "decision_rationale",
        "requires_human_review",
        "signals",
        "signal_tags",
        "signal_metrics",
        "citations_internal",
        "citations_external",
        "evidence_bundle",
        "pro_fraud_argument",
        "pro_customer_argument",
        "explanation_customer",
        "explanation_audit",
        "hitl_required",
        "hitl_reason",
        "hitl_queue_item",
        "audit_saved",
        "audit_event_id",
        "agent_trace",
        "decision_trace",
        "errors",
    ]

    for field in required_fields:
        assert field in data


def test_decision_basis_is_structured():
    response = client.get("/evaluate/T-1003")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["decision_basis"], dict)
    assert "basis_type" in data["decision_basis"]
    assert "applied_rule" in data["decision_basis"]


def test_agent_trace_is_not_empty():
    response = client.get("/evaluate/T-1007")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["agent_trace"], list)
    assert len(data["agent_trace"]) > 0


def test_decision_trace_is_not_empty():
    response = client.get("/evaluate/T-1007")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["decision_trace"], list)
    assert len(data["decision_trace"]) > 0

    for item in data["decision_trace"]:
        assert "step" in item
        assert "value" in item


def test_internal_and_external_citations_are_present_when_expected():
    response = client.get("/evaluate/T-1007")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["citations_internal"], list)
    assert isinstance(data["citations_external"], list)

    assert len(data["citations_internal"]) > 0
    assert len(data["citations_external"]) > 0


def test_hitl_case_generates_human_review_fields():
    response = client.get("/evaluate/T-1005")
    assert response.status_code == 200

    data = response.json()

    assert data["decision"] == "ESCALATE_TO_HUMAN"
    assert data["requires_human_review"] is True
    assert data["hitl_required"] is True
    assert data["hitl_reason"] is not None
    assert data["hitl_queue_item"] is not None


def test_audit_trail_is_saved():
    response = client.get("/evaluate/T-1007")
    assert response.status_code == 200

    data = response.json()

    assert data["audit_saved"] is True
    assert data["audit_event_id"] is not None


def test_audit_trail_file_contains_valid_jsonl_entries():
    response = client.get("/evaluate/T-1007")
    assert response.status_code == 200

    data = response.json()
    assert data["audit_saved"] is True
    assert data["audit_event_id"] is not None

    audit_file = Path("data/audit/audit_trail.jsonl")
    assert audit_file.exists()

    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) > 0

    last_event = json.loads(lines[-1])

    assert "audit_event_id" in last_event
    assert "evaluation_id" in last_event
    assert "transaction_id" in last_event
    assert "final_decision" in last_event
    assert "confidence" in last_event
    assert "decision_basis" in last_event
    assert "agent_trace" in last_event
    assert "decision_trace" in last_event
    assert "created_at" in last_event


def test_hitl_queue_endpoint_lists_pending_items():
    response_eval = client.get("/evaluate/T-1005")
    assert response_eval.status_code == 200

    eval_data = response_eval.json()
    assert eval_data["hitl_required"] is True
    assert eval_data["hitl_queue_item"] is not None

    response_queue = client.get("/hitl/queue")
    assert response_queue.status_code == 200

    queue_data = response_queue.json()

    assert "item_count" in queue_data
    assert "items" in queue_data
    assert queue_data["item_count"] >= 1

    item_ids = [
        item["hitl_queue_id"]
        for item in queue_data["items"]
    ]

    assert eval_data["hitl_queue_item"]["hitl_queue_id"] in item_ids


def test_hitl_queue_item_can_be_read_by_id():
    response_eval = client.get("/evaluate/T-1005")
    assert response_eval.status_code == 200

    eval_data = response_eval.json()
    hitl_queue_id = eval_data["hitl_queue_item"]["hitl_queue_id"]

    response_item = client.get(f"/hitl/queue/{hitl_queue_id}")
    assert response_item.status_code == 200

    item = response_item.json()

    assert item["hitl_queue_id"] == hitl_queue_id
    assert item["transaction_id"] == "T-1005"
    assert item["status"] == "PENDING_REVIEW"


def test_hitl_queue_item_can_be_resolved():
    response_eval = client.get("/evaluate/T-1005")
    assert response_eval.status_code == 200

    eval_data = response_eval.json()
    hitl_queue_id = eval_data["hitl_queue_item"]["hitl_queue_id"]

    payload = {
        "reviewer": "analyst_01",
        "resolution": "APPROVE",
        "notes": "Cliente validado manualmente."
    }

    response_resolve = client.post(
        f"/hitl/queue/{hitl_queue_id}/resolve",
        json=payload,
    )

    assert response_resolve.status_code == 200

    resolved_data = response_resolve.json()
    item = resolved_data["item"]

    assert resolved_data["resolved"] is True
    assert item["hitl_queue_id"] == hitl_queue_id
    assert item["status"] == "RESOLVED"
    assert item["reviewer"] == "analyst_01"
    assert item["resolution"] == "APPROVE"
    assert item["resolution_notes"] == "Cliente validado manualmente."
    assert item["resolved_at"] is not None

def test_confidence_scoring_is_formalized():
    response = client.get("/evaluate/T-1007")
    assert response.status_code == 200

    data = response.json()

    assert "confidence" in data
    assert "confidence_level" in data
    assert "confidence_factors" in data

    assert data["confidence_level"] in ["HIGH", "MEDIUM", "LOW"]
    assert isinstance(data["confidence_factors"], list)
    assert len(data["confidence_factors"]) > 0

    for factor in data["confidence_factors"]:
        assert "factor" in factor
        assert "impact" in factor
        assert "direction" in factor
        assert "description" in factor
        assert "evidence" in factor

def test_agent_events_observability_file_is_written():
    response = client.get("/evaluate/T-1007")
    assert response.status_code == 200

    agent_events_file = Path("data/observability/agent_events.jsonl")
    assert agent_events_file.exists()

    lines = agent_events_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) > 0

    last_event = json.loads(lines[-1])

    assert "event_id" in last_event
    assert "transaction_id" in last_event
    assert "agent" in last_event
    assert "status" in last_event
    assert "details" in last_event
    assert "created_at" in last_event

    assert last_event["transaction_id"] == "T-1007"

def test_unknown_transaction_returns_controlled_error():
    response = client.get("/evaluate/T-9999")

    assert response.status_code == 404

    data = response.json()
    detail = data["detail"]

    assert detail["status"] == "error"
    assert detail["error_code"] == "TRANSACTION_NOT_FOUND"
    assert "trace_id" in detail
    assert detail["details"]["transaction_id"] == "T-9999"


def test_unknown_hitl_item_returns_controlled_error():
    response = client.get("/hitl/queue/HITL-NOT-FOUND")

    assert response.status_code == 404

    data = response.json()
    detail = data["detail"]

    assert detail["status"] == "error"
    assert detail["error_code"] == "HITL_ITEM_NOT_FOUND"
    assert "trace_id" in detail
    assert detail["details"]["hitl_queue_id"] == "HITL-NOT-FOUND"


def test_resolve_unknown_hitl_item_returns_controlled_error():
    payload = {
        "reviewer": "analyst_01",
        "resolution": "APPROVE",
        "notes": "Intento de resolución para item inexistente."
    }

    response = client.post(
        "/hitl/queue/HITL-NOT-FOUND/resolve",
        json=payload,
    )

    assert response.status_code == 404

    data = response.json()
    detail = data["detail"]

    assert detail["status"] == "error"
    assert detail["error_code"] == "HITL_ITEM_NOT_FOUND"
    assert "trace_id" in detail
    assert detail["details"]["hitl_queue_id"] == "HITL-NOT-FOUND"