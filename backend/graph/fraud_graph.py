from langgraph.graph import StateGraph, START, END

from graph.fraud_state import FraudEvaluationState

from agents.transaction_context_agent import TransactionContextAgent
from agents.behavioral_pattern_agent import BehavioralPatternAgent
from agents.internal_policy_rag_agent import InternalPolicyRagAgent
from agents.policy_evaluation_agent import PolicyEvaluationAgent
from agents.decision_agent import DecisionAgent

def build_fraud_graph(): # Construccion del grafo multiagentico

    # Crear el grafo usando el estado compartido
    builder = StateGraph(FraudEvaluationState)

    # Instanciar los agentes construidos
    transaction_context_agent = TransactionContextAgent()
    behavioral_pattern_agent = BehavioralPatternAgent()
    internal_policy_rag_agent = InternalPolicyRagAgent()
    policy_evaluation_agent = PolicyEvaluationAgent()
    decision_agent = DecisionAgent()

    # Registrar nodos en el grafo
    builder.add_node("transaction_context_agent",transaction_context_agent.run)
    builder.add_node("behavioral_pattern_agent",behavioral_pattern_agent.run)
    builder.add_node("internal_policy_rag_agent",internal_policy_rag_agent.run)
    builder.add_node("policy_evaluation_agent",policy_evaluation_agent.run)
    builder.add_node("decision_agent",decision_agent.run)

    # Definir el flujo secuencial
    builder.add_edge(START,"transaction_context_agent")
    builder.add_edge("transaction_context_agent","behavioral_pattern_agent")
    builder.add_edge("behavioral_pattern_agent","internal_policy_rag_agent")
    builder.add_edge("internal_policy_rag_agent","policy_evaluation_agent")
    builder.add_edge("policy_evaluation_agent","decision_agent")
    builder.add_edge("decision_agent",END)

    # Compilar el grafo
    return builder.compile()