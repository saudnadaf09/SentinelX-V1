from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import client_ip, request_id, require
from app.core.container import get_registry
from app.core.errors import AppError, NotFound
from app.db.session import get_db
from app.domain import mitre
from app.domain.rule_loader import parse_yaml_rule
from app.domain.rules import RuleError
from app.models import DetectionRule, User
from app.schemas.api import RulePatchIn, RuleYamlIn
from app.services import audit, rule_service

router = APIRouter(prefix="/rules", tags=["rules"])


def _out(r: DetectionRule, with_source: bool = False) -> dict:
    d = r.definition or {}
    out = {"id": r.id, "rule_key": r.rule_key, "title": r.title, "version": r.version, "severity": r.severity,
           "type": r.rule_type, "enabled": r.enabled, "origin": r.origin, "author": r.author,
           "updated_at": r.updated_at, "tags": d.get("tags", []), "description": d.get("description", ""),
           "mitre": mitre.resolve(d.get("mitre", []))}
    if with_source:
        out["yaml"] = r.yaml_source
    return out


@router.get("")
def list_rules(user: User = Depends(require("rules:read")), db: Session = Depends(get_db)):
    return {"items": [_out(r) for r in db.scalars(select(DetectionRule).order_by(DetectionRule.rule_key))]}


@router.post("/validate")
def validate(body: RuleYamlIn, user: User = Depends(require("rules:write"))):
    try:
        _, rule = parse_yaml_rule(body.yaml)
    except RuleError as exc:
        return {"valid": False, "error": str(exc)}
    return {"valid": True, "rule_key": rule.key, "type": rule.type, "severity": rule.severity}


@router.get("/{rule_id}")
def get_rule(rule_id: uuid.UUID, user: User = Depends(require("rules:read")), db: Session = Depends(get_db)):
    r = db.get(DetectionRule, rule_id)
    if not r:
        raise NotFound("rule not found")
    return _out(r, with_source=True)


@router.post("", status_code=201)
def create_rule(body: RuleYamlIn, request: Request, user: User = Depends(require("rules:write")),
                db: Session = Depends(get_db)):
    try:
        row = rule_service.upsert_rule_from_yaml(db, user, body.yaml, request_id(request))
    except RuleError as exc:
        raise AppError(str(exc)) from exc
    db.commit()
    get_registry().reload()
    return _out(row, with_source=True)


@router.patch("/{rule_id}")
def patch_rule(rule_id: uuid.UUID, body: RulePatchIn, request: Request, user: User = Depends(require("rules:write")),
               db: Session = Depends(get_db)):
    r = db.get(DetectionRule, rule_id)
    if not r:
        raise NotFound("rule not found")
    if body.yaml:
        try:
            _, parsed = parse_yaml_rule(body.yaml)
            if parsed.key != r.rule_key:
                raise AppError("rule id in YAML must match the rule being edited")
            rule_service.upsert_rule_from_yaml(db, user, body.yaml, request_id(request))
        except RuleError as exc:
            raise AppError(str(exc)) from exc
    if body.enabled is not None and body.enabled != r.enabled:
        r.enabled = body.enabled
        audit.record(db, actor=user, action="rule.enabled" if body.enabled else "rule.disabled", target_type="rule",
                     target_id=r.rule_key, request_id=request_id(request), client_ip=client_ip(request))
    db.commit()
    get_registry().reload()
    return _out(r, with_source=True)
