"""
ACASO owner authentication - email + password, single owner account.

  * First POST /api/auth/register creates the owner; afterwards registration is closed (403).
  * Login issues a JWT in an httpOnly, Secure, SameSite=Lax cookie (7 days; 30 days with remember_me).
  * Passwords hashed with bcrypt. Password change requires the current password.
  * Global guard (installed by server.py as HTTP middleware): every /api/* request needs a valid session cookie,
    EXCEPT: /api/auth/*, buyer unlock + gated library links, Google Drive OAuth callback, and any request that
    carries a valid X-ACASO-Key (Local Node, Agent Bridge, runner scripts) - those keep working unchanged.
"""
import logging
import os
import re
import secrets
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

logger = logging.getLogger("auth")
router = APIRouter(prefix="/auth")

db = None
get_bridge_key = None
COOKIE = "acaso_session"
ALG = "HS256"


def init(_db, _get_bridge_key):
    global db, get_bridge_key
    db, get_bridge_key = _db, _get_bridge_key


def _secret() -> str:
    s = os.environ.get("JWT_SECRET")
    if not s:
        # never silently run without a secret; generate a process-local one and warn loudly
        s = secrets.token_urlsafe(48)
        os.environ["JWT_SECRET"] = s
        logger.error("JWT_SECRET missing from backend/.env - using an ephemeral secret (sessions reset on restart)")
    return s


def now():
    return datetime.now(timezone.utc)


# Paths that never require a session cookie (prefix match). Key-auth is handled separately by header check.
PUBLIC_PREFIXES = (
    "/api/auth/",
    "/api/apex/unlock/",
    "/api/apex/library/",
    "/api/oauth/drive/callback",
    "/api/health",
    "/api/",  # exact root handled below
)


def is_public(path: str) -> bool:
    if path == "/api/" or path == "/api":
        return True
    return any(path.startswith(p) for p in PUBLIC_PREFIXES[:-1])


def make_token(user: dict, remember: bool) -> tuple[str, int]:
    days = 30 if remember else 7
    exp = now() + timedelta(days=days)
    payload = {"sub": user["id"], "email": user["email"], "role": "owner", "iat": int(now().timestamp()), "exp": int(exp.timestamp()),
               "pv": user.get("password_version", 1)}
    return jwt.encode(payload, _secret(), algorithm=ALG), days * 86400


def read_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, _secret(), algorithms=[ALG])
    except Exception:
        return None


async def user_from_request(request: Request) -> Optional[dict]:
    tok = request.cookies.get(COOKIE)
    if not tok:
        auth = request.headers.get("authorization") or ""
        if auth.lower().startswith("bearer "):
            tok = auth[7:].strip()
    if not tok:
        return None
    claims = read_token(tok)
    if not claims:
        return None
    user = await db.users.find_one({"id": claims.get("sub")}, {"_id": 0})
    if not user or user.get("password_version", 1) != claims.get("pv", 1):
        return None
    return user


async def guard(request: Request, call_next):
    """HTTP middleware: enforce session on /api/* except public paths and valid X-ACASO-Key requests."""
    path = request.url.path
    if not path.startswith("/api") or request.method == "OPTIONS" or is_public(path):
        return await call_next(request)
    key = request.headers.get("x-acaso-key")
    if key:
        try:
            if key == await get_bridge_key():
                request.state.auth = {"kind": "key"}
                return await call_next(request)
        except Exception as e:
            logger.error(f"key check failed: {e}")
    user = await user_from_request(request)
    if user:
        request.state.auth = {"kind": "session", "user_id": user["id"], "email": user["email"]}
        return await call_next(request)
    has_owner = await db.users.count_documents({}) > 0
    from fastapi.responses import JSONResponse
    return JSONResponse({"detail": "Authentication required", "has_owner": has_owner}, status_code=401,
                        headers={"WWW-Authenticate": "Cookie"})


# ----------------------------------------------------------------------------------------------
class Credentials(BaseModel):
    email: str
    password: str
    remember_me: bool = False
    name: Optional[str] = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


def _valid_email(e: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e or ""))


def _check_password_strength(p: str):
    if len(p or "") < 10:
        raise HTTPException(400, "Password must be at least 10 characters")
    if p.lower() == p or p.upper() == p or not re.search(r"\d", p):
        raise HTTPException(400, "Use upper and lower case letters and at least one digit")


def _set_cookie(resp: Response, token: str, max_age: int, request: Request):
    secure = request.url.scheme == "https" or request.headers.get("x-forwarded-proto", "") == "https"
    resp.set_cookie(COOKIE, token, max_age=max_age, httponly=True, secure=secure, samesite="lax", path="/")


