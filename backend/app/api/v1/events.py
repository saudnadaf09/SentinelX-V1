from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require
from app.core.container import get_store
from app.core.errors import AppError, NotFound
from app.db.session import get_db
from app.domain.query import EventQuery, Filter, QueryError
from app.models import SavedQuery, User
from app.schemas.api import HuntIn, SavedQueryIn

router = APIRouter(tags=["events"])


def _run(q: EventQuery) -> dict:
    try:
        total, hits = get_store().search(q.validate())
    except QueryError as exc:
        raise AppError(str(exc)) from exc
    return {"total": total, "page": q.page, "size": q.size, "items": hits}


@router.get("/events")
def list_events(user: User = Depends(require("events:read")),
                start: datetime | None = None, end: datetime | None = None, q: str | None = Query(None, max_length=200),
                host: str | None = Query(None, max_length=255), user_name: str | None = Query(None, max_length=255),
                source_ip: str | None = Query(None, max_length=64), action: str | None = Query(None, max_length=64),
                dataset: str | None = Query(None, max_length=64), category: str | None = Query(None, max_length=64),
                page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=100)):
    end = end or datetime.now(timezone.utc) + timedelta(minutes=1)
    start = start or end - timedelta(hours=24)
    pairs = [("host.name", host), ("user.name", user_name), ("source.ip", source_ip), ("event.action", action),
             ("event.dataset", dataset), ("event.category", category)]
    filters = [Filter(f, "eq", v) for f, v in pairs if v]
    return _run(EventQuery(start=start, end=end, filters=filters, text=q, page=page, size=size))


@router.get("/events/{event_id}")
def get_event(event_id: str, user: User = Depends(require("events:read"))):
    doc = get_store().get(event_id)
    if not doc:
        raise NotFound("event not found (it may have been removed by retention)")
    return doc


@router.post("/hunt/search")
def hunt(body: HuntIn, user: User = Depends(require("hunt:run"))):
    return _run(EventQuery(start=body.start, end=body.end, text=body.text, page=body.page, size=body.size,
                           filters=[Filter(f.field, f.op, f.value) for f in body.filters]))


@router.get("/hunt/saved")
def saved(user: User = Depends(require("hunt:run")), db: Session = Depends(get_db)):
    rows = db.scalars(select(SavedQuery).where(SavedQuery.owner_id == user.id).order_by(SavedQuery.created_at.desc()))
    return {"items": [{"id": r.id, "name": r.name, "definition": r.definition, "created_at": r.created_at} for r in rows]}


@router.post("/hunt/saved", status_code=201)
def save_query(body: SavedQueryIn, user: User = Depends(require("hunt:run")), db: Session = Depends(get_db)):
    row = SavedQuery(owner_id=user.id, name=body.name, definition=body.definition)
    db.add(row)
    db.commit()
    return {"id": row.id, "name": row.name, "definition": row.definition, "created_at": row.created_at}


@router.delete("/hunt/saved/{query_id}", status_code=204)
def delete_saved(query_id: str, user: User = Depends(require("hunt:run")), db: Session = Depends(get_db)):
    import uuid
    try:
        row = db.get(SavedQuery, uuid.UUID(query_id))
    except ValueError:
        raise NotFound("saved query not found") from None
    if not row or row.owner_id != user.id:  # object-level check: owners only
        raise NotFound("saved query not found")
    db.delete(row)
    db.commit()
