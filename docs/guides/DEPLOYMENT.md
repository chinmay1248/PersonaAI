# PersonaAI Deployment Guide

## Overview
This document provides step-by-step instructions to deploy PersonaAI, including both the backend (Python/FastAPI) and frontend (React Native/Expo).

## Recommended Path For Ollama

If your goal is a real production app backed by open-source local models, use [OLLAMA_PRODUCTION.md](OLLAMA_PRODUCTION.md).

That guide covers the self-hosted stack where:

- the backend
- Ollama
- PostgreSQL
- Redis
- the worker
- HTTPS

all run together on the same VPS.

## Critical Fixes Applied
✅ Added GET endpoint for chat configs (was breaking the chat config UI)  
✅ Fixed hardcoded JWT and encryption secrets (security vulnerability)  
✅ Created database migrations (was preventing schema creation)  
✅ Fixed docker-compose to include PostgreSQL and Redis services  
✅ Created proper .env configuration files  
✅ Fixed CORS to restrict origins in production  
✅ Fixed frontend storage to use persistent MMKV instead of in-memory  
✅ Added API error handling and token refresh logic  

---

## Part 1: Backend Deployment

### Prerequisites
- Python 3.10+
- PostgreSQL 13+ (for production)
- Redis (for Celery tasks)
- Docker & Docker Compose (for containerized deployment)

### Local Development Setup

1. **Navigate to backend directory:**
   ```bash
   cd personaai-backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database:**
   ```bash
   alembic upgrade head
   ```

5. **Run development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

Server will be available at `http://localhost:8000`

### Docker Deployment (Recommended)

1. **Build and run with docker-compose:**
   ```bash
   cd personaai-backend
   docker-compose up -d
   ```

   This will:
   - Start PostgreSQL database
   - Start Redis server
   - Run migrations automatically
   - Start the FastAPI server
   - Start the Celery worker (for async tasks)

2. **Verify deployment:**
   ```bash
   curl http://localhost:8000/v1/health
   ```

   Expected response:
   ```json
   {"status": "ok", "environment": "development"}
   ```

### Railway Deployment (Production)

1. **Setup Railway Project:**
   - Create account at [Railway.app](https://railway.app)
   - Create new project
   - Select "Deploy from GitHub"
   - Connect your repository

2. **Configure Environment Variables on Railway:**
   Go to your Railway project settings and add:
   ```
   JWT_SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
   ENCRYPTION_KEY=<generate-with-Fernet.generate_key().decode()>
   APP_ENV=production
   FRONTEND_URL=<your-frontend-url>
   ```

3. **Add PostgreSQL Service:**
   - In Railway dashboard, click "Create Service"
   - Select "PostgreSQL"
   - Railway will automatically set `DATABASE_URL` environment variable

4. **Add Redis Service (Optional but Recommended):**
   - In Railway dashboard, click "Create Service"
   - Select "Redis"
   - Railway will set `REDIS_URL` environment variable

5. **Deploy:**
   - Push code to your connected GitHub branch
   - Railway will automatically build and deploy
   - Check deployment logs for any errors

6. **Verify Production:**
   ```bash
   curl https://<your-railway-url>/v1/health
   ```

---

## Part 2: Frontend Deployment

### Prerequisites
- Node.js 18+
- Expo CLI: `npm install -g expo-cli`
- EAS CLI: `npm install -g eas-cli`
- (Optional) Xcode for iOS builds

### Local Development Setup

1. **Navigate to app directory:**
   ```bash
   cd personaai-app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start development server:**
   ```bash
   npm start
   # or
   expo start
   ```

4. **Test on emulator/device:**
   - Android: Press `a`
   - iOS: Press `i`
   - Web: Press `w`

### EAS Build & Deployment

1. **Login to EAS:**
   ```bash
   eas login
   ```

2. **Build for Preview (Android APK):**
   ```bash
   cd personaai-app
   eas build --platform android --profile preview
   ```

3. **Build for Production:**
   ```bash
   eas build --platform android --profile production
   eas build --platform ios --profile production  (if on macOS)
   ```

4. **Configure .env for Production:**
   Update `personaai-app/.env`:
   ```
   EXPO_PUBLIC_API_URL=https://<your-railway-backend-url>/v1
   EXPO_PUBLIC_ENV=production
   ```

5. **Submit to Google Play / App Store:**
   ```bash
   eas submit --platform android --latest
   ```

---

## Environment Variables Reference

### Backend (.env)

```
# Database (local development)
DATABASE_URL=sqlite:///./personaai.db

# Database (Docker/Production - PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname
DB_USER=personaai
DB_PASSWORD=personaai
DB_NAME=personaai_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth & Security (REQUIRED - Generate strong random values!)
JWT_SECRET_KEY=<min 32 chars, generate with: secrets.token_urlsafe(32)>
ENCRYPTION_KEY=<generate with: Fernet.generate_key().decode()>

# Optional AI Services
OPENAI_API_KEY=<your-openai-api-key>
PINECONE_API_KEY=<your-pinecone-api-key>
PINECONE_ENVIRONMENT=us-east-1

# Environment
APP_ENV=development|production
FRONTEND_URL=http://localhost:3000  (for CORS)
```

### Frontend (.env)

```
EXPO_PUBLIC_API_URL=http://localhost:8000/v1  (dev) or https://your-api-url/v1 (prod)
EXPO_PUBLIC_ENV=development|production
EXPO_PUBLIC_APP_NAME=PersonaAI
```

---

## Troubleshooting

### Backend Issues

**Error: "JWT_SECRET_KEY not provided"**
- Solution: Set `JWT_SECRET_KEY` environment variable with a strong random value

**Error: "ENCRYPTION_KEY not provided"**
- Solution: Set `ENCRYPTION_KEY` environment variable using Fernet

**Error: "Connection refused: PostgreSQL"**
- Solution: Ensure PostgreSQL is running; check `DATABASE_URL` is correct
- For Docker: `docker-compose up -d db`

**Error: "Chat configs not found" in UI**
- This is now fixed! The GET `/v1/chats/config` endpoint has been added

### Frontend Issues

**Error: "Cannot connect to backend"**
- Check `EXPO_PUBLIC_API_URL` in .env is correct
- Ensure backend is running and accessible
- Check CORS configuration on backend (should allow your frontend URL)

**Error: "Network error" after login**
- Check if access token is expired
- Error handler will automatically attempt refresh
- Check browser console for detailed error

**Error: "Storage not found"**
- This is now fixed! Storage uses persistent MMKV storage

---

## Testing the Deployment

### API Health Check
```bash
curl https://<your-api-url>/v1/health
```

### Authentication Flow
1. Register: `POST /v1/auth/register`
2. Login: `POST /v1/auth/login`
3. Get Chat Configs: `GET /v1/chats/config` (Fixed!)
4. Create Chat Config: `POST /v1/chats/config`

### Database Migrations
```bash
# Check migration status
alembic current

# Apply new migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

---

## Performance Recommendations

1. **Enable Redis caching** for frequently accessed data
2. **Configure Celery workers** for async tasks (email, notifications)
3. **Use PostgreSQL** instead of SQLite for production
4. **Enable CORS restrictions** in production (only allow your frontend URL)
5. **Implement rate limiting** in production (currently a placeholder)
6. **Use HTTPS** for all communications
7. **Regular database backups** via Railway dashboard

---

## Next Steps

1. ✅ All critical fixes have been applied
2. Generate secure JWT and encryption keys for production
3. Set up Railway PostgreSQL and Redis services
4. Deploy backend to Railway
5. Update frontend `.env` with production API URL
6. Build and submit frontend to app stores

Good luck! 🚀
