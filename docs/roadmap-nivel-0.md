Detector de Fraudes Multi Agentico - MVP
-> Objetivo: 
    ¿Puedo detectar un fraude a partir de una transaccion ingresada?
-> Tecnologia:
    - Inferencia por logica booleana (sin implementación de agentes)
-> Actividades:
    - Diseñar arquitectura basica del proyecto.
    - Definir de estructura de almacenamiento de datos en Bases de Batos Relacionales (SQL)
    - Conceptualización de Backend / Frontend a nivel local
    - Definición de entornos virtuales por capas Backend / Frontend
    - Definición de fuentes de datos y recursos:
        -> Data: dataset de transacciones / dataset de customer behivor (actualizable para un entrenamiento en paralelo)
        -> Resources: politicas de fraude (json) / recursos de sistema estáticos (no se generan o actualizan en tiempo real)
            -> Añadir un nuevo elemento a la lista de ambas politicas: "decision"
    - Construcción de comunicación entre módulos
    - Evaluación de métricas según los datos sintaticos atravez de un motor de fraudes
        -> Analisis de Hora de transacción
        -> Analisis de Monto de transacción
        -> Analisis de Dispositivo de transacción
        -> Analisis de Origen Geográfico de transacción
    - Tabulación manual de "confidence" para los escenarios de transacción / Es decir, estoy o muy seguro de que es veridico o muy seguro que es fraude
        - APPROVE: 0.95
        - CHALLENGE: 0.65
        - ESCALATE_TO_HUMAN: 0.50
        - BLOCK: 0.90
-> Pruebas:
    - Demostración de funcionalidad con datos sinteticos de entrada
        *INPUT*
            {
                "transaction_id": "T-1002"
            }
        *OUTPUT*
            {
                "transaction_id": "T-1002",
                "decision": "CHALLENGE",
                "confidence": 0.65,
                "signals": [
                    "Monto fuera de rango",
                    "Horario fuera de rango"
                ]
            }

-> Notas:
    - Se implemento el artificio __init__.py para el test modular de pipelines

--------------------------------------------------------------------------------------------------------------------

-> Actividades: 1.0.2
    - Desacoplamiento de reglas en el motor de fraude, para perfil de datos en busqueda RAG
    - Dividir el servico de motor de respuestas de fraude en 4 steps
        -> detectar señales
        -> aplicar politicas
        -> descidir
        -> responder

-> Pruebas:
    - Demostración de funcionalidad con datos sinteticos de entrada
        *INPUT*
            {
                "transaction_id": "T-1002"
            }
        *OUTPUT*
            {
                "transaction_id": "T-1002",
                "decision": "CHALLENGE",
                "confidence": 0.65,
                "signals": [
                    "Monto fuera de rango",
                    "Horario fuera de rango"
                ]
                "citations_internal": [
                    { 
                        "policy_id": "FP-01",
                        "version": "2025.1" 
                    }
                ],
            }