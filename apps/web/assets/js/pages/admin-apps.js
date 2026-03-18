import { api, apiGet } from "../api.js";
import { requireAuth } from "../auth.js";

const state = {
  items: [],
  total: 0,
  limit: 25,
  offset: 0,
  filters: {
    status: "",
    application_type: "",
    search: "",
  },
};

const STAGE_SEQUENCES = {
  staff: [
    "submitted",
    "hr_interview",
    "lead_interview",
    "director_review",
    "officer_review",
    "hr_onboarding",
    "complete",
  ],
  vendor: [
    "submitted",
    "review",
    "complete",
  ],
  panel: [
    "submitted",
    "review",
    "complete",
  ],
};

function getStageSequence(type) {
  return STAGE_SEQUENCES[type] || ["submitted", "review", "complete"];
}

function renderStageOptions(app) {
  const sequence = getStageSequence(app.application_type);
  const current = app.current_stage || sequence[0];

  return sequence.map((stage) => {
    const selected = stage === current ? "selected" : "";
    return `<option value="${escapeHtml(stage)}" ${selected}>${escapeHtml(stage)}</option>`;
  }).join("");
}

const els = {
  tbody: document.getElementById("applications-tbody"),
  summary: document.getElementById("queue-summary"),
  pagination: document.getElementById("pagination"),
  refreshBtn: document.getElementById("refresh-btn"),
  filterStatus: document.getElementById("filter-status"),
  filterType: document.getElementById("filter-type"),
  filterSearch: document.getElementById("filter-search"),
};

const reviewPanel = document.getElementById("review-panel");
const reviewContent = document.getElementById("review-content");
const reviewStage = document.getElementById("review-stage");
const reviewNotes = document.getElementById("review-notes");

let currentApplicationId = null;
let currentApplication = null;

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function badgeClass(type, value) {
  const safe = String(value || "").toLowerCase();

  if (type === "status") {
    if (safe === "approved") return "badge success";
    if (safe === "declined") return "badge danger";
    if (safe === "waitlisted") return "badge warning";
    if (safe === "submitted") return "badge warning";
    if (safe === "under_review") return "badge info";
    if (safe === "withdrawn") return "badge muted";
  }

  return "badge";
}

function getApplicantName(app) {
  const data = app.data_json || {};
  return (
    data.display_name ||
    data.legal_name ||
    data.contact_name ||
    data.business_name ||
    data.panel_title ||
    app.title ||
    app.id ||
    "Unknown"
  );
}

function getApplicantEmail(app) {
  const data = app.data_json || {};
  return data.email || "—";
}

function getDetailsText(app) {
  const data = app.data_json || {};

  if (typeof data === "string") return data;
  if (data.experience) return data.experience;
  if (data.panel_description) return data.panel_description;
  if (data.inventory_summary) return data.inventory_summary;

  return JSON.stringify(data, null, 2);
}

function rowTemplate(app) {
  const submitted = app.submitted_at || app.created_at;
  const details = getDetailsText(app);

  return `
    <tr data-id="${escapeHtml(app.id)}">
      <td>${escapeHtml(formatDate(submitted))}</td>
      <td>
        <div class="cell-primary">${escapeHtml(getApplicantName(app))}</div>
        <div class="cell-secondary">${escapeHtml(getApplicantEmail(app))}</div>
      </td>
      <td>${escapeHtml(app.application_type || "—")}</td>
      <td><span class="${badgeClass("status", app.status)}">${escapeHtml(app.status || "—")}</span></td>
      <td>${escapeHtml(app.current_stage || "—")}</td>
      <td>
        <div class="row-actions">
          <button class="button tiny secondary" data-action="review">Review</button>
          <button class="button tiny success" data-action="approve">Approve</button>
          <button class="button tiny danger" data-action="decline">Decline</button>
        </div>
      </td>
    </tr>
    <tr class="details-row">
      <td colspan="6">
        <div class="details-card">
          <strong>Details:</strong>
          <pre>${escapeHtml(details)}</pre>
        </div>
      </td>
    </tr>
  `;
}

function renderTable() {
  if (!state.items.length) {
    els.tbody.innerHTML = `<tr><td colspan="6">No applications found.</td></tr>`;
    return;
  }

  els.tbody.innerHTML = state.items.map(rowTemplate).join("");
}

