from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import os

# ------------------------------------- Raiz del proyecto y Backend -------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

BACKEND_DIR = PROJECT_ROOT / "backend"
load_dotenv(find_dotenv())

# ------------------------------------- Ruta a DATA -------------------------------------
DATA_DIR = BACKEND_DIR / "data"
CUSTOMER_BEHIVOR_DIR = DATA_DIR / "customer_behivor.csv"
TRANSACTIONS_DIR = DATA_DIR / "transactions.csv"

# ------------------------------------- Ruta a Resources -------------------------------------
RESOURCES_DIR = BACKEND_DIR / "resources"
FRAUD_POLICY_DIR = RESOURCES_DIR / "fraud_policies_nivel_02.json"

# ------------------------------------- Ruta a RAG -------------------------------------
RAG_DIR = BACKEND_DIR / "rag"

VECTORSTORE_DIR = RAG_DIR / "vectorstore"
POLICY_INDEX_DIR = VECTORSTORE_DIR / "policy_index"

POLICY_CHUNKS_JSON = POLICY_INDEX_DIR / "policy_chunks.json"
POLICY_EMBEDDINGS_NPY = POLICY_INDEX_DIR / "policy_embeddings.npy"
EMBEDDING_CONFIG_JSON = POLICY_INDEX_DIR / "embedding_config.json"

# ------------------------------------- Configuración de Embeddings -------------------------------------
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").strip().lower()

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-3-small"
).strip()

EMBEDDING_DIMENSIONS_RAW = os.getenv("EMBEDDING_DIMENSIONS", "").strip()

EMBEDDING_DIMENSIONS = (
    int(EMBEDDING_DIMENSIONS_RAW)
    if EMBEDDING_DIMENSIONS_RAW
    else None
)

# ------------------------------------- OpenAI -------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ------------------------------------- Azure OpenAI -> proyeccion -------------------------------------

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2024-02-01"
)
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
)


# ------------------------------------- Validaciones ------------------------------------- 

def validate_embedding_environment() -> None:

    """
        Valida la configuración de credenciales configuradas
    """

    if EMBEDDING_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY no está configurado en backend/.env"
            )

    elif EMBEDDING_PROVIDER == "azure_openai":
        missing = []

        if not AZURE_OPENAI_API_KEY:
            missing.append("AZURE_OPENAI_API_KEY")

        if not AZURE_OPENAI_ENDPOINT:
            missing.append("AZURE_OPENAI_ENDPOINT")

        if not AZURE_OPENAI_EMBEDDING_DEPLOYMENT:
            missing.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

        if missing:
            raise ValueError(
                "Faltan variables de entorno para Azure OpenAI: "
                + ", ".join(missing)
            )

    else:
        raise ValueError(
            f"Proveedor de embeddings no soportado: {EMBEDDING_PROVIDER}"
        )