def _public_user(u: dict) -> dict:
    return {"id": u["id"], "email": u["email"], "name": u.get("name"), "role": u.get("role", "owner"),
            "created_at": u.get("created_at"), "last_login_at": u.get("last_login_at")}


@router.get("/status")
async def status():
    n = await db.users.count_documents({})
    return {"has_owner": n > 0, "registration_open": n == 0}


@router.post("/register")
async def register(c: Credentials, request: Request, response: Response):
    if await db.users.count_documents({}) > 0:
        raise HTTPException(403, "Registration is closed - the owner account already exists. Log in instead.")
    email = (c.email or "").strip().lower()
    if not _valid_email(email):
        raise HTTPException(400, "Valid email required")
    _check_password_strength(c.password)
    user = {"id": str(uuid.uuid4()), "email": email, "name": (c.name or "").strip()[:80] or None, "role": "owner",
            "password_hash": bcrypt.hashpw(c.password.encode(), bcrypt.gensalt(rounds=12)).decode(), "password_version": 1,
            "created_at": now().isoformat(), "last_login_at": now().isoformat(), "failed_logins": 0}
    await db.users.insert_one(dict(user))
    token, max_age = make_token(user, c.remember_me)
    _set_cookie(response, token, max_age, request)
    await db.auth_events.insert_one({"id": str(uuid.uuid4()), "event": "register", "email": email, "at": now().isoformat(), "ip": request.client.host if request.client else None})
    return {"user": _public_user(user), "session_days": max_age // 86400}


@router.post("/login")
async def login(c: Credentials, request: Request, response: Response):
    email = (c.email or "").strip().lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    ip = request.client.host if request.client else None
    # simple lockout: 8 failures -> 10 minute cool-down
    if user and user.get("locked_until") and datetime.fromisoformat(user["locked_until"]) > now():
        raise HTTPException(423, "Too many failed attempts - try again in a few minutes")
    ok = bool(user) and bcrypt.checkpw((c.password or "").encode(), user["password_hash"].encode())
    if not ok:
        if user:
            fails = int(user.get("failed_logins", 0)) + 1
            upd = {"failed_logins": fails}
            if fails >= 8:
                upd["locked_until"] = (now() + timedelta(minutes=10)).isoformat()
                upd["failed_logins"] = 0
            await db.users.update_one({"id": user["id"]}, {"$set": upd})
        await db.auth_events.insert_one({"id": str(uuid.uuid4()), "event": "login_failed", "email": email, "at": now().isoformat(), "ip": ip})
        raise HTTPException(401, "Invalid email or password")
    await db.users.update_one({"id": user["id"]}, {"$set": {"last_login_at": now().isoformat(), "failed_logins": 0}, "$unset": {"locked_until": ""}})
    token, max_age = make_token(user, c.remember_me)
    _set_cookie(response, token, max_age, request)
    await db.auth_events.insert_one({"id": str(uuid.uuid4()), "event": "login", "email": email, "at": now().isoformat(), "ip": ip})
    return {"user": _public_user(user), "session_days": max_age // 86400}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@router.get("/me")
async def me(request: Request):
    user = await user_from_request(request)
    if not user:
        has_owner = await db.users.count_documents({}) > 0
        raise HTTPException(401, {"detail": "Not logged in", "has_owner": has_owner})
    return _public_user(user)


@router.post("/change-password")
async def change_password(body: ChangePassword, request: Request, response: Response):
    user = await user_from_request(request)
    if not user:
        raise HTTPException(401, "Not logged in")
    if not bcrypt.checkpw(body.current_password.encode(), user["password_hash"].encode()):
        raise HTTPException(400, "Current password is incorrect")
    _check_password_strength(body.new_password)
    if body.new_password == body.current_password:
        raise HTTPException(400, "New password must differ from the current one")
    pv = int(user.get("password_version", 1)) + 1
    await db.users.update_one({"id": user["id"]}, {"$set": {"password_hash": bcrypt.hashpw(body.new_password.encode(), bcrypt.gensalt(rounds=12)).decode(),
                                                            "password_version": pv, "password_changed_at": now().isoformat()}})
    user["password_version"] = pv
    token, max_age = make_token(user, False)  # other sessions are invalidated by the version bump
    _set_cookie(response, token, max_age, request)
    await db.auth_events.insert_one({"id": str(uuid.uuid4()), "event": "password_changed", "email": user["email"], "at": now().isoformat()})
    return {"ok": True, "note": "Password updated. Other devices were signed out."}


@router.get("/events")
async def events(request: Request):
    if not await user_from_request(request):
        raise HTTPException(401, "Not logged in")
    return await db.auth_events.find({}, {"_id": 0}).sort("at", -1).to_list(30)
