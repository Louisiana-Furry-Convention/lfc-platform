import subprocess

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.orm import Session

from lfc_api.core.config import settings
from lfc_api.db.session import SessionLocal

router = APIRouter(tags=["system"])


def get_git_commit() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return "unknown"


def check_database() -> str:
    db: Session = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "error"
    finally:
        db.close()


@router.get("/health")
def health():
    return {
        "ok": True,
        "service": "lfc-platform-api",
        "database": check_database(),
        "environment": settings.app_env,
    }


@router.get("/version")
def version():
    return {
        "ok": True,
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "commit": get_git_commit(),
    }

