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
