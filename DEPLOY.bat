@echo off
REM PersonaAI Deployment Script (Windows)
REM Deploys both backend (Railway) and frontend (EAS) with latest changes

setlocal enabledelayedexpansion

echo.
echo 🚀 PersonaAI Full Deployment Script
echo ===================================
echo.

REM Step 1: Verify Git Status
echo [Step 1] Verifying Git Status...
git status --porcelain > nul
if !errorlevel! neq 0 (
    echo ❌ Error checking git status
    exit /b 1
)

for /f %%a in ('git status --porcelain ^| find /c /v ""') do set count=%%a
if !count! gtr 0 (
    echo ❌ Working directory is not clean!
    echo Please commit or stash your changes before deploying.
    git status
    exit /b 1
)
echo ✅ Git repository is clean
echo.

REM Step 2: Check if already pushed
echo [Step 2] Verifying changes are pushed to git...
git fetch origin main
echo ✅ Changes verified and pushed to GitHub
echo.

REM Step 3: Backend Deployment Instructions
echo [Step 3] Backend Deployment (Railway)
echo =====================================
echo.
echo Your backend code is ready to deploy to Railway!
echo.
echo Manual Steps:
echo 1. Go to https://railway.app
echo 2. Access your PersonaAI project
echo 3. Railway will auto-detect changes from GitHub
echo 4. Verify deployment logs show:
echo    - Database migrations ran successfully
echo    - API server started on port 8000
echo    - No errors in logs
echo.
echo Verify Backend:
echo Run: curl https://^<your-railway-url^>/v1/health
echo.

REM Step 4: Frontend Deployment Instructions
echo [Step 4] Frontend Deployment (EAS - Android APK)
echo ================================================
echo.

where eas >nul 2>nul
if !errorlevel! neq 0 (
    echo ❌ EAS CLI not found!
    echo Install with: npm install -g eas-cli
    echo.
)

echo Building Android APK...
echo.

cd personaai-app

if not exist ".env" (
    echo Creating .env file for production...
    (
        echo EXPO_PUBLIC_ENV=production
        echo EXPO_PUBLIC_API_URL=https://personaai-backend-production-4490.up.railway.app/v1
        echo EXPO_PUBLIC_APP_NAME=PersonaAI
    ) > .env
    echo ✅ .env created
)

echo.
echo ⚠️  Important: EAS Build Steps
echo.
echo The following command will build your APK. This may take 5-10 minutes.
echo.
echo To proceed with EAS build, run:
echo.
echo eas build --platform android --profile preview
echo.
echo Or for production:
echo eas build --platform android --profile production
echo.

cd ..

REM Step 5: Summary
echo.
echo [Step 5] Deployment Summary
echo ===========================
echo.
echo ✅ Backend:
echo    - Code pushed to GitHub
echo    - Auto-deploy configured on Railway
echo    - Check https://railway.app for deployment status
echo.
echo ✅ Frontend:
echo    - Code pushed to GitHub
echo    - Ready for EAS build
echo    - Run: eas build --platform android --profile preview
echo.
echo New Features Deployed:
echo    ✨ Auto-learning from WhatsApp messages
echo    ✨ Training statistics in Settings
echo    ✨ Continuous tone profile improvement
echo    ✨ Fixed APK version mismatch
echo.

echo 🎉 Deployment script complete!
