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