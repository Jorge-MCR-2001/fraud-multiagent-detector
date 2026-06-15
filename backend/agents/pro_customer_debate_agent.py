from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from services.llm_client import DebateLLMClient

class ProCustomerDebateAgent(BaseAgent):

    """
        Responsabilidad: Argumentar por qué la transacción podría ser legitima.
        - Calcular customer_trust_score de forma determinística.
        - Calcular suggested_decision de forma determinística.
        - Generar el argumento a base de un LLM
    """

    # Asignar el nombre al Agente
    name: str = "ProCustomerDebateAgent"

    def __init__(self) -> None:
        self.llm_client = DebateLLMClient()
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        # Recuperar la evidencia de trazabilidad en el grafo
        evidence_bundle = state.get("evidence_bundle", {})

        # Validar la existencia de evidencias
        if not evidence_bundle:
            self.add_error(
                state=state,
                message="evidence_bundle no encontrado para debate Pro-Customer"
            )
            return state
        
        try:

            argument = self._build_argument(evidence_bundle)

            # Almacenar el argumento en el estado
            state["pro_customer_argument"] = argument

            self.add_trace(
                state=state,
                status="completed",
                details={
                    "position": argument.get("position"),
                    "customer_trust_score": argument.get("customer_trust_score"),
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
                message="Error durante debate generado en Pro-Customer",
                details={
                    "error": str(exc)
                }
            )
            return state
        

    def _build_argument(self, evidence_bundle: Dict[str, Any]) -> Dict[str, Any]:

        # Extraer informacion del parametro evidencias, dentro del estado compartido del grafo
        transaction_context = evidence_bundle.get("transaction_context", {})
        customer_behavior = evidence_bundle.get("customer_behavior", {})

        internal_evidence = evidence_bundle.get("internal_evidence", {})
        external_evidence = evidence_bundle.get("external_evidence", {})

        signal_tags = internal_evidence.get("signal_tags", [])
        signals = internal_evidence.get("signals", [])

        external_signals = external_evidence.get("external_signals", [])

        arguments: List[str] = []

        # Extraccion de datos de transaccion
        transaction_country = self._normalize_text(
            transaction_context.get("country")
        )
        transaction_device = self._normalize_text(
            transaction_context.get("device_id")
        )
        transaction_channel = self._normalize_text(
            transaction_context.get("channel")
        )

        # Extracccion de comportamientos
        usual_countries = self._normalize_list(
            customer_behavior.get("usual_countries")
        )
        usual_devices = self._normalize_list(
            customer_behavior.get("usual_devices")
        )

        # País habitual
        if transaction_country and transaction_country in usual_countries:
            arguments.append(
                "El país de la transacción coincide con el país habitual del cliente."
            )

        # Dispositivo habitual
        if transaction_device and transaction_device in usual_devices:
            arguments.append(
                "El dispositivo utilizado coincide con un dispositivo habitual del cliente."
            )

        # Canal conocido
        if transaction_channel:
            arguments.append(
                f"La operación se realizó por el canal {transaction_channel}, "
                "lo cual puede ser consistente con el comportamiento digital del cliente."
            )

        # Evalua la ausencia de señales críticas específicas
        if "signal_c" not in signal_tags:
            arguments.append(
                "No se detectó cambio geográfico inusual en la transacción."
            )

        if "signal_d" not in signal_tags:
            arguments.append(
                "No se detectó uso de dispositivo desconocido."
            )

        # Ausencia de evidencia externa
        if not external_signals:
            arguments.append(
                "No se encontraron alertas externas asociadas a la transacción."
            )

        customer_trust_score = self._calculate_customer_trust_score(
            signal_tags=signal_tags,
            external_signals=external_signals,
            transaction_country=transaction_country,
            usual_countries=usual_countries,
            transaction_device=transaction_device,
            usual_devices=usual_devices,
        )

        suggested_decision = self._suggest_decision(
            signal_tags=signal_tags,
            external_signals=external_signals,
            customer_trust_score=customer_trust_score
        )

        llm_result = self.llm_client.generate_debate_argument(
            role_name="ProCustomerDebateAgent",
            position="POSSIBLY_LEGITIMATE",
            deterministic_arguments=arguments,
            evidence_payload={
                "transaction_country": transaction_country,
                "usual_countries": usual_countries,
                "transaction_device": transaction_device,
                "usual_devices": usual_devices,
                "transaction_channel": transaction_channel,
                "signal_tags": signal_tags,
                "signals": signals,
                "external_signals": external_signals
            },
            score_name="customer_trust_score",
            score_value=customer_trust_score,
            suggested_decision=suggested_decision
        )

        return {
            "position": "POSSIBLY_LEGITIMATE",
            "arguments": arguments,
            "llm_argument": llm_result.get("text"),
            "llm_used": llm_result.get("used"),
            "llm_error": llm_result.get("error"),
            "customer_trust_score": customer_trust_score,
            "suggested_decision": suggested_decision,
            "countered_signals": signals,
            "known_customer_attributes": {
                "country_is_usual": transaction_country in usual_countries
                if transaction_country
                else False,
                "device_is_usual": transaction_device in usual_devices
                if transaction_device
                else False,
                "channel": transaction_channel
            }
        }
    
    def _calculate_customer_trust_score(
        self,
        signal_tags: List[str],
        external_signals: List[str],
        transaction_country: str,
        usual_countries: List[str],
        transaction_device: str,
        usual_devices: List[str],
    ) -> float:

        # Score de riesgo inicial
        score = 0.50

        # Empieza a analizar confianza en la transaccion

        # Analisis en base a pais de origen
        if transaction_country and transaction_country in usual_countries:
            score += 0.20

        # Analisis en base a dispositivo de transaccion
        if transaction_device and transaction_device in usual_devices:
            score += 0.20

        # Penalizacion por señales internas

        if "signal_c" in signal_tags:
            score -= 0.20

        if "signal_d" in signal_tags:
            score -= 0.20

        if "signal_a" in signal_tags:
            score -= 0.10

        if "signal_b" in signal_tags:
            score -= 0.10

        # Penalizacion por señales externas en base a busqueda inteligente

        if external_signals:
            score -= min(len(external_signals) * 0.08, 0.20)

        return round(max(0.0, min(score, 1.0)), 2)
    

    def _suggest_decision(self, signal_tags: List[str], external_signals: List[str], customer_trust_score: float) -> str:

        signal_count = len(signal_tags or [])
        has_external = bool(external_signals)

        # País inusual + dispositivo desconocido sí requiere humano
        if "signal_c" in signal_tags and "signal_d" in signal_tags:
            return "ESCALATE_TO_HUMAN"

        # Muchas señales internas + evidencia externa
        if signal_count >= 3 and has_external:
            return "ESCALATE_TO_HUMAN"

        # Cliente confiable, bajo riesgo y sin alertas externas
        if customer_trust_score >= 0.75 and signal_count <= 1 and not has_external:
            return "APPROVE"

        # Caso típico FP-01: monto + horario
        # Se valida con CHALLENGE, no con humano.
        if signal_count <= 2:
            return "CHALLENGE"

        return "CHALLENGE"
    
    def _normalize_text(self, value: Any) -> str | None:
        if value is None: # Garantizar un valor valido
            return None

        text = str(value).strip()

        if text == "": # Garantizar la existencia de texto
            return None

        return text
    
    def _normalize_list(self, value: Any) -> List[str]:
        if value is None: # Garantizar un valor valido
            return []

        text = str(value).strip()

        if text == "": # Garantizar el retorno de una lista valida
            return []

        return [
            item.strip()
            for item in text.split(",")
            if item.strip()
        ]
