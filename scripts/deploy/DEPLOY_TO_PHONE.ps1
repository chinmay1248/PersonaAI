#!/usr/bin/env powershell

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$appDir = Join-Path $repoRoot "personaai-app"
$envFile = Join-Path $appDir ".env"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PERSONAAI - COMPLETE ANDROID DEPLOYMENT SCRIPT" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[STEP 1] Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCommand) {
    Write-Host ("  [OK] Node.js: {0}" -f (node --version)) -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Node.js not found. Install it from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

$npmCommand = Get-Command npm -ErrorAction SilentlyContinue
if ($npmCommand) {
    Write-Host ("  [OK] npm: {0}" -f (npm --version)) -ForegroundColor Green
} else {
    Write-Host "  [ERROR] npm not found." -ForegroundColor Red
    exit 1
}

$easCommand = Get-Command eas -ErrorAction SilentlyContinue
if ($easCommand) {
    Write-Host ("  [OK] EAS CLI: {0}" -f (eas --version)) -ForegroundColor Green
} else {
    Write-Host "  [INFO] EAS CLI not found. Installing it globally..." -ForegroundColor Yellow
    npm install -g eas-cli
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] Failed to install EAS CLI." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] EAS CLI installed successfully." -ForegroundColor Green
}

Write-Host ""
Write-Host "[STEP 2] Setting up the app directory..." -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $appDir)) {
    Write-Host ("  [ERROR] App directory not found: {0}" -f $appDir) -ForegroundColor Red
    exit 1
}

Set-Location $appDir
Write-Host ("  [OK] Working directory: {0}" -f $appDir) -ForegroundColor Green

Write-Host ""
Write-Host "[STEP 3] Configuring environment variables..." -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $envFile)) {
    Write-Host ("  [ERROR] .env file not found: {0}" -f $envFile) -ForegroundColor Red
    exit 1
}

Write-Host "  Current EXPO_PUBLIC values:" -ForegroundColor Cyan
Get-Content $envFile |
    Select-String -Pattern "^EXPO_PUBLIC" |
    ForEach-Object { Write-Host ("    {0}" -f $_.Line) }

Write-Host ""
Write-Host "  Choose your API configuration:" -ForegroundColor Yellow
Write-Host "  1. Local Development (http://localhost:8000/v1)" -ForegroundColor Cyan
Write-Host "  2. Local LAN (http://YOUR_COMPUTER_IP:8000/v1)" -ForegroundColor Cyan
Write-Host "  3. Production Railway (https://your-railway-url/v1)" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "  Enter choice (1/2/3)"
$apiUrl = "http://localhost:8000/v1"

switch ($choice) {
    "1" {
        $apiUrl = "http://localhost:8000/v1"
        Write-Host "  Selected: Local Development" -ForegroundColor Green
    }
    "2" {
        $ipAddress = Read-Host "  Enter your computer's IP address (for example 192.168.1.100)"
        $apiUrl = "http://$ipAddress:8000/v1"
        Write-Host ("  Selected: Local LAN - {0}" -f $apiUrl) -ForegroundColor Green
    }
    "3" {
        $railwayUrl = Read-Host "  Enter your Railway backend URL"
        $apiUrl = "$railwayUrl/v1"
        Write-Host ("  Selected: Production Railway - {0}" -f $apiUrl) -ForegroundColor Green
    }
    default {
        Write-Host "  Defaulting to Local Development" -ForegroundColor Green
    }
}

$newEnvContent = @"
# Frontend Environment Configuration
# Used for Expo development and builds

# API Configuration
# Leave EXPO_PUBLIC_API_URL blank to use automatic local defaults:
# - Android emulator: http://10.0.2.2:8000/v1
# - Web/iOS simulator: http://localhost:8000/v1
# For a physical phone, set this to http://YOUR_COMPUTER_LAN_IP:8000/v1
EXPO_PUBLIC_API_URL=$apiUrl
EXPO_PUBLIC_ENV=production

# App Configuration
EXPO_PUBLIC_APP_NAME=PersonaAI
"@

Set-Content -Path $envFile -Value $newEnvContent
Write-Host "  [OK] .env file updated successfully." -ForegroundColor Green

Write-Host ""
Write-Host "[STEP 4] Checking npm dependencies..." -ForegroundColor Yellow
Write-Host ""

$nodeModulesDir = Join-Path $appDir "node_modules"
if (Test-Path $nodeModulesDir) {
    Write-Host "  [OK] node_modules found." -ForegroundColor Green
} else {
    Write-Host "  [INFO] node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] Failed to install dependencies." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] Dependencies installed successfully." -ForegroundColor Green
}

Write-Host ""
Write-Host "[STEP 5] Building APK..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Choose build type:" -ForegroundColor Yellow
Write-Host "  1. Preview (faster, for testing)" -ForegroundColor Cyan
Write-Host "  2. Production (optimized, for release)" -ForegroundColor Cyan
Write-Host ""

$buildChoice = Read-Host "  Enter choice (1/2)"
$buildProfile = if ($buildChoice -eq "2") { "production" } else { "preview" }

Write-Host ("  Building {0} APK..." -f $buildProfile) -ForegroundColor Cyan
Write-Host "  This may take 5-15 minutes." -ForegroundColor Yellow
Write-Host ""

eas build --platform android --profile $buildProfile

if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Build failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "  [OK] APK build completed successfully." -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open the download link from above" -ForegroundColor Cyan
Write-Host "  2. Download the APK file" -ForegroundColor Cyan
Write-Host "  3. Transfer the APK to your Android phone" -ForegroundColor Cyan
Write-Host "  4. Install the APK on your phone" -ForegroundColor Cyan
Write-Host "  5. Open PersonaAI" -ForegroundColor Cyan
Write-Host "  6. Login with: demo@persona.ai / StrongPass123" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
