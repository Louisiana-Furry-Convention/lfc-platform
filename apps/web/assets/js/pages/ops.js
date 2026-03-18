import { requireAuth } from "../auth.js";
import { apiGet } from "../api.js";

const issuedEl = document.getElementById("stat-issued");
const checkedInEl = document.getElementById("stat-checked-in");
const last5El = document.getElementById("stat-last-5");
const surgeEl = document.getElementById("stat-surge");
const surgeCard = document.getElementById("surge-card");
const liveFeedEl = document.getElementById("live-feed");
const laneAnalyticsEl = document.getElementById("lane-analytics");
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

function renderFeed(items) {
  if (!items.length) {
    liveFeedEl.innerHTML = "No recent activity.";
    return;
  }

  liveFeedEl.innerHTML = items.map((item) => `
    <div class="feed-item">
      <div><strong>${escapeHtml(item.display_name || item.email || "Unknown attendee")}</strong></div>
      <div>${escapeHtml(item.tier || "Unknown tier")}</div>
      <div class="feed-time">${escapeHtml(formatDate(item.time))}</div>
    </div>
  `).join("");
}

function renderLanes(data) {
  const lanes = data.lanes || [];

  if (!lanes.length) {
    laneAnalyticsEl.innerHTML = "No lane activity yet.";
    return;
  }

  laneAnalyticsEl.innerHTML = lanes.map((lane) => `
    <div class="lane-item">
      <div><strong>${escapeHtml(lane.lane || "main")}</strong></div>
      <div class="lane-meta">${escapeHtml(String(lane.count || 0))} check-ins</div>
    </div>
  `).join("");
}

async function loadOps() {
  try {
    const [stats, liveFeed, laneAnalytics, surge] = await Promise.all([
      apiGet("/admin/stats"),
      apiGet("/admin/live_feed"),
      apiGet("/admin/lane_analytics"),
      apiGet("/admin/arrival_surge"),
    ]);

    issuedEl.textContent = stats.tickets_issued ?? 0;
    checkedInEl.textContent = stats.checked_in ?? 0;
    last5El.textContent = laneAnalytics.last_5_min ?? 0;
    surgeEl.textContent = surge.surge ? "YES" : "NO";

    surgeCard.classList.toggle("surge-true", !!surge.surge);

    renderFeed(Array.isArray(liveFeed) ? liveFeed : []);
    renderLanes(laneAnalytics);
  } catch (error) {
    issuedEl.textContent = "!";
    checkedInEl.textContent = "!";
    last5El.textContent = "!";
    surgeEl.textContent = "!";
    liveFeedEl.textContent = `Failed to load live feed: ${error.message}`;
    laneAnalyticsEl.textContent = `Failed to load lane analytics: ${error.message}`;
  }
}

async function init() {
  const session = await requireAuth();
  if (!session) return;

  refreshBtn.addEventListener("click", loadOps);
  loadOps();
  setInterval(loadOps, 15000);
}

init();
