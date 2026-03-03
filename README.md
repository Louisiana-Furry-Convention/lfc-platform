# LFC Platform (Starter Backbone)

This repo contains a **Pi-first Edge** backbone for:
- Website + Registration + Phone App (future clients)
- One backend API (FastAPI)
- Local **SQLite** for edge/dev on Raspberry Pi 2
- Migration-ready (Alembic) so you can move to **Postgres** later
- Event ledger (`domain_events`) to enable future cloud<->edge sync

## Quick start (Raspberry Pi OS Lite, username `pi`)
1) Clone repo to the Pi:
```bash
cd ~
git clone https://github.com/Thorthedefender/lfc-platform.git
cd lfc-platform
```

2) Bootstrap (installs deps, sets up service):
```bash
chmod +x scripts/bootstrap_edge.sh
./scripts/bootstrap_edge.sh
```

3) Start and check health:
```bash
sudo systemctl start lfc-api
curl http://127.0.0.1:8000/health
```

4) Open API docs:
- `http://PI_IP:8000/docs`

## Day-to-day (Thor workflow)
- Update to latest code + migrate DB + restart:
```bash
scripts/lfc update
```
- Status:
```bash
scripts/lfc status
```
- Logs:
```bash
scripts/lfc logs
```

## Dev notes (Cache workflow)
- Run locally (venv):
```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python3 seed.py
uvicorn lfc_api.main:app --reload
```

## Environment variables
- `DATABASE_URL` (default: `sqlite:///./lfc_edge.db`)
- `JWT_SECRET` (default: `dev_change_me`)

> For production, set `JWT_SECRET` to a strong random value.
