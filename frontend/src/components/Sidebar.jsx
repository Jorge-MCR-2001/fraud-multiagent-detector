const items = [
  { id: "evaluation", label: "Evaluación", caption: "Multi-agente" },
  { id: "hitl", label: "HITL", caption: "Revisión humana" },
  { id: "runtime", label: "Runtime", caption: "Cloud ready" },
];

export default function Sidebar({ activeView, onChangeView }) {
  return (
    <aside className="sidebar">
      <div>
        <div className="brand">
          <div className="brandMark">AI</div>
          <div>
            <h1>Fraud Console</h1>
            <p>Multi-Agent Detection</p>
          </div>
        </div>

        <nav className="navMenu">
          {items.map((item) => (
            <button
              key={item.id}
              className={activeView === item.id ? "active" : ""}
              onClick={() => onChangeView(item.id)}
            >
              <span>{item.label}</span>
              <small>{item.caption}</small>
            </button>
          ))}
        </nav>
      </div>

      <div className="sidebarFooter">
        <span>Nivel 4</span>
        <strong>LangGraph Cloud Ready</strong>
        <small>FastAPI · RAG · HITL · Audit Trail</small>
      </div>
    </aside>
  );
}
