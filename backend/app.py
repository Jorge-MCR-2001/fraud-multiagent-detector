from typing import Optional

from fastapi import FastAPI, HTTPException

from schemas.hitl_schema import (
    HITLQueueResponse,
    HITLQueueItem,
    HITLResolveRequest,
    HITLResolveResponse,
)

from services.hitl_queue_service import (
    list_hitl_queue,
    get_hitl_item,
    resolve_hitl_item,
)

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


@app.get("/hitl/queue", response_model=HITLQueueResponse)
def get_hitl_queue(status: Optional[str] = "PENDING_REVIEW"):
    items = list_hitl_queue(status=status)

    return {
        "item_count": len(items),
        "items": items,
    }

@app.get("/hitl/queue/{hitl_queue_id}", response_model=HITLQueueItem)
def get_hitl_queue_item(hitl_queue_id: str):
    item = get_hitl_item(hitl_queue_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail=f"HITL item not found: {hitl_queue_id}",
        )

    return item


@app.post("/hitl/queue/{hitl_queue_id}/resolve", response_model=HITLResolveResponse)
def resolve_hitl_queue_item(hitl_queue_id: str, request: HITLResolveRequest):
    try:
        item = resolve_hitl_item(
            hitl_queue_id=hitl_queue_id,
            reviewer=request.reviewer,
            resolution=request.resolution,
            notes=request.notes,
        )

        return {
            "resolved": True,
            "item": item,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )