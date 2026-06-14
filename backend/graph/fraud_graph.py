from langgraph.graph import StateGraph, START, END

from graph.fraud_state import FraudEvaluationState

from agents.transaction_context_agent import TransactionContextAgent
from agents.behavioral_pattern_agent import BehavioralPatternAgent
from agents.internal_policy_rag_agent import InternalPolicyRagAgent
from agents.external_threat_intel_agent import ExternalThreatIntelAgent
from agents.evidence_aggregation_agent import EvidenceAggregationAgent
from agents.pro_fraud_debate_agent import ProFraudDebateAgent
from agents.pro_customer_debate_agent import ProCustomerDebateAgent
from agents.decision_arbiter_agent import DecisionArbiterAgent

def build_fraud_graph(): # Construccion del grafo multiagentico

    # Crear el grafo usando el estado compartido
    builder = StateGraph(FraudEvaluationState)

    # Instanciar los agentes construidos
    transaction_context_agent = TransactionContextAgent()
    behavioral_pattern_agent = BehavioralPatternAgent()
    internal_policy_rag_agent = InternalPolicyRagAgent()
    external_threat_intel_agent = ExternalThreatIntelAgent()
    evidence_aggregation_agent = EvidenceAggregationAgent()
    pro_fraud_debate_agent = ProFraudDebateAgent()
    pro_customer_debate_agent = ProCustomerDebateAgent()
    decision_arbiter_agent = DecisionArbiterAgent()

    # Registrar nodos en el grafo
    builder.add_node("transaction_context",transaction_context_agent.run)
    builder.add_node("behavioral_pattern",behavioral_pattern_agent.run)
    builder.add_node("internal_policy_rag",internal_policy_rag_agent.run)
    builder.add_node("external_threat_intel",external_threat_intel_agent.run)
    builder.add_node("evidence_aggregation",evidence_aggregation_agent.run)
    builder.add_node("pro_fraud_debate",pro_fraud_debate_agent.run)
    builder.add_node("pro_customer_debate",pro_customer_debate_agent.run)
    builder.add_node("decision_arbiter",decision_arbiter_agent.run)

    # Definir el flujo secuencial
    builder.add_edge(START,"transaction_context")
    builder.add_edge("transaction_context","behavioral_pattern")
    builder.add_edge("behavioral_pattern","internal_policy_rag")
    builder.add_edge("internal_policy_rag", "external_threat_intel")
    builder.add_edge("external_threat_intel","evidence_aggregation")
    builder.add_edge("evidence_aggregation", "pro_fraud_debate")
    builder.add_edge("pro_fraud_debate", "pro_customer_debate")
    builder.add_edge("pro_customer_debate", "decision_arbiter")
    builder.add_edge("decision_arbiter", END)

    # Compilar el grafo
    return builder.compile()