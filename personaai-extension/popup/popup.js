const elements = {
  statusText: document.querySelector("#statusText"),
  authPanel: document.querySelector("#authPanel"),
  actionPanel: document.querySelector("#actionPanel"),
  authForm: document.querySelector("#authForm"),
  registerButton: document.querySelector("#registerButton"),
  logoutButton: document.querySelector("#logoutButton"),
  replyButton: document.querySelector("#replyButton"),
  summaryButton: document.querySelector("#summaryButton"),
  trainButton: document.querySelector("#trainButton"),
  settingsForm: document.querySelector("#settingsForm"),
  apiBaseUrlInput: document.querySelector("#apiBaseUrlInput"),
  suggestionCountInput: document.querySelector("#suggestionCountInput"),
  personalityInput: document.querySelector("#personalityInput"),
  emailInput: document.querySelector("#emailInput"),
  passwordInput: document.querySelector("#passwordInput"),
  results: document.querySelector("#results")
};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  bindEvents();
  await refreshState();
}

function bindEvents() {
  elements.authForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitAuth("LOGIN");
  });

  elements.registerButton.addEventListener("click", async () => {
    await submitAuth("REGISTER");
  });

  elements.logoutButton.addEventListener("click", async () => {
    await sendMessage({ type: "LOGOUT" });
    renderInfo("Signed out.");
    await refreshState();
  });

  elements.replyButton.addEventListener("click", async () => {
    await runAction("GENERATE_FOR_ACTIVE_TAB", renderReplies, "Generating replies...");
  });

  elements.summaryButton.addEventListener("click", async () => {
    await runAction("SUMMARIZE_ACTIVE_TAB", renderSummary, "Summarizing visible chat...");
  });

  elements.trainButton.addEventListener("click", async () => {
    await runAction("TRAIN_FROM_ACTIVE_TAB", renderTraining, "Training tone...");
  });

  elements.settingsForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const response = await sendMessage({
      type: "SAVE_SETTINGS",
      settings: {
        apiBaseUrl: elements.apiBaseUrlInput.value,
        suggestionCount: Number(elements.suggestionCountInput.value),
        personalityMode: elements.personalityInput.value
      }
    });

    applyState(response);
    renderInfo("Settings saved.");
  });

  elements.results.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-insert-text]");
    if (!button) {
      return;
    }

    await withBusy(async () => {
      await sendMessage({ type: "INSERT_IN_ACTIVE_TAB", text: button.dataset.insertText || "" });
      renderInfo("Inserted into the active chat.");
    });
  });