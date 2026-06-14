from pathlib import Path

# Raiz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Backend
BACKEND_DIR = PROJECT_ROOT / "backend"

# Ruta a DATA
DATA_DIR = BACKEND_DIR / "data"
CUSTOMER_BEHIVOR_DIR = DATA_DIR / "customer_behivor.csv"
TRANSACTIONS_DIR = DATA_DIR / "transactions.csv"

# Ruta a Resources
RESOURCES_DIR = BACKEND_DIR / "resources"
FRAUD_POLICY_DIR = RESOURCES_DIR / "fraud_policies_nivel_02.json"

# Rutas relacionadas a herramienta RAG
RAG_DIR = BACKEND_DIR / "rag"

VECTORSTORE_DIR = RAG_DIR / "vectorstore"
POLICY_INDEX_DIR = VECTORSTORE_DIR / "policy_index"

POLICY_CHUNKS_JSON = POLICY_INDEX_DIR / "policy_chunks.json"
POLICY_EMBEDDINGS_NPY = POLICY_INDEX_DIR / "policy_embeddings.npy"
EMBEDDING_CONFIG_JSON = POLICY_INDEX_DIR / "embedding_config.json"