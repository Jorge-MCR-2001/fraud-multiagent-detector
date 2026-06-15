# Backend - Multi-Agent Fraud Detection 1.0.0

Backend FastAPI del sistema multi-agente para detección de fraude ambiguo en transacciones financieras.

Este backend concentra la lógica principal del desafío: procesamiento de transacciones, orquestación LangGraph, agentes especializados, RAG de políticas internas, inteligencia externa gobernada, debate, decisión, explicabilidad, Human-in-the-loop, audit trail, observabilidad y health checks cloud-ready.

## Rol del backend

El backend expone una API REST que permite:

- Evaluar una transacción por `transaction_id`.
- Generar una decisión: `APPROVE`, `CHALLENGE`, `BLOCK` o `ESCALATE_TO_HUMAN`.
- Calcular confianza y factores de confianza.
- Registrar señales, evidencias internas y evidencias externas.
- Generar explicación para cliente y auditoría.
- Persistir audit trail.
- Crear y resolver casos Human-in-the-loop.
- Exponer readiness/liveness para despliegue cloud.

## Arquitectura interna

```text
app.py
  -> FraudOrchestrator
      -> fraud_graph.py / LangGraph
          -> TransactionContextAgent
          -> BehavioralPatternAgent
          -> InternalPolicyRAGAgent
          -> ExternalThreatIntelAgent
          -> EvidenceAggregationAgent
          -> ProFraudDebateAgent
          -> ProCustomerDebateAgent
          -> DecisionArbiterAgent
          -> ExplainabilityAgent
          -> HITLRouterAgent
          -> AuditTrailAgent
```

## Estructura principal

```text
backend/
  app.py
  dockerfile
  requirements.txt
  .env.example
  agents/
  graph/
  orchestrators/
  rag/
  resources/
  schemas/
  services/
  settings/
  storage/
  test/
  data/
    source/
    audit/
    hitl/
    observability/
  docs/
```

## Componentes

| Carpeta / archivo | Descripción |
|---|---|
| `app.py` | API FastAPI y endpoints principales |
| `orchestrators/fraud_orchestrator.py` | Carga datos y ejecuta el grafo |
| `graph/fraud_graph.py` | Workflow LangGraph |
| `graph/fraud_state.py` | Estado compartido entre agentes |
| `agents/` | Agentes especializados del flujo |
| `rag/` | Indexación y recuperación RAG local / Azure AI Search preparado |
| `resources/` | Políticas de fraude e inteligencia externa gobernada |
| `schemas/` | Contratos Pydantic de respuesta, error y HITL |
| `services/` | Servicios de datos, scoring, auditoría, HITL, LLM y observabilidad |
| `settings/` | Paths y configuración runtime |
| `test/` | Pruebas automatizadas Nivel 3 y Nivel 4 |

## Instalación local

```powershell
cd backend
python -m venv venvBackend
.\venvBackend\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Variables de entorno

Archivo base:

```text
.env.example
```

Configuración mínima local:

```env
APP_VERSION=4.0.0
ENVIRONMENT=local
STORAGE_PROVIDER=local_jsonl
RAG_PROVIDER=local_vectorstore
OBSERVABILITY_PROVIDER=local_jsonl
LLM_ENABLED=false
LLM_PROVIDER=openai
```

Configuración con LLM OpenAI:

```env
OPENAI_API_KEY=tu_api_key
LLM_ENABLED=true
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
LLM_MAX_OUTPUT_TOKENS=220
```

Configuración cloud objetivo:

```env
ENVIRONMENT=azure
LLM_PROVIDER=azure_openai
RAG_PROVIDER=azure_ai_search
STORAGE_PROVIDER=azure_cosmos
OBSERVABILITY_PROVIDER=application_insights
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_AI_SEARCH_ENDPOINT=
AZURE_AI_SEARCH_API_KEY=
AZURE_COSMOS_ENDPOINT=
AZURE_COSMOS_KEY=
APPLICATIONINSIGHTS_CONNECTION_STRING=
```

## Ejecución local

```powershell
cd backend
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Docker

Construir imagen:

```powershell
cd backend
docker build -t fraud-multiagent -f dockerfile .
```

Ejecutar API:

```powershell
docker run --rm -p 8000:8000 --env-file .env fraud-multiagent
```

Ejecutar pruebas:

```powershell
docker run --rm --env-file .env fraud-multiagent pytest -v
```

Resultado de cierre validado:

