# Multi-Agent Fraud Detection 1.0.0

Sistema **multi-agente** para detección de fraude ambiguo en transacciones financieras, construido como una Web App con **Backend FastAPI + LangGraph** y **Frontend React/Vite**.

El proyecto implementa un flujo trazable para analizar transacciones, comparar comportamiento histórico, consultar políticas internas vía RAG, incorporar inteligencia externa gobernada, debatir evidencia entre agentes, decidir una acción final y derivar a revisión humana cuando corresponde.

## Estado de cierre

Este repositorio se cierra como una solución **Nivel 4 cloud-ready**:

- Backend funcional con FastAPI.
- Orquestación multi-agente con LangGraph.
- RAG interno local para políticas de fraude.
- Threat Intel gobernado mediante fuente externa controlada.
- Debate multi-agente: Pro-Fraud vs Pro-Customer.
- Decision Arbiter Agent con `decision_basis`, confianza y trazabilidad.
- Explainability Agent con explicación para cliente y auditoría.
- Human-in-the-loop con cola persistida.
- Audit trail JSONL por evaluación.
- Observabilidad estructurada por agente.
- Contratos Pydantic y pruebas automatizadas.
- Runtime cloud-ready con `/health/live` y `/health/ready`.
- Frontend React para operar y visualizar evaluaciones.
- Documentación de evolución en `docs/`.

> La ejecución por defecto usa providers locales (`local_jsonl`, `local_vectorstore`) para facilitar revisión técnica rápida. La arquitectura queda preparada para migrar a servicios gestionados en Azure.

## Alineamiento con el desafío técnico

El desafío solicita una Web App Backend + Frontend capaz de analizar transacciones, evaluar señales internas, consultar políticas mediante RAG, usar inteligencia externa gobernada, orquestar agentes, incluir HITL, registrar audit trail y generar explicaciones por transacción.

| Requerimiento | Implementación en el proyecto |
|---|---|
| Backend + Frontend | `backend/` FastAPI y `frontend/` React/Vite |
| Análisis de transacciones | `TransactionContextAgent` + `BehavioralPatternAgent` |
| Señales internas | monto, horario, país, dispositivo, comportamiento |
| RAG de políticas internas | `InternalPolicyRAGAgent` + `backend/rag/` |
| Inteligencia externa gobernada | `ExternalThreatIntelAgent` + `external_threat_context.json` |
| Orquestación de agentes | `LangGraph` en `backend/graph/fraud_graph.py` |
| Evidencia agregada | `EvidenceAggregationAgent` |
| Debate de agentes | `ProFraudDebateAgent` y `ProCustomerDebateAgent` |
| Decisión final | `DecisionArbiterAgent` |
| Explicabilidad | `ExplainabilityAgent` |
| Human-in-the-loop | `HITLRouterAgent` + `/hitl/queue` |
| Audit trail | `AuditTrailAgent` + `data/audit/audit_trail.jsonl` |
| 4 escenarios | `APPROVE`, `CHALLENGE`, `BLOCK`, `ESCALATE_TO_HUMAN` |
| Cloud readiness | Docker, providers configurables, health/readiness checks |

## Arquitectura funcional

```text
Frontend React/Vite
        |
        v
FastAPI Backend
        |
        v
FraudOrchestrator
        |
        v
LangGraph Workflow
        |
        +--> TransactionContextAgent
        +--> BehavioralPatternAgent
        +--> InternalPolicyRAGAgent
        +--> ExternalThreatIntelAgent
        +--> EvidenceAggregationAgent
        +--> ProFraudDebateAgent
        +--> ProCustomerDebateAgent
        +--> DecisionArbiterAgent
        +--> ExplainabilityAgent
        +--> HITLRouterAgent
        +--> AuditTrailAgent
```

## Decisiones soportadas

| Decisión | Significado |
|---|---|
| `APPROVE` | Transacción legítima o de bajo riesgo |
| `CHALLENGE` | Requiere validación adicional |
| `BLOCK` | Bloqueo por sospecha fuerte de fraude |
| `ESCALATE_TO_HUMAN` | Revisión humana obligatoria |

Escenarios principales usados para validación:

| Transaction ID | Decisión esperada |
|---|---|
| `T-1003` | `APPROVE` |
| `T-1007` | `CHALLENGE` |
| `T-1004` | `BLOCK` |
| `T-1005` | `ESCALATE_TO_HUMAN` |

## Estructura del repositorio

```text
multi-agent-fraud-detection-1.0.0/
  README.md
  backend/
    README.md
    readme_backend.md
    app.py
    dockerfile
    requirements.txt
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
  frontend/
    README.md
    readme_frontend.md
    package.json
    vite.config.js
    src/
    dist/
  docs/
    README.md
    Desafio Tecnico.txt
    roadmap-nivel-0.md
    roadmap-nivel-1.md
    roadmap-nivel-2.md
    roadmap-nivel-3.md
    roadmap-nivel-4.md
    level_4_cloud_readiness.md
    evidence/
  scripts/
    generate_evidence.ps1
```

## Ejecución rápida local

### 1. Backend

```powershell
cd backend
python -m venv venvBackend
.\venvBackend\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Validar backend:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health/live
http://127.0.0.1:8000/health/ready
```

### 2. Frontend

En otra terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abrir:

```text
http://127.0.0.1:5173
```

## Ejecución con Docker

Desde `backend/`:

```powershell
docker build -t fraud-multiagent -f dockerfile .
docker run --rm -p 8000:8000 --env-file .env fraud-multiagent
```

Ejecutar pruebas en Docker:

```powershell
docker run --rm --env-file .env fraud-multiagent pytest -v
```

