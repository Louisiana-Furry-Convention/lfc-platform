import { requireAuth } from "../auth.js";
import { apiGet } from "../api.js";

const tbody = document.getElementById("attendees-tbody");
const searchInput = document.getElementById("search-input");
const refreshBtn = document.getElementById("refresh-btn");

let allItems = [];

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function statusBadge(status) {
  const safe = String(status || "").toLowerCase();
  const klass = safe === "checked_in" ? "badge success" : "badge warning";
  const label = safe || "unknown";
  return `<span class="${klass}">${escapeHtml(label)}</span>`;
}

function renderRows(items) {
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="5">No attendees found.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map((item) => `
    <tr>
      <td>${escapeHtml(item.display_name || "—")}</td>
      <td>${escapeHtml(item.email || "—")}</td>
      <td>${escapeHtml(item.ticket_type_name || "—")}</td>
      <td>${statusBadge(item.status)}</td>
      <td>${escapeHtml(item.event_id || "—")}</td>
    </tr>
  `).join("");
}

function applySearch() {
  const q = (searchInput.value || "").trim().toLowerCase();

  if (!q) {
    renderRows(allItems);
    return;
  }

  const filtered = allItems.filter((item) =>
    JSON.stringify(item).toLowerCase().includes(q)
  );

  renderRows(filtered);
}

async function loadAttendees() {
  tbody.innerHTML = `<tr><td colspan="5">Loading attendees…</td></tr>`;

  try {
    const [ticketsData, usersData, ticketTypesData] = await Promise.all([
      apiGet("/admin/db/table?table=tickets"),
      apiGet("/admin/users"),
      apiGet("/admin/ticket_types"),
    ]);

    const tickets = ticketsData.rows || [];
    const users = Array.isArray(usersData) ? usersData : [];
    const ticketTypes = Array.isArray(ticketTypesData) ? ticketTypesData : [];

    const userMap = new Map(users.map((u) => [u.id, u]));
    const typeMap = new Map(ticketTypes.map((t) => [t.id, t]));

    allItems = tickets.map((ticket) => {
      const user = userMap.get(ticket.user_id) || {};
      const type = typeMap.get(ticket.ticket_type_id) || {};

      return {
        id: ticket.id,
        display_name: user.display_name || user.email || ticket.user_id,
        email: user.email || "—",
        ticket_type_name: type.name || ticket.ticket_type_id || "—",
        status: ticket.status || "—",
        event_id: ticket.event_id || "—",
      };
    });

    applySearch();
  } catch (error) {
    tbody.innerHTML = `<tr><td colspan="5">Failed to load attendees: ${escapeHtml(error.message)}</td></tr>`;
  }
}

async function init() {
  const session = await requireAuth();
  if (!session) return;

  searchInput.addEventListener("input", applySearch);
  refreshBtn.addEventListener("click", loadAttendees);
  loadAttendees();
}

init();

