import { login, restoreSession } from "../auth.js";

const form = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginButton = document.getElementById("login-button");
const statusMessage = document.getElementById("login-status");

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
  statusMessage.classList.toggle("success", !isError && !!message);
}

function setLoading(isLoading) {
  loginButton.disabled = isLoading;
  loginButton.textContent = isLoading ? "Signing In..." : "Sign In";
}

function getRedirectPathForUser(user) {
  if (!user) {
    return "/login.html";
  }

  if (["admin", "director", "officer"].includes(user.role)) {
    return "/admin.html";
  }

  return "/applications.html";
}

async function init() {
  const session = await restoreSession();

  if (session?.user) {
    window.location.href = getRedirectPathForUser(session.user);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = emailInput.value.trim();
  const password = passwordInput.value;

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
});

init();

