from langgraph.graph import StateGraph, START, END

from graph.fraud_state import FraudEvaluationState

from agents.transaction_context_agent import TransactionContextAgent
from agents.behavioral_pattern_agent import BehaivoralPatternAgent
from agents.policy_evaluation_agent import PolicyEvaluationAgent
from agents.decision_agent import DecisionAgent

def build_fraud_graph(): # Construccion del grafo multiagentico

    # Crear el grafo usando el estado compartido
    builder = StateGraph(FraudEvaluationState)

    # Instanciar los agentes construidos
    transaction_context_agent = TransactionContextAgent()
    behaivoral_pattern_agent = BehaivoralPatternAgent()
    policy_evaluation_agent = PolicyEvaluationAgent()
    decision_agent = DecisionAgent()

    # Registrar nodos en el grafo
    builder.add_node("transaction_context_agent",transaction_context_agent.run)
    builder.add_node("behaivoral_pattern_agent",behaivoral_pattern_agent.run)
    builder.add_node("policy_evaluation_agent",policy_evaluation_agent.run)
    builder.add_node("decision_agent",decision_agent.run)

    # Definir el flujo secuencial
    builder.add_edge(START,"transaction_context_agent")
    builder.add_edge("transaction_context_agent","behaivoral_pattern_agent")
    builder.add_edge("behaivoral_pattern_agent","policy_evaluation_agent")
    builder.add_edge("policy_evaluation_agent","decision_agent")
    builder.add_edge("decision_agent",END)

    # Compilar el grafo
    return builder.compile()