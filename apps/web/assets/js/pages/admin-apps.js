import { api, apiGet } from "../api.js";
import { requireAuth } from "../auth.js";

const TERMINAL_STATUSES = ["approved", "declined", "waitlisted", "withdrawn"];

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
  vendor: ["submitted", "review", "complete"],
  panel: ["submitted", "review", "complete"],
};

const els = {
  tbody: document.getElementById("applications-tbody"),
  summary: document.getElementById("queue-summary"),
  pagination: document.getElementById("pagination"),
  refreshBtn: document.getElementById("refresh-btn"),
  filterStatus: document.getElementById("filter-status"),
  filterType: document.getElementById("filter-type"),
  filterSearch: document.getElementById("filter-search"),
  reviewContent: document.getElementById("review-content"),
  reviewStage: document.getElementById("review-stage"),
  reviewNotes: document.getElementById("review-notes"),
  reviewApprove: document.getElementById("review-approve"),
  reviewDecline: document.getElementById("review-decline"),
  reviewUnder: document.getElementById("review-under"),
  reviewSave: document.getElementById("review-save"),
};

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
    return String(value);
  }
}

function formatStatusLabel(status) {
  const map = {
    draft: "Draft",
    submitted: "Submitted",
    under_review: "Under Review",
    approved: "Approved",
    declined: "Declined",
    waitlisted: "Waitlisted",
    withdrawn: "Withdrawn",
  };

  return map[status] || status || "—";
}

function formatDecisionLabel(decision) {
  const map = {
    note: "Note",
    under_review: "Under Review",
    approved: "Approved",
    declined: "Declined",
    waitlisted: "Waitlisted",
    withdrawn: "Withdrawn",
  };

  return map[decision] || decision || "Note";
}

function formatStageLabel(stage) {
  const map = {
    submitted: "Submitted",
    hr_interview: "HR Interview",
    lead_interview: "Lead Interview",
    director_review: "Director Review",
    officer_review: "Officer Review",
    hr_onboarding: "HR Onboarding",
    review: "Review",
    complete: "Complete",
  };

  return map[stage] || stage || "—";
}

function badgeClass(type, value) {
  const safe = String(value || "").toLowerCase();

  if (type === "status" || type === "decision") {
    if (safe === "approved") return "badge success";
    if (safe === "declined") return "badge danger";
    if (safe === "waitlisted") return "badge warning";
    if (safe === "submitted") return "badge warning";
    if (safe === "under_review") return "badge info";
    if (safe === "withdrawn") return "badge muted";
    if (safe === "draft") return "badge muted";
    if (safe === "note") return "badge";
  }

  return "badge";
}

function getStageSequence(type) {
  return STAGE_SEQUENCES[type] || ["submitted", "review", "complete"];
}

