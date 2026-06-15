import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { pct } from "../utils/formatters";
import Card from "./Card";
import DecisionBadge from "./DecisionBadge";
import JsonBlock from "./JsonBlock";
import Metric from "./Metric";

const resolutionOptions = ["APPROVE", "CHALLENGE", "BLOCK", "ESCALATE_TO_HUMAN"];

function HitlCard({ item, onResolved }) {
  const [reviewer, setReviewer] = useState("analyst.demo");
  const [resolution, setResolution] = useState("CHALLENGE");
  const [notes, setNotes] = useState("Resolución revisada desde consola React.");
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function resolve() {
    setLoading(true);
    setError(null);

    try {
      await apiClient.resolveHitlItem(item.hitl_queue_id, {
        reviewer,
        resolution,
        notes: notes || null,
      });
      onResolved?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <article className="hitlCard">
      <div className="hitlTopline">
        <div>
          <span className="eyebrow">Caso HITL</span>
          <h3>{item.transaction_id}</h3>
          <p>{item.reason}</p>
        </div>
        <span className={`priority ${item.priority || "MEDIUM"}`}>{item.priority || "MEDIUM"}</span>
      </div>

      <div className="metricGrid four">
        <Metric label="Estado" value={item.status} />
        <Metric label="Decisión original" value={item.original_decision || "-"} />
        <Metric label="Confianza" value={item.original_confidence != null ? pct(item.original_confidence) : "-"} />
        <Metric label="Revisión humana" value={item.requires_human_review ? "Sí" : "No"} />
      </div>

      <div className="hitlResolveGrid">
        <div className="formControl compact">
          <label>Reviewer</label>
          <input value={reviewer} onChange={(event) => setReviewer(event.target.value)} />
        </div>
        <div className="formControl compact">
          <label>Resolución</label>
          <select value={resolution} onChange={(event) => setResolution(event.target.value)}>
            {resolutionOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>
        <div className="formControl full">
          <label>Notas</label>
          <textarea value={notes} onChange={(event) => setNotes(event.target.value)} />
        </div>
        <button className="primaryButton full" disabled={loading} onClick={resolve}>
          {loading ? "Resolviendo..." : "Resolver caso HITL"}
        </button>
      </div>

      {error && <div className="errorBox">{error}</div>}

      <button className="linkButton" type="button" onClick={() => setExpanded((value) => !value)}>
        {expanded ? "Ocultar snapshot" : "Ver snapshot de decisión"}
      </button>

      {expanded && (
        <div className="snapshotBlock">
          {item.original_decision && <DecisionBadge decision={item.original_decision} />}
          <JsonBlock value={item.decision_snapshot} />
        </div>
      )}
    </article>
  );
}

export default function HitlQueue({ refreshToken = 0 }) {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("PENDING_REVIEW");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);

    try {
      const queue = await apiClient.getHitlQueue(status);
      setData(queue);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, refreshToken]);

  return (
    <div className="viewStack">
      <div className="heroPanel">
        <div>
          <span className="eyebrow">Human-in-the-loop</span>
          <h2>Cola de revisión humana</h2>
          <p>
            Visualiza decisiones ambiguas, revisa el snapshot de decisión y resuelve casos con trazabilidad.
          </p>
        </div>
        <div className="heroStats">
          <Metric label="Filtro" value={status} />
          <Metric label="Casos" value={data?.item_count ?? "-"} />
        </div>
      </div>

      <Card
        title="Casos HITL"
        subtitle="Casos pendientes o resueltos en la cola de revisión humana."
        actions={
          <div className="inlineActions">
            <select value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="PENDING_REVIEW">PENDING_REVIEW</option>
              <option value="RESOLVED">RESOLVED</option>
            </select>
            <button className="secondaryButton" onClick={load} disabled={loading}>
              {loading ? "Actualizando..." : "Actualizar"}
            </button>
          </div>
        }
      >
        {error && <div className="errorBox">{error}</div>}

        {!error && loading && <div className="emptyState">Cargando cola HITL...</div>}

        {!loading && !data?.items?.length && (
          <div className="emptyState tall">No hay casos con el filtro seleccionado.</div>
        )}

        <div className="hitlList">
          {data?.items?.map((item) => (
            <HitlCard key={item.hitl_queue_id} item={item} onResolved={load} />
          ))}
        </div>
      </Card>
    </div>
  );
}
