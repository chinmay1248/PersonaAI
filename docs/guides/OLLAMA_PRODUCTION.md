# Ollama Production Guide

This is the recommended path if you want PersonaAI to run with open-source local models in production.

## Architecture

Use one VPS for the whole stack:

- `caddy` for HTTPS and reverse proxy
- `api` for FastAPI
- `worker` for Celery jobs
- `postgres` for production data
- `redis` for background jobs
- `ollama` for local LLM inference

The phone app only talks to your backend API. The backend talks to Ollama.

## Recommended Server

Start with:

- 4 vCPU
- 8 GB RAM minimum
- 16 GB RAM preferred
- 80+ GB SSD
- Ubuntu 22.04 or 24.04

For `llama3.2:3b`, 8 GB RAM is the practical floor. If you later move to larger models, plan for more memory or a GPU host.

## Files Added For This Flow

- `personaai-backend/docker-compose.ollama.yml`
- `personaai-backend/.env.production.example`
- `personaai-backend/deploy/Caddyfile`
- `scripts/deploy/DEPLOY_OLLAMA_VPS.sh`

## Step 1: Prepare DNS

Point a domain or subdomain to your VPS public IP.

Example:

- `api.example.com -> your VPS IP`

That domain becomes `APP_DOMAIN` in `.env.production`.

## Step 2: Install Docker On The VPS

On the server:

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker "$USER"
newgrp docker
docker --version
docker compose version
```

## Step 3: Copy The Repo To The VPS

```bash
git clone https://github.com/chinmay1248/PersonaAI.git
cd PersonaAI
```

Or pull the latest changes if the repo already exists there.

## Step 4: Create Production Env

Copy the template:

```bash
cd personaai-backend
cp .env.production.example .env.production
```

Update these values:

- `APP_DOMAIN`
- `LETSENCRYPT_EMAIL`
- `DB_PASSWORD`
- `JWT_SECRET_KEY`
- `ENCRYPTION_KEY`

Generate secrets with:

```bash
python - <<'PY'
from cryptography.fernet import Fernet
import secrets
print("JWT_SECRET_KEY=" + secrets.token_urlsafe(32))
print("ENCRYPTION_KEY=" + Fernet.generate_key().decode())
PY
```

## Step 5: Start The Full Stack

From the repo root on the server:

```bash
bash scripts/deploy/DEPLOY_OLLAMA_VPS.sh
```

Or manually:

```bash
cd personaai-backend
docker compose --env-file .env.production -f docker-compose.ollama.yml up -d --build
```

On first boot, the stack will:

- start Postgres
- start Redis
- start Ollama
- pull `llama3.2:3b`
- pull `nomic-embed-text`
- run migrations
- start the API
- start the Celery worker
- expose HTTPS through Caddy

## Step 6: Verify The Backend

Run:

```bash
curl https://api.example.com/v1/health
```

Expected response:

```json
{"status":"ok","environment":"production"}
```

Useful logs:

```bash
cd personaai-backend
docker compose --env-file .env.production -f docker-compose.ollama.yml logs -f api
docker compose --env-file .env.production -f docker-compose.ollama.yml logs -f ollama
docker compose --env-file .env.production -f docker-compose.ollama.yml logs -f worker
```

## Step 7: Point The App At Production

Update `personaai-app/.env` before your production build:

```env
EXPO_PUBLIC_API_URL=https://api.example.com/v1
EXPO_PUBLIC_ENV=production
EXPO_PUBLIC_APP_NAME=PersonaAI
```

Then build:

```bash
cd personaai-app
eas build --platform android --profile production
```

## What Works With Ollama In This Stack

- reply generation
- summarization
- mood detection
- tone embeddings
- training endpoints
- phone login and onboarding

## Operational Notes

- First deploy is slower because Ollama has to pull models.
- Keep Ollama and the API on the same server if you want the simplest setup.
- If you change models later, update `.env.production` and restart the stack.
- Postgres and Ollama data are persisted in Docker volumes.

## Troubleshooting

### API returns 502 or does not start

Check:

```bash
docker compose --env-file .env.production -f docker-compose.ollama.yml logs -f api
```

### Ollama model calls are slow or timing out

Check:

```bash
docker compose --env-file .env.production -f docker-compose.ollama.yml logs -f ollama
```

Try a smaller model or use a larger VPS.

### HTTPS certificate does not issue

Usually one of these is wrong:

- `APP_DOMAIN` does not point to the VPS yet
- ports `80` and `443` are blocked
- `LETSENCRYPT_EMAIL` is missing

### Phone app cannot connect

Check all of these:

- `EXPO_PUBLIC_API_URL` points to the final HTTPS domain
- backend health works in a browser
- you rebuilt the app after changing `.env`
