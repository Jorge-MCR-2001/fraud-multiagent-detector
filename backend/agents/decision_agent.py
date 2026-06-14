from typing import List, Dict, Any, Optional

from agents.base_agent import BaseAgent

class DecisionAgent(BaseAgent):

    # Asignar nombre al agente
    name: str = "DecisionAgent"

    # Rango de severidad por acción relativa a una politica
    DECISION_RANGES = {
        "APPROVE": 0,
        "CHALLENGE": 1,
        "ESCALATE_TO_HUMAN": 2,
        "BLOCK": 3
    }

    # Confidence relativa a acción / en caso de no hacer match con una politica
    FALLBACK_CONFIDENCE_TABLE = {
        "APPROVE": 0.95,
        "CHALLENGE": 0.65,
        "ESCALATE_TO_HUMAN": 0.50,
        "BLOCK": 0.90
    }

    # Formato de metodo de ejecución de nodos (por cada agente)
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:

        try:
            # Cargar estados input en el Agente de Toma de decisiones
            signal_tags = state.get("signal_tags",[])
            matched_policies = state.get("matched_policies",[])
            policy_suggested_decision = state.get("policy_suggested_decision",[]) 
            policy_suggested_confidence = state.get("policy_suggested_confidence",[])  

            # 1. Determinar desicion final del sistema Agentico
            decision, confidence, decision_source = self._resolve_final_decision(
                signal_tags=signal_tags,
                policy_suggested_decision=policy_suggested_decision,
                policy_suggested_confidence=policy_suggested_confidence
            )

            # 2. Inyectar los resultados en el estado compartido multiagentico
            state["decision"] = decision
            state["confidence"] = confidence

            # 3. Construir la trazabilidad del agente
            state["decision_trace"] = self._build_decision_trade(
                signal_tags=signal_tags,
                matched_policies=matched_policies,
                decision=decision,
                confidence=confidence,
                decision_source=decision_source
            )

            return state

        except Exception as exc:
            self.add_error(
                state=state,
                message="O . . ",
                details={
                    "error": exc
                }
            )

            return state

    def _resolve_final_decision(self,
                                signal_tags: List[str],
                                policy_suggested_decision: Optional[str],
                                policy_suggested_confidence: Optional[float]
                            ) -> tuple[str, float, str]:
        
        # Caso #01: Existe una decision sugerida por politica, se usa como principal, con sus metadatos
        if policy_suggested_decision:
            decision = policy_suggested_decision
            confidence = policy_suggested_confidence

            if confidence is None: # En caso no se haya adjuntado informacion -> ya que fue inserccion manual en la información de politicas del caso 
                confidence = self.FALLBACK_CONFIDENCE_TABLE.get(decision, 0.5) # En caso de tener una decision ambigua -> asignar valor minimo
            
            # Se agrupa la fuente de decision
            return decision, confidence, "policy_engine"
        
        # Caso #02: No hubo match de politcas, se usa la regla de asignación por cantidad de señales
        signal_count = len(signal_tags or []) # en caso de estar vacio, asignar lista vacia para el conteo de elementos

        if signal_count == 0:
            decision = "APPROVE"
        elif signal_count <= 2:
            decision = "CHALLENGE"
        elif signal_count == 3:
            decision = "ESCALATE_TO_HUMAN"
        else: 
            decision = "BLOCK"

        confidence = self.FALLBACK_CONFIDENCE_TABLE[decision] # Valor de confidence fijo / seguro, por Fallback
        
        # Se agrupa la fuente de decision
        return decision, confidence, "fallback_signal_count"
    

    def _build_decision_trade(self,
                            signal_tags:List[Dict[str, Any]],
                            matched_policies:List[Dict[str, Any]],
                            decision:str,
                            confidence:float,
                            decision_source:str
                        ):
        
        # Agrupar la trazabilidad de la decision
        trace = []

        trace.append(
            {
                "step": "signals_detected", # paso 01: Señales detectadas
                "value": signal_tags or []
            }
        )

        if matched_policies: # Existe match con politicas?
            trace.append(
                {
                    "step": "policies_matched",
                    "value": [
                        {
                            "policy_id": policy.get("policy_id"),
                            "action": policy.get("action"),
                            "confidence": policy.get("confidence"),
                            "version": policy.get("version")
                        }
                        for policy in matched_policies
                    ]
                }
            )

            trace.append(
                {
                    "step": "severity_priority",
                    "value": self._get_highest_severity_action(matched_policies) # seleccina la accion con mayor severdiad dentro de las politicas identificadas
                }
            )

        else:

            trace.append(
                {
                    "step": "policies_matched", # No hubo match con politicas
                    "value": []
                }
            )

            trace.append(
                {
                    "step": "fallback_applied", # Decision por Fallback de cantidad de señales encontradas
                    "value": "decision_by_signal_count"
                }
            )

        
        trace.append(
            {
                "step": "decision_source", # Fuente de decision -> Por Politicas / Por fallback
                "value": decision_source
            }
        )

        trace.append(
            {
                "step": "final_decision", # Inyeccion de desicion final 
                "value": decision
            }
        )

        trace.append(
            {
                "step": "final_confidence", # Inyeccion de confidence final
                "value": confidence
            }
        )

        return trace

    def _get_highest_severity_action(self, matched_policies:List[Dict[str, Any]]) -> Optional[str]:

        # Mantener el orden segun el rango establecido por la politica

        if not matched_policies: # Asegura la existencia de coincidencia con politicas
            return None
        
        # Escoje la politica con accion mas severa segun el DICCIONARIO DE RANGOS / para evitar ambiguedad
        selected_policy = max(
            matched_policies,
            key=lambda policy: self.DECISION_RANGES.get(policy.get("action"), 0)
        )

        # Retorna solo el nombre de la decision
        return selected_policy.get("action")
        