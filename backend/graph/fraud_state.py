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

    # Decisiones finales: Accion / Confianza
    decision: Optional[str]
    confidence: Optional[float]

    # Trazabilidad de Decision / agentes ejecutados
    decision_trace: List[Dict[str, Any]]
    agent_trace: List[Dict[str, Any]]

    # Manejo de Errores
    errors: List[Dict[str, Any]]