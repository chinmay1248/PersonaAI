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

    const action = target.dataset.action;
    if (action === "toggle") {
      state.minimized = !state.minimized;
      state.panel.classList.toggle("is-minimized", state.minimized);
      target.textContent = state.minimized ? "+" : "-";
      return;
    }

    if (action === "insert") {
      await insertIntoComposer(target.dataset.text || "");
      setStatus("Inserted into the message box.");
      return;
    }

    if (action === "generate") {
      await runAction("CONTENT_GENERATE_REPLY", renderReplies, "Generating replies...");
      return;
    }

    if (action === "summarize") {
      await runAction("CONTENT_SUMMARIZE", renderSummary, "Summarizing chat...");
      return;
    }

    if (action === "train") {
      await runAction("CONTENT_TRAIN", renderTraining, "Training from your visible outgoing messages...");
    }
  }

  async function runAction(type, render, loadingText) {
    try {
      setStatus(loadingText);
      state.resultNode.innerHTML = "";
      const context = extractContext();
      const response = await chrome.runtime.sendMessage({ type, context });
      if (!response?.ok) {
        throw new Error(response?.error || "PersonaAI could not complete that action.");
      }

      render(response.result);
      setStatus(`Using ${context.chatTitle || context.platformLabel}.`);
    } catch (error) {
      setStatus(error.message || "Something went wrong.");
    }
  }

  function renderReplies(result) {
    const suggestions = result?.suggestions || [];
    if (!suggestions.length) {
      state.resultNode.innerHTML = `<p class="personaai-empty">No suggestions returned.</p>`;
      return;
    }

    state.resultNode.innerHTML = suggestions.map((suggestion) => `
      <article class="personaai-result">
        <p>${escapeHtml(suggestion.text)}</p>
        <button class="personaai-button small" type="button" data-action="insert" data-text="${escapeAttr(suggestion.text)}">Use</button>
      </article>
    `).join("");
  }

  function renderSummary(result) {
    const items = result?.action_items || [];
    state.resultNode.innerHTML = `
      <article class="personaai-result">
        <h3>Summary</h3>
        <p>${escapeHtml(result?.summary || "No summary returned.")}</p>
        ${items.length ? `<h3>Action items</h3><ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
      </article>
    `;
  }

  function renderTraining(result) {
    const score = Math.round(Number(result?.accuracy_score || 0) * 100);
    state.resultNode.innerHTML = `
      <article class="personaai-result">
        <h3>Tone updated</h3>
        <p>Profile accuracy: ${score}%</p>
      </article>
    `;
  }

  function extractContext() {
    const platform = getPlatform();
    const extractor = platform === "telegram" ? extractTelegram : extractWhatsApp;
    const context = extractor();
    return {
      platform,
      platformLabel: platform === "telegram" ? "Telegram Web" : "WhatsApp Web",
      url: location.href,
      chatTitle: context.chatTitle,
      messages: context.messages.slice(-50)
    };
  }

  function extractWhatsApp() {
    const title = textFromFirst([
      "header span[title]",
      "header [data-testid='conversation-info-header-chat-title']",
      "header [role='button'] span"
    ]);

    const nodes = [
      ...document.querySelectorAll("[data-testid='msg-container']"),
      ...document.querySelectorAll(".message-in, .message-out")
    ];

    return {
      chatTitle: title || "WhatsApp chat",
      messages: normalizeExtractedMessages(nodes.map((node) => ({
        role: node.closest(".message-out") ? "self" : "contact",
        text: readMessageText(node, [
          "span.selectable-text",
          "[data-pre-plain-text]",
          "span[dir='ltr']",
          "span[dir='auto']"