Resultado validado de cierre:

```text
23 passed, 1 warning
```

El warning corresponde a `TestClient`/Starlette y no bloquea la ejecución funcional.

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Estado del runtime y capacidades habilitadas |
| `GET` | `/health/live` | Liveness check para despliegue cloud |
| `GET` | `/health/ready` | Readiness check con providers y recursos |
| `GET` | `/evaluate/{transaction_id}` | Evaluación multi-agente de una transacción |
| `GET` | `/hitl/queue` | Lista la cola HITL |
| `GET` | `/hitl/queue/{hitl_queue_id}` | Consulta un caso HITL |
| `POST` | `/hitl/queue/{hitl_queue_id}/resolve` | Resuelve un caso HITL |

## Ejemplos de uso

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/evaluate/T-1003"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/evaluate/T-1007"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/evaluate/T-1004"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/evaluate/T-1005"
```

La respuesta incluye, entre otros campos:

```json
{
  "decision": "CHALLENGE",
  "confidence": 0.65,
  "signals": [],
  "citations_internal": [],
  "citations_external": [],
  "explanation_customer": "...",
  "explanation_audit": "...",
  "agent_trace": [],
  "decision_trace": []
}
```

## Evidencias e informes generados

El endpoint `GET /evaluate/{transaction_id}` funciona como informe explicativo generado por IA/grafo para cada transacción: incluye decisión, confianza, señales, citas internas, evidencias externas, explicación para cliente, explicación para auditoría, trazas de agentes y trazas de decisión.

Para facilitar la revisión, se puede generar la carpeta `docs/evidence/`:

```powershell
.\scripts\generate_evidence.ps1 -RunDockerTests
```

Archivos esperados:

```text
docs/evidence/
  evaluate_T-1003_APPROVE.json
  evaluate_T-1007_CHALLENGE.json
  evaluate_T-1004_BLOCK.json
  evaluate_T-1005_ESCALATE_TO_HUMAN.json
  hitl_queue_sample.json
  audit_trail_sample.jsonl
  agent_events_sample.jsonl
  runtime_root_response.json
  health_ready_response.json
  test_result_23_passed.txt
```

## Variables de entorno

Archivo base:

```text
backend/.env.example
```

Valores locales recomendados:

```env
APP_VERSION=4.0.0
ENVIRONMENT=local
STORAGE_PROVIDER=local_jsonl
RAG_PROVIDER=local_vectorstore
OBSERVABILITY_PROVIDER=local_jsonl
LLM_ENABLED=false
LLM_PROVIDER=openai
```

Con LLM habilitado:

```env
OPENAI_API_KEY=tu_api_key
LLM_ENABLED=true
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
```

Con Azure como arquitectura objetivo:

```env
ENVIRONMENT=azure
LLM_PROVIDER=azure_openai
RAG_PROVIDER=azure_ai_search
STORAGE_PROVIDER=azure_cosmos
OBSERVABILITY_PROVIDER=application_insights
```

## Cloud readiness

El proyecto se entrega cloud-ready, con ejecución local por defecto y providers configurables para migración a Azure:

| Capa | Local actual | Cloud objetivo |
|---|---|---|
| API | FastAPI Docker | Azure Container Apps / App Service |
| RAG | Vectorstore local | Azure AI Search |
| Audit trail | JSONL | Azure Cosmos DB |
| HITL queue | JSONL | Azure Cosmos DB |
| Observabilidad | JSONL | Application Insights |
| Secretos | `.env` | Azure Key Vault |
| LLM | OpenAI / fallback | Azure OpenAI |

Ver detalle en:

```text
docs/level_4_cloud_readiness.md
```

## Documentación

| Documento | Propósito |
|---|---|
| `backend/README.md` | Ejecución, endpoints, arquitectura backend, tests y Docker |
| `frontend/README.md` | Ejecución, build, proxy y uso de la consola React |
| `docs/README.md` | Índice de evolución, evidencias y documentación de control |
| `docs/roadmap-nivel-0.md` | MVP inicial por reglas |
| `docs/roadmap-nivel-1.md` | Migración a grafo multi-agente |
| `docs/roadmap-nivel-2.md` | RAG, threat intel, debate y explicabilidad |
| `docs/roadmap-nivel-3.md` | Contratos, HITL, audit trail, observabilidad y tests |
| `docs/roadmap-nivel-4.md` | Cierre cloud-ready y frontend |
| `docs/Desafio Tecnico.txt` | Enunciado del desafío usado como base |

## Alcance y supuestos

- Los datos son sintéticos y no contienen datos personales reales.
- La inteligencia externa se implementa como fuente gobernada/controlada para asegurar reproducibilidad.
- El sistema puede operar sin LLM (`LLM_ENABLED=false`) usando fallback determinístico para demo y pruebas.
- El cloud real se documenta como arquitectura objetivo y readiness contractual; la ejecución local/Docker es la ruta principal de revisión.
- La seguridad de secretos se deja preparada para Key Vault mediante variables de entorno y providers configurables.

## Checklist de cierre

- [x] Backend FastAPI operativo.
- [x] Frontend React operativo.
- [x] LangGraph como framework de orquestación.
- [x] RAG interno para políticas.
- [x] Threat Intel gobernado.
- [x] Debate multi-agente.
- [x] Decision Arbiter.
- [x] Explainability Agent.
- [x] HITL queue.
- [x] Audit trail.
- [x] Observabilidad.
- [x] Health checks cloud-ready.
- [x] Dockerfile.
- [x] Tests automatizados: 23 passed.
- [x] Documentación de evolución.
- [x] Script de evidencias.
