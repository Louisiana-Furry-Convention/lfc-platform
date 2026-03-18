import { requireAuth } from "../auth.js";
import { apiPost } from "../api.js";

const form = document.getElementById("application-form");
const typeInput = document.getElementById("application-type");
const departmentInput = document.getElementById("department");
const experienceInput = document.getElementById("experience");
const submitButton = document.getElementById("submit-application");
const statusMessage = document.getElementById("application-status");

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
  statusMessage.classList.toggle("success", !isError && !!message);
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? "Submitting..." : "Submit Application";
}

async function init() {
  const session = await requireAuth();
  if (!session) return;
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();

  setStatus("");
  setLoading(true);

  try {
    const payload = {
      event_id: "lfc-2027",
      application_type: typeInput.value,
      data: {
        department: departmentInput.value.trim(),
        experience: experienceInput.value.trim(),
      },
    };

    await apiPost("/applications", payload);
    setStatus("Application submitted successfully.");
    form.reset();
  } catch (error) {
    setStatus(error.message || "Failed to submit application.", true);
  } finally {
    setLoading(false);
  }
});

init();
