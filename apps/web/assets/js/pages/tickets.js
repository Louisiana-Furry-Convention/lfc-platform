import { requireAuth } from "../auth.js";
import { apiGet, apiPost } from "../api.js";

const form = document.getElementById("ticket-form");
const emailInput = document.getElementById("email");
const nameInput = document.getElementById("display-name");
const typeSelect = document.getElementById("ticket-type");
const status = document.getElementById("status");
const qrOutput = document.getElementById("qr-output");

async function loadTypes() {
  const types = await apiGet("/admin/ticket_types");

  typeSelect.innerHTML = types.map(t => `
    <option value="${t.id}">
      ${t.name} ($${(t.price_cents/100).toFixed(2)})
    </option>
  `).join("");
}

function renderQR(token) {
  qrOutput.innerHTML = `
    <p><strong>QR Token:</strong></p>
    <code>${token}</code>
    <p>(QR image later)</p>
  `;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    status.textContent = "Issuing ticket...";

    const data = await apiPost("/tickets/issue", {
      email: emailInput.value,
      display_name: nameInput.value,
      ticket_type_id: typeSelect.value
    });

    status.textContent = "Ticket issued.";
    renderQR(data.qr_token);

  } catch (err) {
    status.textContent = "Error: " + err.message;
  }
});

async function init() {
  const session = await requireAuth();
  if (!session) return;

  await loadTypes();
}

init();
