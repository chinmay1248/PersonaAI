const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/v1";
const SUPPORTED_HOSTS = new Set(["web.whatsapp.com", "web.telegram.org", "k.telegram.org", "a.telegram.org"]);

const DEFAULT_SETTINGS = {
  apiBaseUrl: DEFAULT_API_BASE_URL,
  suggestionCount: 3,
  personalityMode: "funny"
};

chrome.runtime.onInstalled.addListener(async () => {
  const { personaAISettings } = await storageGet(["personaAISettings"]);
  if (!personaAISettings) {
    await storageSet({ personaAISettings: DEFAULT_SETTINGS });
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender)
    .then((payload) => sendResponse({ ok: true, ...payload }))
    .catch((error) => sendResponse({ ok: false, error: normalizeError(error) }));

  return true;
});

async function handleMessage(message, sender) {
  switch (message?.type) {
    case "GET_STATE":
      return getPublicState();
    case "SAVE_SETTINGS":
      return saveSettings(message.settings || {});
    case "HEALTH_CHECK":
      return { result: await healthCheck() };
    case "LOGIN":
      return login(message.credentials || {});
    case "REGISTER":
      return register(message.credentials || {});
    case "LOGOUT":
      return logout();
    case "GET_ACTIVE_CONTEXT":
      return { context: await getActiveContext() };
    case "GENERATE_FOR_ACTIVE_TAB":
      return { result: await generateForActiveTab(message.options || {}) };
    case "SUMMARIZE_ACTIVE_TAB":
      return { result: await summarizeActiveTab() };
    case "TRAIN_FROM_ACTIVE_TAB":
      return { result: await trainFromActiveTab() };
    case "INSERT_IN_ACTIVE_TAB":
      return insertInActiveTab(message.text || "");
    case "CONTENT_GENERATE_REPLY":
      return { result: await generateFromContext(message.context, message.options || {}) };
    case "CONTENT_SUMMARIZE":
      return { result: await summarizeFromContext(message.context) };
    case "CONTENT_TRAIN":
      return { result: await trainFromContext(message.context) };
    default:
      throw new Error("Unknown PersonaAI action.");
  }
}

async function getPublicState() {
  const { personaAISettings, accessToken, userId } = await storageGet([
    "personaAISettings",
    "accessToken",
    "userId"
  ]);

  return {
    settings: { ...DEFAULT_SETTINGS, ...(personaAISettings || {}) },
    authenticated: Boolean(accessToken),
    userId: userId || null
  };
}

async function saveSettings(nextSettings) {
  const current = await getSettings();
  const settings = {
    ...current,
    ...nextSettings,
    apiBaseUrl: normalizeBaseUrl(nextSettings.apiBaseUrl || current.apiBaseUrl),
    suggestionCount: clamp(Number(nextSettings.suggestionCount || current.suggestionCount), 1, 5)
  };

  await storageSet({ personaAISettings: settings });
  return { settings };
}

async function login(credentials) {
  const response = await apiFetch("/auth/login", {
    method: "POST",
    body: credentials
  }, { auth: false });

  await persistAuth(response);
  return getPublicState();
}

async function register(credentials) {
  const response = await apiFetch("/auth/register", {
    method: "POST",
    body: credentials
  }, { auth: false });

  await persistAuth(response);
  return getPublicState();
}

async function logout() {
  await storageRemove(["accessToken", "refreshToken", "userId"]);
  return getPublicState();
}

async function persistAuth(response) {
  await storageSet({
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    userId: response.user_id
  });
}

async function generateForActiveTab(options) {
  const context = await getActiveContext();
  return generateFromContext(context, options);
}

async function summarizeActiveTab() {
  const context = await getActiveContext();
  return summarizeFromContext(context);
}

async function trainFromActiveTab() {
  const context = await getActiveContext();
  return trainFromContext(context);
}

async function generateFromContext(context, options = {}) {
  assertUsableContext(context);
  const settings = await getSettings();
  const chatConfig = await ensureChatConfig(context, settings);
  const messages = normalizeMessages(context.messages);
  const selectedMessage = normalizeSelectedMessage(context.selectedMessage);

  if (selectedMessage?.role === "self") {
    throw new Error("Select a message from the other person to generate a reply.");
  }

  const incomingMessages = selectedMessage?.text
    ? [selectedMessage]
    : selectLatestIncomingMessages(messages);
  const fallbackIncoming = messages.slice(-3);
  const conversationHistory = messages.slice(-50).map((message) => ({
    role: message.role === "self" ? "user" : "contact",
    text: message.text
  }));

  return apiFetch("/ai/generate-reply", {
    method: "POST",
    body: {
      chat_config_id: chatConfig.id,
      incoming_messages: (incomingMessages.length ? incomingMessages : fallbackIncoming).map((message) => message.text),
      conversation_history: conversationHistory,
      count: clamp(Number(options.count || settings.suggestionCount), 1, 5)
    }
  });
}

