import { requireAuth } from "../auth.js";
import { apiPost } from "../api.js";

const form = document.getElementById("checkin-form");
const ticketCodeInput = document.getElementById("ticket-code");
const laneSelect = document.getElementById("lane-select");
const checkinButton = document.getElementById("checkin-button");
const clearButton = document.getElementById("clear-button");
const statusMessage = document.getElementById("checkin-status");
const resultCard = document.getElementById("result-card");
const resultBadge = document.getElementById("result-state-badge");
const resultGrid = document.getElementById("checkin-result");
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

function setResultState(state) {
  resultCard.classList.remove("state-neutral", "state-success", "state-warning", "state-error");

  if (state === "success") {
    resultCard.classList.add("state-success");
    resultBadge.textContent = "Checked In";
    return;
  }

  if (state === "warning") {
    resultCard.classList.add("state-warning");
    resultBadge.textContent = "Already Checked In";
    return;
  }

  if (state === "error") {
    resultCard.classList.add("state-error");
    resultBadge.textContent = "Error";
    return;
  }

  resultCard.classList.add("state-neutral");
  resultBadge.textContent = "Waiting";
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
          <div class="activity-line-1">${escapeHtml(item.primary)}</div>
          <div class="activity-line-2">${escapeHtml(item.secondary)}</div>
          <div class="activity-time">${escapeHtml(item.time)}</div>
        </div>
      `
    )
    .join("");
}

function addActivity(primary, secondary) {
  activityItems.unshift({
    primary,
    secondary,
    time: new Date().toLocaleString(),
  });

  if (activityItems.length > 10) {
    activityItems.length = 10;
  }

  renderRecentActivity();
}

function renderResult(data, submittedCode) {
  const state =
    data.status === "already_checked_in"
      ? "warning"
      : data.status === "checked_in"
      ? "success"
      : "neutral";

  setResultState(state);

  const attendeeName = data.display_name || data.email || submittedCode;
  const statusLabel =
    data.status === "already_checked_in"
      ? "Already Checked In"
      : data.status === "checked_in"
      ? "Checked In"
      : data.status || "Processed";

  resultGrid.innerHTML = `
    <div>
      <div class="result-label">Attendee</div>
      <div class="result-value">${escapeHtml(attendeeName)}</div>
    </div>
    <div>
      <div class="result-label">Ticket Type</div>
      <div class="result-value">${escapeHtml(data.ticket_type_name || data.ticket_type_id || "—")}</div>
    </div>
    <div>
      <div class="result-label">Lane</div>
      <div class="result-value">${escapeHtml(data.lane || laneSelect.value || "main")}</div>
    </div>
    <div>
      <div class="result-label">Status</div>
      <div class="result-value">${escapeHtml(statusLabel)}</div>
    </div>
  `;
}

async function submitCheckin() {
  const code = ticketCodeInput.value.trim();
  const lane = laneSelect.value || "main";

  if (!code) {
    setStatus("Enter a QR token first.", true);
    setResultState("error");
    return;
  }

  setStatus("");
  setLoading(true);

  try {
    const data = await apiPost("/checkin", {
      qr_token: code,
      lane,
    });

    renderResult(data, code);

    const message =
      data.status === "already_checked_in"
        ? "Attendee was already checked in."
        : "Check-in successful.";

    setStatus(message);
    addActivity(
      data.display_name || data.email || code,
      `${message} • ${data.ticket_type_name || data.ticket_type_id || "Unknown type"} • ${lane}`
    );

    ticketCodeInput.value = "";
    ticketCodeInput.focus();
  } catch (error) {
    setResultState("error");
    resultGrid.innerHTML = `
      <div>
        <div class="result-label">Error</div>
        <div class="result-value">${escapeHtml(error.message || "Check-in failed.")}</div>
      </div>
    `;
    setStatus(error.message || "Check-in failed.", true);
    addActivity(code || "Unknown token", `Failed: ${error.message || "Check-in failed."}`);
    ticketCodeInput.focus();
  } finally {
    setLoading(false);
  }
}

async function init() {
  const session = await requireAuth();
  if (!session) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitCheckin();
  });

  clearButton.addEventListener("click", () => {
    ticketCodeInput.value = "";
    setStatus("");
    setResultState("neutral");
    resultGrid.innerHTML = `
      <div>
        <div class="result-label">Attendee</div>
        <div class="result-value">No attendee checked in yet.</div>
      </div>
      <div>
        <div class="result-label">Ticket Type</div>
        <div class="result-value">—</div>
      </div>
      <div>
        <div class="result-label">Lane</div>
        <div class="result-value">—</div>
      </div>
      <div>
        <div class="result-label">Status</div>
        <div class="result-value">—</div>
      </div>
    `;
    ticketCodeInput.focus();
  });

  renderRecentActivity();
  ticketCodeInput.focus();
}

init();
