import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from app import app
from services.runtime_health_service import build_readiness_status
from settings.runtime_config import as_bool


client = TestClient(app)


def test_root_endpoint_reports_level_4():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "running"
    assert data["level"] == "4"
    assert data["architecture"] == "langgraph_multi_agent_cloud_ready"
    assert "runtime" in data


def test_liveness_endpoint_is_available():
    response = client.get("/health/live")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "alive"
    assert data["level"] == "4"
    assert data["service"] == "multi-agent-fraud-api"


def test_readiness_endpoint_has_cloud_runtime_contract():
    response = client.get("/health/ready")

    assert response.status_code in [200, 503]

    payload = response.json()
    data = payload if response.status_code == 200 else payload["detail"]

    assert data["level"] == "4"
    assert data["status"] in ["ready", "not_ready"]
    assert "environment" in data
    assert "runtime" in data
    assert "checks" in data

    checks = data["checks"]

    assert "storage_provider_supported" in checks
    assert "rag_provider_supported" in checks
    assert "observability_provider_supported" in checks
    assert "transactions_csv" in checks
    assert "customer_behavior_csv" in checks
    assert "fraud_policy_json" in checks


def test_readiness_service_returns_boolean_checks():
    readiness = build_readiness_status()

    assert readiness["status"] in ["ready", "not_ready"]
    assert isinstance(readiness["checks"], dict)

    for check in readiness["checks"].values():
        assert "ok" in check
        assert isinstance(check["ok"], bool)


def test_as_bool_parses_environment_strings_correctly():
    assert as_bool("true") is True
    assert as_bool("True") is True
    assert as_bool("1") is True
    assert as_bool("yes") is True
    assert as_bool("on") is True

    assert as_bool("false") is False
    assert as_bool("False") is False
    assert as_bool("0") is False
    assert as_bool("no") is False
    assert as_bool("off") is False
    assert as_bool("") is False

    assert as_bool(None, default=False) is False
    assert as_bool(None, default=True) is True