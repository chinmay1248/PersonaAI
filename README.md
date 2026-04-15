<p align="center">
  <img src="assets/logo.png" width="120" alt="PersonaAI Logo">
</p>

<h1 align="center">PersonaAI</h1>

<p align="center">
  <strong>Your Digital Echo: An AI that learns to text like you.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React Native">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

---

<p align="center">
  <img src="assets/hero_banner.png" alt="PersonaAI Banner" width="100%">
</p>

##  Overview

**PersonaAI** is an intelligent chat assistant designed to be your digital twin. It seamlessly learns your personality, tone, and texting style to generate context-aware replies, summarize long conversations, and provide instant smart suggestions—exactly how you would respond.

Whether you're managing dozens of chats or just want to maintain your unique voice while using AI, PersonaAI bridges the gap between automated assistance and human personality.

##  Key Features

| Feature | Description |
| :--- | :--- |
| ** Personality Engine** | Learns from your previous interactions to mimic your unique writing style and vocabulary. |
| ** Privacy First** | Secure, encrypted storage for your personal data and chat configurations using Fernet encryption. |
| ** Context-Aware** | Deep understanding of conversation history for highly relevant suggestions via GPT-4o. |
| ** Smart Summaries** | Quickly catch up on missed messages with intelligent conversation summarization. |
| ** Cross-Platform** | Native mobile experience built with React Native for seamless integration. |
| ** WhatsApp Integration** | Native Android accessibility service that auto-reads WhatsApp chats and continuously trains your profile. |
| ** Mood Detection** | Automatically detects the mood of incoming messages (happy, sad, curious, etc.) for contextually appropriate replies. |
| ** Rate-Limited API** | Built-in sliding-window rate limiter (60 req/min) to protect the backend from abuse. |

