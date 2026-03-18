import { login, restoreSession } from "../auth.js";

const form = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginButton = document.getElementById("login-button");
const statusMessage = document.getElementById("login-status");

function setStatus(message, isError = false) {
  if (!statusMessage) return;
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
  statusMessage.classList.toggle("success", !isError && !!message);
}

function setLoading(isLoading) {
  if (!loginButton) return;
  loginButton.disabled = isLoading;
  loginButton.textContent = isLoading ? "Signing In..." : "Sign In";
}

function getRedirectPathForUser(user) {
  if (!user) return "/login.html";
  if (["admin", "director", "officer"].includes(user.role)) {
    return "/admin.html";
  }
  return "/applications.html";
}

async function submitLogin() {
  const email = emailInput?.value.trim() || "";
  const password = passwordInput?.value || "";

  setStatus("");
  setLoading(true);

  try {
    const session = await login(email, password);
    setStatus("Login successful.");
    window.location.href = getRedirectPathForUser(session.user);
  } catch (error) {
    setStatus(error.message || "Login failed.", true);
  } finally {
    setLoading(false);
  }
}

async function init() {
  try {
    const session = await restoreSession();
    if (session?.user) {
      window.location.href = getRedirectPathForUser(session.user);
      return;
    }
  } catch (_) {}

  form?.addEventListener("submit", (event) => {
    event.preventDefault();
    return false;
  });

  loginButton?.addEventListener("click", submitLogin);

  passwordInput?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      submitLogin();
    }
  });
}

init();
