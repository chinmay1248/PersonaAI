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