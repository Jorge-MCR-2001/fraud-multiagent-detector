import { useMemo, useState } from "react";
import { apiClient } from "../api/client";
import { clampPct, getDecisionDescription, pct } from "../utils/formatters";
import Card from "./Card";
import CitationList from "./CitationList";
import DecisionBadge from "./DecisionBadge";
import JsonBlock from "./JsonBlock";
import Metric from "./Metric";
import SignalTags from "./SignalTags";
import Timeline from "./Timeline";

const demoTransactions = [
  { id: "T-1003", expected: "APPROVE" },
  { id: "T-1007", expected: "CHALLENGE" },
  { id: "T-1004", expected: "BLOCK" },
  { id: "T-1005", expected: "ESCALATE_TO_HUMAN" },
  { id: "T-1001", expected: "CORE" },
  { id: "T-1002", expected: "CORE" },
];

export default function EvaluationView({ onEvaluationCompleted }) {
  const [transactionId, setTransactionId] = useState("T-1003");
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const confidencePct = useMemo(() => clampPct(evaluation?.confidence), [evaluation]);

  async function evaluate(id = transactionId) {
    const cleanId = id.trim();
    if (!cleanId) {
      setError("Ingresa un transaction_id válido.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await apiClient.evaluateTransaction(cleanId);
      setEvaluation(data);
      onEvaluationCompleted?.(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function copyJson() {
    if (!evaluation) return;
    await navigator.clipboard.writeText(JSON.stringify(evaluation, null, 2));
  }

  return (
    <div className="viewStack">
      <div className="heroPanel">
        <div>
          <span className="eyebrow">Evaluación transaccional</span>
          <h2>Sistema Multi-Agente para Fraude Ambiguo</h2>
          <p>
            Ejecuta el flujo Context → Behavioral Pattern → RAG → Threat Intel → Evidence
            Aggregation → Debate → Decision Arbiter → Explainability → HITL.
          </p>
        </div>
        <div className="heroStats">
          <Metric label="Framework" value="LangGraph" />
          <Metric label="Backend" value="FastAPI" />
          <Metric label="Modo" value="Cloud-ready" />
        </div>
      </div>

      <div className="grid two">
        <Card title="Transacción" subtitle="Evalúa por transaction_id o usa los escenarios de demo.">
          <div className="scenarioGrid">
            {demoTransactions.map((tx) => (
              <button
                key={tx.id}
                className="scenarioButton"
                type="button"
                onClick={() => {
                  setTransactionId(tx.id);
                  evaluate(tx.id);
                }}
              >
                <strong>{tx.id}</strong>
                <span>{tx.expected}</span>
              </button>
            ))}
          </div>

          <div className="formControl">
            <label htmlFor="transaction-id">Transaction ID</label>
            <input
              id="transaction-id"
              value={transactionId}
              onChange={(event) => setTransactionId(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") evaluate();
              }}
              placeholder="Ejemplo: T-1007"
            />
          </div>

          <button className="primaryButton" type="button" onClick={() => evaluate()} disabled={loading}>
            {loading ? "Evaluando flujo multi-agente..." : "Ejecutar evaluación"}
          </button>

          {error && <div className="errorBox">{error}</div>}
        </Card>

        <Card title="Resultado ejecutivo" subtitle="Decisión final, confianza y enrutamiento HITL.">
          {!evaluation ? (
            <div className="emptyState tall">Ejecuta una evaluación para visualizar la decisión.</div>
          ) : (
            <div className="resultSummary">
              <div className="decisionLine">
                <DecisionBadge decision={evaluation.decision} />
                <div>
                  <strong>{getDecisionDescription(evaluation.decision)}</strong>
                  <p>{evaluation.decision_rationale || evaluation.decision_basis?.basis_type || "-"}</p>
                </div>
              </div>

              <div className="confidenceCard">
                <div>
                  <span>Confianza</span>
                  <strong>{pct(evaluation.confidence)}</strong>
                </div>
                <div className="progressBar">
                  <div style={{ width: `${confidencePct}%` }} />
                </div>
              </div>

              <div className="metricGrid three">
                <Metric label="Nivel" value={evaluation.confidence_level} />
                <Metric label="HITL" value={evaluation.hitl_required || evaluation.requires_human_review ? "Sí" : "No"} />
                <Metric label="Audit ID" value={evaluation.audit_event_id || "-"} />
              </div>

              {(evaluation.hitl_required || evaluation.requires_human_review) && (
                <div className="warningBox">{evaluation.hitl_reason || "Caso enviado a revisión humana."}</div>
              )}
            </div>
          )}
        </Card>
      </div>

      {evaluation && (
        <>
          <div className="grid two">
            <Card title="Explicación para cliente" subtitle="Lenguaje natural orientado al usuario final.">
              <p className="narrative">{evaluation.explanation_customer}</p>
            </Card>
            <Card title="Explicación para auditoría" subtitle="Detalle técnico trazable para revisión interna.">
              <p className="narrative">{evaluation.explanation_audit}</p>
            </Card>
          </div>

          <div className="grid two">
            <Card title="Señales detectadas" subtitle="Señales funcionales y tags técnicos.">
              <SignalTags signals={evaluation.signals} tags={evaluation.signal_tags} />
            </Card>
            <Card title="Métricas y factores de confianza" subtitle="Score formalizado y factores explicables.">
              <JsonBlock value={{ signal_metrics: evaluation.signal_metrics, confidence_factors: evaluation.confidence_factors }} />
            </Card>
          </div>

          <div className="grid two">
            <Card title="Citas internas RAG" subtitle="Políticas internas recuperadas desde la base vectorial.">
              <CitationList type="internal" items={evaluation.citations_internal} />
            </Card>
            <Card title="Inteligencia externa gobernada" subtitle="Fuentes externas o mock gobernado de threat intel.">
              <CitationList type="external" items={evaluation.citations_external} />
            </Card>
          </div>

          <div className="grid two">
            <Card title="Argumento Pro-Fraud" subtitle="Agente que defiende hipótesis de fraude.">
              <JsonBlock value={evaluation.pro_fraud_argument} />
            </Card>
            <Card title="Argumento Pro-Customer" subtitle="Agente que defiende posible legitimidad.">
              <JsonBlock value={evaluation.pro_customer_argument} />
            </Card>
          </div>

          <Card title="Ruta de agentes" subtitle="Secuencia de agentes y handoffs dentro del flujo.">
            <Timeline items={evaluation.agent_trace} />
          </Card>

          <Card title="Traza de decisión" subtitle="Evidencia usada por el árbitro para decidir.">
            <Timeline items={evaluation.decision_trace} />
          </Card>

          <Card
            title="JSON completo"
            subtitle="Respuesta contractual del backend. Útil para evidencias del README."
            actions={<button className="secondaryButton" onClick={copyJson}>Copiar JSON</button>}
          >
            <JsonBlock value={evaluation} large />
          </Card>
        </>
      )}
    </div>
  );
}
