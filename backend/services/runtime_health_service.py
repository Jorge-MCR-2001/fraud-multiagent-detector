from typing import Any, Dict

from settings.paths import (
    AGENT_EVENTS_JSONL,
    AUDIT_TRAIL_JSONL,
    CUSTOMER_BEHAVIOR_CSV,
    EXTERNAL_THREAT_CONTEXT_JSON,
    FRAUD_POLICY_JSON,
    HITL_QUEUE_JSONL,
    POLICY_CHUNKS_JSON,
    POLICY_EMBEDDINGS_NPY,
    TRANSACTIONS_CSV,
)

from settings.runtime_config import (
    API_KEY,
    APPLICATIONINSIGHTS_CONNECTION_STRING,
    AUTH_ENABLED,
    AZURE_AI_SEARCH_API_KEY,
    AZURE_AI_SEARCH_ENDPOINT,
    AZURE_AI_SEARCH_INDEX_NAME,
    AZURE_COSMOS_DATABASE_NAME,
    AZURE_COSMOS_ENDPOINT,
    AZURE_COSMOS_KEY,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_ENDPOINT,
    ENVIRONMENT,
    LLM_ENABLED,
    LLM_PROVIDER,
    OBSERVABILITY_PROVIDER,
    OPENAI_API_KEY,
    RAG_PROVIDER,
    STORAGE_PROVIDER,
    get_runtime_metadata,
)

SUPPORTED_STORAGE_PROVIDERS = {
    "local_jsonl",
    "azure_cosmos",
}

SUPPORTED_RAG_PROVIDERS = {
    "local_vectorstore",
    "azure_ai_search",
}

SUPPORTED_OBSERVABILITY_PROVIDERS = {
    "local_jsonl",
    "application_insights",
}

SUPPORTED_LLM_PROVIDERS = {
    "openai",
    "azure_openai",
}


def _check_file(path) -> Dict[str, Any]:
    return {
        "ok": path.exists(),
        "path": str(path),
    }

def _check_parent_writable(path) -> Dict[str, Any]:
    parent = path.parent

    return {
        "ok": parent.exists() and parent.is_dir(),
        "path": str(path),
        "parent": str(parent),
    }


def _check_env_value(value: str | None, secret: bool = False) -> Dict[str, Any]:
    exists = bool(value)

    return {
        "ok": exists,
        "configured": exists,
        "value": "***" if exists and secret else value,
    }


def build_liveness_status() -> Dict[str, Any]:
    return {
        "status": "alive",
        "service": "multi-agent-fraud-api",
        "level": "4",
        "runtime": get_runtime_metadata(),
    }


def build_readiness_status() -> Dict[str, Any]:
    checks: Dict[str, Any] = {}

    checks["storage_provider_supported"] = {
        "ok": STORAGE_PROVIDER in SUPPORTED_STORAGE_PROVIDERS,
        "value": STORAGE_PROVIDER,
        "supported": sorted(SUPPORTED_STORAGE_PROVIDERS),
    }

    checks["rag_provider_supported"] = {
        "ok": RAG_PROVIDER in SUPPORTED_RAG_PROVIDERS,
        "value": RAG_PROVIDER,
        "supported": sorted(SUPPORTED_RAG_PROVIDERS),
    }

    checks["observability_provider_supported"] = {
        "ok": OBSERVABILITY_PROVIDER in SUPPORTED_OBSERVABILITY_PROVIDERS,
        "value": OBSERVABILITY_PROVIDER,
        "supported": sorted(SUPPORTED_OBSERVABILITY_PROVIDERS),
    }

    checks["transactions_csv"] = _check_file(TRANSACTIONS_CSV)
    checks["customer_behavior_csv"] = _check_file(CUSTOMER_BEHAVIOR_CSV)
    checks["fraud_policy_json"] = _check_file(FRAUD_POLICY_JSON)
    checks["external_threat_context_json"] = _check_file(EXTERNAL_THREAT_CONTEXT_JSON)

    if STORAGE_PROVIDER == "local_jsonl":
        checks["audit_trail_parent"] = _check_parent_writable(AUDIT_TRAIL_JSONL)
        checks["hitl_queue_parent"] = _check_parent_writable(HITL_QUEUE_JSONL)

    elif STORAGE_PROVIDER == "azure_cosmos":
        checks["azure_cosmos_endpoint"] = _check_env_value(AZURE_COSMOS_ENDPOINT)
        checks["azure_cosmos_key"] = _check_env_value(
            AZURE_COSMOS_KEY,
            secret=True,
        )
        checks["azure_cosmos_database_name"] = _check_env_value(
            AZURE_COSMOS_DATABASE_NAME
        )

    if RAG_PROVIDER == "local_vectorstore":
        checks["policy_chunks_json"] = _check_file(POLICY_CHUNKS_JSON)
        checks["policy_embeddings_npy"] = _check_file(POLICY_EMBEDDINGS_NPY)

    elif RAG_PROVIDER == "azure_ai_search":
        checks["azure_ai_search_endpoint"] = _check_env_value(
            AZURE_AI_SEARCH_ENDPOINT
        )
        checks["azure_ai_search_api_key"] = _check_env_value(
            AZURE_AI_SEARCH_API_KEY,
            secret=True,
        )
        checks["azure_ai_search_index_name"] = _check_env_value(
            AZURE_AI_SEARCH_INDEX_NAME
        )

    if OBSERVABILITY_PROVIDER == "local_jsonl":
        checks["agent_events_parent"] = _check_parent_writable(AGENT_EVENTS_JSONL)

    elif OBSERVABILITY_PROVIDER == "application_insights":
        checks["applicationinsights_connection_string"] = _check_env_value(
            APPLICATIONINSIGHTS_CONNECTION_STRING,
            secret=True,
        )

    if LLM_ENABLED:
        checks["llm_provider_supported"] = {
            "ok": LLM_PROVIDER in SUPPORTED_LLM_PROVIDERS,
            "value": LLM_PROVIDER,
            "supported": sorted(SUPPORTED_LLM_PROVIDERS),
        }

        if LLM_PROVIDER == "openai":
            checks["openai_api_key"] = _check_env_value(
                OPENAI_API_KEY,
                secret=True,
            )

        elif LLM_PROVIDER == "azure_openai":
            checks["azure_openai_endpoint"] = _check_env_value(
                AZURE_OPENAI_ENDPOINT
            )
            checks["azure_openai_api_key"] = _check_env_value(
                AZURE_OPENAI_API_KEY,
                secret=True,
            )
            checks["azure_openai_deployment_name"] = _check_env_value(
                AZURE_OPENAI_DEPLOYMENT_NAME
            )

    else:
        checks["llm_disabled"] = {
            "ok": True,
            "message": "LLM is disabled; deterministic fallback mode is allowed.",
        }

    if AUTH_ENABLED:
        checks["api_key"] = _check_env_value(
            API_KEY,
            secret=True,
        )
    else:
        checks["auth_disabled"] = {
            "ok": True,
            "message": "AUTH_ENABLED=false. API key validation is disabled.",
        }

    ready = all(
        check.get("ok", False)
        for check in checks.values()
    )

    return {
        "status": "ready" if ready else "not_ready",
        "level": "4",
        "environment": ENVIRONMENT,
        "runtime": get_runtime_metadata(),
        "checks": checks,
    }