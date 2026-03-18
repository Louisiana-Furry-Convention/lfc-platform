import { requireAuth } from "../auth.js";
import { apiPost } from "../api.js";

const form = document.getElementById("checkin-form");
const ticketCodeInput = document.getElementById("ticket-code");
const checkinButton = document.getElementById("checkin-button");
const clearButton = document.getElementById("clear-button");
const statusMessage = document.getElementById("checkin-status");
const resultCard = document.getElementById("checkin-result");
const recentActivity = document.getElementById("recent-activity");

const activityItems = [];

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
  statusMessage.classList.toggle("success", !isError && !!message);
}

function setLoading(isLoading) {
  checkinButton.disabled = isLoading;
  checkinButton.textContent = isLoading ? "Checking In..." : "Check In";
}

function renderRecentActivity() {
  if (!activityItems.length) {
    recentActivity.innerHTML = "No recent activity yet.";
    return;
  }

  recentActivity.innerHTML = activityItems
    .map(
      (item) => `
        <div class="activity-item">
          <div><strong>${escapeHtml(item.code)}</strong></div>
          <div>${escapeHtml(item.message)}</div>
          <div class="activity-time">${escapeHtml(item.time)}</div>
        </div>
      `
    )
    .join("");
}

function addActivity(code, message) {
  activityItems.unshift({
    code,
    message,
    time: new Date().toLocaleString(),
  });

  if (activityItems.length > 10) {
    activityItems.length = 10;
  }

  renderRecentActivity();
}

function renderResult(data, submittedCode) {
  const checkedIn = data.checked_in === true;
  const alreadyCheckedIn = data.already_checked_in === true;
  const attendeeName =
    data.display_name ||
    data.name ||
    data.attendee_name ||
    data.email ||
    submittedCode;

  let stateLabel = "Processed";
  if (checkedIn) stateLabel = "Checked In";
  if (alreadyCheckedIn) stateLabel = "Already Checked In";

  resultCard.innerHTML = `
    <div class="result-grid">
      <div>
        <div class="result-label">Attendee</div>
        <div class="result-value">${escapeHtml(attendeeName)}</div>
      </div>
      <div>
        <div class="result-label">Ticket</div>
        <div class="result-value">${escapeHtml(submittedCode)}</div>
      </div>
      <div>
        <div class="result-label">Status</div>
        <div class="result-value">${escapeHtml(stateLabel)}</div>
      </div>
    </div>
  `;
}

async function submitCheckin() {
  const code = ticketCodeInput.value.trim();

  if (!code) {
    setStatus("Enter a ticket code first.", true);
    return;
  }

  setStatus("");
  setLoading(true);

  try {
    const data = await apiPost("/checkin", { ticket_code: code });

    renderResult(data, code);

    const message = data.already_checked_in
      ? "Attendee was already checked in."
      : "Check-in successful.";

    setStatus(message, false);
    addActivity(code, message);
    ticketCodeInput.value = "";
    ticketCodeInput.focus();
  } catch (error) {
    resultCard.textContent = "Check-in failed.";
    setStatus(error.message || "Check-in failed.", true);
    addActivity(code, `Failed: ${error.message || "Check-in failed."}`);
  } finally {
    setLoading(false);
  }
}

async function init() {
  const session = await requireAuth();
  if (!session) return;

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitCheckin();
  });

  clearButton?.addEventListener("click", () => {
    ticketCodeInput.value = "";
    setStatus("");
    resultCard.textContent = "No attendee checked in yet.";
    ticketCodeInput.focus();
  });

  ticketCodeInput?.focus();
}

init();
