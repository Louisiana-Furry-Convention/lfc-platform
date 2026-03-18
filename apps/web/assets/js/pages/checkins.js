import { requireAuth } from "../auth.js";
import { apiGet } from "../api.js";

const tbody = document.getElementById("checkins-tbody");
const summary = document.getElementById("checkins-summary");
const refreshBtn = document.getElementById("refresh-btn");

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

function renderRows(items) {
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="5">No check-ins found.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map((item) => `
    <tr>
      <td>${escapeHtml(formatDate(item.created_at))}</td>
      <td>${escapeHtml(item.display_name || item.email || "—")}</td>
      <td>${escapeHtml(item.ticket_type_id || "—")}</td>
      <td>main</td>
      <td>—</td>
    </tr>
  `).join("");
}

async function loadCheckins() {
  tbody.innerHTML = `<tr><td colspan="5">Loading check-ins…</td></tr>`;

  try {
    const data = await apiGet("/admin/checkins");
    const items = Array.isArray(data) ? data : (data.checkins || data.items || []);
    summary.textContent = `Showing ${items.length} recent check-ins`;
    renderRows(items);
  } catch (error) {
    summary.textContent = "Load failed";
    tbody.innerHTML = `<tr><td colspan="5">Failed to load check-ins: ${escapeHtml(error.message)}</td></tr>`;
  }
}

async function init() {
  const session = await requireAuth();
  if (!session) return;

  refreshBtn?.addEventListener("click", loadCheckins);
  loadCheckins();
}

init();