function renderStageOptions(app) {
  const sequence = getStageSequence(app.application_type);
  const current = app.current_stage || sequence[0];

  return sequence
    .map((stage) => {
      const selected = stage === current ? "selected" : "";
      return `<option value="${escapeHtml(stage)}" ${selected}>${escapeHtml(formatStageLabel(stage))}</option>`;
    })
    .join("");
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

function getApplicantSubline(app) {
  const data = app.data_json || {};

  if (app.application_type === "staff") {
    const department = app.target_department || data.department || "—";
    const role = app.target_role || data.target_role || data.role || "—";
    return `Department: ${department} | Role: ${role}`;
  }

  if (app.application_type === "vendor") {
    return `Business: ${data.business_name || "—"}`;
  }

  if (app.application_type === "panel") {
    return `Panel: ${data.panel_title || app.title || "—"}`;
  }

  return "";
}

function field(label, value) {
  return `
    <div class="review-field">
      <div class="review-label">${escapeHtml(label)}</div>
      <div class="review-value">${escapeHtml(value ?? "—")}</div>
    </div>
  `;
}

function rowTemplate(app) {
  const submitted = app.submitted_at || app.created_at;

  return `
    <tr data-id="${escapeHtml(app.id)}">
      <td>${escapeHtml(formatDate(submitted))}</td>
      <td>
        <div class="cell-primary">${escapeHtml(getApplicantName(app))}</div>
        <div class="cell-secondary">${escapeHtml(getApplicantEmail(app))}</div>
        <div class="cell-tertiary">${escapeHtml(getApplicantSubline(app))}</div>
      </td>
      <td>${escapeHtml(app.application_type || "—")}</td>
      <td><span class="${badgeClass("status", app.status)}">${escapeHtml(formatStatusLabel(app.status))}</span></td>
      <td>${escapeHtml(formatStageLabel(app.current_stage))}</td>
      <td>
        <div class="row-actions">
          <button class="button tiny secondary" data-action="review" type="button">Review</button>
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
    <button id="page-prev" class="button secondary" type="button" ${prevDisabled}>Previous</button>
    <span class="pagination-status">Page ${Math.floor(state.offset / state.limit) + 1}</span>
    <button id="page-next" class="button secondary" type="button" ${nextDisabled}>Next</button>
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

function renderStructuredDetails(app) {
  const data = app.data_json || {};
  const type = app.application_type || "application";

  const typeLabelMap = {
    staff: "Staff Application",
    vendor: "Vendor Application",
    panel: "Panel Submission",
  };

  const typeLabel = typeLabelMap[type] || "Application";

  let specificFields = "";

  if (type === "staff") {
    specificFields = `
      ${field("Department", app.target_department || data.department || "—")}
      ${field("Target Role", app.target_role || data.target_role || data.role || "—")}
      ${field("Experience", data.experience || "—")}
      ${field(
        "Availability",
        Array.isArray(data.availability) ? data.availability.join(", ") : (data.availability || "—")
      )}
    `;
  } else if (type === "vendor") {
    specificFields = `
      ${field("Business Name", data.business_name || "—")}
      ${field("Contact Name", data.contact_name || "—")}
      ${field("Inventory Summary", data.inventory_summary || "—")}
      ${field(
        "Needs Power",
        data.needs_power === true ? "Yes" : data.needs_power === false ? "No" : "—"
      )}
    `;
  } else if (type === "panel") {
    specificFields = `
      ${field("Panel Title", data.panel_title || app.title || "—")}
      ${field("Duration", data.duration_minutes ? `${data.duration_minutes} minutes` : "—")}
      ${field(
        "Tech Needs",
        Array.isArray(data.tech_needs) ? data.tech_needs.join(", ") : (data.tech_needs || "—")
      )}
      ${field("Description", data.panel_description || "—")}
    `;
  } else {
    specificFields = `<pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
  }

  return `
    <div class="review-section">
      <h3>${escapeHtml(typeLabel)}</h3>
      <div class="review-grid">
        ${field("Application ID", app.id)}
        ${field("Status", formatStatusLabel(app.status))}
        ${field("Stage", formatStageLabel(app.current_stage))}
        ${field("Submitted", formatDate(app.submitted_at || app.created_at))}
        ${field("Applicant", getApplicantName(app))}
        ${field("Email", getApplicantEmail(app))}
        ${type === "staff" ? field("Department", app.target_department || data.department || "—") : ""}
        ${type === "staff" ? field("Target Role", app.target_role || data.target_role || data.role || "—") : ""}
      </div>
    </div>

    <div class="review-section">
      <h4>Application Details</h4>
      <div class="review-grid">
        ${specificFields}
      </div>
    </div>

    <div class="review-section">
      <button class="button secondary tiny" type="button" id="toggle-raw-payload">
        Show Raw Payload
      </button>
      <div id="raw-payload-wrap" class="hidden">
        <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
      </div>
    </div>
  `;
}

function setReviewControlsDisabled(disabled) {
  els.reviewStage.disabled = disabled;
  els.reviewNotes.disabled = disabled;
  els.reviewApprove.disabled = disabled;
  els.reviewDecline.disabled = disabled;
  els.reviewUnder.disabled = disabled;
  els.reviewSave.disabled = disabled;
}

