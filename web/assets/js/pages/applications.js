import { restoreSession, logout, loadToken } from "../auth.js";
import { getMyApplications, submitApplication } from "../api.js";

const applicationsStatus = document.getElementById("applications-status");
const applicationsOutput = document.getElementById("applications-output");
const applicationForm = document.getElementById("application-form");
const submitStatus = document.getElementById("submit-status");
const logoutButton = document.getElementById("logout-button");

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
  element.classList.toggle("success", !isError && !!message);
}

function formatJson(data) {
  return JSON.stringify(data, null, 2);
}

async function loadApplications() {
  const token = loadToken();
  const data = await getMyApplications(token);
  applicationsOutput.textContent = formatJson(data);
  applicationsStatus.textContent = "Applications loaded.";
}

logoutButton.addEventListener("click", () => {
  logout("/login.html");
});

applicationForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const token = loadToken();
  const eventId = document.getElementById("event_id").value.trim();
  const applicationType = document.getElementById("application_type").value.trim();
  const payloadRaw = document.getElementById("payload_json").value.trim();

  let payload = {};
  if (payloadRaw) {
    try {
      payload = JSON.parse(payloadRaw);
    } catch {
      setStatus(submitStatus, "Payload JSON is invalid.", true);
      return;
    }
  }

  try {
    setStatus(submitStatus, "Submitting...");
    await submitApplication(
      {
        event_id: eventId,
        application_type: applicationType,
        payload,
      },
      token
    );

    setStatus(submitStatus, "Application submitted successfully.");
    applicationForm.reset();
    await loadApplications();
  } catch (error) {
    setStatus(submitStatus, error.message || "Failed to submit application.", true);
  }
});

async function init() {
  const session = await restoreSession();

  if (!session?.user) {
    window.location.href = "/login.html";
    return;
  }

  await loadApplications();
}

init();
