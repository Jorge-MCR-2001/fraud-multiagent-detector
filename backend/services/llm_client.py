import json
from typing import Dict, Any, List

from openai import OpenAI, AzureOpenAI

import settings.runtime_config as settings

# Obtener configuracion para el pipeline
def _get_setting(name: str, default=None):
    return getattr(settings, name, default)

# Verificar la condicion Boleana
def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    return str(value).strip().lower() in ["1", "true", "yes", "y", "on"]

class DebateLLMClient:

    """
        Cliente llm para debates:
        Responsabilidad:
        - Redactar argumentos.
        - No tomar decisiones.
        - No modificar scores.
        - No modificar suggested_decision.

        Soporta:
        - LLM_PROVIDER=openai
        - LLM_PROVIDER=azure_openai
    """

    def __init__(self) -> None:

        self.enabled = _as_bool(_get_setting("LLM_ENABLED", False))
        self.provider = str(
            _get_setting("LLM_PROVIDER", "openai") or "openai"
        ).lower()

        self.max_output_tokens = int(
            _get_setting("LLM_MAX_OUTPUT_TOKENS", 220) or 220
        )

        self.client = None
        self.model = None

        if not self.enabled:
            return
        
        if self.provider == "azure_openai":
            self._validate_azure_config()

            self.client = AzureOpenAI(
                api_key=_get_setting("AZURE_OPENAI_API_KEY"),
                azure_endpoint=_get_setting("AZURE_OPENAI_ENDPOINT"),
                api_version=_get_setting(
                    "AZURE_OPENAI_API_VERSION",
                    "2024-02-15-preview"
                ),
            )

            self.model = _get_setting("AZURE_OPENAI_DEPLOYMENT_NAME")

        elif self.provider == "openai":
            self._validate_openai_config()
            
            self.client = OpenAI(
                api_key=_get_setting("OPENAI_API_KEY")
            )

            self.model = _get_setting("LLM_MODEL", "gpt-4.1-mini")

        else:
            raise ValueError(
                f"El provaider no esta soportado: {self.provider}"
            )

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
                max_output_tokens=self.max_output_tokens
            )

            # Splitar la respuesta
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
    
    # Validar configuracion de OPENAI
    def _validate_openai_config(self) -> None:
        missing = []

        if not _get_setting("OPENAI_API_KEY"):
            missing.append("OPENAI_API_KEY")

        if not _get_setting("LLM_MODEL", "gpt-4.1-mini"):
            missing.append("LLM_MODEL")

        if missing:
            raise ValueError(
                "Faltan variables para LLM_PROVIDER=openai: "
                + ", ".join(missing)
            )

    # Validar configuracion de AzureOpenAI
    def _validate_azure_config(self) -> None:
        missing = []

        if not _get_setting("AZURE_OPENAI_ENDPOINT"):
            missing.append("AZURE_OPENAI_ENDPOINT")

        if not _get_setting("AZURE_OPENAI_API_KEY"):
            missing.append("AZURE_OPENAI_API_KEY")

        if not _get_setting("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"):
            missing.append("AZURE_OPENAI_API_VERSION")

        if not _get_setting("AZURE_OPENAI_DEPLOYMENT_NAME"):
            missing.append("AZURE_OPENAI_DEPLOYMENT_NAME")

        if missing:
            raise ValueError(
                "Faltan variables para LLM_PROVIDER=azure_openai: "
                + ", ".join(missing)
            )