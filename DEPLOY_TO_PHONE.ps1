#!/usr/bin/env powershell

# PersonaAI - Complete Android Phone Deployment Script
# This script handles all steps to build and deploy PersonaAI APK

Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host "PERSONAAI - COMPLETE ANDROID DEPLOYMENT SCRIPT" -ForegroundColor Green
Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$APP_DIR = "C:\Users\DELL\Desktop\PersonaAI\personaai-app"
$ENV_FILE = "$APP_DIR\.env"

# Step 1: Check prerequisites
Write-Host "[STEP 1] Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check Node.js
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Node.js: NOT FOUND" -ForegroundColor Red
    Write-Host "    Install from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check npm
$npmVersion = npm --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ npm: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ npm: NOT FOUND" -ForegroundColor Red
    exit 1
}

# Check EAS CLI
$easVersion = eas --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ EAS CLI: $easVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ EAS CLI: NOT FOUND" -ForegroundColor Yellow
    Write-Host "  Installing EAS CLI globally..." -ForegroundColor Cyan
    npm install -g eas-cli
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ EAS CLI installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to install EAS CLI" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 2: Navigate to app directory
Write-Host "[STEP 2] Setting Up App Directory..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path $APP_DIR) {
    Write-Host "  ✓ App directory found: $APP_DIR" -ForegroundColor Green
    Set-Location $APP_DIR
    Write-Host "  ✓ Changed to app directory" -ForegroundColor Green
} else {
    Write-Host "  ✗ App directory not found: $APP_DIR" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Configure .env file
Write-Host "[STEP 3] Configuring Environment Variables..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path $ENV_FILE) {
    Write-Host "  Current .env configuration:" -ForegroundColor Cyan
    $envContent = Get-Content $ENV_FILE | Select-String -Pattern "^EXPO_PUBLIC" | ForEach-Object { "    $_" }
    Write-Host "$envContent"
    Write-Host ""
    
    # Ask user for API configuration
    Write-Host "  Choose your API configuration:" -ForegroundColor Yellow
    Write-Host "  1. Local Development (http://localhost:8000/v1)" -ForegroundColor Cyan
    Write-Host "  2. Local LAN (http://YOUR_COMPUTER_IP:8000/v1)" -ForegroundColor Cyan
    Write-Host "  3. Production Railway (https://your-railway-url/v1)" -ForegroundColor Cyan
    Write-Host ""
    $choice = Read-Host "  Enter choice (1/2/3)"
    
    $apiUrl = ""
    switch ($choice) {
        "1" {
            $apiUrl = "http://localhost:8000/v1"
            Write-Host "  Selected: Local Development" -ForegroundColor Green
        }
        "2" {
            $ipAddress = Read-Host "  Enter your computer's IP address (e.g., 192.168.1.100)"
            $apiUrl = "http://$($ipAddress):8000/v1"
            Write-Host "  Selected: Local LAN - $apiUrl" -ForegroundColor Green
        }
        "3" {
            $railwayUrl = Read-Host "  Enter your Railway backend URL"
            $apiUrl = "$railwayUrl/v1"
            Write-Host "  Selected: Production Railway - $apiUrl" -ForegroundColor Green
        }
        default {
            $apiUrl = "http://localhost:8000/v1"
            Write-Host "  Default: Local Development" -ForegroundColor Green
        }
    }
    
    # Update .env file
    Write-Host ""
    Write-Host "  Updating .env file..." -ForegroundColor Cyan
    
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
    
    Set-Content -Path $ENV_FILE -Value $newEnvContent
    Write-Host "  ✓ .env file updated successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ .env file not found" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Check npm dependencies
Write-Host "[STEP 4] Checking npm Dependencies..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path "$APP_DIR\node_modules") {
    Write-Host "  ✓ node_modules found" -ForegroundColor Green
} else {
    Write-Host "  ! node_modules not found, installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 5: Build APK
Write-Host "[STEP 5] Building APK..." -ForegroundColor Yellow
Write-Host ""

Write-Host "  Choose build type:" -ForegroundColor Yellow
Write-Host "  1. Preview (faster, for testing)" -ForegroundColor Cyan
Write-Host "  2. Production (optimized, for release)" -ForegroundColor Cyan
Write-Host ""
$buildChoice = Read-Host "  Enter choice (1/2)"

$buildProfile = if ($buildChoice -eq "2") { "production" } else { "preview" }

Write-Host "  Building $buildProfile APK..." -ForegroundColor Cyan
Write-Host "  (This may take 5-15 minutes)" -ForegroundColor Yellow
Write-Host ""

eas build --platform android --profile $buildProfile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "  ✓ APK build completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Open the download link from above" -ForegroundColor Cyan
    Write-Host "  2. Download the APK file" -ForegroundColor Cyan
    Write-Host "  3. Transfer APK to your Android phone (USB/Email/Cloud)" -ForegroundColor Cyan
    Write-Host "  4. On phone: Open File Manager → Downloads → Tap APK → Install" -ForegroundColor Cyan
    Write-Host "  5. Open PersonaAI app" -ForegroundColor Cyan
    Write-Host "  6. Login with: demo@persona.ai / StrongPass123" -ForegroundColor Cyan
} else {
    Write-Host "  ✗ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================================" -ForegroundColor Cyan
