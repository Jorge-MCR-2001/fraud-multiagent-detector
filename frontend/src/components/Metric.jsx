export default function Metric({ label, value, hint }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value ?? "-"}</strong>
      {hint && <small>{hint}</small>}
    </div>
  );
}
