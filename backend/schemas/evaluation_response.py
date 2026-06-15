from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field

DecisionType = Literal[
    "APPROVE",
    "CHALLENGE",
    "BLOCK",
    "ESCALATE_TO_HUMAN",
]

ConfidenceLevel = Literal[
    "HIGH",
    "MEDIUM",
    "LOW",
]

class CitationInternal(BaseModel):
    policy_id: str
    chunk_id: Optional[str] = None
    version: Optional[str] = None


class CitationExternal(BaseModel):
    threat_id: Optional[str] = None
    source_id: Optional[str] = None
    source_type: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    risk_level: Optional[str] = None
    matched_field: Optional[str] = None
    matched_value: Optional[str] = None


class AgentTraceItem(BaseModel):
    agent: str
    status: str = "completed"
    message: Optional[str] = None
    input_keys: Optional[List[str]] = None
    output_keys: Optional[List[str]] = None
    timestamp: Optional[str] = None


class DecisionTraceItem(BaseModel):
    step: Optional[str] = None
    agent: Optional[str] = None
    decision: Optional[str] = None
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HITLQueueItem(BaseModel):
    hitl_queue_id: Optional[str] = None
    transaction_id: Optional[str] = None
    reason: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    decision_snapshot: Optional[Dict[str, Any]] = None

class ConfidenceFactor(BaseModel):
    factor: str
    impact: float
    direction: str
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)

class EvaluationResponse(BaseModel):
    transaction_id: str

    decision: DecisionType
    confidence: float = Field(ge=0.0, le=1.0)

    decision_basis: Dict[str, Any] = Field(default_factory=dict)
    decision_rationale: str
    requires_human_review: bool

    signals: List[str] = Field(default_factory=list)
    signal_tags: List[str] = Field(default_factory=list)
    signal_metrics: Dict[str, Any] = Field(default_factory=dict)

    citations_internal: List[CitationInternal] = Field(default_factory=list)
    citations_external: List[CitationExternal] = Field(default_factory=list)

    evidence_bundle: Dict[str, Any] = Field(default_factory=dict)

    pro_fraud_argument: Dict[str, Any] = Field(default_factory=dict)
    pro_customer_argument: Dict[str, Any] = Field(default_factory=dict)

    explanation_customer: str
    explanation_audit: str

    hitl_required: bool
    hitl_reason: Optional[str] = None
    hitl_queue_item: Optional[Dict[str, Any]] = None

    audit_saved: bool
    audit_event_id: Optional[str] = None

    confidence_level: ConfidenceLevel
    confidence_factors: List[ConfidenceFactor] = Field(default_factory=list)

    agent_trace: List[Dict[str, Any]] = Field(default_factory=list)
    decision_trace: List[Dict[str, Any]] = Field(default_factory=list)

    errors: List[Dict[str, Any]] = Field(default_factory=list)