function syncReviewControls(app) {
  if (!app) {
    setReviewControlsDisabled(true);
    return;
  }

  const isTerminal = TERMINAL_STATUSES.includes(app.status);
  els.reviewStage.disabled = isTerminal;
  els.reviewNotes.disabled = false;
  els.reviewApprove.disabled = isTerminal;
  els.reviewDecline.disabled = isTerminal;
  els.reviewUnder.disabled = isTerminal;
  els.reviewSave.disabled = isTerminal;
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
  els.reviewContent.innerHTML = "<p>Loading...</p>";
  setReviewControlsDisabled(true);
  els.reviewNotes.value = "";

  try {
    const res = await api.getApplication(applicationId);
    const app = res.application || res;
    currentApplication = app;

    let reviews = [];
    try {
      const reviewResponse = await apiGet(`/admin/applications/${applicationId}/reviews`);
      reviews = reviewResponse?.reviews || reviewResponse || [];
      if (!Array.isArray(reviews)) {
        reviews = [];
      }
    } catch (error) {
      console.warn("Review history unavailable:", error);
      reviews = [];
    }

    els.reviewStage.innerHTML = renderStageOptions(app);
    els.reviewStage.value = app.current_stage || getStageSequence(app.application_type)[0];

    const historyHtml = reviews.length
      ? reviews
          .map(
            (review) => `
              <div class="review-section">
                <div class="history-title">
                  <strong>${escapeHtml(formatStageLabel(review.stage))}</strong>
                  <span class="${badgeClass("decision", review.decision)}">${escapeHtml(formatDecisionLabel(review.decision))}</span>
                </div>
                <div>${escapeHtml(review.notes || "")}</div>
                <small>${escapeHtml(formatDate(review.created_at))}</small>
              </div>
            `
          )
          .join("")
      : "<p>No review history available yet.</p>";

    els.reviewContent.innerHTML = `
      ${TERMINAL_STATUSES.includes(app.status) ? `
        <div class="review-section">
          <div class="status-lock-message">
            This application is in a terminal status and can no longer be changed.
          </div>
        </div>
      ` : ""}
      ${renderStructuredDetails(app)}
      <div class="review-section">
        <h4>Review History</h4>
        ${historyHtml}
      </div>
    `;

    const toggleRawBtn = document.getElementById("toggle-raw-payload");
    const rawPayloadWrap = document.getElementById("raw-payload-wrap");

    toggleRawBtn?.addEventListener("click", () => {
      const isHidden = rawPayloadWrap?.classList.contains("hidden");
      rawPayloadWrap?.classList.toggle("hidden", !isHidden);
      toggleRawBtn.textContent = isHidden ? "Hide Raw Payload" : "Show Raw Payload";
    });

    syncReviewControls(app);
    els.reviewNotes.focus();
  } catch (error) {
    els.reviewContent.innerHTML = `<p>Error loading application: ${escapeHtml(error.message)}</p>`;
    setReviewControlsDisabled(true);
  }
}

async function updateStatus(status) {
  if (!currentApplicationId || !currentApplication) return;

  if (TERMINAL_STATUSES.includes(currentApplication.status)) {
    alert("Cannot change status on a terminal application.");
    return;
  }

  const notes = els.reviewNotes.value.trim();
  if (!notes) {
    alert("Reviewer notes are required before changing status.");
    return;
  }

  try {
    await api.updateApplicationStatus(currentApplicationId, status);

    await api.createApplicationReview(currentApplicationId, {
      stage: els.reviewStage.value,
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
  if (!currentApplicationId || !currentApplication) return;

  if (TERMINAL_STATUSES.includes(currentApplication.status)) {
    alert("Cannot change stage on a terminal application.");
    return;
  }

  const notes = els.reviewNotes.value.trim();
  if (!notes) {
    alert("Reviewer notes are required when saving a review.");
    return;
  }

  try {
    await api.updateApplicationStage(currentApplicationId, els.reviewStage.value);

    await api.createApplicationReview(currentApplicationId, {
      stage: els.reviewStage.value,
      decision: "note",
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

  try {
    await openReviewPanel(applicationId);
  } catch (error) {
    console.error(error);
    alert("Failed to open application.");
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
    state.offset = 0;
    loadApplications();
  });

  els.refreshBtn?.addEventListener("click", () => {
    loadApplications();
  });

  els.tbody?.addEventListener("click", handleActionClick);

  els.reviewApprove?.addEventListener("click", async () => {
    await updateStatus("approved");
  });

  els.reviewDecline?.addEventListener("click", async () => {
    await updateStatus("declined");
  });

  els.reviewUnder?.addEventListener("click", async () => {
    await updateStatus("under_review");
  });

  els.reviewSave?.addEventListener("click", async () => {
    await saveReview();
  });
}

async function init() {
  const session = await requireAuth();
  if (!session) return;

  setReviewControlsDisabled(true);
  bindFilters();
  await loadApplications();
}

init();
