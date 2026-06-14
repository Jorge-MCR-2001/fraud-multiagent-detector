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

FRAUD_POLICY_DIR = RESOURCES_DIR / "fraud_policy.json"