# backend/settings/paths.py

from pathlib import Path
from dotenv import load_dotenv
import os


# -------------------------------------
# Raíz del proyecto y backend
# -------------------------------------

_DEFAULT_BACKEND_DIR = Path(__file__).resolve().parents[1]

BACKEND_DIR = Path(
    os.getenv("BACKEND_DIR", str(_DEFAULT_BACKEND_DIR))
).resolve()

PROJECT_ROOT = BACKEND_DIR.parent

ENV_DIR = BACKEND_DIR / ".env"

if ENV_DIR.exists():
    load_dotenv(ENV_DIR)


# -------------------------------------
# DATA
# -------------------------------------

DATA_DIR = BACKEND_DIR / "data"

SOURCE_DATA_DIR = DATA_DIR / "source"

TRANSACTIONS_CSV = SOURCE_DATA_DIR / "transactions.csv"
CUSTOMER_BEHAVIOR_CSV = SOURCE_DATA_DIR / "customer_behivor.csv"

# Backward compatibility con nombres usados en el proyecto
TRANSACTIONS_DIR = TRANSACTIONS_CSV
CUSTOMER_BEHIVOR_DIR = CUSTOMER_BEHAVIOR_CSV


# -------------------------------------
# Audit Trail local
# -------------------------------------

AUDIT_DIR = DATA_DIR / "audit"
AUDIT_TRAIL_JSONL = AUDIT_DIR / "audit_trail.jsonl"


# -------------------------------------
# HITL Queue local
# -------------------------------------

HITL_DIR = DATA_DIR / "hitl"
HITL_QUEUE_JSONL = HITL_DIR / "hitl_queue.jsonl"


# -------------------------------------
# Observabilidad local
# -------------------------------------

OBSERVABILITY_DIR = DATA_DIR / "observability"
AGENT_EVENTS_JSONL = OBSERVABILITY_DIR / "agent_events.jsonl"


# -------------------------------------
# Resources
# -------------------------------------

RESOURCES_DIR = BACKEND_DIR / "resources"

FRAUD_POLICY_JSON = RESOURCES_DIR / "fraud_policies_nivel_02.json"
EXTERNAL_THREAT_CONTEXT_JSON = RESOURCES_DIR / "external_threat_context.json"

# Backward compatibility con nombre usado previamente
FRAUD_POLICY_DIR = FRAUD_POLICY_JSON


# -------------------------------------
# RAG local
# -------------------------------------

RAG_DIR = BACKEND_DIR / "rag"

VECTORSTORE_DIR = RAG_DIR / "vectorstore"
POLICY_INDEX_DIR = VECTORSTORE_DIR / "policy_index"

POLICY_CHUNKS_JSON = POLICY_INDEX_DIR / "policy_chunks.json"
POLICY_EMBEDDINGS_NPY = POLICY_INDEX_DIR / "policy_embeddings.npy"
EMBEDDING_CONFIG_JSON = POLICY_INDEX_DIR / "embedding_config.json"


# -------------------------------------
# Helpers de directorios locales
# -------------------------------------

def ensure_local_directories() -> None:
    """
    Crea directorios locales necesarios para ejecución en modo local_jsonl.
    No crea archivos de datos fuente.
    """

    for directory in [
        DATA_DIR,
        AUDIT_DIR,
        HITL_DIR,
        OBSERVABILITY_DIR,
        POLICY_INDEX_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)


def get_paths_metadata() -> dict:
    """
    Devuelve rutas principales para health checks o debugging controlado.
    No incluye secretos ni variables cloud.
    """

    return {
        "backend_dir": str(BACKEND_DIR),
        "data_dir": str(DATA_DIR),
        "source_data_dir": str(SOURCE_DATA_DIR),
        "transactions_csv": str(TRANSACTIONS_CSV),
        "customer_behavior_csv": str(CUSTOMER_BEHAVIOR_CSV),
        "audit_trail_jsonl": str(AUDIT_TRAIL_JSONL),
        "hitl_queue_jsonl": str(HITL_QUEUE_JSONL),
        "agent_events_jsonl": str(AGENT_EVENTS_JSONL),
        "resources_dir": str(RESOURCES_DIR),
        "fraud_policy_json": str(FRAUD_POLICY_JSON),
        "external_threat_context_json": str(EXTERNAL_THREAT_CONTEXT_JSON),
        "policy_chunks_json": str(POLICY_CHUNKS_JSON),
        "policy_embeddings_npy": str(POLICY_EMBEDDINGS_NPY),
    }
