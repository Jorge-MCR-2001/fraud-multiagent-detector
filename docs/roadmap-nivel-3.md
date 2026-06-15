Detector de Fraudes Multi Agentico - Nivel 03

-> Objetivo:
    Convertir el backend multi agentico de Nivel 2 en un proyecto mas robusto, testeable, observable y preparado para revision humana formal.

-> Tecnologia:
    - Uso local del backend FastAPI + LangGraph
    - Uso de schemas Pydantic para respuestas estaticas
    - Uso de testing automatizado con pytest
    - Uso de ficheros JSONL para audit trail, HITL queue y observabilidad
    - Manejo de errores controlados para endpoints principales
    - No se implementa aun Cloud, CI/CD, Azure AI Search, Cosmos DB o despliegue productivo

-> Alcances:
    - Formalizar el contrato de respuesta del endpoint /evaluate/{transaction_id}
    - Validar automaticamente los casos principales del desafio
    - Estandarizar decision_basis como estructura auditable
    - Estandarizar confidence con confidence_level y confidence_factors
    - Formalizar audit trail como evento JSONL
    - Formalizar cola HITL local como archivo JSONL
    - Agregar endpoints para consultar y resolver casos HITL
    - Agregar observabilidad estructurada por agente
    - Agregar manejo de errores enterprise para casos no encontrados
    - Mantener la arquitectura del Nivel 2 sin cambiar el flujo principal del grafo

-> Actividades:

    - Se crean schemas de respuesta para estabilizar el contrato del endpoint:
        -> schemas/evaluation_response.py
        -> decision
        -> confidence
        -> confidence_level
        -> confidence_factors
        -> decision_basis
        -> citations_internal
        -> citations_external
        -> agent_trace
        -> decision_trace
        -> hitl_queue_item
        -> audit_event_id

    - Se configura el endpoint /evaluate/{transaction_id} con response_model:
        -> response_model=EvaluationResponse
        -> Esto permite que FastAPI valide automaticamente la estructura de salida

    - Se corrige decision_basis para que ya no sea un string simple:
        -> Antes: "decision_basis": "policy_fp01_or_amount_time_risk"
        -> Ahora: decision_basis es un diccionario con:
            -> basis_type
            -> decision
            -> confidence
            -> internal_signals
            -> internal_policy_evidence
            -> external_threat_evidence
            -> debate_summary
            -> applied_rule

    - Se implementan pruebas automatizadas con pytest:
        -> test/test_level_3_contracts.py
        -> Se validan los cuatro escenarios principales:
            -> T-1003 -> APPROVE
            -> T-1004 -> BLOCK
            -> T-1005 -> ESCALATE_TO_HUMAN
            -> T-1007 -> CHALLENGE

    - Se valida que la respuesta tenga trazabilidad:
        -> agent_trace
        -> decision_trace
        -> citations_internal
        -> citations_external
        -> explanation_customer
        -> explanation_audit

    - Se formaliza el audit trail:
        -> services/audit_trail_service.py
        -> data/audit/audit_trail.jsonl
        -> Cada evaluacion genera un evento con:
            -> audit_event_id
            -> evaluation_id
            -> transaction_id
            -> final_decision
            -> confidence
            -> decision_basis
            -> citations_internal
            -> citations_external
            -> agent_trace
            -> decision_trace
            -> created_at

    - Se formaliza la cola HITL:
        -> services/hitl_queue_service.py
        -> schemas/hitl_schema.py
        -> data/hitl/hitl_queue.jsonl
        -> Cuando una transaccion requiere revision humana se guarda un caso con:
            -> hitl_queue_id
            -> transaction_id
            -> reason
            -> priority
            -> status
            -> original_decision
            -> original_confidence
            -> decision_snapshot
            -> created_at

    - Se agregan endpoints para la cola HITL:
        -> GET /hitl/queue
        -> GET /hitl/queue/{hitl_queue_id}
        -> POST /hitl/queue/{hitl_queue_id}/resolve

    - Se implementa confidence scoring formal:
        -> services/confidence_scoring_service.py
        -> Se agregan campos:
            -> confidence_level
            -> confidence_factors
        -> La decision final no cambia, solo se agrega explicabilidad de confianza

    - Se actualiza DecisionArbiterAgent:
        -> Sigue siendo el responsable de decision final
        -> Ahora usa build_confidence_assessment
        -> Genera confidence
        -> Genera confidence_level
        -> Genera confidence_factors
        -> Mantiene decision_basis estructurado

    - Se implementa observabilidad por agente:
        -> services/observability_service.py
        -> data/observability/agent_events.jsonl
        -> Se conecta desde agents/base_agent.py
        -> Cada llamada a add_trace o add_error genera un evento observable

    - Se implementa manejo de errores enterprise:
        -> schemas/error_schema.py
        -> services/error_handler.py
        -> Se controlan errores como:
            -> TRANSACTION_NOT_FOUND
            -> HITL_ITEM_NOT_FOUND
            -> EVALUATION_FAILED
        -> Cada error devuelve:
            -> status
            -> error_code
            -> message
            -> trace_id
            -> details

    - Se agregan pruebas para errores controlados:
        -> /evaluate/T-9999
        -> /hitl/queue/HITL-NOT-FOUND
        -> /hitl/queue/HITL-NOT-FOUND/resolve

-> Estado actual:
    - Nivel 3 en fase avanzada
    - Contratos Pydantic implementados
    - Testing automatizado implementado
    - Audit trail formal implementado
    - HITL queue formal implementado
    - Confidence scoring formal implementado
    - Observabilidad por agente implementada
    - Manejo de errores enterprise implementado

-> Pruebas:
    - Comando principal:
        pytest -v

    - Resultado actual:
        18 passed, 1 warning

    - El warning actual corresponde a TestClient / Starlette:
        -> No bloquea el cierre funcional del Nivel 3

-> Notas:
    - No se cambia el flujo principal del grafo del Nivel 2
    - No se agregan servicios cloud
    - No se implementa frontend
    - No se implementa CI/CD
    - No se implementa Azure AI Search
    - No se implementa Cosmos DB
    - No se implementa Terraform
    - El Nivel 3 prepara el backend para una futura etapa cloud y productiva

-> Pendiente para cierre final:
    - Actualizar README.md
    - Crear .env.example
    - Crear documentacion corta:
        -> docs/api_contract.md
        -> docs/testing_guide.md
        -> docs/hitl_workflow.md
        -> docs/audit_trail_schema.md
    - Ejecutar pytest -v antes del cierre
    - Crear commit final del Nivel 3
    - Crear tag:
        -> level-3-closed

-> Criterio de cierre:
    - El backend responde correctamente los cuatro escenarios del desafio
    - El endpoint /evaluate/{transaction_id} tiene contrato estable
    - pytest valida automaticamente los flujos principales
    - audit_trail.jsonl registra cada evaluacion
    - hitl_queue.jsonl registra casos de revision humana
    - agent_events.jsonl registra eventos por agente
    - Los errores principales tienen respuesta controlada
    - La documentacion permite levantar y probar el proyecto desde cero
