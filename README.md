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
| ** Privacy First** | Secure, encrypted storage for your personal data and chat configurations. |
| ** Context-Aware** | Deep understanding of conversation history for highly relevant suggestions. |
| ** Smart Summaries** | Quickly catch up on missed messages with intelligent conversation summarization. |
| ** Cross-Platform** | Native mobile experience built with React Native for seamless integration. |

##  Tech Stack

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Database:** [PostgreSQL](https://www.postgresql.org/) with [Alembic](https://alembic.sqlalchemy.org/) migrations
- **Caching & Queue:** [Redis](https://redis.io/) & [Celery](https://docs.celeryq.dev/)
- **AI/ML:** OpenAI Integration & Vector Search capabilities

### Frontend
- **Framework:** [React Native](https://reactnative.dev/) via [Expo](https://expo.dev/)
- **State Management:** Persistent [MMKV](https://github.com/mrousavy/react-native-mmkv) storage
- **UI Components:** Customized design system for a premium feel

##  Documentation

Explore our detailed guides to get started or deploy to production:

- [ **Quick Start Guide**](QUICK_START.md) - Get up and running in under 5 minutes.
- [ **Deployment Guide**](DEPLOYMENT.md) - Full instructions for Railway, Docker, and Mobile builds.
- [ **Auto-Learning Guide**](AUTO_LEARNING_GUIDE.md) - How the personality engine works.
- [ **Testing Results**](TESTING_RESULTS.md) - Latest validation and QA status.

##  Getting Started

### 1. Prerequisites
- Docker Desktop
- Node.js 18+

### 2. Launch Backend
```bash
cd personaai-backend
docker-compose up -d
```

### 3. Launch App
```bash
cd personaai-app
npm install
npx expo start
```

##  Project Structure

```text
PersonaAI/
├── personaai-backend/    # FastAPI server, migrations, and docker config
├── personaai-app/        # React Native mobile application
├── assets/               # Branding and README visuals
└── ...                   # Documentation and utility scripts
```

---

<p align="center">
  Built with  by the PersonaAI Team
</p>
