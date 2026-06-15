# Level 3 Enterprise Readiness

Documento de preparacion enterprise para el backend de deteccion de fraude multiagente.

## Estado objetivo

Nivel 3 significa que el sistema no solo retorna una decision de fraude, sino que tambien entrega evidencia, explicabilidad, trazabilidad, auditoria, observabilidad, manejo controlado de errores y escalamiento humano.

## Capacidades implementadas

| Capacidad | Estado | Evidencia en codigo |
| --- | --- | --- |
| API FastAPI versionada | Implementado | `app.py` |
| Orquestacion multiagente con grafo | Implementado | `orchestrators/fraud_orchestrator.py`, `graph/fraud_graph.py` |
| RAG de politicas internas | Implementado | `rag/vectorstore/policy_index/*` |
| Inteligencia externa | Implementado | `resources/external_threat_context.json` |
| Debate pro-fraude/pro-cliente | Implementado | `agents/pro_fraud_debate_agent.py`, `agents/pro_customer_debate_agent.py` |
| Arbitraje de decision | Implementado | `agents/decision_arbiter_agent.py` |
| Explicabilidad cliente/auditoria | Implementado | `agents/explainability_agent.py` |
| HITL | Implementado | `services/hitl_queue_service.py`, `schemas/hitl_schema.py` |
| Auditoria persistente | Implementado | `services/audit_trail_service.py` |
| Observabilidad por agente | Implementado | `services/observability_service.py` |
| Errores controlados | Implementado | `services/error_handler.py`, `schemas/error_schema.py` |
| Contratos automatizados | Implementado | `test/test_level_3_contracts.py` |

## Flujo funcional

1. La API recibe `transaction_id` en `/evaluate/{transaction_id}`.
2. `FraudOrchestrator` carga la transaccion y el comportamiento historico del cliente.
3. El grafo ejecuta agentes especializados.
4. Los agentes producen senales, evidencias, argumentos, citas y trazas.
5. `DecisionArbiterAgent` define `decision`, `confidence`, `decision_basis` y `decision_rationale`.
6. `ExplainabilityAgent` genera explicaciones para cliente y auditoria.
7. `HITLRouterAgent` determina si requiere revision humana.
8. `AuditTrailAgent` persiste el evento auditable.
9. La API responde con `EvaluationResponse`.

## Controles enterprise

### Contrato de API estable

El contrato principal esta definido por `schemas/evaluation_response.py` y validado con `response_model=EvaluationResponse`. Esto reduce regresiones en integraciones externas.

Campos criticos:

- Decision final con enum controlado.
- Confianza normalizada entre `0.0` y `1.0`.
- Nivel y factores de confianza.
- Evidencia interna y externa.
- Trazas de agentes y decision.
- Estado HITL.
- Confirmacion de auditoria.
- Lista de errores no fatales.

### Auditoria

Cada evaluacion exitosa debe persistir un evento en `data/audit/audit_trail.jsonl`.

Campos minimos auditables:

- `audit_event_id`
- `evaluation_id`
- `transaction_id`
- `final_decision`
- `confidence`
- `decision_basis`
- `agent_trace`
- `decision_trace`
- `created_at`

La auditoria debe permitir reconstruir por que se aprobo, bloqueo, desafio o escalo una transaccion.

### Observabilidad

Los eventos tecnicos por agente se escriben en `data/observability/agent_events.jsonl`.

Campos minimos:

- `event_id`
- `evaluation_id`
- `transaction_id`
- `agent`
- `status`
- `message`
- `latency_ms`
- `details`
- `created_at`

Esta capa complementa `agent_trace`: `agent_trace` viaja en la respuesta, mientras que `agent_events.jsonl` queda persistido para monitoreo y diagnostico.

### HITL

La cola HITL se persiste en `data/hitl/hitl_queue.jsonl`.

Un caso HITL debe incluir:

- ID estable `hitl_queue_id`.
- Transaccion asociada.
- Motivo de revision.
- Prioridad.
- Decision y confianza originales.
- Snapshot de decision.
- Estado `PENDING_REVIEW` o `RESOLVED`.
- Revisor, resolucion, notas y fecha de resolucion cuando aplique.

### Manejo de errores

Los errores controlados deben responder con:

- `status`
- `error_code`
- `message`
- `trace_id`
- `details`

Codigos actuales:

| Codigo | HTTP | Uso |
| --- | --- | --- |
| `TRANSACTION_NOT_FOUND` | 404 | La transaccion no existe o no puede evaluarse. |
| `HITL_ITEM_NOT_FOUND` | 404 | El item HITL no existe. |
| `EVALUATION_FAILED` | 500 | Error inesperado durante la evaluacion. |

## Criterios de aceptacion nivel 3

El backend se considera listo para nivel 3 cuando:

- `/` reporta RAG, HITL y auditoria habilitados.
- Las transacciones de referencia retornan decisiones esperadas.
- `/evaluate/{transaction_id}` cumple el contrato completo.
- `decision_basis` es estructurado.
- `agent_trace` y `decision_trace` no estan vacios.
- Las citas internas y externas aparecen cuando son esperadas.
- Los casos ambiguos generan `hitl_queue_item`.
- Los eventos de auditoria se guardan como JSONL valido.
- Los eventos de observabilidad se guardan como JSONL valido.
- La cola HITL permite listar, consultar y resolver casos.
- La confianza se expresa con nivel y factores explicables.
- Los errores se devuelven con esquema controlado y `trace_id`.

## Riesgos conocidos

- El endpoint raiz reporta `level: "2"` aunque la descripcion y los tests permiten componentes de nivel 3. Conviene alinear este valor a `"3"` cuando el release sea formalmente nivel 3.
- `signal_metrics` forma parte del contrato esperado por tests, por lo que cualquier constructor de respuesta debe garantizarlo aunque no existan metricas.
- Los archivos JSONL son simples y utiles para demo o prototipo, pero en produccion deberian migrarse a almacenamiento transaccional o log centralizado.
- Si `LLM_ENABLED=true`, la disponibilidad y latencia del proveedor LLM pasan a ser dependencia operativa.
- Las pruebas generan datos en `data/audit`, `data/hitl` y `data/observability`; los pipelines deben considerar limpieza o aislamiento por corrida.

## Recomendaciones para produccion

- Persistir auditoria, HITL y observabilidad en una base o plataforma de logs con retencion y control de acceso.
- Agregar autenticacion y autorizacion a endpoints HITL.
- Agregar correlation ID por request y propagarlo a auditoria, observabilidad y errores.
- Separar configuracion por ambiente: local, staging y produccion.
- Agregar pruebas de carga para `/evaluate/{transaction_id}`.
- Agregar pruebas de contrato OpenAPI para consumidores externos.
- Versionar politicas RAG y registrar la version usada en cada evaluacion.
- Definir SLA para resolucion HITL segun prioridad.

## Evidencia automatizada

La evidencia principal esta en:

```powershell
pytest test/test_level_3_contracts.py
```

Esa suite valida el comportamiento enterprise minimo esperado para nivel 3.

