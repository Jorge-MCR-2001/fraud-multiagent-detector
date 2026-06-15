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
        -> fraud_policies.json -> fuente canoncia estructurada / funcion: motor de sugerencia de decisiones
        -> policy_chunks.json -> versión enriquecida para búsqueda RAG
    - Se implementan pipelines para la construcción del rag:
        -> embedding_client.py -> Clase que complila a los providers para la creacion de un KB
        -> rag_indexer.py -> Curación del json crudo para la generacion de chunks enriquecidos -> Creacion del vectorstore
            -> Para la construcción del CHUNK JSON, se considera 1 Diccionario de Politica x Chunk
        -> policy_chunks.py -> indice local tipo vectorstore
        -> rag_retiever.py -> recupera las politicas por señales y/o por contexto -> score hibrido
            -> El chunk solo debe parecerse semánticamente a la consulta, también debe estar alineado con las señales detectadas en la transacción.
        -> "Internal Policy RAG Agent" -> Agente que realiza la recuperación de contexto para el grafo
    - Se asocia "Internal Policy RAG Agent" al grafo:
        builder.add_edge("behavioral_pattern","internal_policy_rag")
        builder.add_edge("internal_policy_rag","policy_evaluation") 
    - Se construye una fuente de datos externa (mock)
    - Se asocia "External Threat Intel" al grafo:
        builder.add_edge("behavioral_pattern","internal_policy_rag")
        builder.add_edge("internal_policy_rag", "external_threat_intel")
        builder.add_edge("external_threat_intel","policy_evaluation")
    - Se reconfiguro police_engine.py para adaptarlo correctamente a la ingesta del archivo .json -> comparacion con json crudo
    - Agregar la evidencia en el Agente: "Evidence Aggregation Agent" / En la que se hace apila la metadata de la busqueda agrupando:
        -> señales internas
        -> evidencia rag
        -> evidencia externa
    - Ademas se asocia "Evidence Aggregation Agent" al grafo:
        builder.add_edge("behavioral_pattern","internal_policy_rag")
        builder.add_edge("internal_policy_rag", "external_threat_intel")
        builder.add_edge("external_threat_intel","policy_evaluation")
        builder.add_edge("policy_evaluation", "evidence_aggregation")
    - Se añaden los estados: pro_fraud_argument & pro_customer_argument, para el debate de agentes, se inicia por una debate deterministico (previo al LLM)
        -> "pro_fraud_argument": Que tan probable es que sea fraude -------> se realiza un calculo deterministico orientado a prediccion de fraude
        -> "pro_customer_argument": Que tan probalbe es que sea veridico --> se realiza un calculo deterministico orientado a prediccion de veracidad
    - Se asumen una logica de score de riesgo de desicion de forma deterministica -> hardcodeada, sumando Agentes al grafo
        builder.add_edge("behavioral_pattern","internal_policy_rag")
        builder.add_edge("internal_policy_rag", "external_threat_intel")
        builder.add_edge("external_threat_intel","policy_evaluation")
        builder.add_edge("policy_evaluation", "evidence_aggregation")
        builder.add_edge("evidence_aggregation", "pro_fraud_debate")
        builder.add_edge("pro_fraud_debate", "pro_customer_debate")
        builder.add_edge("pro_customer_debate", "decision")
    -> Se diseña el Agente de desicion arbitraria: "Decision Arbiter Agent"
        -> Recopila toda la evidencia y contraste de ambos argumentos del proceso de Debate
        -> Se asigna una Decision y Confidence finales
        -> El antiguo Agente Decision Agent queda descontinuado
    -> Se asocia "Decision Arbiter Agent" al grafo:
        builder.add_edge("behavioral_pattern","internal_policy_rag")
        builder.add_edge("internal_policy_rag", "external_threat_intel")
        builder.add_edge("external_threat_intel","policy_evaluation")
        builder.add_edge("policy_evaluation", "evidence_aggregation")
        builder.add_edge("evidence_aggregation", "pro_fraud_debate")
        builder.add_edge("pro_fraud_debate", "pro_customer_debate")
        builder.add_edge("pro_customer_debate", "decision_arbiter")
        builder.add_edge("decision_arbiter", END)
    -> Se diseña Agente de explicacion de Resultados de Analisis obtenidos: "Explainability Agent"
    -> Se asocia "Explainability Agent" al grafo:
        builder.add_edge("pro_fraud_debate", "pro_customer_debate")
        builder.add_edge("pro_customer_debate", "decision_arbiter")
        builder.add_edge("decision_arbiter", "explainability")
        builder.add_edge("explainability", END)
    -> Se diseña Agente de administración de conflictos en el analisis:
        -> HITLRouterAgent: Evalación a revision de un humano
        -> AuditTrailAgent: Creación de ficheros para auditorias de control
    -> Se asocia "HITL Router Agent" & "Audit Trail Agent" al grafo:
        builder.add_edge("decision_arbiter", "explainability")
        builder.add_edge("explainability", "hitl_router")
        builder.add_edge("hitl_router", "audit_trail")
        builder.add_edge("audit_trail", END)
    -> Se implementaron modelos LLM desde services/llm_client.py para la generacion de argumentos por LLM en los agentes de Debate

