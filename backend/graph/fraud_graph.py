from langgraph.graph import StateGraph, START, END

from graph.fraud_state import FraudEvaluationState

from agents.transaction_context_agent import TransactionContextAgent
from agents.behavioral_pattern_agent import BehavioralPatternAgent
from agents.internal_policy_rag_agent import InternalPolicyRagAgent
from agents.external_threat_intel_agent import ExternalThreatIntelAgent
from agents.policy_evaluation_agent import PolicyEvaluationAgent
from agents.decision_agent import DecisionAgent

def build_fraud_graph(): # Construccion del grafo multiagentico

    # Crear el grafo usando el estado compartido
    builder = StateGraph(FraudEvaluationState)

    # Instanciar los agentes construidos
    transaction_context_agent = TransactionContextAgent()
    behavioral_pattern_agent = BehavioralPatternAgent()
    internal_policy_rag_agent = InternalPolicyRagAgent()
    external_threat_intel_agent = ExternalThreatIntelAgent()
    policy_evaluation_agent = PolicyEvaluationAgent()
    decision_agent = DecisionAgent()

    # Registrar nodos en el grafo
    builder.add_node("transaction_context",transaction_context_agent.run)
    builder.add_node("behavioral_pattern",behavioral_pattern_agent.run)
    builder.add_node("internal_policy_rag",internal_policy_rag_agent.run)
    builder.add_node("external_threat_intel",external_threat_intel_agent.run)
    builder.add_node("policy_evaluation",policy_evaluation_agent.run)
    builder.add_node("decision",decision_agent.run)

    # Definir el flujo secuencial
    builder.add_edge(START,"transaction_context")
    builder.add_edge("transaction_context","behavioral_pattern")
    builder.add_edge("behavioral_pattern","internal_policy_rag")
    builder.add_edge("internal_policy_rag", "external_threat_intel")
    builder.add_edge("external_threat_intel","policy_evaluation")
    builder.add_edge("policy_evaluation","decision")
    builder.add_edge("decision",END)

    # Compilar el grafo
    return builder.compile()