export default function CitationList({ items = [], type = "internal" }) {
  if (!items?.length) {
    return <div className="emptyState">Sin citas registradas.</div>;
  }

  return (
    <div className="citationList">
      {items.map((item, index) => {
        const title =
          type === "internal"
            ? item.policy_id || `Política ${index + 1}`
            : item.title || item.threat_id || item.source_id || `Fuente ${index + 1}`;

        return (
          <article className="citationItem" key={`${title}-${index}`}>
            <div className="citationHeader">
              <strong>{title}</strong>
              {item.risk_level && <span className={`risk ${item.risk_level}`}>{item.risk_level}</span>}
            </div>

            {type === "internal" ? (
              <p>
                Chunk: <b>{item.chunk_id || "-"}</b> · Versión: <b>{item.version || "-"}</b>
              </p>
            ) : (
              <>
                <p>{item.summary || "Sin resumen disponible."}</p>
                <small>
                  {item.source_type || "source"}
                  {item.matched_field ? ` · ${item.matched_field}: ${item.matched_value || "-"}` : ""}
                </small>
                {item.url && (
                  <a href={item.url} target="_blank" rel="noreferrer">
                    Abrir fuente
                  </a>
                )}
              </>
            )}
          </article>
        );
      })}
    </div>
  );
}
