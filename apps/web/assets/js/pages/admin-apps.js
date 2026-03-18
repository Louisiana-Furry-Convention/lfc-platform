import { api } from "../api.js";
import { requireAuth } from "../auth.js";

const state = {
  items: [],
  total: 0,
  limit: 25,
  offset: 0,
  filters: {
    status: "",
    application_type: "",
    reviewed: "",
    search: "",
  },
};

const els = {
  tbody: document.getElementById("applications-tbody"),
  summary: document.getElementById("queue-summary"),
  pagination: document.getElementById("pagination"),
  refreshBtn: document.getElementById("refresh-btn"),
  filterStatus: document.getElementById("filter-status"),
  filterType: document.getElementById("filter-type"),
  filterReviewed: document.getElementById("filter-reviewed"),
  filterSearch: document.getElementById("filter-search"),
};

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
    if (safe === "denied") return "badge danger";
    if (safe === "submitted") return "badge warning";
    if (safe === "under_review") return "badge info";
  }

  if (type === "reviewed") {
    return safe === "true" ? "badge info" : "badge muted";
  }

  return "badge";
}

function rowTemplate(app) {
  const applicantName =
    app.display_name ||
    app.name ||
    [app.first_name, app.last_name].filter(Boolean).join(" ") ||
    app.email ||
    "Unknown";

  const isReviewed = !!(app.reviewed || app.reviewed_at);

  return `
    <tr data-id="${escapeHtml(app.id)}">
      <td>${escapeHtml(formatDate(app.created_at || app.submitted_at))}</td>
      <td>
        <div class="cell-primary">${escapeHtml(applicantName)}</div>
        <div class="cell-secondary">${escapeHtml(app.email || "—")}</div>
      </td>
      <td>${escapeHtml(app.application_type || "—")}</td>
      <td><span class="${badgeClass("status", app.status)}">${escapeHtml(app.status || "—")}</span></td>
      <td><span class="${badgeClass("reviewed", String(isReviewed))}">${isReviewed ? "Reviewed" : "Pending"}</span></td>
      <td>
        <div class="row-actions">
          <button class="button tiny secondary" data-action="review">Review</button>
          <button class="button tiny success" data-action="approve">Approve</button>
          <button class="button tiny danger" data-action="deny">Deny</button>
        </div>
      </td>
    </tr>
    <tr class="details-row">
      <td colspan="6">
        <div class="details-card">
          <strong>Notes:</strong>
          <div>${escapeHtml(app.notes || app.why_join || app.description || app.data_json || "No additional details")}</div>
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

async function loadApplications() {
  els.tbody.innerHTML = `<tr><td colspan="6">Loading applications…</td></tr>`;

  try {
    const data = await api.listApplications({
      status: state.filters.status || undefined,
      application_type: state.filters.application_type || undefined,
      reviewed: state.filters.reviewed === "" ? undefined : state.filters.reviewed,
      limit: state.limit,
      offset: state.offset,
    });

    let items = data.applications || [];
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
      await api.updateApplicationStatus(applicationId, "under_review");
    }
    if (action === "approve") {
      await api.updateApplicationStatus(applicationId, "approved");
    }
    if (action === "deny") {
      await api.updateApplicationStatus(applicationId, "denied");
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

  els.filterReviewed?.addEventListener("change", () => {
    state.filters.reviewed = els.filterReviewed.value;
    state.offset = 0;
    loadApplications();
  });

  els.filterSearch?.addEventListener("input", () => {
    state.filters.search = els.filterSearch.value;
    renderTable();
  });

  els.refreshBtn?.addEventListener("click", loadApplications);
  els.tbody?.addEventListener("click", handleActionClick);
}

async function init() {
  const session = await requireAuth();
  if (!session) return;

  bindFilters();
  loadApplications();
}

init();
