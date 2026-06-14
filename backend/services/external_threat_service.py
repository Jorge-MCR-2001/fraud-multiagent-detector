import json
from typing import Dict, Any, List

from settings.paths import EXTERNAL_THREAT_CONTEXT_JSON

def search_external_threats(transaction_context: Dict[str, Any])-> Dict[str, Any]:
    """
        Busca informacio externa gobernada para una transacción consultada.
        - Usa una fuente local/mock gobernada.
        - No hace web search real 
        - Solo devuelve señales externas y citas externas, sin asumir confidence
    """


    # Cargar informacion por mocks
    threat_items = _load_external_threat_context()

    matched_threats = []

    # Apliar la contextualizacion externa y agrupa solo las que hacen match con el contexto de la transaccion
    for threat in threat_items:
        if _matches_threat(
            transaction_context=transaction_context,
            threat=threat
        ):
            matched_threats.append(threat)

    # Construir señales por match externos
    external_signals = _build_external_signals(matched_threats)
    # Construir citas externas
    citations_external = _build_external_citations(matched_threats)

    return {
        "external_signals": external_signals,
        "citations_external": citations_external,
        "external_threat_context": matched_threats
    }


def _load_external_threat_context() -> List[Dict[str, Any]]:
    if not EXTERNAL_THREAT_CONTEXT_JSON.exists(): # Garantiza la fuente de informacion externa
        return []

    with open(EXTERNAL_THREAT_CONTEXT_JSON, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "external_threat_context.json debe contener una lista"
        )

    return data


def _matches_threat(transaction_context: Dict[str, Any], threat: Dict[str, Any]) -> bool:
    """
        Se considera match si coincide al menos uno de estos campos:
        - merchant_id
        - country
        - channel
        - device_id
    """

    # Aplicacion de compatibilidad por estos parametros
    match_fields = [
        "merchant_id",
        "country",
        "channel",
        "device_id"
    ]

    # Realizar la busqueda iterativa
    for field in match_fields:
        # Normalizar la informacion relativa a la fuente externa en base al parameter match
        threat_value = _normalize_text(threat.get(field))
        # Normalizar la informacion relativa a la transaccion en base al parameter match
        transaction_value = _normalize_text(transaction_context.get(field))

        # analizar si existe match entre fuente externa y transaccion en base al parameter match
        if threat_value and transaction_value and threat_value == transaction_value:
            return True

    return False


def _build_external_signals(matched_threats: List[Dict[str, Any]]) -> List[str]:
    # Construir lista de señales provenientes del match externo
    signals = []

    for threat in matched_threats:
        signal = threat.get("signal")

        if signal and signal not in signals:
            signals.append(signal)

    return signals


def _build_external_citations(matched_threats: List[Dict[str, Any]])-> List[Dict[str, Any]]:

    # Construir lista de citas externas
    citations = []

    for threat in matched_threats:
        citations.append(
            {
                "threat_id": threat.get("threat_id"),
                "url": threat.get("url"),
                "summary": threat.get("summary"),
                "risk_level": threat.get("risk_level"),
                "source_type": threat.get("source_type", "governed_mock_source")
            }
        )

    return citations


def _normalize_text(value: Any) -> str | None:

    # Normalizar el texto

    if value is None: # Garantiza input validos
        return None

    text = str(value).strip()

    if text == "": # Garantiza texto valido
        return None

    return text