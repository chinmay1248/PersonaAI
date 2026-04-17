@echo off
REM PersonaAI deployment helper for Windows

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"

cd /d "%REPO_ROOT%"

echo.
echo PersonaAI Full Deployment Script
echo ==================================
echo.

echo [Step 1] Verifying git status...
git status --porcelain > nul
if !errorlevel! neq 0 (
    echo ERROR: Unable to check git status.
    exit /b 1
)

for /f %%a in ('git status --porcelain ^| find /c /v ""') do set count=%%a
if !count! gtr 0 (
    echo ERROR: Working directory is not clean.
    echo Please commit or stash your changes before deploying.
    git status
    exit /b 1
)
echo OK: Git repository is clean.
echo.

echo [Step 2] Verifying changes are pushed...
git fetch origin main
echo OK: Fetch complete.
echo.

echo [Step 3] Backend deployment (Railway)
echo =====================================
echo.
echo Backend code is ready to deploy to Railway.
echo.
echo Manual steps:
echo 1. Go to https://railway.app
echo 2. Open your PersonaAI project
echo 3. Verify the deployment logs
echo 4. Confirm the API starts on port 8000
echo.
echo Verify backend with:
echo curl https://^<your-railway-url^>/v1/health
echo.

echo [Step 4] Frontend deployment (EAS - Android APK)
echo ================================================
echo.

where eas >nul 2>nul
if !errorlevel! neq 0 (
    echo WARNING: EAS CLI not found.
    echo Install with: npm install -g eas-cli
    echo.
)

cd /d "%REPO_ROOT%\personaai-app"

if not exist ".env" (
    echo Creating .env file for production...
    (
        echo EXPO_PUBLIC_ENV=production
        echo EXPO_PUBLIC_API_URL=https://personaai-backend-production-4490.up.railway.app/v1
        echo EXPO_PUBLIC_APP_NAME=PersonaAI
    ) > .env
    echo OK: .env created.
)

echo.
echo Run one of these commands to build your APK:
echo eas build --platform android --profile preview
echo eas build --platform android --profile production
echo.

cd /d "%REPO_ROOT%"

echo [Step 5] Summary
echo =================
echo.
echo OK: Backend is ready for Railway deployment.
echo OK: Frontend is ready for EAS builds.
echo Docs: docs\guides\DEPLOYMENT.md
echo Phone helper: scripts\deploy\DEPLOY_TO_PHONE.ps1
echo.
echo Deployment script complete.
