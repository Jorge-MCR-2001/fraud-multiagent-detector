from typing import Dict, Any, Optional

from graph.fraud_graph import build_fraud_graph
from services.response_builder import build_response
from services.load_data import get_customer_behivor, get_transactions


class FraudOrchestrator:

    # Orquestador del sistema multiagentico
    # - Recibe las tracciones desde la capa API
    # - Carga la data sintetica
    # - Construye el sistema de grafos
    # - Invoca a los grafos
    # - Retornar la respuesta al API

    def __init__(self): # Compilar el grafo al iniciar el orquestador
        self.graph = build_fraud_graph()

    def evaluate(self, transaction_id: str) -> Dict[str, Any]:

        # Evaluar la transacción en funcion al id de transaccion

        # 1. Recuperar la transacción por el id
        transaction = self._load_transaction(transaction_id)

        if not transaction: # En caso de no existir transaccion
            return {
                "transaction_id": transaction_id,
                "error": "transaction_not_found",
                "message": "No se encontro la transacción solicitada"
            }
        
        # 2. Recuperar identificación del cliente que realizo la transaccion
        customer_id = transaction.get("customer_id")

        if not customer_id: # En caso de no mencionarse al cliente
            return {
                "transaction_id": transaction_id,
                "error": "customer_id_not_found",
                "message": "La transacción solicitada no muestra un customer_id"
            }
        
        # 3. Recuperar información asociada al cliente que realizo la transaccion
        customer = self._load_customer_behivor(customer_id)

        if not customer: # En caso de no encontrar informacion relacionada al cliente
            return {
                "transaction_id": transaction_id,
                "customer_id": customer_id,
                "error": "customer_behivor_not_found",
                "message": "No se encontro informacion relacionada al comportamiento historico del cliente"
            }
        
        initial_state = self._build_initial_state(
            transaction_id = transaction_id,
            transaction = transaction,
            customer = customer
        )

        final_state = self.graph.invoke(initial_state)

        return build_response(final_state)
    
    def _build_initial_state(self, transaction_id: str, transaction: Dict[str, Any], customer: Dict[str, Any]) -> Dict[str, Any]:
        
        # Construir el estado inicial del estado compartido

        return {
            "transaction_id": transaction_id,
            "transaction": transaction,
            "customer": customer,
            "agent_trace": [],
            "decision_trace": [],
            "errors": []
        }
    
    def _load_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]: # Carga de la transaccion asociada a transaction_id
        return get_transactions(transaction_id)
        
    def _load_customer_behivor(self, customer_id: str) -> Optional[Dict[str, Any]]: # Carga de la transaccion asociada a transaction_id
        return get_customer_behivor(customer_id)

