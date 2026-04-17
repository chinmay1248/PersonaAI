@echo off
REM PersonaAI - Automated APK build helper

setlocal enabledelayedexpansion
color 0A
title PersonaAI - APK Build

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"
set "APP_DIR=%REPO_ROOT%\personaai-app"

echo.
echo ================================================================
echo        PersonaAI - AUTOMATED APK BUILD
echo ================================================================
echo.

echo [STEP 0] Navigating to app directory...
cd /d "%APP_DIR%"
if errorlevel 1 (
    echo.
    echo ERROR: Could not navigate to app directory.
    echo Expected directory: %APP_DIR%
    echo.
    pause
    exit /b 1
)
echo Current directory: %CD%
echo.

echo [1/7] Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found. Install from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo [2/7] Checking npm...
npm --version
if errorlevel 1 (
    echo ERROR: npm not found.
    pause
    exit /b 1
)

echo.
echo [3/7] Checking EAS CLI...
eas --version
if errorlevel 1 (
    echo Installing EAS CLI globally...
    npm install -g eas-cli
    if errorlevel 1 (
        echo ERROR: Failed to install EAS CLI.
        pause
        exit /b 1
    )
    echo EAS CLI installed successfully.
)

echo.
echo [4/7] Installing npm dependencies...
echo This may take 3-5 minutes...
npm install
if errorlevel 1 (
    echo ERROR: npm install failed.
    pause
    exit /b 1
)

echo.
echo [5/7] Verifying .env configuration...
if not exist ".env" (
    echo ERROR: .env file not found in %APP_DIR%
    pause
    exit /b 1
)
type .env
echo.
echo Configuration OK.

echo.
echo ================================================================
echo [6/7] BUILDING APK - This will take 5-15 minutes
echo ================================================================
echo.
echo The build will:
echo - Upload code to the EAS cloud build service
echo - Compile an Android APK
echo - Show a download link when complete
echo.
echo IMPORTANT: Keep this window open until "Build successful" appears.
echo.
pause

eas build --platform android --profile preview

if errorlevel 1 (
    echo.
    echo ERROR: Build failed.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo [7/7] BUILD COMPLETE
echo ================================================================
echo.
echo SUCCESS! Your APK is ready to download.
echo.
echo NEXT STEPS:
echo 1. Copy the download link shown above
echo 2. Paste it in your browser to download PersonaAI.apk
echo 3. Transfer the APK to your Android phone
echo 4. Install it on your phone
echo 5. Launch PersonaAI
echo 6. Login with: demo@persona.ai / StrongPass123
echo.
pause
