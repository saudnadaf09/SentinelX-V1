from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require
from app.api.serializers import alert_out, asset_out, incident_out
from app.core.container import get_queue, get_store
from app.db.session import get_db
from app.domain.query import EventQuery
from app.models import Alert, Asset, Incident, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(user: User = Depends(require("dashboard:read")), db: Session = Depends(get_db),
             hours: int = Query(24, ge=1, le=168)):
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)
    store = get_store()
    interval = 60 if hours > 6 else 15
    try:
        agg = store.aggregate(start, now + timedelta(minutes=1), interval)
        recent = store.search(EventQuery(start=start, end=now + timedelta(minutes=1), size=10))[1]
        store_ok = True
    except Exception:  # noqa: BLE001 - dashboard must degrade, not fail, if the event store is down
        agg, recent, store_ok = {"total": 0, "timeline": [], "top_hosts": [], "categories": []}, [], False

    sev = dict(db.execute(select(Alert.severity, func.count()).group_by(Alert.severity)).all())
    st = dict(db.execute(select(Alert.status, func.count()).group_by(Alert.status)).all())
    open_inc = list(db.scalars(select(Incident).where(Incident.status != "closed").order_by(Incident.updated_at.desc()).limit(5)))
    counts = dict(db.execute(select(Alert.incident_id, func.count()).where(
        Alert.incident_id.in_([i.id for i in open_inc])).group_by(Alert.incident_id)).all()) if open_inc else {}
    assets = [asset_out(a) for a in db.scalars(select(Asset).order_by(Asset.hostname))]
    return {
        "window_hours": hours, "event_store_available": store_ok,
        "events": {"total": agg["total"], "timeline": agg["timeline"], "top_hosts": agg["top_hosts"],
                   "categories": agg["categories"], "recent": recent},
        "alerts": {"by_severity": sev, "by_status": st, "total": sum(sev.values()),
                   "open": sum(v for k, v in st.items() if k in ("new", "in_review", "escalated")),
                   "latest": [alert_out(a) for a in db.scalars(select(Alert).order_by(Alert.last_seen.desc()).limit(6))]},
        "incidents": {"open": db.scalar(select(func.count()).select_from(Incident).where(Incident.status != "closed")),
                      "items": [incident_out(i, counts.get(i.id, 0)) for i in open_inc]},
        "assets": assets,
        "pipeline": get_queue().stats(),
    }
