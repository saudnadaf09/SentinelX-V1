"""Role -> permission matrix. Enforced server-side by api.deps.require()."""
from __future__ import annotations

ROLES = ("admin", "analyst", "engineer", "viewer")

_VIEWER = {"events:read", "alerts:read", "incidents:read", "assets:read", "response:read",
           "reports:read", "mitre:read", "dashboard:read"}
_ANALYST = _VIEWER | {"alerts:write", "incidents:write", "ai:use", "response:propose", "hunt:run", "rules:read"}
_ENGINEER = _VIEWER | {"rules:read", "rules:write", "assets:write", "keys:manage", "response:propose",
                       "response:approve", "hunt:run"}
_ADMIN = _ANALYST | _ENGINEER | {"users:manage", "audit:read", "settings:read", "response:approve"}

PERMISSIONS: dict[str, frozenset[str]] = {
    "viewer": frozenset(_VIEWER), "analyst": frozenset(_ANALYST),
    "engineer": frozenset(_ENGINEER), "admin": frozenset(_ADMIN),
}


def has_permission(role: str, permission: str) -> bool:
    return permission in PERMISSIONS.get(role, frozenset())
