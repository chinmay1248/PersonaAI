# PersonaAI

<p align="center">
  <img src="assets/logo.png" width="96" alt="PersonaAI logo">
</p>

<p align="center">
  AI-assisted replies, summaries, and tone learning that aim to sound like you.
</p>

<p align="center">
  <img src="assets/hero_banner.png" alt="PersonaAI banner" width="100%">
</p>

## What This Repo Contains

PersonaAI is split into two main products:

- `personaai-app/`: Expo + React Native mobile app, including the Android WhatsApp integration layer.
- `personaai-backend/`: FastAPI backend for auth, reply generation, summarization, tone learning, and feedback.

The repo root is now organized so a first-time reader can tell where to start:

- `docs/`: guides, reports, and archived notes
- `scripts/`: build and deployment helpers
- `artifacts/`: generated outputs such as packaged builds
- `assets/`: branding and README visuals

## Start Here

1. Read [docs/README.md](docs/README.md) for the documentation map.
2. Use [docs/guides/QUICK_START.md](docs/guides/QUICK_START.md) if you want the fastest local setup.
3. Use [docs/guides/DEPLOYMENT.md](docs/guides/DEPLOYMENT.md) if you want deployment instructions.

## Local Development

### Backend

```bash
cd personaai-backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

For free local AI features, run Ollama and point the backend at it:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Then set `ENABLE_LLM=true` and `LLM_PROVIDER=ollama` in `personaai-backend/.env`.

### App

```bash
cd personaai-app
npm install
npx expo start
```

### Tests

```bash
cd personaai-backend
python -m pytest tests -v
```

## Demo Login

```text
Email: demo@persona.ai
Password: StrongPass123
```

## Project Map

```text
PersonaAI/
|-- personaai-app/        Expo app, UI, services, Android native module
|-- personaai-backend/    FastAPI app, models, routers, services, tests
|-- docs/
|   |-- guides/           Setup, deployment, build, phone usage
|   |-- reports/          Reviews, status summaries, testing notes
|   `-- archive/          Older one-off notes kept for reference
|-- scripts/
|   |-- build/            APK helper scripts
|   `-- deploy/           Deployment helper scripts
|-- artifacts/            Generated builds and outputs
`-- assets/               Images used in documentation
```

## Important App Areas

### Frontend

- `personaai-app/app/`: Expo Router screens for auth, onboarding, and the main app flow
- `personaai-app/components/`: reusable UI building blocks
- `personaai-app/services/`: API calls, training, storage, WhatsApp integration
- `personaai-app/android/`: native Android bridge and accessibility code

### Backend

- `personaai-backend/app/routers/`: API endpoints
- `personaai-backend/app/services/`: business logic and AI orchestration
- `personaai-backend/app/models/`: SQLAlchemy models
- `personaai-backend/app/schemas/`: request and response schemas
- `personaai-backend/tests/`: backend test suite

## Helpful Links

- [Documentation index](docs/README.md)
- [Quick start](docs/guides/QUICK_START.md)
- [Deployment guide](docs/guides/DEPLOYMENT.md)
- [Phone setup guide](docs/guides/PHONE_SETUP_GUIDE.md)
