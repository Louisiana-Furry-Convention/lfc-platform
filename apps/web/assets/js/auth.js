import { loginRequest, getMeRequest } from "./api.js";

const TOKEN_KEY = "lfc_token";
const USER_KEY = "lfc_user";

export function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function loadToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function loadUser() {
  const raw = localStorage.getItem(USER_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function clearUser() {
  localStorage.removeItem(USER_KEY);
}

export function clearSession() {
  clearToken();
  clearUser();
}

export function isLoggedIn() {
  return !!loadToken();
}

export async function login(email, password) {
  const data = await loginRequest(email, password);

  if (!data?.access_token) {
    throw new Error("Login succeeded but no access token was returned.");
  }

  saveToken(data.access_token);

  const me = await fetchCurrentUser();

  return {
    token: data.access_token,
    user: me,
  };
}

export async function fetchCurrentUser() {
  const token = loadToken();

  if (!token) {
    throw new Error("No active session found.");
  }

  const user = await getMeRequest(token);
  saveUser(user);
  return user;
}

export async function restoreSession() {
  const token = loadToken();

  if (!token) {
    return null;
  }

  try {
    const user = await fetchCurrentUser();
    return { token, user };
  } catch (error) {
    clearSession();
    return null;
  }
}

export function logout(redirectTo = "/login.html") {
  clearSession();
  window.location.href = redirectTo;
}

export function redirectIfLoggedIn(defaultPath = "/admin-apps.html") {
  if (isLoggedIn()) {
    window.location.href = defaultPath;
  }
}

export async function requireAuth(redirectTo = "/login.html") {
  const session = await restoreSession();

  if (!session) {
    window.location.href = redirectTo;
    return null;
  }

  return session;
}

export function requireRole(allowedRoles = [], redirectTo = "/login.html") {
  const user = loadUser();

  if (!user) {
    window.location.href = redirectTo;
    return false;
  }

  if (allowedRoles.length === 0) {
    return true;
  }

  if (!allowedRoles.includes(user.role)) {
    window.location.href = redirectTo;
    return false;
  }

  return true;
}

