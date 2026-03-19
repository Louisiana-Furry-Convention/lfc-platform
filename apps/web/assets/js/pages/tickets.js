import { requireAuth } from "../auth.js";
import { apiGet, apiPost } from "../api.js";

const form = document.getElementById("ticket-form");
const emailInput = document.getElementById("email");
const nameInput = document.getElementById("display-name");
const typeSelect = document.getElementById("ticket-type");
const status = document.getElementById("status");
const qrOutput = document.getElementById("qr-output");
const badgePreview = document.getElementById("badge-preview");
const badgeStockSelect = document.getElementById("badge-stock");

let lastIssuedTicket = null;

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function loadTypes() {
  const types = await apiGet("/admin/ticket_types");

  typeSelect.innerHTML = types
    .map(
      (t) => `
        <option value="${t.id}">
          ${escapeHtml(t.name)} ($${(t.price_cents / 100).toFixed(2)})
        </option>
      `
    )
    .join("");
}

function badgeTone(ticketTypeName) {
  const safe = String(ticketTypeName || "").toLowerCase();
  if (safe.includes("vip")) return "badge-tone-vip";
  if (safe.includes("staff")) return "badge-tone-staff";
  if (safe.includes("vendor")) return "badge-tone-vendor";
  return "badge-tone-standard";
}

function renderQrInto(elementId, token, size = 220) {
  const el = document.getElementById(elementId);
  if (!el) return;

  el.innerHTML = "";

  if (!window.QRCode) {
    el.innerHTML = `<div class="qr-fallback">QR library not loaded</div>`;
    return;
  }

  new window.QRCode(el, {
    text: token,
    width: size,
    height: size,
    correctLevel: window.QRCode.CorrectLevel.M,
  });
}

function getBadgeStock() {
  return badgeStockSelect?.value || "4x6";
}

function getQrSizeForStock(stock) {
  if (stock === "3x4") return 160;
  if (stock === "half-letter") return 220;
  return 240;
}

function renderBadge(data) {
  const qrToken = data.qr_token || "No QR token returned";
  const email = data.email || emailInput.value || "—";
  const displayName = data.display_name || nameInput.value || email;
  const ticketType =
    data.ticket_type_name ||
    typeSelect.options[typeSelect.selectedIndex]?.text ||
    "Standard";
  const ticketId = data.ticket_id || "—";
  const toneClass = badgeTone(ticketType);
  const stock = getBadgeStock();
  const qrSize = getQrSizeForStock(stock);

  badgePreview.innerHTML = `
    <div class="badge-card ${toneClass} badge-stock-${stock}" id="printable-badge">
      <div class="badge-top">
        <div class="badge-brand">
          <div class="badge-event">Louisiana Fur Con</div>
          <div class="badge-year">2027</div>
        </div>
        <div class="badge-tier">${escapeHtml(ticketType)}</div>
      </div>

      <div class="badge-middle">
        <div class="badge-identity">
          <div class="badge-name">${escapeHtml(displayName)}</div>
          <div class="badge-email">${escapeHtml(email)}</div>
          <div class="badge-ticket-id">Ticket ID: ${escapeHtml(ticketId)}</div>
        </div>

        <div class="badge-qr">
          <div id="badge-qr-render"></div>
        </div>
      </div>

      <div class="badge-bottom">
        <div class="badge-token-label">QR Token</div>
        <div class="badge-token">${escapeHtml(qrToken)}</div>
      </div>
    </div>

    <div class="badge-preview-actions">
      <button type="button" id="print-badge-button" class="button button-primary">Print Badge</button>
      <button type="button" id="print-ticket-button" class="button secondary">Print Ticket Card</button>
    </div>
  `;

  renderQrInto("badge-qr-render", qrToken, qrSize);

  document.getElementById("print-badge-button")?.addEventListener("click", () => {
    document.body.classList.add("print-badge-mode");
    document.body.setAttribute("data-badge-stock", stock);
    window.print();
    setTimeout(() => {
      document.body.classList.remove("print-badge-mode");
      document.body.removeAttribute("data-badge-stock");
    }, 300);
  });

  document.getElementById("print-ticket-button")?.addEventListener("click", () => {
    document.body.classList.remove("print-badge-mode");
    document.body.removeAttribute("data-badge-stock");
    window.print();
  });
}

function renderTicket(data) {
  const qrToken = data.qr_token || "No QR token returned";
  const email = data.email || emailInput.value || "—";
  const displayName = data.display_name || nameInput.value || email;
  const ticketType =
    data.ticket_type_name ||
    typeSelect.options[typeSelect.selectedIndex]?.text ||
    "—";
  const ticketId = data.ticket_id || "—";

  qrOutput.innerHTML = `
    <div class="ticket-card">
      <div class="ticket-card-main">
        <div class="ticket-meta">
          <div class="ticket-label">Attendee</div>
          <div class="ticket-value">${escapeHtml(displayName)}</div>

          <div class="ticket-label">Email</div>
          <div class="ticket-value">${escapeHtml(email)}</div>

          <div class="ticket-label">Ticket Type</div>
          <div class="ticket-value">${escapeHtml(ticketType)}</div>

          <div class="ticket-label">Ticket ID</div>
          <div class="ticket-value">${escapeHtml(ticketId)}</div>

          <div class="ticket-label">QR Token</div>
          <code class="ticket-code">${escapeHtml(qrToken)}</code>
        </div>

        <div class="ticket-qr">
          <div id="ticket-qr-render"></div>
        </div>
      </div>

      <div class="ticket-actions">
        <button type="button" id="copy-token-button" class="button secondary">Copy Token</button>
      </div>
    </div>
  `;

  renderQrInto("ticket-qr-render", qrToken, 220);

  document.getElementById("copy-token-button")?.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(qrToken);
      status.textContent = "QR token copied.";
    } catch {
      status.textContent = "Could not copy QR token.";
    }
  });

  renderBadge(data);
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    status.textContent = "Issuing ticket...";

    const data = await apiPost("/tickets/issue", {
      email: emailInput.value,
      display_name: nameInput.value,
      ticket_type_id: typeSelect.value,
    });

    lastIssuedTicket = data;
    status.textContent = "Ticket issued.";
    renderTicket(data);
  } catch (err) {
    status.textContent = "Error: " + err.message;
  }
});

badgeStockSelect?.addEventListener("change", () => {
  if (lastIssuedTicket) {
    renderBadge(lastIssuedTicket);
  }
});

async function init() {
  const session = await requireAuth();
  if (!session) return;

  await loadTypes();
}

init();