async function summarizeFromContext(context) {
  assertUsableContext(context);
  const messages = normalizeMessages(context.messages).map((message) => message.text).slice(-40);
  if (!messages.length) {
    throw new Error("No visible chat messages found to summarize.");
  }

  try {
    const result = await apiFetch("/ai/summarize", {
      method: "POST",
      body: { messages }
    });

    if (isUsableSummary(result)) {
      return result;
    }
  } catch (error) {
    console.warn("PersonaAI summarize fallback:", error);
  }

  return buildLocalSummary(messages);
}

async function trainFromContext(context) {
  assertUsableContext(context);
  const source = context.platform === "telegram" ? "telegram" : "whatsapp";
  const ownMessages = normalizeMessages(context.messages)
    .filter((message) => message.role === "self")
    .map((message) => message.text)
    .slice(-50);

  if (!ownMessages.length) {
    throw new Error("No outgoing messages found to train from.");
  }

  // 1. Train global tone
  const globalTrainPromise = apiFetch("/tone/train-from-messages", {
    method: "POST",
    body: { source, messages: ownMessages }
  });

  // 2. Train chat-specific tone
  let chatTrainPromise = Promise.resolve();
  try {
    const settings = await getSettings();
    const chatConfig = await ensureChatConfig(context, settings);
    if (chatConfig && chatConfig.id) {
      chatTrainPromise = apiFetch(`/chats/${chatConfig.id}/retrain-tone`, {
        method: "POST"
      });
    }
  } catch (err) {
    console.warn("Could not trigger chat-specific tone retraining:", err);
  }

  const [globalResult] = await Promise.all([globalTrainPromise, chatTrainPromise]);
  return globalResult;
}

async function ensureChatConfig(context, settings) {
  const chatLabel = sanitizeLabel(context.chatTitle || context.platformLabel || "Browser Chat");
  const chatType = context.platform || "browser";
  const configs = await apiFetch("/chats/config");
  const existing = configs.find((config) => (
    config.chat_label.toLowerCase() === chatLabel.toLowerCase()
    && (config.chat_type || "browser") === chatType
  ));

  if (existing) {
    return existing;
  }

  return apiFetch("/chats/config", {
    method: "POST",
    body: {
      chat_label: chatLabel,
      chat_type: chatType,
      personality_mode: settings.personalityMode || null,
      auto_reply_mode: "OFF",
      ai_enabled: true,
      is_private: false
    }
  });
}

async function getActiveContext() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id || !isSupportedUrl(tab.url)) {
    throw new Error("Open WhatsApp Web or Telegram Web, then try again.");
  }

  const response = await sendTabMessage(tab.id, { type: "EXTRACT_CONTEXT" }, { ensureInjected: true });
  if (!response?.ok) {
    throw new Error(response?.error || "Could not read the active chat.");
  }

  return response.context;
}

async function insertInActiveTab(text) {
  if (!text.trim()) {
    throw new Error("No reply text to insert.");
  }

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id || !isSupportedUrl(tab.url)) {
    throw new Error("Open WhatsApp Web or Telegram Web, then try again.");
  }

  const response = await sendTabMessage(tab.id, { type: "INSERT_TEXT", text }, { ensureInjected: true });
  if (!response?.ok) {
    throw new Error(response?.error || "Could not insert the reply.");
  }

  return { inserted: true };
}

async function sendTabMessage(tabId, message, options = {}) {
  try {
    return await chrome.tabs.sendMessage(tabId, message);
  } catch (error) {
    if (!options.ensureInjected || !shouldRetryAfterInjection(error)) {
      throw error;
    }

    await ensureContentScriptInjected(tabId);
    return chrome.tabs.sendMessage(tabId, message);
  }
}

function shouldRetryAfterInjection(error) {
  const message = String(error?.message || "").toLowerCase();
  return message.includes("receiving end does not exist")
    || message.includes("could not establish connection")
    || message.includes("message port closed");
}

async function ensureContentScriptInjected(tabId) {
  await chrome.scripting.insertCSS({
    target: { tabId },
    files: ["content/content.css"]
  }).catch(() => {});

  await chrome.scripting.executeScript({
    target: { tabId },
    files: ["content/content.js"]
  });
}

