import { restoreSession, logout, loadToken } from "../auth.js";
import { getAdminApplications, reviewApplication } from "../api.js";

const queueStatus = document.getElementById("queue-status");
const queueOutput = document.getElementById("queue-output");
const filterForm = document.getElementById("filter-form");
const reviewForm = document.getElementById("review-form");
const reviewStatusMessage = document.getElementById("review-status-message");
const logoutButton = document.getElementById("logout-button");

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
  element.classList.toggle("success", !isError && !!message);
}

function formatJson(data) {
  return JSON.stringify(data, null, 2);
}

function getFilters() {
  return {
    status: document.getElementById("status").value.trim(),
    application_type: document.getElementById("application_type").value.trim(),
    event_id: document.getElementById("event_id").value.trim(),
    reviewed: document.getElementById("reviewed").value,
    limit: document.getElementById("limit").value.trim(),
    offset: document.getElementById("offset").value.trim(),
  };
}

async function loadQueue() {
  try {
    queueStatus.textContent = "Loading queue...";
    const token = loadToken();
    const data = await getAdminApplications(token, getFilters());
    queueOutput.textContent = formatJson(data);
    queueStatus.textContent = "Queue loaded.";
  } catch (error) {
    queueStatus.textContent = error.message || "Failed to load queue.";
    queueOutput.textContent = "No data loaded.";
  }
}

logoutButton.addEventListener("click", () => {
  logout("/login.html");
});

filterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadQueue();
});

reviewForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const token = loadToken();
  const applicationId = document.getElementById("review_application_id").value.trim();
  const status = document.getElementById("review_status").value.trim();
  const notes = document.getElementById("review_notes").value.trim();

  try {
    setStatus(reviewStatusMessage, "Submitting review...");
    await reviewApplication(
      applicationId,
      {
        status,
        review_notes: notes,
      },
      token
    );

    setStatus(reviewStatusMessage, "Review submitted successfully.");
    reviewForm.reset();
    await loadQueue();
  } catch (error) {
    setStatus(reviewStatusMessage, error.message || "Failed to submit review.", true);
  }
});

async function init() {
  const session = await restoreSession();

  if (!session?.user) {
    window.location.href = "/login.html";
    return;
  }

  await loadQueue();
}

init();
