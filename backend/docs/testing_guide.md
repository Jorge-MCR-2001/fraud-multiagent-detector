# Testing Guide

Guia de pruebas para el backend del sistema multiagente de deteccion de fraude.

## Objetivo

Validar que la API, el grafo multiagente, los contratos de respuesta, la cola HITL, la auditoria y la observabilidad funcionen como una unidad verificable de nivel enterprise.

## Preparacion del entorno

Ejecutar los comandos desde `multi-agent-fraud-detection-1.0.0/backend`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

El backend puede ejecutarse sin LLM para las pruebas contractuales base. En ese modo, `LLM_ENABLED=false` evita requerir API key para los agentes de debate.

Variables relevantes en `backend/.env`:

```env
LLM_ENABLED=false
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=
```

Si se regenera el indice RAG con embeddings reales, configurar las credenciales correspondientes antes de ejecutar el indexador.

## Comandos principales

Ejecutar toda la suite:

```powershell
pytest
```

Ejecutar solo contratos de nivel 3:

```powershell
pytest test/test_level_3_contracts.py
```

Ejecutar con salida detallada:

```powershell
pytest -v test/test_level_3_contracts.py
```

Levantar la API localmente:

```powershell
uvicorn app:app --reload
```

Validar manualmente un caso:

```powershell
curl http://127.0.0.1:8000/evaluate/T-1007
```

## Suite contractual de nivel 3

El archivo `test/test_level_3_contracts.py` cubre los comportamientos que no deben romperse entre cambios:

- Salud del sistema en `/`.
- Decisiones esperadas para transacciones base.
- Campos obligatorios del contrato `EvaluationResponse`.
- Estructura de `decision_basis`.
- Trazas de agentes y decision.
- Citas internas RAG y citas externas.
- Enrutamiento HITL para casos ambiguos o de baja confianza.
- Persistencia de auditoria en `data/audit/audit_trail.jsonl`.
- Persistencia de observabilidad en `data/observability/agent_events.jsonl`.
- Lectura y resolucion de cola HITL.
- Errores controlados para transacciones o items HITL inexistentes.
- Factores formales de confianza.

## Casos de referencia

Las pruebas usan estas transacciones como contrato funcional:

| Transaction ID | Decision esperada |
| --- | --- |
| `T-1003` | `APPROVE` |
| `T-1004` | `BLOCK` |
| `T-1005` | `ESCALATE_TO_HUMAN` |
| `T-1007` | `CHALLENGE` |

Si cambia la logica de negocio, actualizar primero los criterios esperados y documentar la razon del cambio.

## Artefactos generados

Durante la evaluacion se escriben archivos JSONL:

- `data/audit/audit_trail.jsonl`: eventos de auditoria por evaluacion.
- `data/hitl/hitl_queue.jsonl`: cola de revision humana.
- `data/observability/agent_events.jsonl`: eventos tecnicos por agente.

Estos archivos forman parte del comportamiento verificable. Las pruebas comprueban que existan y que contengan entradas JSON validas.

## Checklist antes de entregar cambios

- `pytest test/test_level_3_contracts.py` pasa completo.
- `/evaluate/{transaction_id}` mantiene todos los campos de `EvaluationResponse`.
- Los errores HTTP devuelven `status`, `error_code`, `message`, `trace_id` y `details`.
- Los cambios en decisiones quedan reflejados en tests y documentacion.
- La cola HITL sigue permitiendo listar, consultar por ID y resolver items.
- Auditoria y observabilidad siguen persistiendo JSONL valido.

