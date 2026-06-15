import JsonBlock from "./JsonBlock";

function normalizeItem(item, index) {
  return {
    title: item.agent || item.step || `Paso ${index + 1}`,
    status: item.status || item.decision || "registrado",
    message: item.message || item.reason || item.value || item.decision || "Evento registrado",
    raw: item,
  };
}

export default function Timeline({ items = [], emptyText = "Sin traza registrada." }) {
  if (!items?.length) {
    return <div className="emptyState">{emptyText}</div>;
  }

  return (
    <div className="timeline">
      {items.map((item, index) => {
        const normalized = normalizeItem(item, index);

        return (
          <article className="timelineItem" key={`${normalized.title}-${index}`}>
            <div className="timelineMarker">{index + 1}</div>
            <div className="timelineBody">
              <div className="timelineTopline">
                <strong>{normalized.title}</strong>
                <span>{normalized.status}</span>
              </div>
              {typeof normalized.message === "string" && <p>{normalized.message}</p>}
              <JsonBlock value={normalized.raw} />
            </div>
          </article>
        );
      })}
    </div>
  );
}
