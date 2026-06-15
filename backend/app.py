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
from services.error_handler import build_error_response

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

@app.get(
        "/evaluate/{transaction_id}",
        response_model=EvaluationResponse,
        responses={
            404: {
                "description": "Transction not found"
            },
            500: {
                "description": "Interval evaluation error"
            },
        },
    )
def evaluate_transaction(transaction_id: str):
    try:
        result = orchestrator.evaluate(transaction_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=build_error_response(
                    error_code="TRANSACTION_NOT_FOUND",
                    message=f"Transaction {transaction_id} was not found.",
                    details={"transaction_id": transaction_id},
                )
            )
        
        if result.get("decision") is None:
            raise HTTPException(
                status_code=404,
                detail=build_error_response(
                    error_code="TRANSACTION_NOT_FOUND",
                    message=f"Transaction {transaction_id} was not found.",
                    details={"transaction_id": transaction_id},
                ),
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=build_error_response(
                error_code="EVALUATION_FAILED",
                message="Fraud evaluation failed unexpectedly.",
                details={
                    "transaction_id": transaction_id,
                    "error": str(exc),
                },
            ),
        )


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
            detail=build_error_response(
                error_code="HITL_ITEM_NOT_FOUND",
                message=f"HITL item not found: {hitl_queue_id}",
                details={"hitl_queue_id": hitl_queue_id},
            ),
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
            detail=build_error_response(
                error_code="HITL_ITEM_NOT_FOUND",
                message=str(exc),
                details={"hitl_queue_id": hitl_queue_id},
            ),
        )