import { requireAuth } from "../auth.js";
import { apiGet } from "../api.js";

const applicationsEl = document.getElementById("stat-applications");
const checkinsEl = document.getElementById("stat-checkins");
const ticketsEl = document.getElementById("stat-tickets");

async function loadStat(el, loader, mapper) {
  try {
    const data = await loader();
    el.textContent = mapper(data);
  } catch {
    el.textContent = "!";
  }
}

async function init() {
  const session = await requireAuth();
  if (!session) return;

  await Promise.all([
    loadStat(
      applicationsEl,
      () => apiGet("/admin/applications"),
      (data) => data.total ?? data.count ?? 0
    ),
    loadStat(
      checkinsEl,
      () => apiGet("/admin/checkins"),
      (data) => Array.isArray(data) ? data.length : (data.total_checkins ?? data.count ?? 0)
    ),
    loadStat(
      ticketsEl,
      () => apiGet("/admin/stats"),
      (data) => data.tickets_issued ?? 0
    ),
  ]);
}

init();