function renderSummary() {
  const start = state.total === 0 ? 0 : state.offset + 1;
  const end = Math.min(state.offset + state.limit, state.total);
  els.summary.textContent = `Showing ${start}-${end} of ${state.total}`;
}

function renderPagination() {
  const prevDisabled = state.offset <= 0 ? "disabled" : "";
  const nextDisabled = state.offset + state.limit >= state.total ? "disabled" : "";

  els.pagination.innerHTML = `
    <button id="page-prev" class="button secondary" ${prevDisabled}>Previous</button>
    <span class="pagination-status">Page ${Math.floor(state.offset / state.limit) + 1}</span>
    <button id="page-next" class="button secondary" ${nextDisabled}>Next</button>
  `;

  document.getElementById("page-prev")?.addEventListener("click", () => {
    state.offset = Math.max(0, state.offset - state.limit);
    loadApplications();
  });

  document.getElementById("page-next")?.addEventListener("click", () => {
    state.offset += state.limit;
    loadApplications();
  });
}

function field(label, value) {
  return `
    <div class="review-field">
      <div class="review-label">${escapeHtml(label)}</div>
      <div class="review-value">${escapeHtml(value ?? "—")}</div>
    </div>
  `;
}

function renderStructuredDetails(app) {
  const data = app.data_json || {};
  const type = app.application_type || "application";

  let specificFields = "";

  if (type === "staff") {
    specificFields = `
      ${field("Department", app.target_department || data.department || "—")}
      ${field("Target Role", app.target_role || data.target_role || "—")}
      ${field("Experience", data.experience || "—")}
      ${field("Availability", Array.isArray(data.availability) ? data.availability.join(", ") : "—")}
    `;
  } else if (type === "vendor") {
    specificFields = `
      ${field("Business Name", data.business_name || "—")}
      ${field("Contact Name", data.contact_name || "—")}
      ${field("Inventory Summary", data.inventory_summary || "—")}
      ${field("Needs Power", data.needs_power === true ? "Yes" : data.needs_power === false ? "No" : "—")}
    `;
  } else if (type === "panel") {
    specificFields = `
      ${field("Panel Title", data.panel_title || app.title || "—")}
      ${field("Duration", data.duration_minutes ? `${data.duration_minutes} minutes` : "—")}
      ${field("Tech Needs", Array.isArray(data.tech_needs) ? data.tech_needs.join(", ") : "—")}
      ${field("Description", data.panel_description || "—")}
    `;
  } else {
    specificFields = `<pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
  }

  return `
    <div class="review-section">
      <h3>${escapeHtml(type.toUpperCase())}</h3>
      <div class="review-grid">
        ${field("Application ID", app.id)}
        ${field("Status", app.status)}
        ${field("Stage", app.current_stage || "—")}
        ${field("Submitted", formatDate(app.submitted_at || app.created_at))}
        ${field("Applicant", getApplicantName(app))}
        ${field("Email", getApplicantEmail(app))}
      </div>
    </div>

    <div class="review-section">
      <h4>Application Details</h4>
      <div class="review-grid">
        ${specificFields}
      </div>
    </div>

    <div class="review-section">
      <h4>Raw Payload</h4>
      <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
    </div>
  `;
}

async function loadApplications() {
  els.tbody.innerHTML = `<tr><td colspan="6">Loading applications…</td></tr>`;

  try {
    const data = await api.listApplications({
      status: state.filters.status || undefined,
      application_type: state.filters.application_type || undefined,
      limit: state.limit,
      offset: state.offset,
    });

    let items = data.applications || data.items || data || [];
    const search = state.filters.search.trim().toLowerCase();

    if (search) {
      items = items.filter((app) => JSON.stringify(app).toLowerCase().includes(search));
    }

    state.items = items;
    state.total = data.total ?? items.length;

    renderTable();
    renderSummary();
    renderPagination();
  } catch (error) {
    els.tbody.innerHTML = `<tr><td colspan="6">Failed to load applications: ${escapeHtml(error.message)}</td></tr>`;
    els.summary.textContent = "Load failed";
    els.pagination.innerHTML = "";
  }
}

async function openReviewPanel(applicationId) {
  currentApplicationId = applicationId;
  currentApplication = null;

  reviewPanel.classList.remove("hidden");
  reviewContent.innerHTML = "Loading...";

  try {
    const res = await api.getApplication(applicationId);
    const app = res.application || res;
    currentApplication = app;

    const reviews = await apiGet(`/admin/applications/${applicationId}/reviews`);

    reviewStage.innerHTML = renderStageOptions(app);
    reviewStage.value = app.current_stage || getStageSequence(app.application_type)[0];
    reviewNotes.value = "";

    const historyHtml = reviews.length
      ? reviews.map((r) => `
          <div class="review-section">
            <strong>${escapeHtml(r.stage || "—")} | ${escapeHtml(r.decision || "note")}</strong>
            <div>${escapeHtml(r.notes || "")}</div>
            <small>${escapeHtml(r.created_at || "")}</small>
          </div>
        `).join("")
      : "<p>No reviews yet.</p>";

    reviewContent.innerHTML = `
      ${renderStructuredDetails(app)}
      <div class="review-section">
        <h4>Review History</h4>
        ${historyHtml}
      </div>
    `;
  } catch (error) {
    reviewContent.innerHTML = `Error loading application: ${escapeHtml(error.message)}`;
  }
}

async function updateStatus(status) {
  if (!currentApplicationId) return;

  const notes = reviewNotes.value.trim();
  if (!notes) {
    alert("Reviewer notes are required before changing status.");
    return;
  }

  try {
    await api.updateApplicationStatus(currentApplicationId, status);

    await api.createApplicationReview(currentApplicationId, {
      stage: reviewStage.value,
      decision: status,
      notes,
    });

    await loadApplications();
    await openReviewPanel(currentApplicationId);
  } catch (error) {
    alert(error.message);
  }
}

async function saveReview() {
  if (!currentApplicationId) return;
if (currentApplication?.status && ["approved", "declined", "waitlisted", "withdrawn"].includes(currentApplication.status)) {
  alert("Cannot change stage on a terminal application.");
  return;
}

  try {
    await api.updateApplicationStage(currentApplicationId, reviewStage.value);

    const notes = reviewNotes.value.trim();

if (!notes) {
  alert("Reviewer notes are required when saving a review.");
  return;
}

await api.createApplicationReview(currentApplicationId, {
  stage: reviewStage.value,
  decision: null,
  notes,
});

    await loadApplications();
    await openReviewPanel(currentApplicationId);
    alert("Review saved.");
  } catch (error) {
    alert(`Save failed: ${error.message}`);
  }
}

async function handleActionClick(event) {
  const button = event.target.closest("[data-action]");
  if (!button) return;

  const row = button.closest("tr[data-id]");
  if (!row) return;

  const applicationId = row.dataset.id;
  const action = button.dataset.action;

  button.disabled = true;

  try {
    if (action === "review") {
      await openReviewPanel(applicationId);
      return;
    }
    if (action === "approve") {
      await api.updateApplicationStatus(applicationId, "approved");
    }
    if (action === "decline") {
      await api.updateApplicationStatus(applicationId, "declined");
    }

    await loadApplications();
  } catch (error) {
    console.error("admin app action failed:", error);
    alert(`Action failed: ${error.message}`);
  } finally {
    button.disabled = false;
  }
}

function bindFilters() {
  els.filterStatus?.addEventListener("change", () => {
    state.filters.status = els.filterStatus.value;
    state.offset = 0;
    loadApplications();
  });

  els.filterType?.addEventListener("change", () => {
    state.filters.application_type = els.filterType.value;
    state.offset = 0;
    loadApplications();
  });

  els.filterSearch?.addEventListener("input", () => {
    state.filters.search = els.filterSearch.value;
    loadApplications();
  });

  els.refreshBtn?.addEventListener("click", loadApplications);
  els.tbody?.addEventListener("click", handleActionClick);

  document.getElementById("close-review")?.addEventListener("click", () => {
    reviewPanel.classList.add("hidden");
  });

  document.getElementById("review-approve")?.addEventListener("click", async () => {
    await updateStatus("approved");
  });

  document.getElementById("review-decline")?.addEventListener("click", async () => {
    await updateStatus("declined");
  });

  document.getElementById("review-under")?.addEventListener("click", async () => {
    await updateStatus("under_review");
  });

  document.getElementById("review-save")?.addEventListener("click", async () => {
    await saveReview();
  });
}

async function init() {
  const session = await requireAuth();
  if (!session) return;

  bindFilters();
  loadApplications();
}

init();
