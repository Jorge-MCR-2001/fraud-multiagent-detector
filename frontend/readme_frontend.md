# Frontend - Fraud Multi-Agent Console

Frontend React/Vite para operar y visualizar el sistema multi-agente de detección de fraude.

La consola permite ejecutar evaluaciones, inspeccionar decisiones, revisar señales, citas RAG, inteligencia externa, argumentos de debate, explicación para cliente/auditoría, rutas de agentes, trazas de decisión, cola Human-in-the-loop y estado cloud-ready del backend.

## Rol del frontend

El frontend cubre la capa Web App solicitada por el desafío. No implementa lógica de fraude; consume el backend FastAPI y presenta de forma clara la evidencia generada por el sistema multi-agente.

## Funcionalidades

- Evaluar transacciones por `transaction_id`.
- Botones rápidos para los cuatro escenarios del desafío:
  - `T-1003` → `APPROVE`
  - `T-1007` → `CHALLENGE`
  - `T-1004` → `BLOCK`
  - `T-1005` → `ESCALATE_TO_HUMAN`
- Mostrar:
  - decisión final,
  - confianza,
  - nivel de confianza,
  - señales detectadas,
  - métricas de señales,
  - citas internas RAG,
  - inteligencia externa gobernada,
  - argumento Pro-Fraud,
  - argumento Pro-Customer,
  - explicación para cliente,
  - explicación para auditoría,
  - ruta de agentes,
  - traza de decisión,
  - JSON completo de respuesta.
- Gestión HITL:
  - listar casos pendientes,
  - listar casos resueltos,
  - resolver un caso desde la interfaz.
- Vista Runtime:
  - `/`
  - `/health/live`
  - `/health/ready`

## Estructura

```text
frontend/
  package.json
  package-lock.json
  index.html
  vite.config.js
  .env.example
  src/
    main.jsx
    App.jsx
    api/
      client.js
    utils/
      formatters.js
    components/
      Card.jsx
      CitationList.jsx
      DecisionBadge.jsx
      EvaluationView.jsx
      HitlQueue.jsx
      JsonBlock.jsx
      Metric.jsx
      RuntimeView.jsx
      Sidebar.jsx
      SignalTags.jsx
      StatusPill.jsx
      Timeline.jsx
    styles.css
```

## Requisitos

- Node.js 18+ recomendado.
- Backend corriendo en `http://127.0.0.1:8000`.

## Ejecución local

Primero levantar el backend:

```powershell
cd backend
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Luego levantar el frontend:

```powershell
cd frontend
npm install
npm run dev
```

Abrir:

```text
http://127.0.0.1:5173
```

## Configuración de API

Por defecto, el frontend usa el proxy de Vite para apuntar al backend local.

Archivo:

```text
vite.config.js
```

Proxy local:

```text
/api -> http://127.0.0.1:8000
```

Si el backend está desplegado, crear `frontend/.env`:

```env
VITE_API_BASE_URL=https://TU_BACKEND_PUBLICO
```

Luego:

```powershell
npm run build
```

## Scripts disponibles

```powershell
npm run dev
npm run build
npm run preview
```

## Build productivo

```powershell
cd frontend
npm install
npm run build
```

Salida:

```text
frontend/dist/
```

Preview:

```powershell
npm run preview
```

## Endpoints consumidos

| Método | Ruta | Uso en frontend |
|---|---|---|
| `GET` | `/` | Runtime general |
| `GET` | `/health/live` | Estado vivo del backend |
| `GET` | `/health/ready` | Readiness cloud |
| `GET` | `/evaluate/{transaction_id}` | Evaluar transacción |
| `GET` | `/hitl/queue?status=PENDING_REVIEW` | Listar HITL pendiente |
| `GET` | `/hitl/queue?status=RESOLVED` | Listar HITL resuelto |
| `POST` | `/hitl/queue/{hitl_queue_id}/resolve` | Resolver caso HITL |

## Flujo de demo recomendado

1. Abrir frontend en `http://127.0.0.1:5173`.
2. Ejecutar `T-1003` y mostrar `APPROVE`.
3. Ejecutar `T-1007` y mostrar `CHALLENGE`.
4. Ejecutar `T-1004` y mostrar `BLOCK`.
5. Ejecutar `T-1005` y mostrar `ESCALATE_TO_HUMAN`.
6. Abrir la sección HITL y mostrar el caso pendiente.
7. Resolver el caso con usuario `analyst.demo`.
8. Abrir la sección Runtime y mostrar `/health/live` y `/health/ready`.
9. Mostrar el JSON completo como evidencia de trazabilidad.

## Relación con evidencias

El frontend muestra en pantalla la misma respuesta que se guarda en `docs/evidence/` mediante el script:

```powershell
.\scripts\generate_evidence.ps1
```

El script no forma parte del frontend; es una utilidad de entrega para dejar evidencias reproducibles en el repositorio.

## Notas

- El frontend no contiene secretos.
- El frontend no toma decisiones de fraude.
- Toda decisión proviene del backend multi-agente.
- Para despliegue productivo, servir `dist/` desde un hosting estático o integrarlo con Azure Static Web Apps.
