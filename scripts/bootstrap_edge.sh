#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/pi/lfc-platform"
API_DIR="${PROJECT_DIR}/apps/api"

echo "=== LFC Edge Bootstrap (pi) ==="

sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl

mkdir -p "${API_DIR}"
cd "${API_DIR}"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Initialize Alembic if needed (repo includes config, so just upgrade)
export DATABASE_URL="${DATABASE_URL:-sqlite:///./lfc_edge.db}"
alembic upgrade head

# Seed baseline (safe to re-run)
python3 seed.py || true

# Create systemd service
sudo tee /etc/systemd/system/lfc-api.service > /dev/null <<EOF
[Unit]
Description=LFC Platform API (Edge)
After=network.target

[Service]
User=pi
WorkingDirectory=${API_DIR}
Environment=DATABASE_URL=sqlite:///./lfc_edge.db
Environment=JWT_SECRET=dev_change_me
ExecStart=${API_DIR}/.venv/bin/uvicorn lfc_api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable lfc-api

echo "Bootstrap complete."
echo "Start with: sudo systemctl start lfc-api"
echo "Health check: curl http://127.0.0.1:8000/health"