-> Notas:
    - No incluyen herramientas cloud, CI/CD o contemplaciones de despliegue

-> Pruebas:
    - Demostración de funcionalidad con datos sinteticos de entrada (de todo el bloque de grafos)
        *INPUT*
            {
                "transaction_id": "T-1006"
            }
        *OUTPUT*
            {
                "transaction_id": "T-1007",
                "decision": "CHALLENGE",
                "confidence": 0.65,
                "decision_basis": "policy_fp01_or_amount_time_risk",
                "decision_rationale": "Decisión final: CHALLENGE. Criterio aplicado: policy_fp01_or_amount_time_risk. Señales internas detectadas: Monto fuera de rango, Horario no habitual. Políticas recuperadas por RAG: FP-01. Señales externas consideradas: Alerta externa en merchant, Canal móvil con monitoreo reforzado. Score Pro-Fraud: 0.76. Score Pro-Customer: 0.54.",
                "requires_human_review": false,
                "hitl_required": false,
                "hitl_reason": "No requiere revisión humana.",
                "hitl_queue_item": {},
                "audit_saved": true,
                "audit_event_id": "cbc88b7b-dd25-4ffe-a57c-bc44aaab6d52",
                "audit_file": "C:\\Users\\JCristobal\\Desktop\\Jorge-GlexcoRobotics\\Jorge_Cristobal\\credicorp-ai-engineer\\credicorp_ws\\multi-agent-fraud-detection-1.0.0\\backend\\data\\audit\\audit_trail.jsonl",
                "signals": [
                    "Monto fuera de rango",
                    "Horario no habitual"
                ],
                "signal_tags": [
                    "signal_a",
                    "signal_b"
                ],
                "citations_internal": [
                    {
                    "policy_id": "FP-01",
                    "chunk_id": "policy-fp01-001",
                    "version": "2025.1"
                    }
                ],
                "external_signals": [
                    "Alerta externa en merchant",
                    "Canal móvil con monitoreo reforzado"
                ],
                "citations_external": [
                    {
                    "threat_id": "EXT-001",
                    "url": "https://example.com/fraud-alert-merchant-m002",
                    "summary": "Se identificó un incremento reciente de transacciones anómalas asociadas al merchant M-002.",
                    "risk_level": "MEDIUM",
                    "source_type": "governed_mock_source"
                    },
                    {
                    "threat_id": "EXT-003",
                    "url": "https://example.com/mobile-channel-risk-monitoring",
                    "summary": "El canal móvil presenta monitoreo reforzado para operaciones de alto monto.",
                    "risk_level": "LOW",
                    "source_type": "governed_mock_source"
                    }
                ],
                "explanation_customer": "La transacción requiere validación adicional debido a monto fuera de rango, horario no habitual.",
                "explanation_audit": "Decisión final: CHALLENGE. Confianza: 0.65. Criterio aplicado: policy_fp01_or_amount_time_risk. Señales internas detectadas: Monto fuera de rango, Horario no habitual. Tags técnicos asociados: signal_a, signal_b. Políticas recuperadas por RAG: FP-01. Citas internas utilizadas: FP-01/policy-fp01-001. Señales externas consideradas: Alerta externa en merchant, Canal móvil con monitoreo reforzado. Fuentes externas utilizadas: EXT-001, EXT-003. Argumento Pro-Fraud: score 0.76, sugerencia CHALLENGE. Argumento Pro-Customer: score 0.54, sugerencia CHALLENGE. Ruta de agentes: TransactionContextAgent → BehavioralPatternAgent → InternalPolicyRAGAgent → ExternalThreatIntelAgent → EvidenceAggregationAgent → ProFraudDebateAgent → ProCustomerDebateAgent → DecisionArbiterAgent.",
                "rag_policy_context": [
                    {
                    "policy_id": "FP-01",
                    "chunk_id": "policy-fp01-001",
                    "version": "2025.1",
                    "content": "Politica interna: FP-01, Version: 2025.1,  Regla oficial: Monto > 3x promedio habitual y horario fuera de rango -> CHALLENGE, Accion sugerida explicita en la regla: CHALLENGE, Señales internas asociadas: signal_a, signal_b, Esta politica se usa como evidencia interna recuperada por RAG, para agentes posteriores. NO REPRESENTA la decision final.",
                    "suggested_action": "CHALLENGE",
                    "required_signals": [
                        "signal_a",
                        "signal_b"
                    ],
                    "retrieval_score": 0.5091,
                    "hybrid_score": 0.9091
                    }
                ],
                "evidence_bundle": {
                    "transaction_id": "T-1007",
                    "transaction_context": {
                    "transaction_id": "T-1007",
                    "customer_id": "CU-002",
                    "amount": 9600,
                    "currency": "PEN",
                    "country": "PE",
                    "channel": "mobile",
                    "device_id": "D-02",
                    "timestamp": "2025-12-17T23:50:00",
                    "transaction_hour": 23,
                    "merchant_id": "M-002"
                    },
                    "customer_behavior": {
                    "customer_id": "CU-002",
                    "usual_amount_avg": 1200,
                    "usual_hours": "09-22",
                    "usual_countries": "PE",
                    "usual_devices": "D-02"
                    },
                    "internal_evidence": {
                    "signal_tags": [
                        "signal_a",
                        "signal_b"
                    ],
                    "signals": [
                        "Monto fuera de rango",
                        "Horario no habitual"
                    ],
                    "signal_metrics": {
                        "transaction_amount": 9600,
                        "usual_amount_avg": 1200,
                        "amount_ratio": 8,
                        "transaction_hour": 23,
                        "usual_hours": "09-22",
                        "usual_start_hour": 9,
                        "usual_end_hour": 22,
                        "transaction_country": "PE",
                        "usual_countries": [
                        "PE"
                        ],
                        "transaction_device": "D-02",
                        "usual_devices": [
                        "D-02"
                        ]
                    },
                    "signals_count": 2
                    },
                    "rag_evidence": {
                    "rag_policy_context": [
                        {
                        "policy_id": "FP-01",
                        "chunk_id": "policy-fp01-001",
                        "version": "2025.1",
                        "content": "Politica interna: FP-01, Version: 2025.1,  Regla oficial: Monto > 3x promedio habitual y horario fuera de rango -> CHALLENGE, Accion sugerida explicita en la regla: CHALLENGE, Señales internas asociadas: signal_a, signal_b, Esta politica se usa como evidencia interna recuperada por RAG, para agentes posteriores. NO REPRESENTA la decision final.",
                        "suggested_action": "CHALLENGE",
                        "required_signals": [
                            "signal_a",
                            "signal_b"
                        ],
                        "retrieval_score": 0.5091,
                        "hybrid_score": 0.9091
                        }
                    ],
                    "citations_internal": [
                        {
                        "policy_id": "FP-01",
                        "chunk_id": "policy-fp01-001",
                        "version": "2025.1"
                        }
                    ],
                    "retrieved_policy_ids": [
                        "FP-01"
                    ],
                    "required_signals_from_rag": [
                        "signal_a",
                        "signal_b"
                    ],
                    "internal_citations_count": 1
                    },
                    "external_evidence": {
                    "external_signals": [
                        "Alerta externa en merchant",
                        "Canal móvil con monitoreo reforzado"
                    ],
                    "citations_external": [
                        {
                        "threat_id": "EXT-001",
                        "url": "https://example.com/fraud-alert-merchant-m002",
                        "summary": "Se identificó un incremento reciente de transacciones anómalas asociadas al merchant M-002.",
                        "risk_level": "MEDIUM",
                        "source_type": "governed_mock_source"
                        },
                        {
                        "threat_id": "EXT-003",
                        "url": "https://example.com/mobile-channel-risk-monitoring",
                        "summary": "El canal móvil presenta monitoreo reforzado para operaciones de alto monto.",
                        "risk_level": "LOW",
                        "source_type": "governed_mock_source"
                        }
                    ],
                    "external_threat_context": [
                        {
                        "threat_id": "EXT-001",
                        "merchant_id": "M-002",
                        "risk_level": "MEDIUM",
                        "signal": "Alerta externa en merchant",
                        "summary": "Se identificó un incremento reciente de transacciones anómalas asociadas al merchant M-002.",
                        "url": "https://example.com/fraud-alert-merchant-m002",
                        "source_type": "governed_mock_source"
                        },
                        {
                        "threat_id": "EXT-003",
                        "channel": "mobile",
                        "risk_level": "LOW",
                        "signal": "Canal móvil con monitoreo reforzado",
                        "summary": "El canal móvil presenta monitoreo reforzado para operaciones de alto monto.",
                        "url": "https://example.com/mobile-channel-risk-monitoring",
                        "source_type": "governed_mock_source"
                        }
                    ],
                    "external_signals_count": 2,
                    "external_citations_count": 2
                    },
                    "risk_summary": {
                    "total_internal_signals": 2,
                    "total_external_signals": 2,
                    "total_internal_citations": 1,
                    "total_external_citations": 2,
                    "has_rag_evidence": true,
                    "has_external_evidence": true,
                    "has_fp01": true,
                    "has_fp02": false
                    }
                },
                "pro_fraud_argument": {
                    "position": "SUSPECTED_FRAUD",
                    "arguments": [
                    "El monto de la transacción se encuentra fuera del patrón habitual del cliente.",
                    "La transacción ocurrió fuera del horario habitual de operación del cliente.",
                    "El RAG interno recuperó políticas asociadas al patrón de riesgo detectado: FP-01.",
                    "Se encontraron señales externas relacionadas: Alerta externa en merchant, Canal móvil con monitoreo reforzado.",
                    "Existen citas externas asociadas a fuentes gobernadas de inteligencia de amenazas."
                    ],
                    "llm_argument": "La transacción presenta un monto fuera del patrón habitual del cliente y se realizó en un horario no habitual, lo que genera señales internas relevantes. Además, el sistema identificó la política FP-01 asociada a patrones de riesgo específicos. Existen alertas externas relacionadas con el comerciante y el canal móvil, ambos bajo monitoreo reforzado, junto con citas externas provenientes de fuentes confiables de inteligencia de amenazas. Estos elementos combinados sustentan la sospecha de fraude y justifican un análisis más profundo.",
                    "llm_used": true,
                    "llm_error": null,
                    "risk_score": 0.76,
                    "suggested_decision": "CHALLENGE",
                    "supporting_signals": [
                    "Monto fuera de rango",
                    "Horario no habitual"
                    ],
                    "supporting_policy_ids": [
                    "FP-01"
                    ],
                    "supporting_external_signals": [
                    "Alerta externa en merchant",
                    "Canal móvil con monitoreo reforzado"
                    ]
                },
                "pro_customer_argument": {
                    "position": "POSSIBLY_LEGITIMATE",
                    "arguments": [
                    "El país de la transacción coincide con el país habitual del cliente.",
                    "El dispositivo utilizado coincide con un dispositivo habitual del cliente.",
                    "La operación se realizó por el canal mobile, lo cual puede ser consistente con el comportamiento digital del cliente.",
                    "No se detectó cambio geográfico inusual en la transacción.",
                    "No se detectó uso de dispositivo desconocido."
                    ],
                    "llm_argument": "La transacción presenta características consistentes con el comportamiento habitual del cliente, ya que el país y el dispositivo utilizados coinciden con sus patrones previos, y se realizó a través del canal móvil, que es común para este usuario. No se detectaron cambios geográficos ni uso de dispositivos desconocidos, lo que sugiere una baja probabilidad de fraude. Sin embargo, existen señales de alerta como monto fuera de rango y horario no habitual, además de una alerta externa en el comercio y monitoreo reforzado del canal móvil, que justifican una revisión cuidadosa.",
                    "llm_used": true,
                    "llm_error": null,
                    "customer_trust_score": 0.54,
                    "suggested_decision": "CHALLENGE",
                    "countered_signals": [
                    "Monto fuera de rango",
                    "Horario no habitual"
                    ],
                    "known_customer_attributes": {
                    "country_is_usual": true,
                    "device_is_usual": true,
                    "channel": "mobile"
                    }
                },
                "agent_trace": [
                    {
                    "agent": "TransactionContextAgent",
                    "status": "completed",
                    "details": {
                        "transaction_id": "T-1007",
                        "customer_id": "CU-002",
                        "transaction_hour": 23
                    }
                    },
                    {
                    "agent": "BehavioralPatternAgent",
                    "status": "completed",
                    "details": {
                        "signal_tags": [
                        "signal_a",
                        "signal_b"
                        ],
                        "signals_count": 2
                    }
                    },
                    {
                    "agent": "InternalPolicyRAGAgent",
                    "status": "completed",
                    "details": {
                        "retrieved_policies": [
                        "FP-01"
                        ],
                        "citations_internal_count": 1
                    }
                    },
                    {
                    "agent": "ExternalThreatIntelAgent",
                    "status": "completed",
                    "details": {
                        "external_signals": [
                        "Alerta externa en merchant",
                        "Canal móvil con monitoreo reforzado"
                        ],
                        "citations_external_count": 2
                    }
                    },
                    {
                    "agent": "EvidenceAggregationAgent",
                    "status": "completed",
                    "details": {
                        "internal_signals_count": 2,
                        "external_signals_count": 2,
                        "rag_policies": [
                        "FP-01"
                        ]
                    }
                    },
                    {
                    "agent": "ProFraudDebateAgent",
                    "status": "completed",
                    "details": {
                        "position": "SUSPECTED_FRAUD",
                        "risk_score": 0.76,
                        "arguments_count": 5,
                        "suggested_decision": "CHALLENGE",
                        "llm_used": true,
                        "llm_error": null
                    }
                    },
                    {
                    "agent": "ProCustomerDebateAgent",
                    "status": "completed",
                    "details": {
                        "position": "POSSIBLY_LEGITIMATE",
                        "customer_trust_score": 0.54,
                        "arguments_count": 5,
                        "suggested_decision": "CHALLENGE",
                        "llm_used": true,
                        "llm_error": null
                    }
                    },
                    {
                    "agent": "DecisionArbiterAgent",
                    "status": "completed",
                    "details": {
                        "decision": "CHALLENGE",
                        "confidence": 0.65,
                        "requires_human_review": false,
                        "decision_basis": "policy_fp01_or_amount_time_risk"
                    }
                    },
                    {
                    "agent": "ExplainabilityAgent",
                    "status": "completed",
                    "details": {
                        "generated_customer_explanation": true,
                        "generated_audit_explanation": true
                    }
                    },
                    {
                    "agent": "HITLRouterAgent",
                    "status": "completed",
                    "details": {
                        "hitl_required": false,
                        "hitl_reason": "No requiere revisión humana.",
                        "priority": null
                    }
                    },
                    {
                    "agent": "AuditTrailAgent",
                    "status": "completed",
                    "details": {
                        "audit_saved": true,
                        "audit_event_id": "cbc88b7b-dd25-4ffe-a57c-bc44aaab6d52",
                        "audit_file": "C:\\Users\\JCristobal\\Desktop\\Jorge-GlexcoRobotics\\Jorge_Cristobal\\credicorp-ai-engineer\\credicorp_ws\\multi-agent-fraud-detection-1.0.0\\backend\\data\\audit\\audit_trail.jsonl"
                    }
                    }
                ],
                "decision_trace": [
                    {
                    "step": "signals_detected",
                    "value": {
                        "signal_tags": [
                        "signal_a",
                        "signal_b"
                        ],
                        "signals": [
                        "Monto fuera de rango",
                        "Horario no habitual"
                        ]
                    }
                    },
                    {
                    "step": "internal_rag_evidence",
                    "value": {
                        "rag_policy_ids": [
                        "FP-01"
                        ],
                        "citations_internal": [
                        {
                            "policy_id": "FP-01",
                            "chunk_id": "policy-fp01-001",
                            "version": "2025.1"
                        }
                        ]
                    }
                    },
                    {
                    "step": "external_threat_evidence",
                    "value": {
                        "external_signals": [
                        "Alerta externa en merchant",
                        "Canal móvil con monitoreo reforzado"
                        ],
                        "citations_external": [
                        {
                            "threat_id": "EXT-001",
                            "url": "https://example.com/fraud-alert-merchant-m002",
                            "summary": "Se identificó un incremento reciente de transacciones anómalas asociadas al merchant M-002.",
                            "risk_level": "MEDIUM",
                            "source_type": "governed_mock_source"
                        },
                        {
                            "threat_id": "EXT-003",
                            "url": "https://example.com/mobile-channel-risk-monitoring",
                            "summary": "El canal móvil presenta monitoreo reforzado para operaciones de alto monto.",
                            "risk_level": "LOW",
                            "source_type": "governed_mock_source"
                        }
                        ]
                    }
                    },
                    {
                    "step": "debate_arguments",
                    "value": {
                        "pro_fraud": {
                        "risk_score": 0.76,
                        "suggested_decision": "CHALLENGE"
                        },
                        "pro_customer": {
                        "customer_trust_score": 0.54,
                        "suggested_decision": "CHALLENGE"
                        }
                    }
                    },
                    {
                    "step": "contradiction_detected",
                    "value": false
                    },
                    {
                    "step": "decision_basis",
                    "value": "policy_fp01_or_amount_time_risk"
                    },
                    {
                    "step": "final_decision",
                    "value": "CHALLENGE"
                    },
                    {
                    "step": "final_confidence",
                    "value": 0.65
                    },
                    {
                    "step": "requires_human_review",
                    "value": false
                    }
                ]
                }