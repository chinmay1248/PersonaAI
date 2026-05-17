const DEFAULT_API_BASE_URL = "https://personaai-backend-production-4490.up.railway.app/v1";
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
      return { result: await summarizeContext(message.context) };
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
  return summarizeContext(context);
}

async function trainFromActiveTab() {
  const context = await getActiveContext();
  return trainFromContext(context);
}

async function generateFromContext(context, options = {}) {
  assertUsableContext(context);