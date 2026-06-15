from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import os

# ------------------------------------- Raiz del proyecto y Backend -------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

BACKEND_DIR = PROJECT_ROOT / "backend"
ENV_DIR = BACKEND_DIR / ".env"

if ENV_DIR.exists():
    load_dotenv(ENV_DIR)

# ------------------------------------- Ruta a DATA -------------------------------------
DATA_DIR = BACKEND_DIR / "data"

SOURCE_DATA_DIR = DATA_DIR / "source"
CUSTOMER_BEHIVOR_DIR = SOURCE_DATA_DIR / "customer_behivor.csv"
TRANSACTIONS_DIR = SOURCE_DATA_DIR / "transactions.csv"

AUDIT_DIR = DATA_DIR / "audit"
AUDIT_TRAIL_JSONL = AUDIT_DIR / "audit_trail.jsonl"

HITL_DIR = DATA_DIR / "hitl"
HITL_QUEUE_JSONL = HITL_DIR / "hitl_queue.jsonl"

OBSERVABILITY_DIR = DATA_DIR / "observability"
AGENT_EVENTS_JSONL = OBSERVABILITY_DIR / "agent_events.jsonl"

# ------------------------------------- Ruta a Resources -------------------------------------
RESOURCES_DIR = BACKEND_DIR / "resources"
FRAUD_POLICY_DIR = RESOURCES_DIR / "fraud_policies_nivel_02.json"
EXTERNAL_THREAT_CONTEXT_JSON = RESOURCES_DIR / "external_threat_context.json"


# ------------------------------------- Ruta a RAG -------------------------------------
RAG_DIR = BACKEND_DIR / "rag"

VECTORSTORE_DIR = RAG_DIR / "vectorstore"
POLICY_INDEX_DIR = VECTORSTORE_DIR / "policy_index"

POLICY_CHUNKS_JSON = POLICY_INDEX_DIR / "policy_chunks.json"
POLICY_EMBEDDINGS_NPY = POLICY_INDEX_DIR / "policy_embeddings.npy"
EMBEDDING_CONFIG_JSON = POLICY_INDEX_DIR / "embedding_config.json"

# ------------------------------------- Helpers de configuracion --------------------------------------
def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default

    return str(value).strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


def _to_int_or_none(value: str):
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return int(value)

# ------------------------------------- Configuración de Embeddings -------------------------------------
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").strip().lower()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL","text-embedding-3-small").strip()

EMBEDDING_DIMENSIONS_RAW = os.getenv("EMBEDDING_DIMENSIONS", "").strip()

EMBEDDING_DIMENSIONS = _to_int_or_none(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

# ------------------------------------- OpenAI -------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")   

# ------------------------------------- Configuración LLM para agentes de debate -------------------------------------
LLM_ENABLED = _to_bool(os.getenv("LLM_ENABLED", "false"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER","openai").strip().lower()

LLM_MODEL = os.getenv("LLM_MODEL","gpt-4.1-mini").strip()

LLM_MAX_OUTPUT_TOKENS = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "220").strip())


# ------------------------------------- Azure OpenAI -> proyeccion -------------------------------------
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2024-02-01"
)

# Deployment para chat / LLM
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Deployment para embeddings
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

# Compatibilidad con nombre anterior
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
# Deployment final usado por embedding_client.py
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_RESOLVED = (
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
    or AZURE_OPENAI_EMBEDDING_DEPLOYMENT
)

# ------------------------------------- Azure AI Search -------------------------------------
AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_AI_SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
AZURE_AI_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")


# ------------------------------------- Azure Cosmos DB -------------------------------------
AZURE_COSMOS_ENDPOINT = os.getenv("AZURE_COSMOS_ENDPOINT")
AZURE_COSMOS_KEY = os.getenv("AZURE_COSMOS_KEY")
AZURE_COSMOS_DATABASE_NAME = os.getenv("AZURE_COSMOS_DATABASE_NAME")

# ------------------------------------- Aplications Insights --------------------------------
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

# ------------------------------------- Azure Key Vault --------------------------------
KEY_VAULT_NAME = os.getenv("KEY_VAULT_NAME")


# ------------------------------------- Validacion de Embeddings ------------------------------------- 
def validate_embedding_environment() -> None:

    """
        Valida la configuración de credenciales configuradas
    """

    if EMBEDDING_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY no está configurado para EMBEDDING_PROVIDER=openai."
            )

    elif EMBEDDING_PROVIDER == "azure_openai":
        missing = []

        if not AZURE_OPENAI_API_KEY:
            missing.append("AZURE_OPENAI_API_KEY")

        if not AZURE_OPENAI_ENDPOINT:
            missing.append("AZURE_OPENAI_ENDPOINT")

        if not AZURE_OPENAI_EMBEDDING_DEPLOYMENT:
            missing.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

        if not AZURE_OPENAI_EMBEDDING_DEPLOYMENT_RESOLVED:
            missing.append(
                "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
                "or AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
            )

        if missing:
            raise ValueError(
                "Faltan variables de entorno para Azure OpenAI: "
                + ", ".join(missing)
            )

    else:
        raise ValueError(
            f"Proveedor de embeddings no soportado: {EMBEDDING_PROVIDER}"
        )
    
# ------------------------------------- Validacion de LLM  -------------------------------------
def validate_llm_environment() -> None:
    """
        Valida la configuración de credenciales para agentes con LLM.
        Si LLM_ENABLED=false, no obliga a tener API key.
    """

    if not LLM_ENABLED:
        return

    if LLM_PROVIDER == "openai":

        missing = []

        if not OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")

        if not LLM_MODEL:
            missing.append("LLM_MODEL")

        if missing:
            raise ValueError(
                "Faltan variables para LLM_PROVIDER=openai: "
                + ", ".join(missing)
            )
        
    elif LLM_PROVIDER == "azure_openai":
        missing = []

        if not AZURE_OPENAI_ENDPOINT:
            missing.append("AZURE_OPENAI_ENDPOINT")

        if not AZURE_OPENAI_API_KEY:
            missing.append("AZURE_OPENAI_API_KEY")

        if not AZURE_OPENAI_API_VERSION:
            missing.append("AZURE_OPENAI_API_VERSION")

        if not AZURE_OPENAI_DEPLOYMENT_NAME:
            missing.append("AZURE_OPENAI_DEPLOYMENT_NAME")

        if missing:
            raise ValueError(
                "Faltan variables para LLM_PROVIDER=azure_openai: "
                + ", ".join(missing)
            )

    else:
        raise ValueError(
            f"Proveedor LLM no soportado: {LLM_PROVIDER}"
        )
    