#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

echo "PersonaAI Full Deployment Script"
echo "================================"
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Step 1: Verifying git status...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}ERROR: Working directory is not clean.${NC}"
    echo "Please commit or stash your changes before deploying."
    git status
    exit 1
fi
echo -e "${GREEN}OK: Git repository is clean.${NC}"
echo ""

echo -e "${BLUE}Step 2: Verifying changes are pushed...${NC}"
git fetch origin main
if git diff --quiet origin/main; then
    echo -e "${GREEN}OK: All changes are pushed to GitHub.${NC}"
else
    echo -e "${YELLOW}WARNING: Local changes differ from origin/main.${NC}"
fi
echo ""

echo -e "${BLUE}Step 3: Backend deployment (Railway)${NC}"
echo "===================================="
echo ""
echo "Backend code is ready to deploy to Railway."
echo "Verify your service logs and health endpoint after deploy."
echo "curl https://<your-railway-url>/v1/health"
echo ""

echo -e "${BLUE}Step 4: Frontend deployment (EAS - Android APK)${NC}"
echo "================================================"
echo ""

if ! command -v eas >/dev/null 2>&1; then
    echo -e "${YELLOW}WARNING: EAS CLI not found. Install with: npm install -g eas-cli${NC}"
fi

cd "$REPO_ROOT/personaai-app"

if [ ! -f ".env" ]; then
    cat > .env << EOF
EXPO_PUBLIC_ENV=production
EXPO_PUBLIC_API_URL=https://personaai-backend-production-4490.up.railway.app/v1
EXPO_PUBLIC_APP_NAME=PersonaAI
EOF
    echo -e "${GREEN}OK: .env created.${NC}"
fi

echo ""
echo "Run one of these commands to build your APK:"
echo "eas build --platform android --profile preview"
echo "eas build --platform android --profile production"
echo ""

cd "$REPO_ROOT"

echo -e "${BLUE}Step 5: Summary${NC}"
echo "================"
echo ""
echo -e "${GREEN}OK: Backend is ready for Railway deployment.${NC}"
echo -e "${GREEN}OK: Frontend is ready for EAS builds.${NC}"
echo "Docs: docs/guides/DEPLOYMENT.md"
echo "Phone helper: scripts/deploy/DEPLOY_TO_PHONE.ps1"
echo ""
echo -e "${GREEN}Deployment script complete.${NC}"
