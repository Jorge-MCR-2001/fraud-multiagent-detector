from typing import Optional

from fastapi import FastAPI, HTTPException

from settings.runtime_config import get_runtime_metadata

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
    description="Nivel 4: Integración de Langgpraph en Cloud"
)

orchestrator = FraudOrchestrator()

@app.get("/")
def healt():

    runtime = get_runtime_metadata()

    return {
        "status": "running",
        "level": "4",
        "architecture": "langgraph_multi_agent_cloud_ready",
        "rag_enabled": True,
        "llm_enabled": True,
        "hitl_enabled": True,
        "audit_trail_enabled": True,
        "observability_enabled": True,
        "schema_validation_enabled": True,
        "runtime": runtime
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