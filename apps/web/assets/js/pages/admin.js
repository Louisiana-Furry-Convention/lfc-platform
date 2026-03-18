import { requireAuth, logout, loadUser } from "../auth.js";

const logoutButton = document.getElementById("logout-button");
const sessionStatus = document.getElementById("admin-session-status");

async function init() {
  const session = await requireAuth();
  if (!session) return;

  const user = loadUser();

  sessionStatus.textContent = user
    ? `Signed in as ${user.display_name || user.email || "Unknown user"} (${user.role || "unknown role"})`
    : "Signed in.";

  logoutButton?.addEventListener("click", () => logout("/login.html"));
}

init();
