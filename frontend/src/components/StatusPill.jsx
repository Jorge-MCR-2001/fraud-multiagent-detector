export default function StatusPill({ status = "muted", children }) {
  return <span className={`statusPill ${status}`}>{children}</span>;
}
