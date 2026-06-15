# API Contract

Contrato publico del backend FastAPI para evaluacion de fraude multiagente.

## Base

Servidor local:

```text
http://127.0.0.1:8000
```

Formato de respuesta:

- Exito: JSON.
- Error controlado: JSON dentro de `detail`.

## GET /

Retorna el estado operativo del backend.

### Response 200

```json
{
  "status": "running",
  "level": "2",
  "architecture": "langgraph_multi_agent_rag_debate_hitl_audit",
  "rag_enabled": true,
  "llm_enabled": false,
  "hitl_enabled": true,
  "audit_trail_enabled": true,
  "flow": [
    "TransactionContextAgent",
    "BehavioralPatternAgent",
    "InternalPolicyRAGAgent",
    "ExternalThreatIntelAgent",
    "EvidenceAggregationAgent",
    "ProFraudDebateAgent",
    "ProCustomerDebateAgent",
    "DecisionArbiterAgent",
    "ExplainabilityAgent",
    "HITLRouterAgent",
    "AuditTrailAgent"
  ]
}
```

## GET /evaluate/{transaction_id}

Evalua una transaccion y retorna la decision final del grafo multiagente.

### Path params

| Campo | Tipo | Requerido | Descripcion |
| --- | --- | --- | --- |
| `transaction_id` | string | Si | ID de transaccion existente en `data/source/transactions.csv`. |

### Response 200

Campos obligatorios:

| Campo | Tipo | Descripcion |
| --- | --- | --- |
| `transaction_id` | string | ID evaluado. |
| `decision` | enum | `APPROVE`, `CHALLENGE`, `BLOCK`, `ESCALATE_TO_HUMAN`. |
| `confidence` | number | Valor entre `0.0` y `1.0`. |
| `confidence_level` | enum | `HIGH`, `MEDIUM`, `LOW`. |
| `confidence_factors` | array | Factores que explican el puntaje de confianza. |
| `decision_basis` | object | Base estructurada de la decision. Debe incluir `basis_type` y `applied_rule` cuando aplique. |
| `decision_rationale` | string | Razonamiento resumido de la decision. |
| `requires_human_review` | boolean | Indica si la evaluacion requiere revision humana. |
| `signals` | array | Senales detectadas por los agentes. |
| `signal_tags` | array | Etiquetas normalizadas de riesgo. |
| `signal_metrics` | object | Metricas asociadas a las senales. |
| `citations_internal` | array | Evidencia de politicas internas RAG. |
| `citations_external` | array | Evidencia de inteligencia externa. |
| `evidence_bundle` | object | Paquete consolidado de evidencias. |
| `pro_fraud_argument` | object | Argumento a favor de fraude. |
| `pro_customer_argument` | object | Argumento a favor del cliente. |
| `explanation_customer` | string | Explicacion apta para comunicacion al cliente. |
| `explanation_audit` | string | Explicacion tecnica para auditoria. |
| `hitl_required` | boolean | Indica si se creo o se requiere caso HITL. |
| `hitl_reason` | string/null | Motivo de escalamiento humano. |
| `hitl_queue_item` | object/null | Item creado en cola HITL cuando corresponde. |
| `audit_saved` | boolean | Indica si la auditoria fue persistida. |
| `audit_event_id` | string/null | ID del evento de auditoria. |
| `agent_trace` | array | Traza de agentes ejecutados. |
| `decision_trace` | array | Pasos relevantes de decision. |
| `errors` | array | Errores no fatales capturados durante el flujo. |

### Example

