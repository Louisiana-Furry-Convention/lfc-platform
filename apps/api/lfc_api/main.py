from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from lfc_api.routers import auth, events, tickets, checkin, admin, me, attendance, rfid, payments

app = FastAPI(title="LFC Platform API", version="0.1.3")

# Routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(checkin.router)
app.include_router(admin.router)
app.include_router(me.router)
app.include_router(attendance.router)
app.include_router(rfid.router)
app.include_router(payments.router)

# Dev CORS (lock down later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the web UI (apps/web/index.html) at /
WEB_DIR = Path(__file__).resolve().parents[2] / "web"   # -> apps/web
app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

@app.get("/")
def root():
    return FileResponse(str(WEB_DIR / "index.html"))

@app.get("/health")
def health():
    return {"ok": True}