```text
23 passed, 1 warning
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Metadata de runtime y capacidades habilitadas |
| `GET` | `/health/live` | Liveness check |
| `GET` | `/health/ready` | Readiness check de providers y recursos |
| `GET` | `/evaluate/{transaction_id}` | Ejecuta evaluación multi-agente |
| `GET` | `/hitl/queue` | Lista casos HITL, por defecto `PENDING_REVIEW` |
| `GET` | `/hitl/queue/{hitl_queue_id}` | Consulta un caso HITL específico |
| `POST` | `/hitl/queue/{hitl_queue_id}/resolve` | Resuelve caso HITL con revisor, decisión y notas |

## Contrato de evaluación

Ejemplo:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/evaluate/T-1007"
```

Campos principales de respuesta:

```json
{
  "transaction_id": "T-1007",
  "decision": "CHALLENGE",
  "confidence": 0.65,
  "confidence_level": "MEDIUM",
  "confidence_factors": {},
  "decision_basis": {},
  "decision_rationale": "...",
  "requires_human_review": false,
  "signals": [],
  "signal_tags": [],
  "signal_metrics": {},
  "citations_internal": [],
  "citations_external": [],
  "evidence_bundle": {},
  "pro_fraud_argument": {},
  "pro_customer_argument": {},
  "explanation_customer": "...",
  "explanation_audit": "...",
  "hitl_required": false,
  "hitl_queue_item": null,
  "audit_saved": true,
  "audit_event_id": "...",
  "agent_trace": [],
  "decision_trace": [],
  "errors": []
}
```

## Escenarios principales

| Transaction ID | Decisión esperada | Propósito |
|---|---|---|
| `T-1003` | `APPROVE` | Caso legítimo / bajo riesgo |
| `T-1007` | `CHALLENGE` | Validación adicional por señales ambiguas |
| `T-1004` | `BLOCK` | Sospecha fuerte de fraude |
| `T-1005` | `ESCALATE_TO_HUMAN` | Revisión humana obligatoria |

## RAG interno

El RAG local usa:

```text
backend/resources/fraud_policies_nivel_02.json
backend/rag/vectorstore/policy_index/
```

El agente responsable es:

```text
agents/internal_policy_rag_agent.py
```

El proyecto también contiene módulos preparados para Azure AI Search:

```text
rag/azure_ai_search_indexer.py
rag/azure_ai_search_retriever.py
```

## Inteligencia externa gobernada

La fuente externa controlada está en:

```text
backend/resources/external_threat_context.json
```

Se usa para simular búsqueda web gobernada y mantener reproducibilidad durante pruebas y revisión técnica.

## Human-in-the-loop

Cuando una evaluación requiere revisión humana:

- Se marca `hitl_required=true`.
- Se crea un item en `data/hitl/hitl_queue.jsonl`.
- Se expone por `/hitl/queue`.
- Puede resolverse con `/hitl/queue/{hitl_queue_id}/resolve`.

Payload de resolución:

```json
{
  "reviewer": "analyst.demo",
  "resolution": "APPROVE",
  "notes": "Revisión manual completada."
}
```

## Audit trail y observabilidad

Audit trail:

```text
data/audit/audit_trail.jsonl
```

Eventos de agentes:

```text
data/observability/agent_events.jsonl
```

Cada evaluación registra:

- `audit_event_id`
- `evaluation_id`
- `transaction_id`
- `final_decision`
- `confidence`
- `decision_basis`
- `citations_internal`
- `citations_external`
- `agent_trace`
- `decision_trace`
- `created_at`

## Pruebas

```powershell
cd backend
pytest -v
```

Suites actuales:

```text
test/test_level_3_contracts.py
test/test_level_4_cloud_runtime.py
```

Validan:

- 4 decisiones principales.
- Contrato completo de respuesta.
- Citas RAG y externas.
- Agent trace y decision trace.
- Audit trail.
- HITL queue.
- Manejo de errores controlados.
- Health checks Nivel 4.
- Parsing correcto de variables booleanas.

## Readiness cloud

`/health/ready` puede responder `200` o `503`.

Un `503` no necesariamente significa falla funcional del backend; significa que algún provider configurado no tiene recursos completos. Esto es útil para despliegue cloud porque permite distinguir API viva de API lista para operar con todos sus recursos.

## Notas de seguridad

- No subir `.env` con secretos reales.
- Usar `.env.example` como plantilla.
- Para cloud, migrar secretos a Azure Key Vault.
- En producción, habilitar autenticación por API Key/OAuth y HTTPS.
