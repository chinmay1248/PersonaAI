(function bootPersonaAI() {
  /* ═══════════════════════════════════════════════════════════
     PersonaAI — Content Script (WhatsApp Web & Telegram Web)
     Fixed: stale replies, chat-switch detection, selectors
     ═══════════════════════════════════════════════════════════ */

  const state = {
    panel: null,
    statusNode: null,
    resultNode: null,
    minimized: false,
    selectedMessageId: null,
    activeChatTitle: "",
    lastGeneratedHash: "",
    observer: null,
    pollTimer: null
  };

  // ── Message listener ────────────────────────────────────────
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

  // ── Init ────────────────────────────────────────────────────
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
    document.addEventListener("click", handleDocumentClick, true);

    // Start watching for chat changes
    startChatChangeDetection();
  }

  // ── Chat Change Detection (MutationObserver + polling) ─────
  function startChatChangeDetection() {
    const platform = getPlatform();

    // Polling fallback — check the chat header title every 1.5s
    state.pollTimer = setInterval(() => {
      const currentTitle = getCurrentChatTitle();
      if (currentTitle && currentTitle !== state.activeChatTitle) {
        onChatChanged(currentTitle);
      }
    }, 1500);

    // MutationObserver on the header area for faster detection
    const observeTarget = platform === "telegram"
      ? document.querySelector(".chat-info, .topbar, header")
      : document.querySelector("header, #main header, [data-testid='conversation-header']");

    if (observeTarget) {
      state.observer = new MutationObserver(() => {
        const currentTitle = getCurrentChatTitle();
        if (currentTitle && currentTitle !== state.activeChatTitle) {
          onChatChanged(currentTitle);
        }
      });

      state.observer.observe(observeTarget, {
        childList: true,
        subtree: true,
        characterData: true
      });
    }
  }

  function onChatChanged(newTitle) {
    state.activeChatTitle = newTitle;
    state.selectedMessageId = null;
    state.lastGeneratedHash = "";
    updateSelectedMessageHighlight();

    // Clear previous results
    if (state.resultNode) {
      state.resultNode.innerHTML = "";
    }

    setStatus(`Chat: "${truncateText(newTitle, 32)}" — Click Replies or Summary.`);
  }

  function getCurrentChatTitle() {
    const platform = getPlatform();
    if (platform === "telegram") {
      return textFromFirst([
        ".chat-info .title",
        ".topbar .peer-title",
        "[class*='ChatInfo'] [class*='title']",
        "header h3",
        "header [dir='auto']"
      ]);
    }
    return textFromFirst([
      "header span[title]",
      "#main header span[title]",
      "header [data-testid='conversation-info-header-chat-title']",
      "header [role='button'] span[title]",
      "header [role='button'] span"
    ]);
  }

  // ── Panel Builder ───────────────────────────────────────────
  function buildPanel() {
    const root = document.createElement("section");
    root.className = "personaai-widget";
    root.setAttribute("aria-label", "PersonaAI assistant");
    root.innerHTML = `
      <div class="personaai-header">
        <button class="personaai-logo" type="button" title="PersonaAI">P</button>
        <div class="personaai-title">
          <strong>PersonaAI</strong>
          <span>Smart Reply Assistant</span>
        </div>
        <button class="personaai-icon-button" type="button" data-action="toggle" title="Collapse">−</button>
      </div>
      <div class="personaai-body">
        <div class="personaai-actions">
          <button class="personaai-button primary" type="button" data-action="generate">✦ Replies</button>
          <button class="personaai-button" type="button" data-action="summarize">Summary</button>
          <button class="personaai-button ghost" type="button" data-action="train">Train</button>
        </div>
        <div class="personaai-status" role="status">Select a message, or use the latest incoming one.</div>
        <div class="personaai-results"></div>
      </div>
    `;

    state.statusNode = root.querySelector(".personaai-status");
    state.resultNode = root.querySelector(".personaai-results");
    root.addEventListener("click", handlePanelClick);
    return root;
  }

  // ── Panel Click Handler ─────────────────────────────────────
  async function handlePanelClick(event) {
    const target = event.target.closest("button");
    if (!target) {
      return;
    }

    const action = target.dataset.action;
    if (action === "toggle") {
      state.minimized = !state.minimized;
      state.panel.classList.toggle("is-minimized", state.minimized);
      target.textContent = state.minimized ? "+" : "−";
      return;
    }

    if (action === "insert") {
      await insertIntoComposer(target.dataset.text || "");
      setStatus("✓ Inserted into the message box.");
      return;
    }

    if (action === "copy") {
      navigator.clipboard.writeText(target.dataset.text || "");
      setStatus("✓ Copied to clipboard.");
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
      state.selectedMessageId = null;
      updateSelectedMessageHighlight();
      await runAction("CONTENT_TRAIN", renderTraining, "Training from your messages...");
    }
  }

  // ── Run Action (FIXED: always extracts fresh context) ──────
  async function runAction(type, render, loadingText) {
    // Disable buttons during request
    const buttons = state.panel.querySelectorAll(".personaai-button");
    buttons.forEach((b) => { b.disabled = true; });

    try {
      setStatus(loadingText, true);
      state.resultNode.innerHTML = `
        <div class="personaai-loader">
          <span class="personaai-loader-text">${escapeHtml(loadingText)}</span>
        </div>
      `;

      // CRITICAL FIX: Always extract fresh context from the current DOM
      const context = extractContext();

      // Generate a hash of the context to detect staleness
      const contextHash = hashContext(context);

      const response = await chrome.runtime.sendMessage({ type, context });
      if (!response?.ok) {
        throw new Error(response?.error || "PersonaAI could not complete that action.");
      }

      // Update the last generated hash so we know this was fresh
      state.lastGeneratedHash = contextHash;

      render(response.result);
      const focusText = context.selectedMessage?.text
        ? `Selected: "${truncateText(context.selectedMessage.text, 40)}"`
        : "Using latest incoming messages.";
      setStatus(`${focusText} — ${context.chatTitle || context.platformLabel}`);
    } catch (error) {
      state.resultNode.innerHTML = "";
      setStatus(error.message || "Something went wrong.");
    } finally {
      buttons.forEach((b) => { b.disabled = false; });
    }
  }

  // ── Generate context hash to prevent stale results ─────────
  function hashContext(context) {
    const parts = [
      context.chatTitle || "",
      context.messages.length.toString(),
      (context.messages[context.messages.length - 1]?.text || "").slice(0, 100),
      context.selectedMessage?.text || ""
    ];
    return parts.join("|");
  }

  // ── Render Results ──────────────────────────────────────────
  function renderReplies(result) {
    const suggestions = result?.suggestions || [];
    if (!suggestions.length) {
      state.resultNode.innerHTML = `<p class="personaai-empty">No suggestions returned. Try selecting a different message.</p>`;
      return;
    }

    const moodBadge = result?.detected_mood ? `<span class="personaai-mood-badge">${escapeHtml(result.detected_mood)}</span>` : "";

    state.resultNode.innerHTML = suggestions.map((suggestion, i) => `
      <article class="personaai-result" style="animation-delay: ${i * 0.08}s">
        ${moodBadge}
        <p>${escapeHtml(suggestion.text)}</p>
        <div class="personaai-result-actions">
          <button class="personaai-button small" type="button" data-action="insert" data-text="${escapeAttr(suggestion.text)}">↗ Use</button>
          <button class="personaai-button ghost small" type="button" data-action="copy" data-text="${escapeAttr(suggestion.text)}">📋 Copy</button>
        </div>
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
        <h3>Tone Updated</h3>
        <p>Profile accuracy: ${score}%</p>
      </article>
    `;
  }

  // ── Context Extraction (FIXED: always reads fresh DOM) ─────
  function extractContext() {
    const platform = getPlatform();
    const extractor = platform === "telegram" ? extractTelegram : extractWhatsApp;
    const context = extractor();

    // Update active chat title (for change detection)
    const currentTitle = context.chatTitle || "";
    if (currentTitle && currentTitle !== state.activeChatTitle) {
      state.activeChatTitle = currentTitle;
      state.selectedMessageId = null;
      updateSelectedMessageHighlight();
    }

    const selectedIndex = findSelectedMessageIndex(context.messages);
    const anchoredMessages = selectedIndex >= 0 ? context.messages.slice(0, selectedIndex + 1) : context.messages;
    const selectedMessage = selectedIndex >= 0 ? anchoredMessages[selectedIndex] : null;

    return {
      platform,
      platformLabel: platform === "telegram" ? "Telegram Web" : "WhatsApp Web",
      url: location.href,
      chatTitle: context.chatTitle,
      selectedMessage,
      messages: anchoredMessages.slice(-50)
    };
  }

  // ── WhatsApp Extraction (FIXED: robust selectors) ──────────
  function extractWhatsApp() {
    const panel = document.querySelector(
      "#main [data-testid='conversation-panel-messages'], #main [role='application'], #main"
    );
    const title = textFromFirst([
      "#main header span[title]",
      "header span[title]",
      "header [data-testid='conversation-info-header-chat-title']",
      "header [role='button'] span[title]",
      "header [role='button'] span"
    ]);

    let nodes = getWhatsAppMessageNodes(panel);

    return {
      chatTitle: title || "WhatsApp chat",
      messages: normalizeExtractedMessages(nodes.map((node, index) => extractWhatsAppMessage(node, title, index)))
    };
  }

  function getWhatsAppMessageNodes(panel) {
    const root = panel || document;
    const selectorGroups = [
      "[data-testid='msg-container']",
      ".message-in, .message-out",
      "[data-id]",
      "[data-testid*='msg-']",
      "[role='row']"
    ];

    for (const selector of selectorGroups) {
      const found = [...root.querySelectorAll(selector)].filter((node) => isLikelyWhatsAppMessageNode(node, panel));
      if (found.length > 0) {
        return getUniqueMessageNodes(found);
      }
    }

    const fallbackNodes = [
      ...root.querySelectorAll("span.selectable-text, span.copyable-text, span[dir='auto'], span[dir='ltr']")
    ]
      .map((node) => node.closest(
        "[data-testid='msg-container'], .message-in, .message-out, [data-id], [data-testid*='msg-'], [role='row']"
      ))
      .filter((node) => isLikelyWhatsAppMessageNode(node, panel));

    return getUniqueMessageNodes(fallbackNodes);
  }

  function isLikelyWhatsAppMessageNode(node, panel) {
    if (!(node instanceof Element)) {
      return false;
    }
    if (panel && !panel.contains(node)) {
      return false;
    }
    if (!isVisible(node)) {
      return false;
    }

    const text = cleanText(readMessageText(node, [
      "span.selectable-text.copyable-text",
      "span.selectable-text",
      "span.copyable-text",
      "span[dir='ltr']",
      "span[dir='auto']"
    ]));

    if (!text) {
      return false;
    }

    const ariaLabel = String(node.getAttribute("aria-label") || "").toLowerCase();
    if (ariaLabel.includes("unread") || ariaLabel.includes("typing")) {
      return false;
    }

    return true;
  }

  // ── Telegram Extraction ────────────────────────────────────
  function extractTelegram() {
    const title = textFromFirst([
      ".chat-info .title",
      ".topbar .peer-title",
      "[class*='ChatInfo'] [class*='title']",
      "header h3",
      "header [dir='auto']"
    ]);
    const nodes = getUniqueMessageNodes([
      ...document.querySelectorAll(".Message, .message, .bubble, [class*='message-list'] [class*='message']")
    ]);

    return {
      chatTitle: title || "Telegram chat",
      messages: normalizeExtractedMessages(nodes.map((node, index) => extractTelegramMessage(node, title, index)))
    };
  }

  // ── Message Normalization (FIXED: better dedup) ────────────
  function normalizeExtractedMessages(messages) {
    const seen = new Set();
    return messages
      .map((message) => ({
        id: message.id || "",
        role: message.role === "self" ? "self" : "contact",
        text: cleanText(message.text)
      }))
      .filter((message) => {
        if (!message.text || message.text.length < 1) {
          return false;
        }
        // Deduplicate by text content (role-independent) to catch duplicate extractions
        const dedupKey = message.text.toLowerCase().trim();
        if (seen.has(dedupKey)) {
          return false;
        }
        seen.add(dedupKey);
        return true;
      });
  }

  // ── Read Message Text (FIXED: prevent duplicate text) ──────
  function readMessageText(node, selectors) {
    // Try selectors in priority order — return the first one that gives content
    for (const selector of selectors) {
      const elements = node.querySelectorAll(selector);
      if (elements.length === 0) {
        continue;
      }

      const parts = [];
      const seen = new Set();

      elements.forEach((child) => {
        // Skip if this element is nested inside another matched element
        let isNested = false;
        for (const otherSelector of selectors) {
          if (otherSelector === selector) continue;
          if (child.closest(otherSelector) && child.closest(otherSelector) !== child) {
            const parent = child.closest(otherSelector);
            if (node.contains(parent) && parent.contains(child) && parent !== child) {
              isNested = true;
              break;
            }
          }
        }
        if (isNested) return;

        const text = cleanText(child.innerText || child.textContent || "");
        if (!text || seen.has(text)) {
          return;
        }
        seen.add(text);
        parts.push(text);
      });

      if (parts.length > 0) {
        return parts.join(" ");
      }
    }

    // Last-resort fallback
    return cleanText(node.innerText || node.textContent || "");
  }

  // ── Document Click (Message Selection) ─────────────────────
  function handleDocumentClick(event) {
    if (state.panel?.contains(event.target)) {
      return;
    }

    const messageNode = findMessageNode(event.target);
    if (!messageNode) {
      return;
    }

    const message = extractMessageFromNode(messageNode);
    if (!message?.id || !message.text) {
      return;
    }

    if (message.role === "self") {
      setStatus("Select a message from the other person to reply to.");
      return;
    }

    if (state.selectedMessageId === message.id) {
      state.selectedMessageId = null;
      updateSelectedMessageHighlight();
      setStatus("Selection cleared. Using the latest incoming message.");
      return;
    }

    state.selectedMessageId = message.id;
    updateSelectedMessageHighlight();
    setStatus(`Selected: "${truncateText(message.text, 44)}"`);
  }

  function findMessageNode(target) {
    const element = target instanceof Element ? target : null;
    if (!element) {
      return null;
    }

    return element.closest(
      "[data-testid='msg-container'], .message-in, .message-out, [data-id], [data-testid*='msg-'], [role='row'], .Message, .message, .bubble, [class*='message-list'] [class*='message']"
    );
  }

  function extractMessageFromNode(node) {
    const existingId = node.dataset.personaaiMessageId || "";
    const platform = getPlatform();
    if (platform === "telegram") {
      return {
        id: existingId || getMessageId(node, "tg", textFromFirst([".chat-info .title", ".topbar .peer-title", "header h3"]), -1),
        role: isOutgoingTelegramNode(node) ? "self" : "contact",
        text: cleanText(readMessageText(node, [
          ".text-content",
          ".message-content",
          ".TranslatableMessage",
          "[dir='auto']",
          "[dir='ltr']"
        ]))
      };
    }

    return {
      id: existingId || getMessageId(node, "wa", textFromFirst(["header span[title]", "header [data-testid='conversation-info-header-chat-title']"]), -1),
      role: isOutgoingWhatsAppNode(node) ? "self" : "contact",
      text: cleanText(readMessageText(node, [
        "span.selectable-text.copyable-text",
        "span.selectable-text",
        "span[dir='ltr']",
        "span[dir='auto']"
      ]))
    };
  }

  // ── WhatsApp Message Extraction (FIXED: better role detection) ──
  function extractWhatsAppMessage(node, chatTitle, index) {
    const id = getMessageId(node, "wa", chatTitle, index);
    node.dataset.personaaiMessageId = id;
    return {
      id,
      role: isOutgoingWhatsAppNode(node) ? "self" : "contact",
      text: readMessageText(node, [
        "span.selectable-text.copyable-text",
        "span.selectable-text",
        "span[dir='ltr']",
        "span[dir='auto']"
      ])
    };
  }

  // ── Improved outgoing detection for WhatsApp ───────────────
  function isOutgoingWhatsAppNode(node) {
    // Check class-based detection (most common)
    if (node.closest(".message-out")) {
      return true;
    }
    // Check data-id attribute — self messages in WA start with "true_"
    const dataId = node.getAttribute("data-id") || "";
    if (dataId.startsWith("true_")) {
      return true;
    }
    // Check parent containers
    const className = String(node.className || "").toLowerCase();
    if (className.includes("message-out") || className.includes("msg-out")) {
      return true;
    }
    // Check test-id based detection
    const testId = node.getAttribute("data-testid") || "";
    if (testId.includes("msg-self") || testId.includes("out")) {
      return true;
    }

    // Some WhatsApp builds keep direction markers on descendants/ancestors
    const outgoingMarker = node.querySelector("[data-testid*='out'], [aria-label*='You:'], [data-icon='msg-dblcheck'], [data-icon='msg-check']");
    if (outgoingMarker) {
      return true;
    }

    // Fallback heuristic: sent messages usually render on the right side
    const bubble = node.querySelector("[data-testid='msg-container'], .copyable-area, [data-id], span.selectable-text, span.copyable-text") || node;
    const bubbleRect = bubble.getBoundingClientRect();
    const parentRect = (node.parentElement || node).getBoundingClientRect();
    if (bubbleRect.width > 0 && parentRect.width > 0) {
      const bubbleMidpoint = bubbleRect.left + (bubbleRect.width / 2);
      const parentMidpoint = parentRect.left + (parentRect.width / 2);
      if (bubbleMidpoint > parentMidpoint) {
        return true;
      }
    }

    return false;
  }

  function extractTelegramMessage(node, chatTitle, index) {
    const id = getMessageId(node, "tg", chatTitle, index);
    node.dataset.personaaiMessageId = id;
    return {
      id,
      role: isOutgoingTelegramNode(node) ? "self" : "contact",
      text: readMessageText(node, [
        ".text-content",
        ".message-content",
        ".TranslatableMessage",
        "[dir='auto']",
        "[dir='ltr']"
      ])
    };
  }

  function getMessageId(node, prefix, chatTitle, index) {
    const explicitId = node.getAttribute("data-id")
      || node.getAttribute("data-message-id")
      || node.id
      || node.getAttribute("data-testid");
    if (explicitId) {
      return `${prefix}:${explicitId}`;
    }

    const text = cleanText(node.innerText || node.textContent || "");
    return `${prefix}:${chatTitle || "chat"}:${index}:${text.slice(0, 80)}`;
  }

  function getUniqueMessageNodes(nodes) {
    return nodes.filter((node, index, list) => list.indexOf(node) === index);
  }

  function findSelectedMessageIndex(messages) {
    if (!state.selectedMessageId) {
      return -1;
    }
    return messages.findIndex((message) => message.id === state.selectedMessageId);
  }

  function updateSelectedMessageHighlight() {
    const nodes = document.querySelectorAll(
      "[data-testid='msg-container'], .message-in, .message-out, [data-id], [data-testid*='msg-'], [role='row'], .Message, .message, .bubble, [class*='message-list'] [class*='message']"
    );

    nodes.forEach((node) => {
      const message = extractMessageFromNode(node);
      node.classList.toggle("personaai-selected-message", Boolean(message?.id) && message.id === state.selectedMessageId);
    });
  }

  function isOutgoingTelegramNode(node) {
    const className = String(node.className || "").toLowerCase();
    return className.includes("own")
      || className.includes("out")
      || className.includes("is-sent")
      || Boolean(node.closest(".own, .outgoing, .is-out, .is-sent"));
  }

  function getPlatform() {
    return location.hostname.includes("telegram") ? "telegram" : "whatsapp";
  }

  function textFromFirst(selectors) {
    for (const selector of selectors) {
      try {
        const node = document.querySelector(selector);
        const text = cleanText(node?.innerText || node?.textContent || node?.getAttribute?.("title") || "");
        if (text) {
          return text;
        }
      } catch {
        // Invalid selector — skip
      }
    }
    return "";
  }

  // ── Insert Into Composer (FIXED: more robust) ──────────────
  async function insertIntoComposer(text) {
    const replyText = cleanReplyText(text);
    if (!replyText) {
      throw new Error("No reply text to insert.");
    }

    const composer = findComposer();
    if (!composer) {
      throw new Error("Could not find the message box. Make sure a chat is open.");
    }

    composer.focus();

    // Small delay to let WhatsApp register the focus
    await new Promise((resolve) => setTimeout(resolve, 100));

    if ("value" in composer && composer.tagName === "TEXTAREA") {
      composer.value = replyText;
      composer.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: replyText }));
      return;
    }

    // For contenteditable divs (WhatsApp uses these)
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(composer);
    selection.removeAllRanges();
    selection.addRange(range);

    // Clear existing content first
    document.execCommand("selectAll", false, null);
    document.execCommand("insertText", false, replyText);

    // Dispatch input event for WhatsApp to detect the change
    composer.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: replyText }));
  }

  function findComposer() {
    const selectors = [
      "footer div[contenteditable='true'][role='textbox']",
      "#main footer div[contenteditable='true']",
      "footer div[contenteditable='true']",
      "[contenteditable='true'][role='textbox']",
      ".input-message-input[contenteditable='true']",
      "div[contenteditable='true'][data-tab]",
      "div[contenteditable='true']",
      "textarea"
    ];

    for (const selector of selectors) {
      try {
        const nodes = [...document.querySelectorAll(selector)];
        const node = nodes.reverse().find((candidate) => isVisible(candidate));
        if (node) {
          return node;
        }
      } catch {
        // Invalid selector — skip
      }
    }
    return null;
  }

  function isVisible(node) {
    const rect = node.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }

  // ── Utility ─────────────────────────────────────────────────
  function setStatus(text, isLoading = false) {
    if (state.statusNode) {
      state.statusNode.textContent = text;
      state.statusNode.classList.toggle("is-loading", isLoading);
    }
  }

  function cleanText(text) {
    return String(text || "")
      .replace(/\b\d{1,2}:\d{2}\s?(AM|PM)?\b/gi, "")  // timestamps
      .replace(/\b(yesterday|today)\b/gi, "")            // day labels
      .replace(/\s+/g, " ")
      .trim();
  }

  function cleanReplyText(text) {
    return String(text || "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function truncateText(text, limit) {
    const value = String(text || "");
    return value.length > limit ? `${value.slice(0, limit - 1)}…` : value;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
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
})();
