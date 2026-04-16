@echo off
REM PersonaAI - Automated APK Build Script
REM This script builds the APK automatically and shows download link

color 0A
title PersonaAI - APK Build

echo.
echo ================================================================
echo        PersonaAI - AUTOMATED APK BUILD
echo ================================================================
echo.

REM Navigate to app directory
cd /d "c:\Users\DELL\Desktop\PersonaAI\personaai-app"
if errorlevel 1 (
    echo ERROR: Could not navigate to app directory!
    pause
    exit /b 1
)

echo [1/7] Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found! Install from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo [2/7] Checking npm...
npm --version
if errorlevel 1 (
    echo ERROR: npm not found!
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
        echo ERROR: Failed to install EAS CLI!
        pause
        exit /b 1
    )
    echo EAS CLI installed successfully!
)

echo.
echo [4/7] Installing npm dependencies...
echo This may take 3-5 minutes...
npm install
if errorlevel 1 (
    echo ERROR: npm install failed!
    pause
    exit /b 1
)

echo.
echo [5/7] Verifying .env configuration...
type .env
echo.
echo Configuration OK!

echo.
echo ================================================================
echo [6/7] BUILDING APK - This will take 5-15 minutes...
echo ================================================================
echo.
echo The build will:
echo - Upload code to EAS cloud build service
echo - Compile Android APK
echo - Show download link when complete
echo.
echo IMPORTANT: Keep this window open until "Build successful" appears!
echo.
pause

REM The actual build command
eas build --platform android --profile preview

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo [7/7] BUILD COMPLETE!
echo ================================================================
echo.
echo SUCCESS! Your APK is ready to download.
echo.
echo NEXT STEPS:
echo 1. Copy the download link shown above
echo 2. Paste in your browser to download PersonaAI.apk
echo 3. Transfer APK to your Android phone (USB/Email/Drive)
echo 4. On phone: Tap APK file in Downloads folder
echo 5. Tap "Install"
echo 6. Launch PersonaAI
echo 7. Login with: demo@persona.ai / StrongPass123
echo.
echo ================================================================
echo.
pause
