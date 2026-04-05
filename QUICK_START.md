# 🚀 Quick Start Guide

Get PersonaAI running in 5 minutes!

## Prerequisites
- Docker Desktop installed and running
- Node.js 18+ installed
- Git bash/terminal

## Backend (5 minutes)

```bash
# 1. Navigate to backend
cd personaai-backend

# 2. Start with docker-compose (includes DB, cache, and API)
docker-compose up -d

# 3. Verify it's working
curl http://localhost:8000/v1/health
```

✅ Backend is now running on `http://localhost:8000`

**What docker-compose started:**
- PostgreSQL database on port 5432
- Redis cache on port 6379
- FastAPI server on port 8000
- Celery worker for async tasks

## Frontend (3 minutes)

```bash
# 1. Navigate to frontend
cd personaai-app

# 2. Install dependencies
npm install

# 3. Start Expo dev server
npm start
# or: expo start
```

When prompted, select your platform:
- `a` - Android emulator
- `i` - iOS simulator (macOS only)
- `w` - Web browser
- `j` - Debugging with Flipper

✅ Frontend is now running!

## Test It

### Register a User
1. Open the app
2. Tap "Register"
3. Fill in email and password
4. Tap "Create Account"

### Login
1. Use your registered credentials
2. You should see the home screen

### View Chat Configs (Test the Fix!)
- Navigate to "Chat Configs" 
- This would have failed before, but now works! ✅

---

## That's It!

Your app is now running locally with all fixes applied.

**Next Step:** See `DEPLOYMENT.md` for production deployment instructions.

### Common Issues?

- **Backend won't start:** Make sure Docker is running
- **Frontend won't connect:** Check that backend is on `http://localhost:8000`
- **"Port already in use":** Change docker-compose ports or kill existing process
- **Database errors:** Try `docker-compose down` then `docker-compose up -d`

---

## Environment Files

Your configuration is set up in:
- **Backend:** `personaai-backend/.env`
- **Frontend:** `personaai-app/.env`

Both are configured for **local development** by default.

---

## Stopping Services

```bash
# Stop backend
cd personaai-backend
docker-compose down

# You can start it later with:
docker-compose up -d
```

---

Enjoy debugging! 🎉
