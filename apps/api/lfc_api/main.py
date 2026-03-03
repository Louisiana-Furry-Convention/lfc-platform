from fastapi import FastAPI
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from lfc_api.routers import auth_router, events_router, checkin_router, tickets_router, admin_router

app = FastAPI(title="LFC Platform API", version="0.1.0")

# Dev CORS (lock down later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve web UI
WEB_DIR = Path(__file__).resolve().parents[3] / "apps" / "web"
app.mount("/ui", StaticFiles(directory=str(WEB_DIR), html=True), name="ui")

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(checkin_router)
app.include_router(tickets_router)
app.include_router(admin_router)

@app.get("/health")
def health():
    return {"ok": True}
