import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import Card from "./Card";
import JsonBlock from "./JsonBlock";
import Metric from "./Metric";
import StatusPill from "./StatusPill";

function CheckTable({ ready }) {
  const checks = ready?.checks || ready?.detail?.checks || {};
  const entries = Object.entries(checks);

  if (!entries.length) {
    return <div className="emptyState">No hay checks disponibles.</div>;
  }

  return (
    <div className="checkTable">
      {entries.map(([name, check]) => (
        <div className="checkRow" key={name}>
          <div>
            <strong>{name}</strong>
            <small>{check?.message || check?.value || check?.path || "runtime check"}</small>
          </div>
          <StatusPill status={check?.ok ? "ok" : "bad"}>{check?.ok ? "OK" : "FAIL"}</StatusPill>
        </div>
      ))}
    </div>
  );
}

export default function RuntimeView({ apiOnline }) {
  const [root, setRoot] = useState(null);
  const [live, setLive] = useState(null);
  const [ready, setReady] = useState(null);
  const [readyError, setReadyError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setReadyError(null);

    try {
      const [rootData, liveData] = await Promise.all([apiClient.getRoot(), apiClient.getLive()]);
      setRoot(rootData);
      setLive(liveData);

      try {
        const readyData = await apiClient.getReady();
        setReady(readyData);
      } catch (err) {
        setReadyError(err.message);
        try {
          setReady(JSON.parse(err.message));
        } catch {
          setReady(null);
        }
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const runtime = root?.runtime || {};
  const readinessStatus = ready?.status || ready?.detail?.status || (readyError ? "not_ready" : "unknown");

  return (
    <div className="viewStack">
      <div className="heroPanel">
        <div>
          <span className="eyebrow">Runtime y despliegue</span>
          <h2>Health checks cloud-ready</h2>
          <p>
            Verifica liveness, readiness, providers de storage/RAG/observabilidad y configuración LLM.
          </p>
        </div>
        <div className="heroStats">
          <Metric label="API" value={apiOnline ? "Online" : "Offline"} />
          <Metric label="Nivel" value={root?.level || "-"} />
          <Metric label="Readiness" value={readinessStatus} />
        </div>
      </div>

      <Card
        title="Resumen de runtime"
        subtitle="Metadata operacional del backend FastAPI."
        actions={<button className="secondaryButton" onClick={load} disabled={loading}>{loading ? "Refrescando..." : "Refrescar"}</button>}
      >
        <div className="metricGrid four">
          <Metric label="Environment" value={runtime.environment || "-"} />
          <Metric label="Storage" value={runtime.storage_provider || "-"} />
          <Metric label="RAG" value={runtime.rag_provider || "-"} />
          <Metric label="LLM" value={String(runtime.llm_enabled ?? "-")} />
        </div>
      </Card>

      <div className="grid two">
        <Card title="Liveness" subtitle="La API responde y está viva.">
          <JsonBlock value={live} />
        </Card>
        <Card title="Readiness" subtitle="La API está lista para operar según configuración.">
          {readyError && <div className="warningBox">/health/ready respondió 503. Esto es válido si algún provider o recurso falta.</div>}
          <CheckTable ready={ready} />
        </Card>
      </div>

      <div className="grid two">
        <Card title="Root endpoint" subtitle="Contrato ejecutivo del servicio.">
          <JsonBlock value={root} large />
        </Card>
        <Card title="Readiness JSON" subtitle="Detalle completo de checks.">
          <JsonBlock value={ready || readyError} large />
        </Card>
      </div>
    </div>
  );
}
