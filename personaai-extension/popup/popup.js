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
}

async function submitAuth(type) {
  await withBusy(async () => {
    const response = await sendMessage({
      type,
      credentials: {
        email: elements.emailInput.value.trim(),
        password: elements.passwordInput.value
      }
    });

    applyState(response);
    renderInfo("Signed in. Open a chat and generate replies.");
  });
}

async function refreshState() {
  const state = await sendMessage({ type: "GET_STATE" });
  applyState(state);
}

function applyState(state) {
  elements.authPanel.classList.toggle("is-hidden", state.authenticated);
  elements.actionPanel.classList.toggle("is-hidden", !state.authenticated);
  elements.statusText.textContent = state.authenticated ? "Signed in" : "Sign in to start";
  elements.apiBaseUrlInput.value = state.settings.apiBaseUrl || "";
  elements.suggestionCountInput.value = state.settings.suggestionCount || 3;
  elements.personalityInput.value = state.settings.personalityMode || "funny";
}

async function runAction(type, render, loadingText) {
  await withBusy(async () => {
    renderInfo(loadingText);
    const response = await sendMessage({ type });
    render(response.result);
  });
}

function renderReplies(result) {
  const suggestions = result?.suggestions || [];
  if (!suggestions.length) {
    renderInfo("No suggestions returned.");
    return;
  }

  elements.results.innerHTML = suggestions.map((suggestion) => `
    <article class="result-item">
      <h2>Reply ${suggestion.rank || ""}</h2>
      <p>${escapeHtml(suggestion.text)}</p>
      <button class="button primary" type="button" data-insert-text="${escapeAttr(suggestion.text)}">Use in chat</button>
    </article>
  `).join("");
}

function renderSummary(result) {
  const items = result?.action_items || [];
  elements.results.innerHTML = `
    <article class="result-item">
      <h2>Summary</h2>
      <p>${escapeHtml(result?.summary || "No summary returned.")}</p>
      ${items.length ? `<h2>Action items</h2><ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
    </article>
  `;
}

function renderTraining(result) {
  const score = Math.round(Number(result?.accuracy_score || 0) * 100);
  elements.results.innerHTML = `
    <article class="result-item">
      <h2>Tone updated</h2>
      <p>Profile accuracy: ${score}%</p>
    </article>
  `;
}

function renderInfo(message) {
  elements.results.innerHTML = `<p class="empty">${escapeHtml(message)}</p>`;
}

async function withBusy(task) {
  setBusy(true);
  try {
    await task();
  } catch (error) {
    renderInfo(error.message || "Something went wrong.");
  } finally {
    setBusy(false);
  }
}

function setBusy(busy) {
  document.querySelectorAll("button").forEach((button) => {
    button.disabled = busy;
  });
}

async function sendMessage(message) {
  const response = await chrome.runtime.sendMessage(message);
  if (!response?.ok) {
    throw new Error(response?.error || "PersonaAI could not complete that action.");
  }
  return response;
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#96;");
}
