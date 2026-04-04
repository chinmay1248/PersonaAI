<div align="center">
  <img src="https://img.icons8.com/color/144/000000/bot.png" width="100"/>
  <h1>👻 PersonaAI</h1>
  <i>Your Invisible, Hyper-Personalized Communication Assistant</i>
</div>

<br />

**PersonaAI** is an advanced AI assistant that legally bypasses standard Android sandbox restrictions to act as an invisible overlay on top of messaging apps like WhatsApp. It constantly learns your specific tone, local slang, and typing habits to instantly suggest perfect replies—right over your keyboard.

## 🚀 Key Features

*   **📱 Native System Overlays:** Completely intercepts native Android Accessibility trees to scrape text directly off your screen inside WhatsApp, without you ever leaving the app.
*   **🧠 "Digital Brain" Vector Search:** Connects to **Pinecone vector embeddings** to cross-reference thousands of your past text messages to construct an exact mirror of your digital personality.
*   **🤖 Powered by OpenAI:** Integrates **GPT-4o** for high-quality reply generation and intelligent summarization, and **GPT-4o-mini** for ultra-fast mood detection heuristics.
*   **🔒 Military-Grade Vault:** Since this app hooks into private chats, the entire SQLite backend is wrapped in **AES-GCM (Fernet)** symmetric encryption. No raw chat data is ever visible at rest.

---

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph 📱 Android Device
        WA[WhatsApp] -. Accessibility Event .-> nativeScraper[Kotlin Screen Scraper]
        nativeScraper -- RN Native Bridge --> RN[React Native Expo]
        RN -- Spawns --> Float[Floating ChatGPT Widget]
    end

    subgraph ☁️ Backend Architecture
        RN -- REST API --> FastAPI
        FastAPI -- "Wait/Emit" --> Celery[Task Queue]
        Celery -- "Fetch Knowledge" --> VectorDB[(Pinecone DB)]
        Celery -- "Ask LLM" --> OpenAI[GPT-4o]
        FastAPI -- "Encrypt/Save" --> SQLite[(Encrypted SQLite)]
    end
```

---

## 🛠️ Tech Stack
This repository is split perfectly into two major components:

1.  **`personaai-backend`**:
    *   **Python / FastAPI**: Hyper-fast async API router.
    *   **SQLAlchemy / Alembic**: Secure local database generation.
    *   **Celery**: Deployed in "Eager Mode" for rapid, queue-free local development.
2.  **`personaai-app`**:
    *   **React Native (Expo)**: The frontend user interface settings application.
    *   **Kotlin (Native bridging)**: Code bypassing Expo Go to grant `SYSTEM_ALERT_WINDOW` permissions.
    *   **Zustand**: Blazing fast state-management avoiding prop-drilling.

---

## ⚙️ Quick Start Installation

Because PersonaAI requires deep system-level hardware hooks, it **cannot be tested on simple web emulators** or iPhones. 

### 1. Launch the Brain (Backend)
1. Open a terminal and navigate to `/personaai-backend`
2. Configure your environment:
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY and PINECONE_API_KEY
   # Generate an ENCRYPTION_KEY using the fernet cryptography package
   ```
3. Initialize the Encrypted Database: `alembic upgrade head`
4. Start the Server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### 2. Launch the Overlay (Frontend)
1. Plug your physical Android phone into your laptop via USB with USB Debugging on.
2. Open a new terminal and navigate to `/personaai-app`
3. Run the installer to compile the raw Android binaries:
   ```bash
   npm install
   npx expo run:android
   ```
4. **CRITICAL:** Once installed, manually navigate to your Android phone's **Settings app**. Give PersonaAI rights to **"Accessibility"** and **"Display over other apps"**. Open WhatsApp and watch the AI take over!
