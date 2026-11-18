from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import request_id, require
from app.api.serializers import action_out
from app.core.errors import NotFound
from app.db.session import get_db
from app.domain.response_actions import CATALOG
from app.models import Asset, ResponseAction, User
from app.schemas.api import ActionProposeIn, DecisionIn
from app.services import response_service

router = APIRouter(prefix="/response", tags=["response"])


def _enrich(db: Session, rows: list[ResponseAction]) -> list[dict]:
    assets = {a.id: a.hostname for a in db.scalars(select(Asset))}
    ids = {r.requested_by for r in rows} | {r.decided_by for r in rows if r.decided_by}
    users = {u.id: u.email for u in db.scalars(select(User).where(User.id.in_(ids)))} if ids else {}
    return [action_out(r, assets.get(r.asset_id), users.get(r.requested_by), users.get(r.decided_by)) for r in rows]


def _get(db: Session, action_id: uuid.UUID) -> ResponseAction:
    a = db.get(ResponseAction, action_id)
    if not a:
        raise NotFound("action not found")
    return a


@router.get("/catalog")
def catalog(user: User = Depends(require("response:read"))):
    return {"items": [{"action_type": k, **v} for k, v in CATALOG.items()], "adapter": "mock"}


@router.get("/actions")
def list_actions(user: User = Depends(require("response:read")), db: Session = Depends(get_db),
                 status: str | None = None, incident_id: uuid.UUID | None = None, size: int = Query(50, ge=1, le=100)):
    stmt = select(ResponseAction).order_by(ResponseAction.created_at.desc()).limit(size)
    if status:
        stmt = stmt.where(ResponseAction.status == status)
    if incident_id:
        stmt = stmt.where(ResponseAction.incident_id == incident_id)
    return {"items": _enrich(db, list(db.scalars(stmt)))}


@router.post("/actions", status_code=201)
def propose(body: ActionProposeIn, request: Request, user: User = Depends(require("response:propose")),
            db: Session = Depends(get_db)):
    act = response_service.propose(db, user, asset_id=body.asset_id, action_type=body.action_type,
                                   parameters=body.parameters, rationale=body.rationale,
                                   incident_id=body.incident_id, idempotency_key=body.idempotency_key,
                                   request_id=request_id(request))
    db.commit()
    return _enrich(db, [act])[0]


@router.post("/actions/{action_id}/approve")
def approve(action_id: uuid.UUID, body: DecisionIn, request: Request, user: User = Depends(require("response:read")),
            db: Session = Depends(get_db)):
    act = response_service.approve(db, user, _get(db, action_id), body.note, request_id(request))
    db.commit()
    return _enrich(db, [act])[0]


@router.post("/actions/{action_id}/reject")
def reject(action_id: uuid.UUID, body: DecisionIn, request: Request, user: User = Depends(require("response:read")),
           db: Session = Depends(get_db)):
    act = response_service.reject(db, user, _get(db, action_id), body.note, request_id(request))
    db.commit()
    return _enrich(db, [act])[0]


@router.post("/actions/{action_id}/rollback")
def rollback(action_id: uuid.UUID, request: Request, user: User = Depends(require("response:read")),
             db: Session = Depends(get_db)):
    act = response_service.rollback(db, user, _get(db, action_id), request_id(request))
    db.commit()
    return _enrich(db, [act])[0]
