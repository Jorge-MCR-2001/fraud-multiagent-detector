const envBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const API_BASE_URL = envBaseUrl || "/api";

async function parseResponse(response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    const detail = data?.detail ?? data ?? `HTTP ${response.status}`;
    const message = typeof detail === "string" ? detail : JSON.stringify(detail, null, 2);
    throw new Error(message);
  }

  return data;
}

export const apiClient = {
  getRoot: () => request("/"),
  getLive: () => request("/health/live"),
  getReady: () => request("/health/ready"),
  evaluateTransaction: (transactionId) =>
    request(`/evaluate/${encodeURIComponent(transactionId)}`),
  getHitlQueue: (status = "PENDING_REVIEW") =>
    request(`/hitl/queue?status=${encodeURIComponent(status)}`),
  getHitlItem: (hitlQueueId) =>
    request(`/hitl/queue/${encodeURIComponent(hitlQueueId)}`),
  resolveHitlItem: (hitlQueueId, payload) =>
    request(`/hitl/queue/${encodeURIComponent(hitlQueueId)}/resolve`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
