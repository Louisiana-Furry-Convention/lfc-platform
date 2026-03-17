#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <environment> <release_tag>"
  exit 1
fi

APP_ENV_TARGET="$1"
RELEASE_TAG="$2"

APP_DIR="/opt/lfc-platform"
API_DIR="$APP_DIR/apps/api"
SERVICE_NAME="lfc-api"

echo "=== LFC deploy starting ==="
echo "Environment: $APP_ENV_TARGET"
echo "Release tag:  $RELEASE_TAG"

cd "$APP_DIR"

git fetch --all --tags
git checkout "$RELEASE_TAG"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r "$API_DIR/requirements.txt"

if [ -f ".env.$APP_ENV_TARGET" ]; then
  cp ".env.$APP_ENV_TARGET" "$API_DIR/.env"
else
  echo "Missing .env.$APP_ENV_TARGET"
  exit 1
fi

cd "$API_DIR"

if [ -f "alembic.ini" ]; then
  alembic upgrade head
fi

sudo systemctl restart "$SERVICE_NAME"
sleep 3

curl -f http://127.0.0.1:8000/health
curl -f http://127.0.0.1:8000/version

echo "=== LFC deploy completed ==="
