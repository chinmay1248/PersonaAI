# PersonaAI Browser Extension

PersonaAI is moving from an Android APK-first experience to a browser extension for WhatsApp Web and Telegram Web. The extension keeps the existing FastAPI backend for auth, tone learning, reply generation, and summaries.

## What Works Now

- Manifest V3 Chrome/Edge extension shell
- Popup login with demo credentials
- Backend URL and reply-count settings
- WhatsApp Web and Telegram Web content overlay
- Visible chat extraction for replies and summaries
- Reply insertion into the active message composer
- Tone training from visible outgoing messages

## Local Install

1. Start the backend:

   ```bash
   cd personaai-backend
   python -m uvicorn app.main:app --reload
   ```

2. Open Chrome or Edge and go to `chrome://extensions`.
3. Enable Developer mode.
4. Choose Load unpacked.
5. Select `personaai-extension/`.