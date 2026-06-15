from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from services.llm_client import DebateLLMClient

class ProFraudDebateAgent(BaseAgent):

    """
        Responsabilidad: Argumentar por qué la transacción podría ser fraude.
        - Calcular score_risk de forma deterministica
        - Calcular suggested_decision de forma deterministica
        - Generar el argumento a base de un LLM
    """

    # Asignar nombre al Agente
    name: str = "ProFraudDebateAgent"

    def __init__(self):
        self.llm_client = DebateLLMClient()

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        # Recuperar la evidencia de trazabilidad en el grafo
        evidence_bundle = state.get("evidence_bundle", {})

        # Validar la existencia de evidencias
        if not evidence_bundle:
            self.add_error(
                state=state,
                message="evidence_bundle no encontrado para debate Pro-Fraud"
            )
            return state
        
        try:
            # Construir el argumento en base a las evidencias
            argument = self._build_argument(evidence_bundle)

            # Almacenar el argumento en el estado
            state["pro_fraud_argument"] = argument

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "position": argument.get("position"),
                    "risk_score": argument.get("risk_score"),
                    "arguments_count": len(argument.get("arguments", [])), # Cantidad de argumentos
                    "suggested_decision": argument.get("suggested_decision"), # Decision sugerida
                    "llm_used": argument.get("llm_used"),
                    "llm_error": argument.get("llm_error")
                }
            )

            return state

        except Exception as exc:
            self.add_error(
                state=state,
                message="Error durante debate generado en Pro-Fraud",
                details={
                    "error": str(exc)
                }
            )
            return state
        
    
    def _build_argument(self, evidence_bundle: Dict[str, Any]) -> Dict[str, Any]:

        # Extraer informacion del parametro evidencias, dentro del estado compartido del grafo
        internal_evidence = evidence_bundle.get("internal_evidence", {})
        rag_evidence = evidence_bundle.get("rag_evidence", {})
        external_evidence = evidence_bundle.get("external_evidence", {})
        risk_summary = evidence_bundle.get("risk_summary", {})

        signal_tags = internal_evidence.get("signal_tags", [])
        signals = internal_evidence.get("signals", [])

        external_signals = external_evidence.get("external_signals", [])
        citations_external = external_evidence.get("citations_external", [])

        retrieved_policy_ids = rag_evidence.get("retrieved_policy_ids", [])

        arguments: List[str] = []

        # Señales internas -> añadir argumentos textuales
        if "signal_a" in signal_tags:
            arguments.append(
                "El monto de la transacción se encuentra fuera del patrón habitual del cliente."
            )

        if "signal_b" in signal_tags:
            arguments.append(
                "La transacción ocurrió fuera del horario habitual de operación del cliente."
            )

        if "signal_c" in signal_tags:
            arguments.append(
                "La transacción se realizó desde un país no habitual para el cliente."
            )

        if "signal_d" in signal_tags:
            arguments.append(
                "La transacción utilizó un dispositivo no reconocido o no habitual."
            )

        # Evidencia RAG -> añadir argumentos conceptuales respecto a las politicas
        if retrieved_policy_ids:
            arguments.append(
                "El RAG interno recuperó políticas asociadas al patrón de riesgo detectado: "
                + ", ".join(retrieved_policy_ids)
                + "."
            )

        # Evidencia externa -> añadir argumentos respecto a las reglas externas aplicables al caso
        if external_signals:
            arguments.append(
                "Se encontraron señales externas relacionadas: "
                + ", ".join(external_signals)
                + "."
            )

        # Citas externas -> añadir las citas externas a la busqueda inteligente
        if citations_external: 
            arguments.append(
                "Existen citas externas asociadas a fuentes gobernadas de inteligencia de amenazas."
            )

        # Calcular el riesgo de desicion
        risk_score = self._calculate_risk_score(
            signal_tags=signal_tags,
            external_signals=external_signals,
            retrieved_policy_ids=retrieved_policy_ids,
            risk_summary=risk_summary
        )

        # Determinar sugerencia de desicion
        suggested_decision = self._suggest_decision(
            signal_tags=signal_tags,
            external_signals=external_signals,
            risk_score=risk_score
        )

        # Genera el argumento por llm
        llm_result = self.llm_client.generate_debate_argument(
            role_name="ProFraudDebateAgent",
            position="SUSPECTED_FRAUD",
            deterministic_arguments=arguments,
            evidence_payload={
                "signal_tags": signal_tags,
                "signals": signals,
                "external_signals": external_signals,
                "retrieved_policy_ids": retrieved_policy_ids,
                "risk_summary": risk_summary
            },
            score_name="risk_score",
            score_value=risk_score,
            suggested_decision=suggested_decision
        )

        return {
            "position": "SUSPECTED_FRAUD",
            "arguments": arguments,
            "llm_argument": llm_result.get("text"),
            "llm_used": llm_result.get("used"),
            "llm_error": llm_result.get("error"),
            "risk_score": risk_score,
            "suggested_decision": suggested_decision,
            "supporting_signals": signals,
            "supporting_policy_ids": retrieved_policy_ids,
            "supporting_external_signals": external_signals
        }
    

    def _calculate_risk_score(
        self,
        signal_tags: List[str],
        external_signals: List[str],
        retrieved_policy_ids: List[str],
        risk_summary: Dict[str, Any]
    ) -> float:

        # Puntaje de riesgo inicial
        score = 0.0

        # Señales internas ---> se fijan ponderados hardcodeados
        score += min(len(signal_tags or []) * 0.18, 0.60)

        # Evidencia externa ---> se fija un ponderado menor a señal interna
        if external_signals:
            score += min(len(external_signals) * 0.10, 0.25)

        # Solo RAG interno ---> se añade un factor por identificación de politica por inferencia semantica
        if retrieved_policy_ids: 
            score += 0.15

        # Evidencia fuerte adicional --> opcional
        if risk_summary.get("has_external_evidence"):
            score += 0.05

        return round(min(score, 1.0), 2)
    

    def _suggest_decision(self, signal_tags: List[str], external_signals: List[str], risk_score: float) -> str:

        # Extraccion de cantida de señales internas
        signal_count = len(signal_tags or [])

        # Determinacion de señales externas
        has_external = bool(external_signals)

        if signal_count >= 4 and has_external:
            return "BLOCK"

        if signal_count >= 3:
            return "ESCALATE_TO_HUMAN"

        if risk_score >= 0.45: # Si el riesgo es moderadamente bajo
            return "CHALLENGE"

        return "APPROVE"