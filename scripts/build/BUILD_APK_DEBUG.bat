@echo off
REM PersonaAI - Verbose APK build helper

setlocal enabledelayedexpansion
title PersonaAI - APK Build

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"
set "APP_DIR=%REPO_ROOT%\personaai-app"

echo.
echo ========================================
echo   PersonaAI APK Build
echo ========================================
echo.

echo [Step 1] Current directory:
cd
echo.

echo [Step 2] Checking Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found in PATH.
    echo Install from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
node --version
echo OK
echo.

echo [Step 3] Checking npm...
where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm not found in PATH.
    pause
    exit /b 1
)
npm --version
echo OK
echo.

echo [Step 4] Navigating to app directory...
cd /d "%APP_DIR%"
if errorlevel 1 (
    echo ERROR: Cannot navigate to app directory.
    echo Expected: %APP_DIR%
    pause
    exit /b 1
)
echo Current: %CD%
echo OK
echo.

echo [Step 5] Checking for .env file...
if not exist ".env" (
    echo ERROR: .env file not found.
    pause
    exit /b 1
)
echo .env file found.
echo.

echo [Step 6] Installing npm dependencies...
echo This takes 3-5 minutes...
call npm install
if errorlevel 1 (
    echo.
    echo ERROR: npm install failed.
    echo Try: npm cache clean --force
    echo Then: npm install again
    pause
    exit /b 1
)
echo.
echo npm install successful.
echo.

echo [Step 7] Checking EAS CLI...
where eas >nul 2>&1
if errorlevel 1 (
    echo Installing EAS CLI...
    call npm install -g eas-cli
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install EAS CLI.
        pause
        exit /b 1
    )
)
eas --version
echo OK
echo.

echo ========================================
echo [Step 8] BUILDING APK
echo ========================================
echo.
echo This will take 5-15 minutes...
echo Keep this window open.
echo.
echo The build will show a download link.
echo Copy it to download your APK.
echo.
pause

call eas build --platform android --profile preview

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Build failed.
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL
echo ========================================
echo.
echo Your APK is ready.
echo.
echo NEXT:
echo 1. Copy the download link shown above
echo 2. Paste it in a browser to download
echo 3. Transfer the APK to your phone
echo 4. Install it on your phone
echo 5. Login: demo@persona.ai / StrongPass123
echo.
pause
