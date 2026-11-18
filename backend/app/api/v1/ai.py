from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import request_id, require
from app.api.serializers import investigation_out
from app.core.config import get_settings
from app.core.errors import NotFound
from app.core.ratelimit import limiter
from app.core.errors import RateLimited
from app.db.session import get_db
from app.models import Alert, Investigation, User
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status")
def status(user: User = Depends(require("alerts:read"))):
    return ai_service.provider_status(get_settings())


@router.post("/investigate/{alert_id}", status_code=201)
def investigate(alert_id: uuid.UUID, request: Request, user: User = Depends(require("ai:use")),
                db: Session = Depends(get_db)):
    if not limiter.allow(f"ai:{user.id}", 20):
        raise RateLimited("too many investigation requests; try again in a minute")
    alert = db.get(Alert, alert_id)
    if not alert:
        raise NotFound("alert not found")
    inv = ai_service.investigate(db, get_settings(), user, alert, request_id(request))
    db.commit()
    return investigation_out(inv)


@router.get("/investigations")
def history(user: User = Depends(require("alerts:read")), db: Session = Depends(get_db),
            alert_id: uuid.UUID | None = None, size: int = Query(25, ge=1, le=100)):
    stmt = select(Investigation).order_by(Investigation.created_at.desc()).limit(size)
    if alert_id:
        stmt = stmt.where(Investigation.alert_id == alert_id)
    rows = list(db.scalars(stmt))
    titles = {a.id: a.title for a in db.scalars(select(Alert).where(Alert.id.in_([r.alert_id for r in rows])))} if rows else {}
    return {"items": [{**investigation_out(r), "alert_title": titles.get(r.alert_id)} for r in rows]}
