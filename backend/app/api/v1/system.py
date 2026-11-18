from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session

from app import __version__
from app.api.deps import require
from app.core.config import get_settings
from app.core.container import get_queue, get_registry, get_store
from app.db.session import get_db
from app.models import User
from app.services.ai_service import provider_status

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/health/ready")
def ready(db: Session = Depends(get_db)):
    checks = {}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:  # noqa: BLE001
        checks["database"] = False
    checks["queue"] = bool(get_queue().ping())
    checks["event_store"] = bool(get_store().ping())
    return {"status": "ok" if all(checks.values()) else "degraded", "checks": checks}


@router.get("/settings/system")
def system_settings(user: User = Depends(require("settings:read"))):
    s = get_settings()
    return {"version": __version__, "environment": s.app_env, "queue_backend": s.queue_backend,
            "store_backend": s.store_backend, "event_retention_days": s.event_retention_days,
            "collector_key_ttl_days": s.collector_key_ttl_days, "response_adapter": s.response_adapter,
            "approval_ttl_minutes": s.approval_ttl_minutes, "ai": provider_status(s),
            "correlation_window_seconds": get_registry().correlation_window,
            "active_rules": len(get_registry().engine.rules)}
