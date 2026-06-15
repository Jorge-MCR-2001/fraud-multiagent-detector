from fastapi import FastAPI

from orchestrators.fraud_orchestrator import FraudOrchestrator
from settings.paths import (
    LLM_ENABLED,
    POLICY_CHUNKS_JSON,
    POLICY_EMBEDDINGS_NPY,
    AUDIT_TRAIL_JSONL,
)


from schemas.evaluation_response import EvaluationResponse

# Construir el app
app = FastAPI(
    tittle="API - Detector de fraudes Multi-Agentico",
    version="1.0.0",
    description=
        """
            Nivel 3: Integración de Observabilidad
        """
)

orchestrator = FraudOrchestrator()

@app.get("/")
def healt():
    return {
        "status": "running",
        "level": "2",
        "architecture": "langgraph_multi_agent_rag_debate_hitl_audit",
        "rag_enabled": POLICY_CHUNKS_JSON.exists() and POLICY_EMBEDDINGS_NPY.exists(),
        "llm_enabled": LLM_ENABLED,
        "hitl_enabled": True,
        "audit_trail_enabled": AUDIT_TRAIL_JSONL.parent.exists(),
        "flow": [
            "TransactionContextAgent",
            "BehavioralPatternAgent",
            "InternalPolicyRAGAgent",
            "ExternalThreatIntelAgent",
            "EvidenceAggregationAgent",
            "ProFraudDebateAgent",
            "ProCustomerDebateAgent",
            "DecisionArbiterAgent",
            "ExplainabilityAgent",
            "HITLRouterAgent",
            "AuditTrailAgent"
        ]
    }

@app.get("/evaluate/{transaction_id}", response_model=EvaluationResponse)
def evaluate_transaction(transaction_id: str):
    return orchestrator.evaluate(transaction_id)