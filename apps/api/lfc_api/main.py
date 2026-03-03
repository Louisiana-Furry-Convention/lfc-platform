from fastapi import FastAPI
from lfc_api.routers import auth_router, events_router, checkin_router, tickets_router, admin_router

app = FastAPI(title="LFC Platform API", version="0.1.0")

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(checkin_router)
app.include_router(tickets_router)
app.include_router(admin_router)

@app.get("/health")
def health():
    return {"ok": True}
