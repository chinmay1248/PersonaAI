@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"
set "APP_DIR=%REPO_ROOT%\personaai-app"

echo =====================================
echo PersonaAI APK Build Setup Process
echo =====================================
echo.

echo [STEP 1] Current Directory
cd /d "%APP_DIR%"
echo Current directory: %cd%
echo.

echo [STEP 2] Checking Node.js and npm versions
echo.
echo Node.js version:
node --version
echo.
echo npm version:
npm --version
echo.

echo [STEP 3] Checking EAS CLI installation
echo.
eas --version >nul 2>&1
if %errorlevel% equ 0 (
    echo EAS CLI is already installed:
    eas --version
) else (
    echo EAS CLI not found. Installing globally...
    echo.
    npm install -g eas-cli
    echo.
    echo EAS CLI installation complete. Version:
    eas --version
)
echo.

echo [STEP 4] Environment configuration
echo.
echo Current .env contents:
if exist ".env" (
    type .env
) else (
    echo WARNING: .env file not found in %APP_DIR%
)
echo.

echo [STEP 5] Installing npm dependencies
echo.
echo This may take a few minutes...
echo.
npm install

echo.
echo [STEP 6] Project Status Before Build
echo.
echo Directory contents:
dir /B
echo.

echo =====================================
echo Setup Process Complete
echo =====================================
echo.
echo Next steps:
echo - Build preview APK: eas build --platform android --profile preview
echo - Build production APK: eas build --platform android --profile production
echo.

pause
