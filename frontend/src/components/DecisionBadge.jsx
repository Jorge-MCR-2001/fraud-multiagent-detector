import { normalizeDecision } from "../utils/formatters";

export default function DecisionBadge({ decision }) {
  const normalized = normalizeDecision(decision);
  return <span className={`decisionBadge ${normalized}`}>{normalized}</span>;
}
