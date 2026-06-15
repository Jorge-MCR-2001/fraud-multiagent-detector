from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


HITLStatus = Literal[
    "PENDING_REVIEW",
    "RESOLVED",
]

HITLResolution = Literal[
    "APPROVE",
    "CHALLENGE",
    "BLOCK",
    "ESCALATE_TO_HUMAN",
]


class HITLQueueItem(BaseModel):
    hitl_queue_id: str
    transaction_id: str
    reason: str
    priority: str
    status: HITLStatus = "PENDING_REVIEW"

    original_decision: Optional[str] = None
    original_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    requires_human_review: bool = True

    decision_snapshot: Dict[str, Any] = Field(default_factory=dict)

    assigned_to: Optional[str] = None
    reviewer: Optional[str] = None
    resolution: Optional[HITLResolution] = None
    resolution_notes: Optional[str] = None

    created_at: str
    resolved_at: Optional[str] = None


class HITLQueueResponse(BaseModel):
    item_count: int
    items: List[HITLQueueItem]


class HITLResolveRequest(BaseModel):
    reviewer: str
    resolution: HITLResolution
    notes: Optional[str] = None


class HITLResolveResponse(BaseModel):
    resolved: bool
    item: HITLQueueItem