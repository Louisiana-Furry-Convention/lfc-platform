const API_BASE_URL = "http://192.168.1.143:8000";

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
  let data = null;

  if (contentType.includes("application/json")) {
    data = await response.json();
  } else {
    const text = await response.text();
    data = { detail: text };
  }

  if (!response.ok) {
    const errorMessage =
      data?.detail ||
      data?.message ||
      `Request failed with status ${response.status}`;
    throw new Error(errorMessage);
  }

  return data;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  return parseResponse(response);
}

export async function apiGet(path, token = null) {
  return request(path, {
    method: "GET",
    headers: buildHeaders(token),
  });
}

export async function apiPost(path, body, token = null) {
  return request(path, {
    method: "POST",
    headers: buildHeaders(token),
    body: JSON.stringify(body),
  });
}

export async function apiPatch(path, body, token = null) {
  return request(path, {
    method: "PATCH",
    headers: buildHeaders(token),
    body: JSON.stringify(body),
  });
}

export async function apiDelete(path, token = null) {
  return request(path, {
    method: "DELETE",
    headers: buildHeaders(token),
  });
}

export async function loginRequest(email, password) {
  return apiPost("/auth/login", { email, password });
}

export async function getMeRequest(token) {
  return apiGet("/auth/me", token);
}

export async function submitApplication(body, token) {
  return apiPost("/applications", body, token);
}

export async function getMyApplications(token) {
  return apiGet("/applications/me", token);
}

export async function getAdminApplications(token, params = {}) {
  const search = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== "" && value !== null && value !== undefined) {
      search.set(key, value);
    }
  }

  const query = search.toString() ? `?${search.toString()}` : "";
  return apiGet(`/admin/applications${query}`, token);
}

export async function reviewApplication(applicationId, body, token) {
  return apiPatch(`/admin/applications/${applicationId}/review`, body, token);
}

export { API_BASE_URL };
