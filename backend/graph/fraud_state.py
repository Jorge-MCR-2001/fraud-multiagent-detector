from typing import TypedDict, List, Dict, Any, Optional

class FraudEvaluationState(TypedDict, total = False):

    # Definicion para ID de transacciones
    transaction_id: str

    # Definición para la carga de data
    transaction: Dict[str, Any]
    customer: Dict[str, Any]

    # Transacción normalizada
    transaction_context: Dict[str, Any]

    # Relacion de señales para: señales detectadas / señales de negocio / metricas
    signal_tags: List[str]
    signals: List[str]
    signal_metrics: Dict[str, Any]

    # Politicas que hiciero match / Citas internas
    matched_policies: List[Dict[str, Any]]
    citations_internal: List[Dict[str, Any]]

    # Sugerencia de informacion relativa a politicas internas
    policy_suggested_decision: Optional[str]
    policy_suggested_confidence: Optional[float]

    # Rag interno
    rag_query: Optional[str]
    rag_policy_context: List[Dict[str, Any]]

    # Recuperacion inteligente externa
    external_signals: List[str]
    citations_external: List[Dict[str, Any]]
    external_threat_context: List[Dict[str, Any]]

    # Recopilacion de evidencias
    evidence_bundle: Dict[str, Any]

    # Debate de Agentes
    pro_fraud_argument: Dict[str, Any]
    pro_customer_argument: Dict[str, Any]

    # Decisiones finales: Accion / Confianza
    decision: Optional[str]
    confidence: Optional[float]
    decision_basis: Dict[str, Any]

    # Trazabilidad de Decision / agentes ejecutados
    decision_trace: List[Dict[str, Any]]
    agent_trace: List[Dict[str, Any]]

    # Estados para Agente de desicion y revision de un Humano
    decision_rationale: Optional[str]
    requires_human_review: Optional[bool]

    # Estados para explicacion: Cliente/Auditoria
    explanation_customer: Optional[str]
    explanation_audit: Optional[str]

    # HITL
    hitl_required: Optional[bool]
    hitl_reason: Optional[str]
    hitl_queue_item: Dict[str, Any]

    # Audit
    audit_saved: Optional[bool]
    audit_event_id: Optional[str]
    audit_file: Optional[str]
    audit_event: Dict[str, Any]
    evaluation_id: Optional[str]
    
    # Confidence
    confidence_level: Optional[str]
    confidence_factors: List[Dict[str, Any]]

    # Manejo de Errores
    errors: List[Dict[str, Any]]