async function healthCheck() {
  return apiFetch("/health", { method: "GET" }, { auth: false });
}

async function apiFetch(path, options = {}, fetchOptions = {}) {
  const settings = await getSettings();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const auth = fetchOptions.auth !== false;

  if (auth) {
    const { accessToken } = await storageGet(["accessToken"]);
    if (!accessToken) {
      throw new Error("Sign in to PersonaAI first.");
    }
    headers.Authorization = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${settings.apiBaseUrl}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined
  });

  if (response.status === 401 && auth && fetchOptions.retry !== false) {
    await refreshAccessToken();
    return apiFetch(path, options, { ...fetchOptions, retry: false });
  }

  const text = await response.text();
  const payload = parseResponseBody(text);
  if (!response.ok) {
    throw new Error(payload?.detail || payload?.message || `PersonaAI API error ${response.status}`);
  }

  return payload;
}

async function refreshAccessToken() {
  const { refreshToken } = await storageGet(["refreshToken"]);
  if (!refreshToken) {
    throw new Error("Your session expired. Sign in again.");
  }

  const response = await apiFetch("/auth/refresh", {
    method: "POST",
    body: { refresh_token: refreshToken }
  }, { auth: false });

  await storageSet({ accessToken: response.access_token });
}

async function getSettings() {
  const { personaAISettings } = await storageGet(["personaAISettings"]);
  return {
    ...DEFAULT_SETTINGS,
    ...(personaAISettings || {}),
    apiBaseUrl: normalizeBaseUrl(personaAISettings?.apiBaseUrl || DEFAULT_API_BASE_URL)
  };
}

function assertUsableContext(context) {
  if (!context || !Array.isArray(context.messages)) {
    throw new Error("Could not read this chat.");
  }
  if (!context.messages.length) {
    throw new Error("No visible messages found in this chat.");
  }
}

function normalizeMessages(messages) {
  return messages
    .filter((message) => message?.text && message.text.trim().length > 0)
    .map((message) => ({
      role: message.role === "self" ? "self" : "contact",
      text: message.text.trim().replace(/\s+/g, " ")
    }));
}

function normalizeSelectedMessage(message) {
  if (!message?.text || !String(message.text).trim()) {
    return null;
  }
  return {
    role: message.role === "self" ? "self" : "contact",
    text: message.text.trim().replace(/\s+/g, " ")
  };
}

function selectLatestIncomingMessages(messages) {
  const latestIncoming = [];
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    const message = messages[index];
    if (message.role === "self" && latestIncoming.length) {
      break;
    }
    if (message.role !== "self") {
      latestIncoming.unshift(message);
    }
  }

  return latestIncoming.slice(-5);
}

function isUsableSummary(result) {
  const summary = String(result?.summary || "").trim().toLowerCase();
  return Boolean(summary && summary !== "failed to parse summary");
}

function buildLocalSummary(messages) {
  const latest = messages.slice(-8);
  const summaryParts = latest.slice(-3).map((message) => message.slice(0, 120));
  const actionItems = latest.filter((message) => {
    const lowered = message.toLowerCase();
    return message.includes("?")
      || ["send", "share", "call", "meet", "check", "reply", "confirm", "tomorrow", "today"].some((keyword) => lowered.includes(keyword));
  }).slice(-4);

  return {
    summary: summaryParts.length
      ? `Recent chat: ${summaryParts.join(" | ")}`
      : "Recent chat messages are available, but no compact summary could be generated.",
    action_items: actionItems
  };
}

function parseResponseBody(text) {
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch {
    return { message: text };
  }
}

function sanitizeLabel(label) {
  return String(label).replace(/\s+/g, " ").trim().slice(0, 100) || "Browser Chat";
}

function normalizeBaseUrl(url) {
  return String(url || DEFAULT_API_BASE_URL).trim().replace(/\/+$/, "");
}

function clamp(value, min, max) {
  if (Number.isNaN(value)) {
    return min;
  }
  return Math.min(Math.max(value, min), max);
}

function isSupportedUrl(url = "") {
  try {
    return SUPPORTED_HOSTS.has(new URL(url).hostname);
  } catch {
    return false;
  }
}

function normalizeError(error) {
  return error?.message || "Something went wrong.";
}

function storageGet(keys) {
  return chrome.storage.local.get(keys);
}

function storageSet(values) {
  return chrome.storage.local.set(values);
}

function storageRemove(keys) {
  return chrome.storage.local.remove(keys);
}
