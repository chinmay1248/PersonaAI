#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$REPO_ROOT/personaai-backend"
ENV_FILE="$BACKEND_DIR/.env.production"
COMPOSE_FILE="$BACKEND_DIR/docker-compose.ollama.yml"

echo "PersonaAI Ollama VPS deploy"
echo "==========================="

if ! command -v docker >/dev/null 2>&1; then
    echo "docker is required on the target server."
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "Missing $ENV_FILE"
    echo "Copy personaai-backend/.env.production.example to .env.production first."
    exit 1
fi

cd "$BACKEND_DIR"

echo "Pulling latest service images..."
docker compose --env-file .env.production -f "$COMPOSE_FILE" pull

echo "Building and starting PersonaAI..."
docker compose --env-file .env.production -f "$COMPOSE_FILE" up -d --build

echo ""
echo "Deployment started."
echo "Check API health with:"
echo "  curl https://\${APP_DOMAIN}/v1/health"
echo ""
echo "Follow logs with:"
echo "  docker compose --env-file .env.production -f $COMPOSE_FILE logs -f api ollama worker"
