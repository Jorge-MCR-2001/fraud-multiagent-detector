export default function SignalTags({ signals = [], tags = [] }) {
  if (!signals?.length && !tags?.length) {
    return <div className="emptyState">Sin señales críticas detectadas.</div>;
  }

  return (
    <div className="tagWrap">
      {signals.map((signal, index) => (
        <span className="tag signal" key={`signal-${signal}-${index}`}>
          {signal}
        </span>
      ))}
      {tags.map((tag, index) => (
        <span className="tag technical" key={`tag-${tag}-${index}`}>
          {tag}
        </span>
      ))}
    </div>
  );
}
