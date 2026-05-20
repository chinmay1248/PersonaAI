(function bootPersonaAI() {
  const state = {
    panel: null,
    statusNode: null,
    resultNode: null,
    minimized: false
  };

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message?.type === "EXTRACT_CONTEXT") {
      try {
        sendResponse({ ok: true, context: extractContext() });
      } catch (error) {
        sendResponse({ ok: false, error: error.message || "Could not read this chat." });
      }
      return true;
    }

    if (message?.type === "INSERT_TEXT") {
      insertIntoComposer(message.text || "")
        .then(() => sendResponse({ ok: true }))
        .catch((error) => sendResponse({ ok: false, error: error.message || "Could not insert the reply." }));
      return true;
    }

    return false;
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }

  function init() {
    if (state.panel) {
      return;
    }

    state.panel = buildPanel();
    document.documentElement.appendChild(state.panel);
  }

  function buildPanel() {
    const root = document.createElement("section");
    root.className = "personaai-widget";
    root.setAttribute("aria-label", "PersonaAI assistant");
    root.innerHTML = `
      <div class="personaai-header">
        <button class="personaai-logo" type="button" title="PersonaAI">P</button>
        <div class="personaai-title">
          <strong>PersonaAI</strong>
          <span>Browser reply assistant</span>
        </div>
        <button class="personaai-icon-button" type="button" data-action="toggle" title="Collapse">-</button>
      </div>
      <div class="personaai-body">
        <div class="personaai-actions">
          <button class="personaai-button primary" type="button" data-action="generate">Replies</button>
          <button class="personaai-button" type="button" data-action="summarize">Summary</button>
          <button class="personaai-button ghost" type="button" data-action="train">Train</button>
        </div>
        <div class="personaai-status" role="status">Ready on this chat.</div>
        <div class="personaai-results"></div>
      </div>
    `;

    state.statusNode = root.querySelector(".personaai-status");
    state.resultNode = root.querySelector(".personaai-results");
    root.addEventListener("click", handlePanelClick);
    return root;
  }

  async function handlePanelClick(event) {
    const target = event.target.closest("button");
    if (!target) {
      return;
    }