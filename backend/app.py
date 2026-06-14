from fastapi import FastAPI

from orchestrators.fraud_orchestrator import FraudOrchestrator

# Construir el app
app = FastAPI(
    tittle="API - Detector de fraudes Multi-Agentico",
    version="1.0.0",
    description="Implementacion de sistema Langgraph Deterministico"
)

orchestrator = FraudOrchestrator()

@app.get("/")
def healt():
    return {
        "status": "running",
        "level": "1",
        "architecture": "langgraph_multi_agent_deterministic",
        "llm_enabled": False,
        "rag_enabled": False,
        "humman_in_the_loop": False
    }

@app.get("/evaluate/{transaction_id}")
def evaluate_transaction(transaction_id: str):

    return orchestrator.evaluate(transaction_id)