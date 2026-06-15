import os
from typing import Any, Dict


def as_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in ["1", "true", "yes", "y", "on"]


APP_VERSION = os.getenv("APP_VERSION", "4.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local_jsonl")
RAG_PROVIDER = os.getenv("RAG_PROVIDER", "local_vectorstore")
SECRET_PROVIDER = os.getenv("SECRET_PROVIDER", "env")

LLM_ENABLED = as_bool(os.getenv("LLM_ENABLED"), default=False)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")
OBSERVABILITY_PROVIDER = os.getenv("OBSERVABILITY_PROVIDER", "local_jsonl")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2024-02-15-preview"
)


AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
)

AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_AI_SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
AZURE_AI_SEARCH_INDEX_NAME = os.getenv(
    "AZURE_AI_SEARCH_INDEX_NAME",
    "fraud-policy-index"
)

AZURE_COSMOS_ENDPOINT = os.getenv("AZURE_COSMOS_ENDPOINT")
AZURE_COSMOS_KEY = os.getenv("AZURE_COSMOS_KEY")
AZURE_COSMOS_DATABASE_NAME = os.getenv("AZURE_COSMOS_DATABASE_NAME")

APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv(
    "APPLICATIONINSIGHTS_CONNECTION_STRING"
)

AUTH_ENABLED = as_bool(os.getenv("AUTH_ENABLED"), default=False)
API_KEY = os.getenv("API_KEY")

def is_cloud_environment() -> bool:
    return ENVIRONMENT.strip().lower() in {
        "cloud",
        "azure",
        "production",
        "prod",
    }

def get_runtime_metadata() -> Dict[str, Any]:
    return {
        "app_version": APP_VERSION,
        "environment": ENVIRONMENT,
        "storage_provider": STORAGE_PROVIDER,
        "rag_provider": RAG_PROVIDER,
        "secret_provider": SECRET_PROVIDER,
        "llm_enabled": LLM_ENABLED,
        "llm_provider": LLM_PROVIDER,
        "embedding_provider": EMBEDDING_PROVIDER,
        "observability_provider": OBSERVABILITY_PROVIDER,
        "auth_enabled": AUTH_ENABLED,
    }