const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`;

function getStoredToken() {
  return localStorage.getItem("lfc_token");
}

function buildHeaders(token = null, extraHeaders = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...extraHeaders,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  let data = {};

  if (contentType.includes("application/json")) {
    data = await response.json().catch(() => ({}));
  } else {
    const text = await response.text().catch(() => "");
    data = text ? { detail: text } : {};
  }

  if (response.status === 401) {
    localStorage.removeItem("lfc_token");
    localStorage.removeItem("lfc_user");
    throw new Error(data.detail || "Unauthorized");
  }

  if (!response.ok) {
    throw new Error(data.detail || data.message || `Request failed with status ${response.status}`);
  }

  return data;
}

async function request(path, options = {}, token = null) {
  const resolvedToken = token || getStoredToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: buildHeaders(resolvedToken, options.headers || {}),
  });

  return parseResponse(response);
}

export async function apiGet(path, token = null) {
  return request(path, { method: "GET" }, token);
}

export async function apiPost(path, body, token = null) {
  return request(
    path,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
    token
  );
}

export async function apiPatch(path, body, token = null) {
  return request(
    path,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
    token
  );
}

export async function apiDelete(path, token = null) {
  return request(path, { method: "DELETE" }, token);
}

export async function loginRequest(email, password) {
  return apiPost("/auth/login", { email, password }, null);
}

export async function getMeRequest(token) {
  return apiGet("/auth/me", token);
}

export const api = {
  login(credentials) {
    return loginRequest(credentials.email, credentials.password);
  },

  listApplications(params = {}) {
    const search = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== "" && value !== null && value !== undefined) {
        search.set(key, String(value));
      }
    });

    const query = search.toString();
    return apiGet(`/admin/applications${query ? `?${query}` : ""}`);
  },

  updateApplicationStatus(applicationId, status, reviewNotes = null) {
    return apiPatch(`/admin/applications/${applicationId}/status`, {
      status,
      review_notes: reviewNotes,
    });
  },
};

export { API_BASE_URL };
