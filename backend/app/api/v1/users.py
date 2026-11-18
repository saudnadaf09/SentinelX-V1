from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import client_ip, request_id, require
from app.api.serializers import user_out
from app.core import security
from app.core.errors import AppError, Conflict, NotFound
from app.db.session import get_db
from app.models import User
from app.schemas.api import UserCreateIn, UserUpdateIn
from app.services import audit

router = APIRouter(prefix="/users", tags=["users"])


def _pw(pw: str) -> str:
    try:
        security.validate_password_strength(pw)
    except ValueError as exc:
        raise AppError(str(exc)) from exc
    return security.hash_password(pw)


@router.get("")
def list_users(admin: User = Depends(require("users:manage")), db: Session = Depends(get_db)):
    return {"items": [user_out(u) for u in db.scalars(select(User).order_by(User.created_at))]}


@router.get("/directory")
def directory(user: User = Depends(require("alerts:read")), db: Session = Depends(get_db)):
    """Minimal list for assignment dropdowns (no permissions or hashes)."""
    return {"items": [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role}
                      for u in db.scalars(select(User).where(User.is_active.is_(True)).order_by(User.email))]}


@router.post("", status_code=201)
def create_user(body: UserCreateIn, request: Request, admin: User = Depends(require("users:manage")),
                db: Session = Depends(get_db)):
    email = body.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise Conflict("a user with this email already exists")
    u = User(email=email, full_name=body.full_name, role=body.role, password_hash=_pw(body.password))
    db.add(u)
    db.flush()
    audit.record(db, actor=admin, action="user.created", target_type="user", target_id=str(u.id),
                 request_id=request_id(request), client_ip=client_ip(request), details={"role": u.role, "email": email})
    db.commit()
    return user_out(u)


@router.patch("/{user_id}")
def update_user(user_id: uuid.UUID, body: UserUpdateIn, request: Request,
                admin: User = Depends(require("users:manage")), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise NotFound("user not found")
    admins = db.scalar(select(func.count()).select_from(User).where(User.role == "admin", User.is_active.is_(True)))
    demoting = u.role == "admin" and ((body.role and body.role != "admin") or body.is_active is False)
    if demoting and admins <= 1:
        raise Conflict("cannot remove or deactivate the last active admin")
    if u.id == admin.id and body.is_active is False:
        raise Conflict("you cannot deactivate your own account")
    changes = {}
    if body.full_name is not None:
        u.full_name = body.full_name
    if body.role and body.role != u.role:
        changes["role"] = [u.role, body.role]
        u.role = body.role
    if body.is_active is not None and body.is_active != u.is_active:
        changes["is_active"] = body.is_active
        u.is_active = body.is_active
    if body.password:
        u.password_hash = _pw(body.password)
        changes["password_reset"] = True
    audit.record(db, actor=admin, action="user.updated", target_type="user", target_id=str(u.id),
                 request_id=request_id(request), client_ip=client_ip(request), details=changes)
    db.commit()
    return user_out(u)
