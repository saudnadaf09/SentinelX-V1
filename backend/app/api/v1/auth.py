from __future__ import annotations

import uuid
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import client_ip, get_current_user, request_id
from app.api.serializers import user_out
from app.core import security
from app.core.config import get_settings
from app.core.errors import RateLimited, Unauthorized
from app.core.ratelimit import limiter
from app.db.base import utcnow
from app.db.session import get_db
from app.models import RefreshToken, User
from app.schemas.api import LoginIn, PasswordChangeIn, RefreshIn
from app.services import audit

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue(db: Session, user: User) -> dict:
    access = security.create_access_token(user.id)
    refresh, jti, exp = security.create_refresh_token(user.id)
    db.add(RefreshToken(jti=jti, user_id=user.id, expires_at=exp))
    s = get_settings()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer",
            "expires_in": s.access_token_minutes * 60, "user": user_out(user)}


@router.post("/login")
def login(body: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = client_ip(request)
    if not limiter.allow(f"login:{ip}", get_settings().login_rate_per_minute):
        raise RateLimited("too many login attempts; try again in a minute")
    user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    ok = security.verify_password(body.password, user.password_hash if user else None)
    if not ok or user is None or not user.is_active:
        audit.record(db, actor=None, actor_email=body.email.strip().lower()[:320], action="auth.login",
                     outcome="failure", request_id=request_id(request), client_ip=ip)
        db.commit()
        raise Unauthorized("invalid email or password")
    if security.needs_rehash(user.password_hash):
        user.password_hash = security.hash_password(body.password)
    user.last_login_at = utcnow()
    out = _issue(db, user)
    audit.record(db, actor=user, action="auth.login", request_id=request_id(request), client_ip=ip)
    db.commit()
    return out


@router.post("/refresh")
def refresh(body: RefreshIn, request: Request, db: Session = Depends(get_db)):
    try:
        payload = security.decode_token(body.refresh_token, "refresh")
        row = db.get(RefreshToken, payload["jti"])
        user = db.get(User, uuid.UUID(payload["sub"]))
    except (jwt.PyJWTError, ValueError, KeyError):
        raise Unauthorized("invalid refresh token") from None
    if row is None or row.revoked_at is not None or row.expires_at <= datetime.now(timezone.utc) \
            or user is None or not user.is_active:
        raise Unauthorized("invalid refresh token")
    row.revoked_at = utcnow()  # rotation: each refresh token works once
    out = _issue(db, user)
    audit.record(db, actor=user, action="auth.refresh", request_id=request_id(request), client_ip=client_ip(request))
    db.commit()
    return out


@router.post("/logout")
def logout(body: RefreshIn, request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        payload = security.decode_token(body.refresh_token, "refresh")
        row = db.get(RefreshToken, payload["jti"])
        if row and row.user_id == user.id and row.revoked_at is None:
            row.revoked_at = utcnow()
    except jwt.PyJWTError:
        pass
    audit.record(db, actor=user, action="auth.logout", request_id=request_id(request), client_ip=client_ip(request))
    db.commit()
    return {"ok": True}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user_out(user)


@router.post("/change-password")
def change_password(body: PasswordChangeIn, request: Request, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if not security.verify_password(body.current_password, user.password_hash):
        raise Unauthorized("current password is incorrect")
    try:
        security.validate_password_strength(body.new_password)
    except ValueError as exc:
        from app.core.errors import AppError
        raise AppError(str(exc)) from exc
    user.password_hash = security.hash_password(body.new_password)
    for t in db.scalars(select(RefreshToken).where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))):
        t.revoked_at = utcnow()
    audit.record(db, actor=user, action="auth.password_changed", target_type="user", target_id=str(user.id),
                 request_id=request_id(request), client_ip=client_ip(request))
    db.commit()
    return {"ok": True}
