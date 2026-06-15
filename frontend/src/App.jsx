import { useEffect, useState } from "react";
import { apiClient } from "./api/client";
import EvaluationView from "./components/EvaluationView";
import HitlQueue from "./components/HitlQueue";
import RuntimeView from "./components/RuntimeView";
import Sidebar from "./components/Sidebar";
import StatusPill from "./components/StatusPill";

export default function App() {
  const [activeView, setActiveView] = useState("evaluation");
  const [apiOnline, setApiOnline] = useState(false);
  const [apiStatusText, setApiStatusText] = useState("Verificando API...");
  const [hitlRefreshToken, setHitlRefreshToken] = useState(0);

  async function checkApi() {
    try {
      const live = await apiClient.getLive();
      setApiOnline(true);
      setApiStatusText(live?.status === "alive" ? "API online" : "API disponible");
    } catch {
      setApiOnline(false);
      setApiStatusText("API offline");
    }
  }

  useEffect(() => {
    checkApi();
    const id = setInterval(checkApi, 15000);
    return () => clearInterval(id);
  }, []);

  function handleEvaluationCompleted(data) {
    if (data?.hitl_required || data?.requires_human_review) {
      setHitlRefreshToken((value) => value + 1);
    }
  }

  return (
    <div className="appShell">
      <Sidebar activeView={activeView} onChangeView={setActiveView} />

      <main className="mainContent">
        <header className="topbar">
          <div>
            <h1>Credicorp AI Engineer Challenge</h1>
            <p>
              Consola frontend para validar decisiones, señales, RAG, threat intel, debate,
              explicabilidad, HITL y trazabilidad.
            </p>
          </div>
          <StatusPill status={apiOnline ? "ok" : "bad"}>{apiStatusText}</StatusPill>
        </header>

        {activeView === "evaluation" && (
          <EvaluationView onEvaluationCompleted={handleEvaluationCompleted} />
        )}
        {activeView === "hitl" && <HitlQueue refreshToken={hitlRefreshToken} />}
        {activeView === "runtime" && <RuntimeView apiOnline={apiOnline} />}
      </main>
    </div>
  );
}
