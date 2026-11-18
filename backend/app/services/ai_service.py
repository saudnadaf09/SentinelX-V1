"""AI investigation orchestration. Providers are optional; failures fall back to deterministic analysis."""
from __future__ import annotations

import logging

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.domain import ai_analysis as ai
from app.models import Alert, Investigation, User
from app.services import audit

log = logging.getLogger("sentinelx.ai")


def provider_status(s: Settings) -> dict:
    configured = s.ai_provider != "disabled" and (bool(s.ai_api_key) or s.ai_provider == "openai_compatible")
    return {"provider": s.ai_provider, "model": s.ai_model if configured else None, "configured": configured}


def _call_llm(s: Settings, system: str, user: str) -> str:
    timeout = httpx.Timeout(s.ai_timeout_seconds)
    if s.ai_provider == "anthropic":
        base = (s.ai_base_url or "https://api.anthropic.com").rstrip("/")
        r = httpx.post(f"{base}/v1/messages", timeout=timeout,
                       headers={"x-api-key": s.ai_api_key, "anthropic-version": "2023-06-01",
                                "content-type": "application/json"},
                       json={"model": s.ai_model, "max_tokens": 1500, "system": system,
                             "messages": [{"role": "user", "content": user}]})
        r.raise_for_status()
        return "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")
    if s.ai_provider == "openai_compatible":
        if not s.ai_base_url:
            raise ValueError("AI_BASE_URL is required for openai_compatible")
        headers = {"content-type": "application/json"}
        if s.ai_api_key:
            headers["authorization"] = f"Bearer {s.ai_api_key}"
        r = httpx.post(f"{s.ai_base_url.rstrip('/')}/chat/completions", timeout=timeout, headers=headers,
                       json={"model": s.ai_model, "temperature": 0.2, "max_tokens": 1500,
                             "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    raise ValueError("AI provider disabled")


def _alert_dict(a: Alert) -> dict:
    return {"id": str(a.id), "title": a.title, "severity": a.severity, "status": a.status, "rule_key": a.rule_key,
            "rule_version": a.rule_version, "explanation": a.explanation, "first_seen": a.first_seen.isoformat(),
            "last_seen": a.last_seen.isoformat(), "event_count": a.event_count, "host_name": a.host_name,
            "user_name": a.user_name, "source_ip": a.source_ip, "correlation_reason": a.correlation_reason,
            "rule_context": a.rule_context, "mitre": a.mitre, "evidence": a.evidence}


def investigate(db: Session, s: Settings, user: User, alert: Alert, request_id: str = "") -> Investigation:
    related = []
    if alert.incident_id:
        related = [_alert_dict(r) for r in db.scalars(
            select(Alert).where(Alert.incident_id == alert.incident_id, Alert.id != alert.id).limit(10))]
    package = ai.build_evidence_package(_alert_dict(alert), related)
    allowed_ids = {e["event_id"] for e in package["events"] if e.get("event_id")}
    status = provider_status(s)
    mode, note, output = "deterministic", "No AI provider configured; rule-based analysis shown.", None
    if status["configured"]:
        try:
            text = _call_llm(s, ai.SYSTEM_PROMPT, ai.build_user_prompt(package))
            output, mode, note = ai.validate_output(text, allowed_ids), "llm", ""
        except Exception as exc:  # noqa: BLE001 - provider outage must never break the SIEM
            log.warning("AI provider failed; using deterministic fallback", extra={"error": type(exc).__name__})
            mode, note = "fallback", f"AI provider unavailable ({type(exc).__name__}); rule-based analysis shown."
    if output is None:
        output = ai.deterministic_analysis(package)
    inv = Investigation(alert_id=alert.id, requested_by=user.id, mode=mode,
                        provider=s.ai_provider if mode == "llm" else "none",
                        model=s.ai_model if mode == "llm" else "", prompt_version=ai.PROMPT_VERSION,
                        output=output, note=note)
    db.add(inv)
    db.flush()
    audit.record(db, actor=user, action="ai.investigate", target_type="alert", target_id=str(alert.id),
                 request_id=request_id, details={"mode": mode, "model": inv.model, "prompt": ai.PROMPT_VERSION,
                                                 "investigation": str(inv.id)})
    return inv
