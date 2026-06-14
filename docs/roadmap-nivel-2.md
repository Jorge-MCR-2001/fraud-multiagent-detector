Detector de Fraudes Multi Agentico - Niver 02
-> Objetivo: 
    Convertir la arquitectura Langgraph deterministica en un workflow multi agentico completo loca
-> Tecnologia:
    - Uso netamente de herramientas Locales, no hay implementación con cloud, CI/CD, frontend avanzado, monitoreo, Azure AI Search
    - Implementación de tecnologias RAG, LLM, human in the loop
    - Ampliación de Agentes en el sistema de grafos

-> Alcances:
    - Implementar RAG interno para consulta de politicas internas desde una base de datos vectorizada
    - Crear un Agente para recuperación de politicas internas - InternalPolicyRAGAgent
    - Implementar un Agente para consultas o simulaciones de alertas externas gobernadas - External Threat Intel Agent
    - Crear un Agente para reunir señales, politicas, RAG, fuentes externas y metricas - EvidenceAggregationAgent
    - Crear agentes de debate:
        -> ProFraudDebateAgent
        -> ProCustomerDebateAgent
    - Crear un Agente responsable de la toma de desiciones: DecisionArbiterAgent
    - Crear un Agente de explicacion al cliente: DecisionArbiterAgent
    - Implementar una primera version de Human-in-the-loop con cola local (atencion por tickets)
    - Implementar "audit trail" para registrar cada evaluacion
    - La respuesta por enpoint se mantendra a base de audit /evaluate/{transaction_id}
    - Ampliar la defición de estados del GRAFO: fraud_state.py / fraud_graph.py / orquestador
    - Probar los cuatro escenarios: 
        APPROVE
        CHALLENGE
        BLOCK
        ESCALATE_TO_HUMAN



-> Actividades:

    - Preparar la base documental mendiante RAG -> Crear un pipeline de creacion del Knowldege Base
    - Se hace nota de la diferencia de las fuentes de informacion:
        -> fraud_policies.json = fuente canoncia estructurada / funcion: motor de sugerencia de decisiones
        -> fraud_policy.md = representación documental para RAG / funcion: explicación de decisiones    






    - Migrar funcionalidades basicas a arquitectura de Grafos
        -> services/fraud_engine.py ---> orquestador
        -> services/policy_engine.py + services/signal_detector.py ---> agents
    - Conceptualizar motor de fraude monolitico a grafo de agentes especializados
    - Diseño del flujo de Agentes:
        -> Transaction Context Agent: Recopila información la transacción recibida
        -> Behavioral Pattern Agent: Comparar la transacción contra el comportamiento del cliente
        -> Policy Evaluation Agent: Evalua la señales detectadas contra las politicas internas
        -> Decision Arbiter Agent: Toma de decisiones
    - Conceptualizacion de la arquitectura:
        TransactionContextAgent -> BehavioralPatternAgent -> PolicyEvaluationAgent -> DecisionAgent
    - Estructuración de ficheros en Backend:
        -> Creación de folder agent / models / orquestadores
    - Construcción de grafos
        -> agents/base_agent.py --> Utilidades para trazabilidad de grafos
        -> graph/fraud_state.py --> Definición de la sintaxis de comunicacion entre los nodos
                                --> los nodos entregan state -> devuelven state actualizado
        -> agents/transaction_context_agent.py
                                --> Input: state["transaction"]
                                --> Output: state["transaction_context"]
        -> agents/behavioral_pattern_agent.py
                                --> Input: state["transaction_context"] / state["customer"]
                                --> Output: state["signal_tags"] / state["signals"] / state["signal_metrics"]
        -> agents/policy_evaluation_agent.py
                                --> Input: state["signal_tags"]
                                --> Output: state["matched_policies] / state["citations_internal] / state["policy_suggested_decision] / state["policy_suggested_confidence"]
        -> agents/desicion_agent.py
                                --> Input: state["signal_tags"] / state["matched_policies"] / state["policy_suggested_decision"] / state["policy_suggested_confidence"]
                                --> Output: state["decision"] / state["confidence"] / state["decision_trace"] (para trazabilidad)

    -> Definicion de servicio de logica de politicas:
        -> Se modifico la plantilla basica de politicas para evitar ambiguedad de eleccion de acción (decision):
        -> Escoge la politica con accion mas severa, en caso dos politicas fuesen activadas:
            "APPROVE" < "CHALLENGE" < "ESCALATE_TO_HUMAN" < "BLOCK"
        -> En el agente de desicion se apila la trazabilidad del sistema multiagentico, en funcion de:
                source: de "decision" -> Por Politicas / Por fallback (num de señales detectadas)
        -> Se genera un constructor dentro de services, para agrupar los datos de estado durante el ciclo de vida del sistema agentico (output + errores)

    -> Se debe conectar todo mediante Langgpraph, para esto se actualza el entorno virtual con: pip install langgraph
    -> Se construye: fraud_graph el cual implementa la comunicacion de los grafos
        -> Crear el grafo usando el estado compartido
        -> Instanciar los agentes creados
        -> Definir el flujo secuencial
        -> Compilar el grafo
    -> Se construye: fraud_orchestrator -> coordinador de acciones / conexion con capa APP

-> Notas:
    - No incluye LLM, RAG, Vector Database, Web Search, Human in Loop
    - Se añadio manualmente metricas dentro de fraud_policies.json para mayor trazabilidad de la decicion del agente PolicyEvaluationAgent
    - services/policy_engine.py solo debe sugerir que decision / confidence / politica debe usar el agente

-> Pruebas:
    - Demostración de funcionalidad con datos sinteticos de entrada (de todo el bloque de grafos)
        *INPUT*
            {
                "transaction_id": "T-1006"
            }
        *OUTPUT*
            {
                "transaction_id": "T-1006",
                "decision": "CHALLENGE",
                "confidence": 0.65,
                "signals": [
                    "Monto fuera de rango",
                    "País inusual"
                ],
                "signal_tags": [
                    "signal_a",
                    "signal_c"
                ],
                "citations_internal": [],
                "matched_policies": [],
                "agent_trace": [
                    {
                    "agent": "TransactionContextAgent",
                    "status": "completed",
                    "details": {
                        "transaction_id": "T-1006",
                        "customer_id": "CU-001",
                        "transaction_hour": 11
                    }
                    },
                    {
                    "agent": "BehaivoralPatternAgent",
                    "status": "completed",
                    "details": {
                        "signal_tags": [
                        "signal_a",
                        "signal_c"
                        ],
                        "signals_count": 2
                    }
                    },
                    {
                    "agent": "PolicyEvaluationAgent",
                    "status": "completed",
                    "details": {
                        "matched_policies_count": 0,
                        "policy_suggested_decision": null
                    }
                    }
                ],
                "decision_trace": [
                    {
                    "step": "signals_detected",
                    "value": [
                        "signal_a",
                        "signal_c"
                    ]
                    },
                    {
                    "step": "policies_matched",
                    "value": []
                    },
                    {
                    "step": "fallback_applied",
                    "value": "decision_by_signal_count"
                    },
                    {
                    "step": "decision_source",
                    "value": "fallback_signal_count"
                    },
                    {
                    "step": "final_decision",
                    "value": "CHALLENGE"
                    },
                    {
                    "step": "final_confidence",
                    "value": 0.65
                    }
                ]
                }