from typing import Dict, Any, List, Optional

SIGNAL_DICTIONARY = {
    "signal_a": "Monto fuera de rango",
    "signal_b": "Horario no habitual",
    "signal_c": "País inusual",
    "signal_d": "Dispositivo desconocido"
}


def detect_signals(transaction_context: Dict[str, Any], customer: Dict[str, Any]) -> Dict[str, Any]:
    
    signal_tags: List[str] = []
    signals: List[str] = []
    signal_metrics: Dict[str, Any] = {}

    # 1. Parametros relativos al monto de transacción de cliente X
    # 1.1 Monto de Transacción de cliente X
    transaction_amount = _safe_float(transaction_context.get("amount"))
    # 1.2 Comportamiento usual relativo a transacción de X
    usual_amount_avg = _safe_float(customer.get("usual_amount_avg"))

    # 2. Parametros relativos al rango de horario de transaccion de cliente X
    # 2.1 Hora de transacción --> Debido a la precisión de información relativa del cliente (horas)
    transaction_hour = _safe_int(transaction_context.get("transaction_hour"))
    # 2.2 Comportamiento usual relativo a horario de transacciónes del cliente X
    usual_hours = _normalize_text(customer.get("usual_hours"))

    # 3. Parametros relativos al origen geografico de transaccion de cliente X
    # 3.1 Origen de transacción de cliente X
    transaction_country = _normalize_text(transaction_context.get("country"))
    # 3.2 Comportamiento usual de origen de geografico de transacción de cliente X
    usual_countries = _normalize_list(customer.get("usual_countries"))

    # 4. Parametros relativos al dispositivo de transacción de cliente X
    # 4.1 Dispositivo de transacción de cliente X
    transaction_device = _normalize_text(transaction_context.get("device_id"))
    # 4.2 Comportamiento usual relativo al dispositivo de transacción de cliente X
    usual_devices = _normalize_list(customer.get("usual_devices"))


    # Analisis de señales
    # 1. Monto fuera de rango
    amount_ratio: Optional[float] = None # medir varianza de la tranascion respecto a la usual

    if transaction_amount is not None and usual_amount_avg not in (None, 0): # Los datos ingresados son validos

        amount_ratio = round(transaction_amount/usual_amount_avg,2)

        if transaction_amount > 3 * usual_amount_avg:
            signal_tags.append("signal_a")
            signals.append(SIGNAL_DICTIONARY ["signal_a"])

    # Apilar métricas de las señales
    signal_metrics["transaction_amount"] = transaction_amount
    signal_metrics["usual_amount_avg"] = usual_amount_avg
    signal_metrics["amount_ratio"] = amount_ratio

    # 2. Horario Habitual
    first_hour = None
    last_hour = None

    if usual_hours and "-" in usual_hours: # Garantizar la existencia de datos
        try:
            first_hour = int(usual_hours.split("-")[0])
            last_hour = int(usual_hours.split("-")[1])

            # Existe informacion de hora de transacción
            if transaction_hour is not None:
                if (transaction_hour < first_hour or transaction_hour > last_hour):
                    signal_tags.append("signal_b")
                    signals.append(SIGNAL_DICTIONARY ["signal_b"])

        except ValueError:
            pass

    # Apilar métricas de las señales
    signal_metrics["transaction_hour"] = transaction_hour
    signal_metrics["usual_hours"] = usual_hours
    signal_metrics["usual_start_hour"] = first_hour
    signal_metrics["usual_end_hour"] = last_hour

    # 3. Pais Habitual
    if transaction_country and usual_countries: # Garantizar la existencia de datos
        if transaction_country not in usual_countries:
            signal_tags.append("signal_c")
            signals.append(SIGNAL_DICTIONARY ["signal_c"])

    # Apilar métricas de las señales
    signal_metrics["transaction_country"] = transaction_country
    signal_metrics["usual_countries"] = usual_countries

    # 4. Dispositivo desconocido
    if transaction_device and usual_devices: # Garantizar la existencia de datos
        if transaction_device not in usual_devices:
            signal_tags.append("signal_d")
            signals.append(SIGNAL_DICTIONARY["signal_d"])

    # Apilar métricas de las señales
    signal_metrics["transaction_device"] = transaction_device
    signal_metrics["usual_devices"] = usual_devices

    return {
        "signal_tags": signal_tags,
        "signals": signals,
        "signal_metrics": signal_metrics
    }


def _safe_int(value: Any) -> Optional[int]:

    # Retorna vacio si no se declaro vacio el valor explicitamente
    if value is None:
        return None
    
    # Garantizar el formato integer para variables monetarias
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
    

def _safe_float(value: Any) -> Optional[float]:

    # Retorna vacio si no se declaro vacio el valor explicitamente
    if value is None:
        return None
    
    # Garantizar el formato flotante para variables monetarias
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
    

def _normalize_text(value: Any) -> Optional[str]:
    
    # Retorna vacio si no se declaro vacio el valor explicitamente
    if value is None:
        return None
    
    # Garantizar el valor en STRING y eliminar espacios en blanco al inico y final
    text = str(value).strip()

    # Si no se a ingresado un dato de transacción se retornara vacio
    if text == "":
        return None
    
    return text

def _normalize_list(value: Any) -> List[str]:
    
    # Convierte un intput str a lista
    if value is None:
        return []

    text = str(value).strip()

    if text == "":
        return []

    return [
        item.strip()
        for item in text.split(",")
        if item.strip()
    ]