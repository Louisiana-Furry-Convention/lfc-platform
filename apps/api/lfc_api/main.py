from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from lfc_api.db.init_db import init_db
from lfc_api.routers import (
    admin,
    applications,
    attendance,
    auth,
    checkin,
    events,
    me,
    payments,
    rfid,
    tickets,
    system,
    scanner,
)

api_router = APIRouter()

app = FastAPI(
    title="LFC Platform API",
    version="0.2.0",
)

# Ensure DB schema exists before serving requests
init_db()

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
app.include_router(system.router)
app.include_router(scanner.router)
app.include_router(applications.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = Path(__file__).resolve().parents[2] / "web"
app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")


@app.get("/")
def root():
    return FileResponse(str(WEB_DIR / "index.html"))


@app.get("/health")
def health():
    return {"ok": True}