##  Tech Stack

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database:** [PostgreSQL](https://www.postgresql.org/) with [Alembic](https://alembic.sqlalchemy.org/) migrations (SQLite for local dev)
- **Caching & Queue:** [Redis](https://redis.io/) & [Celery](https://docs.celeryq.dev/) with two production workers
- **AI/ML:** OpenAI GPT-4o for reply generation, mood detection, and summarization
- **Security:** JWT authentication, bcrypt password hashing, Fernet encryption for stored data
- **Vector Search:** Pinecone integration for tone profile embeddings

### Frontend
- **Framework:** [React Native](https://reactnative.dev/) via [Expo](https://expo.dev/) (SDK 53)
- **State Management:** [Zustand](https://github.com/pmndrs/zustand) with persistent [MMKV](https://github.com/mrousavy/react-native-mmkv) storage
- **Navigation:** [Expo Router](https://docs.expo.dev/router/introduction/) v5 with file-based routing
- **Native Module:** Custom Kotlin bridge for WhatsApp accessibility service integration

### Android Native (Kotlin)
- **WhatsAppReaderService:** Accessibility service that scrapes visible WhatsApp text with coordinates
- **PersonaAIModule:** React Native bridge that relays scraped data via broadcast receiver
- **OverlayManager:** System overlay button shown when WhatsApp is active

##  Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                      React Native App                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐│
│  │ Auth     │ │ Onboard  │ │ Main     │ │ Android Native   ││
│  │ Screens  │ │ Flow     │ │ Screens  │ │ WhatsApp Reader  ││
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───────┬──────────┘│
│       │             │            │               │            │
│       └─────────────┴────────────┴───────────────┘            │
│                          │ Axios + JWT                        │
└──────────────────────────┼───────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────┐
│                    FastAPI Backend                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ Auth     │ │ AI Reply │ │ Tone     │ │ Summarizer     │  │
│  │ Router   │ │ Router   │ │ Router   │ │ Router         │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬───────┘  │
│       │             │            │                │           │
│  ┌────┴─────────────┴────────────┴────────────────┴───────┐  │
│  │                   Service Layer                        │  │
│  │  AuthService · AIEngine · ToneLearner · MoodDetector   │  │
│  │  Summarizer · FeedbackProcessor · Encryption           │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│  ┌──────────────┐  ┌──────┴──────┐  ┌─────────────────────┐  │
│  │ PostgreSQL   │  │ OpenAI API  │  │ Celery Workers      │  │
│  │ / SQLite     │  │ GPT-4o      │  │ Training + Refresh  │  │
│  └──────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

##  API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/v1/health` | Health check |
| `POST` | `/v1/auth/register` | Create new user |
| `POST` | `/v1/auth/login` | Login and get JWT |
| `POST` | `/v1/auth/refresh` | Refresh access token |
| `GET` | `/v1/chats/config` | List chat configurations |
| `POST` | `/v1/chats/config` | Create chat configuration |
| `PATCH` | `/v1/chats/config/{id}` | Update chat configuration |
| `POST` | `/v1/ai/generate-reply` | Generate AI reply suggestions |
| `POST` | `/v1/ai/summarize` | Summarize messages |
| `POST` | `/v1/tone/train` | Train tone profile manually |
| `POST` | `/v1/tone/train-from-messages` | Train from WhatsApp messages |
| `GET` | `/v1/tone/profile` | Get tone profile |
| `GET` | `/v1/tone/training-stats` | Get training statistics |
| `POST` | `/v1/feedback/reply` | Submit reply feedback |

##  Documentation

Explore our detailed guides to get started or deploy to production:

-  [**Quick Start Guide**](QUICK_START.md) - Get up and running in under 5 minutes.
-  [**Deployment Guide**](DEPLOYMENT.md) - Full instructions for Railway, Docker, and Mobile builds.
-  [**Auto-Learning Guide**](AUTO_LEARNING_GUIDE.md) - How the personality engine works.
-  [**Testing Results**](TESTING_RESULTS.md) - Latest validation and QA status.
-  [**Code Review**](CODE_REVIEW.md) - Complete code review and flow documentation.

##  Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- Docker Desktop (optional, for PostgreSQL/Redis)

### 2. Launch Backend
```bash
cd personaai-backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 3. Launch with Docker
```bash
cd personaai-backend
docker-compose up -d
```

### 4. Launch App
```bash
cd personaai-app
npm install
npx expo start
```

### 5. Demo Credentials
```
Email: demo@persona.ai
Password: StrongPass123
```

##  Project Structure

```text
PersonaAI/
├── personaai-backend/        # FastAPI server
│   ├── app/
│   │   ├── models/           # SQLAlchemy models (7 models)
│   │   ├── routers/          # API endpoints (6 routers)
│   │   ├── services/         # Business logic (7 services)
│   │   ├── schemas/          # Pydantic schemas (5 files)
│   │   ├── middleware/       # Auth + rate limiter
│   │   ├── utils/            # JWT, prompt builder, validators
│   │   └── workers/          # Celery jobs (training + tone refresh)
│   ├── tests/                # pytest test suite (4 tests)
│   ├── alembic/              # Database migrations
│   ├── Dockerfile            # Production container
│   ├── docker-compose.yml    # Full stack with PostgreSQL + Redis
│   └── railway.json          # Railway deployment config
├── personaai-app/            # React Native mobile application
│   ├── app/                  # Expo Router screens
│   │   ├── (auth)/           # Login + Register
│   │   ├── (onboarding)/     # 4-step onboarding flow
│   │   └── (main)/           # Home, Reply, Summarize, Settings, etc.
│   ├── components/           # 8 reusable UI components
│   ├── services/             # 9 API/service modules
│   ├── store/                # 4 Zustand state stores
│   ├── hooks/                # 3 custom React hooks
│   └── android/              # Native Kotlin module (WhatsApp bridge)
├── assets/                   # Branding and README visuals
└── ...                       # Documentation and utility scripts
```

##  Testing

```bash
cd personaai-backend
python -m pytest tests/ -v
```

**Current Status: 4/4 tests passing ✅**

| Test | Description | Status |
| :--- | :--- | :--- |
| `test_register_and_login` | User registration + login flow | ✅ Pass |
| `test_generate_reply_flow` | Chat config + AI reply generation | ✅ Pass |
| `test_summarize_messages` | Message summarization | ✅ Pass |
| `test_tone_training` | Tone profile training | ✅ Pass |

---

<p align="center">
  Built with ❤️ by the PersonaAI Team
</p>
