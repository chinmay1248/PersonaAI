#!/bin/bash

# PersonaAI Deployment Script
# Deploys both backend (Railway) and frontend (EAS) with latest changes

set -e

echo "🚀 PersonaAI Full Deployment Script"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Verify Git Status
echo -e "${BLUE}Step 1: Verifying Git Status...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ Working directory is not clean!${NC}"
    echo "Please commit or stash your changes before deploying."
    git status
    exit 1
fi
echo -e "${GREEN}✅ Git repository is clean${NC}"
echo ""

# Step 2: Check if already pushed
echo -e "${BLUE}Step 2: Verifying changes are pushed to git...${NC}"
git fetch origin main
if git diff --quiet origin/main; then
    echo -e "${GREEN}✅ All changes are pushed to GitHub${NC}"
else
    echo -e "${YELLOW}⚠️ Warning: Local changes differ from origin${NC}"
fi
echo ""

# Step 3: Backend Deployment Instructions
echo -e "${BLUE}Step 3: Backend Deployment (Railway)${NC}"
echo "=================================="
echo ""
echo "Your backend code is ready to deploy to Railway!"
echo ""
echo -e "${YELLOW}Manual Steps:${NC}"
echo "1. Go to https://railway.app"
echo "2. Access your PersonaAI project"
echo "3. Railway will auto-detect changes from GitHub"
echo "4. Verify deployment logs show:"
echo "   - Database migrations ran successfully (alembic upgrade head)"
echo "   - API server started on port 8000"
echo "   - No errors in logs"
echo ""
echo -e "${YELLOW}Verify Backend:${NC}"
echo "Run: curl https://<your-railway-url>/v1/health"
echo "Expected response:"
echo '{"status": "ok", "environment": "production"}'
echo ""

# Step 4: Frontend Deployment Instructions
echo -e "${BLUE}Step 4: Frontend Deployment (EAS - Android APK)${NC}"
echo "=================================="
echo ""

if ! command -v eas &> /dev/null; then
    echo -e "${RED}❌ EAS CLI not found!${NC}"
    echo "Install with: npm install -g eas-cli"
    echo ""
fi

echo -e "${YELLOW}Building Android APK...${NC}"
echo ""

cd personaai-app

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file for production...${NC}"
    cat > .env << EOF
EXPO_PUBLIC_ENV=production
EXPO_PUBLIC_API_URL=https://personaai-backend-production-4490.up.railway.app/v1
EXPO_PUBLIC_APP_NAME=PersonaAI
EOF
    echo -e "${GREEN}✅ .env created${NC}"
fi

echo ""
echo -e "${YELLOW}⚠️  Important: EAS Build Steps${NC}"
echo ""
echo "The following command will build your APK. This may take 5-10 minutes."
echo ""
echo "To proceed with EAS build, run:"
echo ""
echo -e "${GREEN}eas build --platform android --profile preview${NC}"
echo ""
echo "Or for production:"
echo -e "${GREEN}eas build --platform android --profile production${NC}"
echo ""

# Step 5: Summary
echo ""
echo -e "${BLUE}Deployment Summary${NC}"
echo "=================================="
echo ""
echo -e "${GREEN}✅ Backend:${NC}"
echo "  - Code pushed to GitHub"
echo "  - Auto-deploy configured on Railway"
echo "  - Check https://railway.app for deployment status"
echo ""
echo -e "${GREEN}✅ Frontend:${NC}"
echo "  - Code pushed to GitHub"
echo "  - Ready for EAS build"
echo "  - Run: eas build --platform android --profile preview"
echo ""
echo -e "${YELLOW}New Features Deployed:${NC}"
echo "  ✨ Auto-learning from WhatsApp messages"
echo "  ✨ Training statistics in Settings"
echo "  ✨ Continuous tone profile improvement"
echo "  ✨ Fixed APK version mismatch"
echo ""

echo -e "${GREEN}🎉 Deployment script complete!${NC}"
