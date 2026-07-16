const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";

function getToken() {
  return localStorage.getItem("cs_token");
}

async function request(path, { method = "GET", body, isForm = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!isForm && body) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });

  const contentType = res.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await res.json() : null;

  if (!res.ok) {
    const message = (data && data.error) || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

export const api = {
  register: (name, email, password) =>
    request("/api/auth/register", { method: "POST", body: { name, email, password } }),

  login: (email, password) =>
    request("/api/auth/login", { method: "POST", body: { email, password } }),

  me: () => request("/api/auth/me"),

  listProjects: () => request("/api/upload"),

  uploadProject: (file, projectName) => {
    const form = new FormData();
    form.append("file", file);
    form.append("project_name", projectName);
    return request("/api/upload", { method: "POST", body: form, isForm: true });
  },

  runReview: (projectId) => request(`/api/review/${projectId}/run`, { method: "POST" }),

  listReviews: (projectId) => request(`/api/review/${projectId}`),

  reviewDetail: (reviewId) => request(`/api/review/detail/${reviewId}`),

  generateReport: (reviewId) => request(`/api/report/${reviewId}/generate`, { method: "POST" }),

  downloadReportUrl: (reviewId) => `${API_BASE}/api/report/${reviewId}/download`,

  downloadReportBlob: async (reviewId) => {
  const token = getToken();
  const res = await fetch(`${API_BASE}/api/report/${reviewId}/download`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to download report");
  return res.blob();
},
};

export { getToken, API_BASE };
