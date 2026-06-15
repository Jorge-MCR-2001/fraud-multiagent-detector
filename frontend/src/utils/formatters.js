export function asJson(value) {
  return JSON.stringify(value ?? {}, null, 2);
}

export function pct(value) {
  const n = Number(value ?? 0);
  return `${Math.round(n * 100)}%`;
}

export function clampPct(value) {
  const n = Number(value ?? 0);
  return Math.max(0, Math.min(100, Math.round(n * 100)));
}

export function normalizeDecision(decision) {
  return decision || "SIN_DECISION";
}

export function shortText(value, max = 90) {
  const text = String(value ?? "-");
  return text.length > max ? `${text.slice(0, max)}...` : text;
}

export function getDecisionDescription(decision) {
  const map = {
    APPROVE: "Transacción aceptada por bajo riesgo.",
    CHALLENGE: "Requiere validación adicional.",
    BLOCK: "Bloqueo preventivo por alta sospecha.",
    ESCALATE_TO_HUMAN: "Revisión humana obligatoria.",
  };

  return map[decision] || "Resultado de decisión no clasificado.";
}