```json
{
  "transaction_id": "T-1007",
  "decision": "CHALLENGE",
  "confidence": 0.78,
  "confidence_level": "HIGH",
  "confidence_factors": [
    {
      "factor": "policy_match",
      "impact": 0.2,
      "direction": "increase",
      "description": "La transaccion coincide con una politica interna de riesgo.",
      "evidence": {
        "policy_id": "POLICY-001"
      }
    }
  ],
  "decision_basis": {
    "basis_type": "rules_and_evidence",
    "applied_rule": "challenge_high_risk_signal"
  },
  "decision_rationale": "La transaccion requiere desafio por senales de riesgo relevantes.",
  "requires_human_review": false,
  "signals": ["amount_anomaly"],
  "signal_tags": ["HIGH_AMOUNT"],
  "signal_metrics": {},
  "citations_internal": [
    {
      "policy_id": "POLICY-001",
      "chunk_id": "chunk-1",
      "version": "nivel_02"
    }
  ],
  "citations_external": [
    {
      "threat_id": "THREAT-001",
      "source_type": "threat_intel",
      "risk_level": "HIGH"
    }
  ],
  "evidence_bundle": {},
  "pro_fraud_argument": {},
  "pro_customer_argument": {},
  "explanation_customer": "Necesitamos validar esta operacion.",
  "explanation_audit": "Decision basada en senales internas y externas.",
  "hitl_required": false,
  "hitl_reason": null,
  "hitl_queue_item": null,
  "audit_saved": true,
  "audit_event_id": "AUDIT-T-1007-...",
  "agent_trace": [],
  "decision_trace": [
    {
      "step": "final_decision",
      "value": "CHALLENGE"
    }
  ],
  "errors": []
}
```

### Errors

Transaccion inexistente:

```json
{
  "detail": {
    "status": "error",
    "error_code": "TRANSACTION_NOT_FOUND",
    "message": "Transaction T-9999 was not found.",
    "trace_id": "TRACE-...",
    "details": {
      "transaction_id": "T-9999"
    }
  }
}
```

Error inesperado de evaluacion:

```json
{
  "detail": {
    "status": "error",
    "error_code": "EVALUATION_FAILED",
    "message": "Fraud evaluation failed unexpectedly.",
    "trace_id": "TRACE-...",
    "details": {
      "transaction_id": "T-1007",
      "error": "..."
    }
  }
}
```

## GET /hitl/queue

Lista items de revision humana.

### Query params

| Campo | Tipo | Default | Descripcion |
| --- | --- | --- | --- |
| `status` | string | `PENDING_REVIEW` | Filtra por estado. Valores esperados: `PENDING_REVIEW`, `RESOLVED`. |

### Response 200

```json
{
  "item_count": 1,
  "items": [
    {
      "hitl_queue_id": "HITL-T-1005-...",
      "transaction_id": "T-1005",
      "reason": "Human review required.",
      "priority": "HIGH",
      "status": "PENDING_REVIEW",
      "original_decision": "ESCALATE_TO_HUMAN",
      "original_confidence": 0.55,
      "requires_human_review": true,
      "decision_snapshot": {},
      "assigned_to": null,
      "reviewer": null,
      "resolution": null,
      "resolution_notes": null,
      "created_at": "2026-06-15T00:00:00+00:00",
      "resolved_at": null
    }
  ]
}
```

## GET /hitl/queue/{hitl_queue_id}

Retorna un item HITL por ID.

### Response 200

Retorna un objeto `HITLQueueItem`.

### Error 404

```json
{
  "detail": {
    "status": "error",
    "error_code": "HITL_ITEM_NOT_FOUND",
    "message": "HITL item not found: HITL-NOT-FOUND",
    "trace_id": "TRACE-...",
    "details": {
      "hitl_queue_id": "HITL-NOT-FOUND"
    }
  }
}
```

## POST /hitl/queue/{hitl_queue_id}/resolve

Resuelve un item de revision humana.

### Request body

```json
{
  "reviewer": "analyst_01",
  "resolution": "APPROVE",
  "notes": "Cliente validado manualmente."
}
```

`resolution` acepta: `APPROVE`, `CHALLENGE`, `BLOCK`, `ESCALATE_TO_HUMAN`.

### Response 200

```json
{
  "resolved": true,
  "item": {
    "hitl_queue_id": "HITL-T-1005-...",
    "transaction_id": "T-1005",
    "reason": "Human review required.",
    "priority": "HIGH",
    "status": "RESOLVED",
    "reviewer": "analyst_01",
    "resolution": "APPROVE",
    "resolution_notes": "Cliente validado manualmente.",
    "resolved_at": "2026-06-15T00:00:00+00:00"
  }
}
```

## Error schema

Todo error controlado usa:

| Campo | Tipo | Descripcion |
| --- | --- | --- |
| `status` | string | Siempre `error`. |
| `error_code` | string | Codigo estable para integraciones. |
| `message` | string | Descripcion humana del error. |
| `trace_id` | string | ID para correlacion. |
| `details` | object | Contexto especifico del error. |

