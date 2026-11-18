"""Easy Mode launcher: one process, no Docker. Run via run.bat / run.sh.

First run: creates .env with random secrets, creates the database, the admin account,
three demo users, replays synthetic attack data, and writes the logins to DEMO-LOGINS.txt.
Every run: starts the server (API + web UI) and opens your browser.
"""
from __future__ import annotations

import os
import secrets
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
os.chdir(HERE)
sys.path.insert(0, str(HERE))

ENV = HERE / ".env"
DATA = HERE / "data"
MARKER = DATA / ".initialized"
LOGINS = ROOT / "DEMO-LOGINS.txt"


def write_env() -> str:
    admin_pw = secrets.token_urlsafe(12)
    ENV.write_text("\n".join([
        "APP_ENV=development",
        f"SECRET_KEY={secrets.token_hex(32)}",
        "DATABASE_URL=sqlite:///./data/sentinelx.db",
        "QUEUE_BACKEND=memory",
        "STORE_BACKEND=sqlite",
        "EVENTS_DB_PATH=./data/events.db",
        "CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000",
        "BOOTSTRAP_ADMIN_EMAIL=admin@sentinelx.local",
        f"BOOTSTRAP_ADMIN_PASSWORD={admin_pw}",
        "AI_PROVIDER=disabled",
        "AI_API_KEY=",
        "FRONTEND_DIST=../frontend/dist",
        "RULES_DIR=../detection-rules",
        "",
    ]), encoding="utf-8")
    return admin_pw


def free_port(start: int) -> int:
    for port in range(start, start + 20):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise SystemExit("No free port between 8000 and 8019. Close other programs and retry.")


def first_run_setup() -> None:
    from sqlalchemy import select

    from app.cli import cmd_bootstrap, cmd_replay
    from app.core import security
    from app.db.session import get_session_factory
    from app.models import User

    print("First-time setup: creating admin, demo users and demo data...")
    cmd_bootstrap(None)
    lines = [f"ADMIN   admin@sentinelx.local   {os.environ.get('BOOTSTRAP_ADMIN_PASSWORD') or read_env('BOOTSTRAP_ADMIN_PASSWORD')}"]
    with get_session_factory()() as db:
        for role in ("analyst", "engineer", "viewer"):
            email = f"{role}@sentinelx.local"
            if db.scalar(select(User).where(User.email == email)):
                continue
            pw = secrets.token_urlsafe(12)
            db.add(User(email=email, full_name=f"Demo {role.title()}", role=role,
                        password_hash=security.hash_password(pw)))
            lines.append(f"{role.upper():<8}{email:<28}{pw}")
        db.commit()
    LOGINS.write_text(
        "SentinelX logins (local lab only - keep this file private, do not upload it)\n"
        "Open: http://localhost:8000\n\n" + "\n".join(lines) + "\n", encoding="utf-8")

    class Args:  # replay synthetic scenario with fresh, recent timestamps
        file = None
    cmd_replay(Args())
    MARKER.write_text("ok")
    print(f"Done. Your logins are saved in: {LOGINS}")


def read_env(key: str) -> str:
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()
    return ""


def main() -> None:
    DATA.mkdir(exist_ok=True)
    if not ENV.exists():
        write_env()
    if not (ROOT / "frontend" / "dist" / "index.html").exists():
        print("NOTE: the web UI is not built (frontend/dist missing). Only the API will run.\n"
              "      Install Node.js and run run.bat / run.sh again to build it.")

    from alembic import command
    from alembic.config import Config

    cfg = Config(str(HERE / "alembic.ini"))
    cfg.set_main_option("script_location", str(HERE / "alembic"))
    command.upgrade(cfg, "head")

    if not MARKER.exists():
        first_run_setup()

    port = free_port(int(os.environ.get("PORT", "8000")))
    url = f"http://localhost:{port}"
    print("\n" + "=" * 60)
    print(f" SentinelX is starting:  {url}")
    print(f" API docs:               {url}/api/docs")
    print(f" Logins:                 {LOGINS}")
    print(" Stop the server: press Ctrl+C in this window")
    print("=" * 60 + "\n")
    threading.Thread(target=lambda: (time.sleep(3), webbrowser.open(url)), daemon=True).start()

    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
