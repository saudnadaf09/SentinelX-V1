from __future__ import annotations

import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import client_ip, request_id, require
from app.api.serializers import asset_out, key_out
from app.core import security
from app.core.config import get_settings
from app.core.errors import Conflict, NotFound
from app.db.base import utcnow
from app.db.session import get_db
from app.models import ApiKey, Asset, User
from app.schemas.api import AssetRegisterIn, KeyCreateIn
from app.services import audit

router = APIRouter(tags=["assets"])


@router.get("/assets")
def list_assets(user: User = Depends(require("assets:read")), db: Session = Depends(get_db)):
    return {"items": [asset_out(a) for a in db.scalars(select(Asset).order_by(Asset.hostname))]}


@router.post("/assets/register", status_code=201)
def register(body: AssetRegisterIn, request: Request, user: User = Depends(require("assets:write")),
             db: Session = Depends(get_db)):
    if not body.authorized:
        raise Conflict("you must confirm you are authorized to monitor this system")
    if db.scalar(select(Asset).where(Asset.hostname == body.hostname)):
        raise Conflict("an asset with this hostname already exists")
    a = Asset(hostname=body.hostname, platform=body.platform, owner=body.owner, tags=body.tags,
              is_lab_authorized=True, created_by=user.id)
    db.add(a)
    db.flush()
    audit.record(db, actor=user, action="asset.registered", target_type="asset", target_id=str(a.id),
                 request_id=request_id(request), client_ip=client_ip(request),
                 details={"hostname": a.hostname, "platform": a.platform})
    db.commit()
    return asset_out(a)


def _asset(db: Session, asset_id: uuid.UUID) -> Asset:
    a = db.get(Asset, asset_id)
    if not a:
        raise NotFound("asset not found")
    return a


@router.get("/assets/{asset_id}/keys")
def list_keys(asset_id: uuid.UUID, user: User = Depends(require("keys:manage")), db: Session = Depends(get_db)):
    _asset(db, asset_id)
    return {"items": [key_out(k) for k in db.scalars(
        select(ApiKey).where(ApiKey.asset_id == asset_id).order_by(ApiKey.created_at.desc()))]}


@router.post("/assets/{asset_id}/keys", status_code=201)
def create_key(asset_id: uuid.UUID, body: KeyCreateIn, request: Request, user: User = Depends(require("keys:manage")),
               db: Session = Depends(get_db)):
    _asset(db, asset_id)
    full, prefix, digest = security.generate_api_key()
    ttl = body.ttl_days or get_settings().collector_key_ttl_days
    k = ApiKey(asset_id=asset_id, name=body.name, prefix=prefix, key_hash=digest, created_by=user.id,
               expires_at=utcnow() + timedelta(days=ttl))
    db.add(k)
    db.flush()
    audit.record(db, actor=user, action="apikey.created", target_type="api_key", target_id=str(k.id),
                 request_id=request_id(request), client_ip=client_ip(request),
                 details={"asset": str(asset_id), "prefix": prefix, "ttl_days": ttl})
    db.commit()
    return {**key_out(k), "api_key": full, "notice": "Copy this key now. It is shown only once."}


@router.post("/assets/keys/{key_id}/revoke")
def revoke_key(key_id: uuid.UUID, request: Request, user: User = Depends(require("keys:manage")),
               db: Session = Depends(get_db)):
    k = db.get(ApiKey, key_id)
    if not k:
        raise NotFound("key not found")
    if k.revoked_at is None:
        k.revoked_at = utcnow()
        audit.record(db, actor=user, action="apikey.revoked", target_type="api_key", target_id=str(k.id),
                     request_id=request_id(request), client_ip=client_ip(request))
        db.commit()
    return key_out(k)
