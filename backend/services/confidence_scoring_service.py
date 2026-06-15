from typing import Any, Dict, List, Optional


def _clamp_confidence(value: float) -> float:
    return round(max(0.0, min(float(value), 1.0)), 2)


def get_confidence_level(confidence: float) -> str:
    """
        Clasifica la confianza global en niveles auditables.
    """

    confidence = _clamp_confidence(confidence)

    if confidence >= 0.80:
        return "HIGH"

    if confidence >= 0.60:
        return "MEDIUM"

    return "LOW"


def build_confidence_factors(
    decision: str,
    basis: str,
    confidence: float,
    signal_tags: List[str],
    signals: List[str],
    rag_policy_ids: List[str],
    citations_internal: List[Dict[str, Any]],
    external_signals: List[str],
    citations_external: List[Dict[str, Any]],
    pro_fraud_score: float,
    customer_trust_score: float,
    contradiction_detected: bool,
    requires_human_review: bool,
) -> List[Dict[str, Any]]:
    """
    Construye factores explicables de confianza.

    Los factores no cambian la decisión final.
    Sirven para auditar por qué la confianza quedó en determinado nivel.
    """

    factors: List[Dict[str, Any]] = []

    if signal_tags:
        factors.append({
            "factor": "internal_behavioral_signals",
            "impact": min(len(signal_tags) * 0.05, 0.20),
            "direction": "increase_risk_confidence",
            "description": (
                "Se detectaron señales internas de comportamiento transaccional."
            ),
            "evidence": {
                "signal_tags": signal_tags,
                "signals": signals,
            }
        })
    else:
        factors.append({
            "factor": "no_internal_risk_signals",
            "impact": 0.15,
            "direction": "increase_approval_confidence",
            "description": (
                "No se detectaron señales internas relevantes de riesgo."
            ),
            "evidence": {
                "signal_tags": [],
                "signals": [],
            }
        })

    if rag_policy_ids or citations_internal:
        factors.append({
            "factor": "internal_policy_rag_match",
            "impact": 0.15,
            "direction": "increase_policy_grounding",
            "description": (
                "El RAG interno recuperó políticas aplicables como evidencia."
            ),
            "evidence": {
                "rag_policy_ids": rag_policy_ids,
                "citations_internal": citations_internal,
            }
        })

    if external_signals or citations_external:
        max_risk_level = _max_external_risk_level(citations_external)

        factors.append({
            "factor": "external_threat_intelligence",
            "impact": _external_risk_impact(max_risk_level),
            "direction": "increase_external_risk_confidence",
            "description": (
                "Se incorporó evidencia externa gobernada al análisis."
            ),
            "evidence": {
                "external_signals": external_signals,
                "citations_external": citations_external,
                "max_risk_level": max_risk_level,
            }
        })

    factors.append({
        "factor": "pro_fraud_debate_score",
        "impact": round(pro_fraud_score, 2),
        "direction": "fraud_argument_strength",
        "description": (
            "Score generado por el agente Pro-Fraud como fuerza argumentativa de riesgo."
        ),
        "evidence": {
            "pro_fraud_score": pro_fraud_score,
        }
    })

    factors.append({
        "factor": "pro_customer_trust_score",
        "impact": round(customer_trust_score, 2),
        "direction": "customer_legitimacy_strength",
        "description": (
            "Score generado por el agente Pro-Customer como fuerza argumentativa de legitimidad."
        ),
        "evidence": {
            "customer_trust_score": customer_trust_score,
        }
    })

    if contradiction_detected:
        factors.append({
            "factor": "contradictory_agent_arguments",
            "impact": -0.20,
            "direction": "decrease_confidence",
            "description": (
                "Se detectó contradicción relevante entre argumentos de agentes."
            ),
            "evidence": {
                "contradiction_detected": True,
            }
        })

    if requires_human_review:
        factors.append({
            "factor": "human_review_required",
            "impact": -0.15,
            "direction": "decrease_automation_confidence",
            "description": (
                "La evaluación requiere revisión humana, lo que reduce la confianza de automatización."
            ),
            "evidence": {
                "requires_human_review": True,
            }
        })

    factors.append({
        "factor": "applied_decision_rule",
        "impact": _rule_impact(basis),
        "direction": "rule_based_confidence_anchor",
        "description": (
            "La confianza se ancla en la regla aplicada por el DecisionArbiterAgent."
        ),
        "evidence": {
            "decision": decision,
            "basis": basis,
            "confidence": _clamp_confidence(confidence),
        }
    })

    return factors


def build_confidence_assessment(
    decision: str,
    basis: str,
    base_confidence: float,
    signal_tags: List[str],
    signals: List[str],
    rag_policy_ids: List[str],
    citations_internal: List[Dict[str, Any]],
    external_signals: List[str],
    citations_external: List[Dict[str, Any]],
    pro_fraud_score: float,
    customer_trust_score: float,
    contradiction_detected: bool,
    requires_human_review: bool,
) -> Dict[str, Any]:
    """
    Devuelve una evaluación formal de confianza.

    Importante:
    - No cambia la decisión.
    - No reescribe la lógica del árbitro.
    - Normaliza confidence.
    - Agrega nivel y factores auditables.
    """

    confidence = _clamp_confidence(base_confidence)

    confidence_factors = build_confidence_factors(
        decision=decision,
        basis=basis,
        confidence=confidence,
        signal_tags=signal_tags,
        signals=signals,
        rag_policy_ids=rag_policy_ids,
        citations_internal=citations_internal,
        external_signals=external_signals,
        citations_external=citations_external,
        pro_fraud_score=pro_fraud_score,
        customer_trust_score=customer_trust_score,
        contradiction_detected=contradiction_detected,
        requires_human_review=requires_human_review,
    )

    return {
        "confidence": confidence,
        "confidence_level": get_confidence_level(confidence),
        "confidence_factors": confidence_factors,
    }


def _max_external_risk_level(
    citations_external: List[Dict[str, Any]]
) -> Optional[str]:

    priority = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    max_level = None
    max_score = 0

    for citation in citations_external or []:
        risk_level = str(citation.get("risk_level", "")).upper()
        score = priority.get(risk_level, 0)

        if score > max_score:
            max_score = score
            max_level = risk_level

    return max_level


def _external_risk_impact(risk_level: Optional[str]) -> float:

    if risk_level == "HIGH":
        return 0.20

    if risk_level == "MEDIUM":
        return 0.10

    if risk_level == "LOW":
        return 0.05

    return 0.0


def _rule_impact(basis: str) -> float:

    impacts = {
        "no_risk_signals": 0.20,
        "critical_evidence_combination": 0.25,
        "policy_fp02_or_geo_device_risk": 0.15,
        "policy_fp01_or_amount_time_risk": 0.15,
        "contradictory_agent_arguments": -0.20,
        "moderate_pro_fraud_score": 0.10,
        "fallback_low_risk": 0.10,
    }

    return impacts.get(basis, 0.0)