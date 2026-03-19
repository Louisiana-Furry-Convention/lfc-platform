import { restoreSession, logout } from "../auth.js";

const welcomeText = document.getElementById("welcome-text");
const userOutput = document.getElementById("user-output");
const logoutButton = document.getElementById("logout-button");

function formatUser(user) {
  return JSON.stringify(user, null, 2);
}

async function init() {
  const session = await restoreSession();

  if (!session?.user) {
    window.location.href = "/login.html";
    return;
  }

  const user = session.user;
  const name = user.display_name || user.email || "User";

  welcomeText.textContent = `Welcome, ${name}`;
  userOutput.textContent = formatUser(user);
}

logoutButton.addEventListener("click", () => {
  logout("/login.html");
});

init();
