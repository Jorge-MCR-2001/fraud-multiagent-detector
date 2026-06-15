from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from services.confidence_scoring_service import build_confidence_assessment

class DecisionArbiterAgent(BaseAgent):

    """
        Responsabilidad: Tomar una desicion final usando evidencia agregada
        - Usar señales internas, recuperaciones RAG, evidencia externa y debate.
        - Generar confidence
        - Generar decision
        - Generar requirimiento de revision por humanos
    """

    name: str = "DecisionArbiterAgent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        try:
            # Extraccion de data procesada del estado compartido
            pro_fraud_argument = state.get("pro_fraud_argument", {})
            pro_customer_argument = state.get("pro_customer_argument", {})

            signal_tags = state.get("signal_tags", [])
            signals = state.get("signals", [])

            citations_internal = state.get("citations_internal", [])
            citations_external = state.get("citations_external", [])

            rag_policy_context = state.get("rag_policy_context", [])

            external_signals = state.get("external_signals", [])

            decision_result = self._resolve_decision(
                signal_tags=signal_tags,
                signals=signals,
                citations_internal=citations_internal,
                citations_external=citations_external,
                rag_policy_context=rag_policy_context,
                external_signals=external_signals,
                pro_fraud_argument=pro_fraud_argument,
                pro_customer_argument=pro_customer_argument,
            )

            # Apilar data en el estado compartido

            state["decision"] = decision_result["decision"]
            state["confidence"] = decision_result["confidence"]
            state["confidence_level"] = decision_result["confidence_level"]
            state["confidence_factors"] = decision_result["confidence_factors"]

            state["decision_basis"] = decision_result["decision_basis"]
            state["decision_rationale"] = decision_result["decision_rationale"]
            state["requires_human_review"] = decision_result["requires_human_review"]
            state["decision_trace"] = decision_result["decision_trace"]

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "decision": state["decision"],
                    "confidence": state["confidence"],
                    "confidence_level": state["confidence_level"],
                    "confidence_factors_count": len(state.get("confidence_factors", [])),
                    "requires_human_review": state["requires_human_review"], # Inserccion de estado para revision de humano
                    "basis_type": state["decision_basis"].get("basis_type"),
                    "applied_rule": state["decision_basis"].get("applied_rule", {})
                }
            )

            return state
        
        except Exception as exc:
            self.add_error(
                state=state,
                message="Error durante arbitraje de decisión final en el Agente de Desiciones",
                details={
                    "error": str(exc)
                }
            )
            return state
        
    
    def _resolve_decision(
        self,
        signal_tags: List[str],
        signals: List[str],
        citations_internal: List[Dict[str, Any]],
        citations_external: List[Dict[str, Any]],
        rag_policy_context: List[Dict[str, Any]],
        external_signals: List[str],
        pro_fraud_argument: Dict[str, Any],
        pro_customer_argument: Dict[str, Any],
    ) -> Dict[str, Any]:

        signal_count = len(signal_tags or [])

        rag_policy_ids = self._extract_policy_ids(rag_policy_context)

        has_fp01 = "FP-01" in rag_policy_ids
        has_fp02 = "FP-02" in rag_policy_ids

        has_external_evidence = bool(external_signals or citations_external)
        has_high_external_risk = self._has_high_external_risk(citations_external)

        pro_fraud_score = self._safe_float(
            pro_fraud_argument.get("risk_score"),
            default=0.0
        )

        customer_trust_score = self._safe_float(
            pro_customer_argument.get("customer_trust_score"),
            default=0.5
        )

        pro_fraud_suggestion = pro_fraud_argument.get("suggested_decision")
        pro_customer_suggestion = pro_customer_argument.get("suggested_decision")

        contradiction_detected = self._has_contradiction(
            pro_fraud_score=pro_fraud_score,
            customer_trust_score=customer_trust_score,
            pro_fraud_suggestion=pro_fraud_suggestion,
            pro_customer_suggestion=pro_customer_suggestion,
        )

        # Determinación de Parametros finales de evaluación

        # Regla 1: Sin señales ni evidencia externa => APPROVE
        if signal_count == 0 and not has_external_evidence:
            decision = "APPROVE"
            confidence = 0.95
            basis = "no_risk_signals"
            requires_human_review = False

        # Regla 2: Riesgo crítico => BLOCK
        elif (signal_count >= 4 and (has_high_external_risk or pro_fraud_score >= 0.80)):
            decision = "BLOCK"
            confidence = 0.90
            basis = "critical_evidence_combination"
            requires_human_review = False

        # Regla 3: FP-02 o señales país/dispositivo => ESCALATE_TO_HUMAN
        elif has_fp02 or ("signal_c" in signal_tags and "signal_d" in signal_tags):
            decision = "ESCALATE_TO_HUMAN"
            confidence = 0.60
            basis = "policy_fp02_or_geo_device_risk"
            requires_human_review = True

        # Regla 4: FP-01 o monto/horario => CHALLENGE
        elif has_fp01 or ("signal_a" in signal_tags and "signal_b" in signal_tags):
            decision = "CHALLENGE"
            confidence = self._challenge_confidence(
                has_external_evidence=has_external_evidence,
                has_high_external_risk=has_high_external_risk,
                pro_fraud_score=pro_fraud_score,
                customer_trust_score=customer_trust_score,
            )
            basis = "policy_fp01_or_amount_time_risk"
            requires_human_review = False

        # Regla 5: Contradicción fuerte => ESCALATE_TO_HUMAN
        elif contradiction_detected and signal_count >= 2:
            decision = "ESCALATE_TO_HUMAN"
            confidence = 0.55
            basis = "contradictory_agent_arguments"
            requires_human_review = True

        # Regla 6: Riesgo medio por score Pro-Fraud => CHALLENGE
        elif pro_fraud_score >= 0.45:
            decision = "CHALLENGE"
            confidence = 0.62
            basis = "moderate_pro_fraud_score"
            requires_human_review = False

        # Fallback: APPROVE
        else:
            decision = "APPROVE"
            confidence = 0.90
            basis = "fallback_low_risk"
            requires_human_review = False

        # Construccion de desicion interna
        decision_rationale = self._build_decision_rationale(
            decision=decision,
            basis=basis,
            signals=signals,
            rag_policy_ids=rag_policy_ids,
            external_signals=external_signals,
            pro_fraud_score=pro_fraud_score,
            customer_trust_score=customer_trust_score,
            contradiction_detected=contradiction_detected,
        )

        confidence_assessment = build_confidence_assessment(
            decision=decision,
            basis=basis,
            base_confidence=confidence,
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

        final_confidence = confidence_assessment["confidence"]

        # Constriuccion de trazabilidad de decision
        decision_trace = self._build_decision_trace(
            decision=decision,
            confidence=final_confidence,
            basis=basis,
            signal_tags=signal_tags,
            signals=signals,
            rag_policy_ids=rag_policy_ids,
            citations_internal=citations_internal,
            external_signals=external_signals,
            citations_external=citations_external,
            pro_fraud_argument=pro_fraud_argument,
            pro_customer_argument=pro_customer_argument,
            requires_human_review=requires_human_review,
            contradiction_detected=contradiction_detected,
        )

        decision_basis = self._build_decision_basis(
            basis=basis,
            decision=decision,
            confidence=final_confidence,
            signal_tags=signal_tags,
            signals=signals,
            rag_policy_ids=rag_policy_ids,
            citations_internal=citations_internal,
            external_signals=external_signals,
            citations_external=citations_external,
            pro_fraud_score=pro_fraud_score,
            customer_trust_score=customer_trust_score,
            pro_fraud_suggestion=pro_fraud_suggestion,
            pro_customer_suggestion=pro_customer_suggestion,
            contradiction_detected=contradiction_detected,
            requires_human_review=requires_human_review,
        )

        
                
        return {
            "decision": decision,
            "confidence": final_confidence,
            "confidence_level": confidence_assessment["confidence_level"],
            "confidence_factors": confidence_assessment["confidence_factors"],
            "decision_rationale": decision_rationale,
            "requires_human_review": requires_human_review,
            "decision_trace": decision_trace,
            "decision_basis": decision_basis,
        }
    

    def _challenge_confidence(self, has_external_evidence: bool, has_high_external_risk: bool, pro_fraud_score: float, customer_trust_score: float) -> float:
        """
            Confidence para CHALLENGE.
            - CHALLENGE suele estar alrededor de 0.65. (se ajusta levemente según evidencia externa y debate.)
        """

        # Confidence incial
        confidence = 0.65

        if has_high_external_risk:
            confidence += 0.10

        elif has_external_evidence and pro_fraud_score >= 0.85:
            confidence += 0.05

        if customer_trust_score >= 0.75:
            confidence -= 0.05

        return round(max(0.50, min(confidence, 0.80)), 2)
    
    
    def _has_high_external_risk(self, citations_external: List[Dict[str, Any]]) -> bool:

        # Determinacion de riesgo alto
        for citation in citations_external or []:
            risk_level = str(citation.get("risk_level", "")).upper()

            if risk_level == "HIGH":
                return True

        return False

    def _has_contradiction(
        self,
        pro_fraud_score: float,
        customer_trust_score: float,
        pro_fraud_suggestion: Optional[str],
        pro_customer_suggestion: Optional[str],
    ) -> bool:
        """
            Detecta contradicción si ambos lados tienen argumentos fuertes o si sugieren decisiones claramente diferentes.
        """

        fraud_strong = pro_fraud_score >= 0.85
        customer_strong = customer_trust_score >= 0.75

        # Logica boleana de contradicciones fuertes
        severe_block_vs_customer = (
            pro_fraud_suggestion == "BLOCK"
            and pro_customer_suggestion in ["APPROVE", "CHALLENGE"]
        )

        severe_escalate_vs_approve = (
            pro_fraud_suggestion == "ESCALATE_TO_HUMAN"
            and pro_customer_suggestion == "APPROVE"
        )

        both_sides_strong = fraud_strong and customer_strong

        return bool(
            severe_block_vs_customer
            or severe_escalate_vs_approve
            or both_sides_strong
        )
    
    def _build_decision_rationale(
        self,
        decision: str,
        basis: str,
        signals: List[str],
        rag_policy_ids: List[str],
        #matched_policy_ids: List[str],
        external_signals: List[str],
        pro_fraud_score: float,
        customer_trust_score: float,
        contradiction_detected: bool,
    ) -> str:

        # construccion de desiciones -> armado de formato de respuesta
        parts = [
            f"Decisión final: {decision}.",
            f"Criterio aplicado: {basis}."
        ]


        if signals:
            parts.append(
                "Señales internas detectadas: "
                + ", ".join(signals)
                + "."
            )

        if rag_policy_ids:
            parts.append(
                "Políticas recuperadas por RAG: "
                + ", ".join(rag_policy_ids)
                + "."
            )

        if external_signals:
            parts.append(
                "Señales externas consideradas: "
                + ", ".join(external_signals)
                + "."
            )

        parts.append(
            f"Score Pro-Fraud: {pro_fraud_score}."
        )

        parts.append(
            f"Score Pro-Customer: {customer_trust_score}."
        )

        if contradiction_detected:
            parts.append(
                "Se detectó contradicción relevante entre argumentos de agentes."
            )

        return " ".join(parts)

    def _build_decision_trace(
        self,
        decision: str,
        confidence: float,
        basis: str,
        signal_tags: List[str],
        signals: List[str],
        rag_policy_ids: List[str],
        citations_internal: List[Dict[str, Any]],
        external_signals: List[str],
        citations_external: List[Dict[str, Any]],
        pro_fraud_argument: Dict[str, Any],
        pro_customer_argument: Dict[str, Any],
        requires_human_review: bool,
        contradiction_detected: bool,
    ) -> List[Dict[str, Any]]:

        # Construccion de trazabilidad de desicion
        return [
            {
                "step": "signals_detected",
                "value": {
                    "signal_tags": signal_tags,
                    "signals": signals
                }
            },
            {
                "step": "internal_rag_evidence",
                "value": {
                    "rag_policy_ids": rag_policy_ids,
                    "citations_internal": citations_internal
                }
            },
            {
                "step": "external_threat_evidence",
                "value": {
                    "external_signals": external_signals,
                    "citations_external": citations_external
                }
            },
            {
                "step": "debate_arguments",
                "value": {
                    "pro_fraud": {
                        "risk_score": pro_fraud_argument.get("risk_score"),
                        "suggested_decision": pro_fraud_argument.get("suggested_decision")
                    },
                    "pro_customer": {
                        "customer_trust_score": pro_customer_argument.get("customer_trust_score"),
                        "suggested_decision": pro_customer_argument.get("suggested_decision")
                    }
                }
            },
            {
                "step": "contradiction_detected",
                "value": contradiction_detected
            },
            {
                "step": "decision_basis",
                "value": basis
            },
            {
                "step": "final_decision",
                "value": decision
            },
            {
                "step": "final_confidence",
                "value": round(confidence, 2)
            },
            {
                "step": "requires_human_review",
                "value": requires_human_review
            }
        ]

    def _build_decision_basis(
        self,
        basis: str,
        decision: str,
        confidence: float,
        signal_tags: List[str],
        signals: List[str],
        rag_policy_ids: List[str],
        citations_internal: List[Dict[str, Any]],
        external_signals: List[str],
        citations_external: List[Dict[str, Any]],
        pro_fraud_score: float,
        customer_trust_score: float,
        pro_fraud_suggestion: Optional[str],
        pro_customer_suggestion: Optional[str],
        contradiction_detected: bool,
        requires_human_review: bool,
    ) -> Dict[str, Any]:
        
        """
            Construye una base estructurada de decisión.
        """

        return {
            "basis_type": basis,
            "decision": decision,
            "confidence": round(confidence, 2),
            "requires_human_review": requires_human_review,

            "internal_signals": {
                "signal_count": len(signal_tags or []),
                "signal_tags": signal_tags or [],
                "signals": signals or [],
            },

            "internal_policy_evidence": {
                "rag_policy_ids": rag_policy_ids or [],
                "citations_internal": citations_internal or [],
            },

            "external_threat_evidence": {
                "has_external_evidence": bool(external_signals or citations_external),
                "external_signals": external_signals or [],
                "citations_external": citations_external or [],
            },

            "debate_summary": {
                "pro_fraud_score": pro_fraud_score,
                "pro_fraud_suggestion": pro_fraud_suggestion,
                "customer_trust_score": customer_trust_score,
                "pro_customer_suggestion": pro_customer_suggestion,
                "contradiction_detected": contradiction_detected,
            },

            "applied_rule": {
                "rule_code": basis,
                "rule_description": self._describe_basis(basis),
            },
        }

    def _describe_basis(self, basis: str) -> str:
        """
            Traduce el código interno de decisión a una descripción auditable.
        """

        descriptions = {
            "no_risk_signals": (
                "No se identificaron señales internas de riesgo ni evidencia externa relevante."
            ),
            "critical_evidence_combination": (
                "Se detectó una combinación crítica de múltiples señales internas y evidencia externa o score Pro-Fraud alto."
            ),
            "policy_fp02_or_geo_device_risk": (
                "Se recuperó FP-02 o se detectó combinación de país/dispositivo nuevo que requiere revisión humana."
            ),
            "policy_fp01_or_amount_time_risk": (
                "Se recuperó FP-01 o se detectó combinación de monto fuera de rango y horario no habitual."
            ),
            "contradictory_agent_arguments": (
                "Se detectó contradicción relevante entre los argumentos Pro-Fraud y Pro-Customer."
            ),
            "moderate_pro_fraud_score": (
                "El score Pro-Fraud indica riesgo medio que requiere challenge."
            ),
            "fallback_low_risk": (
                "No se alcanzaron condiciones de riesgo suficientes; se aplica aprobación por bajo riesgo."
            ),
        }

        return descriptions.get(
            basis,
            "Criterio de decisión no catalogado."
        )

    def _extract_policy_ids(self, items: List[Dict[str, Any]]) -> List[str]:

        policy_ids = []

        for item in items or []:
            policy_id = item.get("policy_id")

            if policy_id and policy_id not in policy_ids:
                policy_ids.append(policy_id)

        return policy_ids

    def _safe_float(self, value: Any, default: float = 0.0) -> float:

        try:
            if value is None: # Valida formato correcto para determinación de valores
                return default

            return float(value)

        except (TypeError, ValueError):
            return default
