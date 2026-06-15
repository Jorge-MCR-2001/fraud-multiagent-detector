import json
from typing import Dict, Any, List

from openai import OpenAI

from settings.paths import (
    OPENAI_API_KEY,
    LLM_ENABLED,
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_MAX_OUTPUT_TOKENS,
    validate_llm_environment
)


class DebateLLMClient:

    """
        Cliente llm para debates:
        * NOTAS:
            - SOLO REDACCIÓN DE ARGUMENTOS
            - NO TOMA DECISIONES
    """

    def __init__(self) -> None:

        self.enabled = LLM_ENABLED
        self.provider = LLM_PROVIDER
        self.model = LLM_MODEL

        if self.enabled:
            validate_llm_environment()
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.client = None

    def generate_debate_argument(
        self,
        role_name: str,
        position: str,
        deterministic_arguments: List[str],
        evidence_payload: Dict[str, Any],
        score_name: str,
        score_value: float,
        suggested_decision: str
    ) -> Dict[str, Any]:
        
        """
        Genera un argumento textual usando LLM.
            Retorna:
            {
                "text": str,
                "used": bool,
                "error": str | None
            }
        """

        fallback_text = self._build_fallback_text(
            role_name=role_name,
            deterministic_arguments=deterministic_arguments,
            score_name=score_name,
            score_value=score_value,
            suggested_decision=suggested_decision
        )

        # Verifica si esta habilitado la opcion de generacion por llm
        if not self.enabled:
            return {
                "text": fallback_text,
                "used": False,
                "error": None
            }

        try:
            # Implementar el sistem prompt
            system_prompt = (
                "Eres un agente de debate dentro de un sistema bancario "
                "multi-agente de detección de fraude. "
                "Tu función es redactar un argumento breve y controlado. "
                "No inventes evidencia. "
                "No cambies la decisión sugerida. "
                "No cambies el score. "
                "No emitas la decisión final del sistema. "
                "Usa solamente la evidencia entregada. "
                "Responde en español profesional, máximo 90 palabras."
            )

            # Construir el payload de request
            user_payload = {
                "role_name": role_name,
                "position": position,
                "deterministic_arguments": deterministic_arguments,
                "evidence_payload": evidence_payload,
                "score_name": score_name,
                "score_value": score_value,
                "suggested_decision": suggested_decision,
                "output_instruction": (
                    "Redacta un único párrafo que defienda la postura del agente. "
                    "Debe ser útil para auditoría y para el DecisionArbiterAgent, "
                    "pero sin decidir."
                )
            }

            # Esperar la respuesta de la consulta a la API
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            user_payload,
                            ensure_ascii=False
                        )
                    }
                ],
                temperature=0.2,
                max_output_tokens=LLM_MAX_OUTPUT_TOKENS
            )

            # Splitar la respuest
            text = str(response.output_text or "").strip()

            # En caso de no obtener una respuesta generativa consiza recurrir a un texto fallback
            if not text:
                text = fallback_text

            return {
                "text": text,
                "used": True,
                "error": None
            }

        except Exception as exc:
            return {
                "text": fallback_text,
                "used": False,
                "error": str(exc)
            }
        
    
    def _build_fallback_text(
        self,
        role_name: str,
        deterministic_arguments: List[str],
        score_name: str,
        score_value: float,
        suggested_decision: str
    ) -> str:

        # Generar el argmuento en base a datos deterministicos
        joined_arguments = " ".join(deterministic_arguments or [])

        if not joined_arguments:
            joined_arguments = (
                "No se generaron argumentos determinísticos suficientes."
            )

        return (
            f"{role_name}: {joined_arguments} "
            f"{score_name}: {score_value}. "
            f"Decisión sugerida por el agente: {suggested_decision}."
        )
