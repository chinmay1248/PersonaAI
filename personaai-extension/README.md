# PersonaAI Browser Extension

PersonaAI is moving from an Android APK-first experience to a browser extension for WhatsApp Web and Telegram Web. The extension keeps the existing FastAPI backend for auth, tone learning, reply generation, and summaries.

## What Works Now

- Manifest V3 Chrome/Edge extension shell
- Popup login with demo credentials
- Backend URL and reply-count settings
- Backend connection testing from the popup
- WhatsApp Web and Telegram Web content overlay
- Visible chat extraction for replies and summaries
- Reply insertion into the active message composer
- Tone training from visible outgoing messages

## Local Install

1. Start the backend:

   ```bash
   cd personaai-backend
   copy .env.example .env
   python -m uvicorn app.main:app --reload
   ```

2. Open Chrome or Edge and go to `chrome://extensions`.
3. Enable Developer mode.
4. Choose Load unpacked.
5. Select `personaai-extension/`.
6. Open the extension popup, set Backend URL to `http://localhost:8000/v1`, and sign in.

Demo login:

```text
Email: demo@persona.ai
Password: StrongPass123
```

## Production Backend

The default backend URL is:

```text
https://personaai-backend-production-4490.up.railway.app/v1
```

Change it in the popup settings when testing a local or staging backend.
For non-default backend URLs, the extension may ask for host permission before it can connect.

## Migration Notes

- The Expo app and Android native module remain in `personaai-app/` for reference.
- Browser chat access now happens through `content/content.js` instead of Android accessibility services.
- Auth tokens and extension settings are stored in `chrome.storage.local`.
- Cross-origin backend access is declared in `manifest.json` host permissions.
- DOM selectors are intentionally defensive because WhatsApp Web and Telegram Web update their markup often.
