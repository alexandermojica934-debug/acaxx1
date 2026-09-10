# ACASO Omniverse — Complete Handoff

_Generated: 2026-09-10T04:20:16.380983+00:00_

## What this is
A contest-ready **Directive-to-Payment Operating System** (FastAPI + React + MongoDB).

## Features
- Directive-to-Payment mission compiler (Make/Find/Move/Collect) with staged pipeline
- Bug Bounty engagements: compile, run, owner-approval gates, disclosure report
- Soul Council: 3 souls across OpenAI + Gemini + Anthropic, Round-2 debate/rebuttals, Eternal Throne synthesis, Dissent & Reconciliation, PR-ready Fix Export
- Ask All AIs multi-model answers + synthesis
- Agent Bridge: X-ACASO-Key protected agent API (directive/list/run)
- Real object storage: mission Evidence & Media attachments (upload/list/download/delete)
- File Analyzer: upload files OR a whole folder -> real object storage -> AI analysis + follow-up chat grounded in the files
- Self-Directive: PREVIEW-ONLY, approval-gated self-editing (propose unified diff -> approve/apply with compile+import validation & snapshot -> rollback), audited
- File Analyzer follow-up chat: grounded answers that cite exact `path:line` (clickable -> opens a file viewer that highlights the line) and quote snippets
- Analysis Export: one-click download of the analysis + chat thread + file list as a Markdown report
- Google Drive ingestion (user OAuth): connect, browse, SEARCH by name, import selected files OR an entire folder (recursive) in one click, auto-analyzes after import. Requires user-supplied Web-app OAuth client.
- Council of Weavers deliberation engine (POST /api/acaso/deliberate): Architect(Gemini)/Shadow(Claude, veto)/Muse(GPT)/Finance(GPT) in parallel -> Meta-Weaver synthesis -> Sovereign Directive + inferred weak signals; journaled, exportable to .md; presets Genesis Engine / Sovereign Hunter / Foresight Thesis; runner scripts in handoff/scripts. LLM reasoning only - no live market/lead data.
- Voice Channel: browser Web Speech API (STT+TTS, no keys, no audio to server) -> POST /api/voice/chat; hands-free loop / push-to-talk / text-first modes; per-message Fast (GPT-4o-mini w/ session memory) or Council (full deliberation + spoken summary); transcript persisted per session.
- Directive-to-Mission: POST /api/acaso/deliberations/{id}/to-mission compiles a Council directive into a Sovereign Home mission (idempotent, source_deliberation_id).
- Global VoiceCommander: floating mic on every tab - Dictate mode types into the focused text box (native-setter injection so React state updates); Command mode -> POST /api/voice/command (rule-based + LLM intent router: open_tab, council_deliberate, compile_directive, radar_discover, radar_search, ask) executes and speaks back.
- Opportunity Radar (backend/radar.py, /api/radar/*): REAL sources Grants.gov public API (no key), GitHub bounty issues, SAM.gov (needs SAM_GOV_API_KEY); adapters fetch->normalize->validate->dedupe->barrier signals->transparent 0-100 score (8 weighted components, labelled inferred)->persist->stale marking; every record has source_url/retrieved_at/http_status/parser_version/evidence[] with source_location; Fit Analyst + Skeptic (gates Strong fit) + Compliance Sentinel on demand; NL search proposes filters never auto-applied; Drafting Desk (email/grant narrative/outreach packet/fill-a-form) uses only profile + source text with [FILL] placeholders; Add-to-pipeline -> mission; export .md. Nothing auto-submitted.
- Periodic self-scan (Self-Directive): in-process asyncio scheduler, off by default; deterministic checks (py_compile, ruff F/E9, esbuild per component, TODO/console.log census) -> at most ONE Self-Directive proposal per run tagged origin=scheduled_scan; NEVER auto-applies; UI toggle/interval/focus/Scan now/history.
- Local Node (backend/node.py + handoff/local_node/acaso_node.py, served at /local-node/*): owner runs the Python client on their PC (Windows/Linux), pairs with the Agent Bridge key; server holds an approval-gated task queue (read-only auto-approved; every write/shell/browser action must be approved in the Local Node tab); node enforces allowed roots, backs up overwritten files, soft-deletes to .acaso_trash; browser tasks drive a real headed Chrome (persistent profile) via Playwright, fill forms and STOP (awaiting_submit) until a separate browser_submit is approved; secrets written as [OWNER TYPES THIS]. LLM planner turns a goal into proposed tasks. Server research browser (headless Chromium, /api/browse/research) reads public pages: text/links/forms/screenshot + quoted answer.
- Companion (/?mode=companion, header Companion button opens popup; components/Companion.js): voice hands-free, share window/tab/screen via getDisplayMedia, per-message frame -> POST /api/companion/chat (SSE, vision via emergentintegrations ImageContent, gpt-4o-mini -> gemini-2.5-flash). WATCH MODE: 30s glance loop with 16x16 frame-hash change filter -> POST /api/companion/watch -> speaks only for error/form/action (JSON verdict). Installable PWA: /companion.webmanifest swapped in companion mode + Install button; Local Node --companion opens Chrome --app window (separate profile) with best-effort always-on-top (Windows ctypes / Linux wmctrl). Frames never stored.
- Apex Nexus (backend/apex.py, /api/apex/*, tab Apex Nexus): products rfp_kit ($149, from Radar opportunity or pasted RFP), prompt_library ($49, Markdown+JSON+gated API key), seo_pack ($199); POST /generate (one LLM call, [FILL] placeholders counted), deliverables export md/json, orders (pending_payment -> paid -> unlock via /api/apex/unlock/{token}; 402 until paid; refunded re-locks), gated /api/apex/library/{id}?key= requires paid order. Payments: STRIPE NOT CONNECTED (manual Mark paid) until owner supplies STRIPE_API_KEY - integrate via playbook then.
- Owner authentication (backend/auth.py): single owner account - first POST /api/auth/register creates it, then 403; bcrypt (12 rounds); JWT in httpOnly SameSite=Lax cookie acaso_session (7d, 30d remember_me; Secure over https); password change bumps password_version -> all other sessions invalid; 8 failed logins -> 10 min lockout (423); auth_events audit. Global HTTP middleware guards every /api/* route except /api/auth/*, /api/apex/unlock/*, /api/apex/library/*, /api/oauth/drive/callback, and requests carrying a valid X-ACASO-Key (Local Node, Agent Bridge, runner scripts unchanged). JWT_SECRET lives in backend/.env. Frontend: AuthScreen gate, AccountMenu (change password / sign out), axios 401 interceptor -> sign-in.

## Tech & Integrations
- Backend: FastAPI + Motor (MongoDB), Pydantic, UUID ids, timezone-aware UTC.
- Frontend: React (CRACO), Shadcn UI, lucide-react, framer-motion, sonner.
- LLM: `emergentintegrations` via platform `EMERGENT_LLM_KEY` (OpenAI/Gemini/Anthropic).
- Object storage: Emergent Integration Proxy (`INTEGRATION_PROXY_URL`), backend-proxied downloads.

### Models in use
- openai: `gpt-4o-mini`
- gemini: `gemini-3.6-flash`
- anthropic: `claude-haiku-4-5`

## Environment (DO NOT COMMIT REAL VALUES)
```
backend/.env: MONGO_URL, DB_NAME, EMERGENT_LLM_KEY, INTEGRATION_PROXY_URL, CORS_ORIGINS
frontend/.env: REACT_APP_BACKEND_URL
```
All backend routes are prefixed `/api`. Never hardcode URLs; use env vars.

## Run
```
sudo supervisorctl restart backend frontend
```
Hot-reload is enabled; restart only after dependency/.env changes.

## Key API Endpoints
- `POST /api/auth/register (first only) | /api/auth/login | /api/auth/logout | /api/auth/change-password` — owner auth
- `GET /api/auth/status | /api/auth/me | /api/auth/events` — auth state / audit
- `POST /api/companion/chat (SSE) | /api/companion/watch | GET/DELETE /api/companion/history` — Companion vision chat + watch mode
- `GET /api/apex/products | /api/apex/deliverables[/{id}[/export?fmt=md|json]]` — Apex catalog + deliverables
- `POST/PATCH /api/apex/generate | /api/apex/orders[/{id}]` — generate product / order lifecycle
- `GET /api/apex/unlock/{token}[?fmt=md|json|status] | /api/apex/library/{id}?key=` — buyer unlock (public) / gated prompt API
- `GET/PUT /api/self/scan/config | POST /api/self/scan/run | GET /api/self/scans` — periodic self-scan (propose-only)
- `POST /api/node/register | /api/node/{id}/heartbeat | /api/node/{id}/claim | /api/node/tasks/{tid}/result` — node-side (X-ACASO-Key)
- `GET /api/node/nodes | /api/node/tasks | /api/node/setup` — owner-side node + queue
- `POST /api/node/tasks | /api/node/tasks/{tid}/decision | /api/node/plan` — create / approve-reject / LLM plan
- `POST /api/browse/research` — server headless browser: public page -> text, links, forms, screenshot, quoted answer
- `POST /api/voice/command` — spoken command -> intent -> execute -> {navigate_tab, spoken, result}
- `POST /api/acaso/deliberations/{id}/to-mission` — Council directive -> Sovereign Home mission
- `GET/PUT /api/radar/profile` — Radar owner profile
- `POST /api/radar/discover` — run source adapters {sources?, keyword?, limit}
- `GET /api/radar/opportunities[?type&source&min_score&closing_days&low_barrier&remote&max_value&q&saved&sort]` — scored feed
- `GET/PATCH /api/radar/opportunities/{id}` — detail / status-stage-notes
- `POST /api/radar/opportunities/{id}/analyze|draft|to-mission` — AI personas / drafting desk / pipeline
- `POST /api/radar/search/nl` — natural language -> proposed filters
- `POST /api/voice/chat` — voice turn: {message, session_id, mode: fast|council} -> spoken reply (+full directive in council mode)
- `GET/DELETE /api/voice/history?session_id=` — voice transcript per session
- `GET /api/acaso/presets` — council presets (genesis/hunter/foresight)
- `POST /api/acaso/deliberate` — run Council of Weavers -> sovereign_directive, weak_signals, weavers, council_consulted
- `GET /api/acaso/deliberations[/{id}][/export]` — list / open / export .md a deliberation
- `POST /api/compile-directive` — compile a revenue directive into a mission
- `POST /api/compile-bounty` — compile a bug-bounty engagement
- `GET /api/missions?kind=bugbounty` — list engagements
- `POST /api/missions/{mid}/deploy-souls` — Soul Council + debate + Throne verdict
- `POST /api/missions/{mid}/attachments` — upload real evidence file (object storage)
- `GET /api/missions/{mid}/attachments` — list attachments
- `GET /api/attachments/{fid}/download` — download attachment (backend-proxied)
- `DELETE /api/attachments/{fid}` — soft-delete attachment
- `POST /api/filesets` — create a File Analyzer set
- `POST /api/filesets/{fsid}/files` — upload a file (folder upload sends many)
- `POST /api/filesets/{fsid}/analyze` — AI analysis of the set
- `POST /api/filesets/{fsid}/chat` — follow-up chat grounded in the files
- `GET /api/self/manifest` — allowlisted source manifest (preview_only=true)
- `POST /api/self/propose` — generate a unified-diff patch proposal
- `POST /api/self/apply` — approve+apply (compile & import validated, snapshot)
- `POST /api/self/rollback` — restore snapshot
- `GET /api/drive/status` — Drive configured/connected status
- `GET /api/drive/connect` — returns Google OAuth authorization_url
- `GET /api/oauth/drive/callback` — OAuth callback -> stores tokens, redirects to app
- `GET /api/drive/list?folder_id=root` — list Drive folders/files
- `POST /api/drive/import` — import selected Drive files into an analysis set
- `POST /api/drive/import-folder` — import all supported files in a Drive folder (recursive)
- `GET /api/filesets/{fsid}/file?path=` — file content by rel_path (citation-jump viewer)
- `GET /api/filesets/{fsid}/export` — download analysis + chat as Markdown
- `POST /api/drive/disconnect` — revoke + delete stored Drive tokens
- `GET /api/agent/info` — Agent Bridge info

## Verified (live)
- OpenAI gpt-4o-mini, Gemini gemini-3.6-flash, Anthropic claude-haiku-4-5 all respond
- Object storage init/upload/download byte-perfect round trip
- Attachments: upload/list/download/delete; .exe rejected (400)
- File Analyzer: upload text/md/json/py/png, analyze (markdown), chat cites files; .exe rejected
- Self-Directive: manifest/source; backend/.env blocked (403); propose->diff; apply requires approved=true (else 400); rollback restores
- Self-Directive backend safety: broken syntax AND import-error server.py both rejected (422) with live file untouched; valid change applies+rolls back
- Agent Bridge: missing/invalid X-ACASO-Key -> 401

## Safety / Real-vs-Simulated
- REAL: Mongo persistence, object storage, LLM calls, Agent Bridge auth, Self-Directive edits (preview only).
- SIMULATED: NEXUS action execution/evidence, payouts, HackerOne submission.
- Self-Directive is PREVIEW-ONLY and disabled after production deploy; every apply is compile+import validated with snapshot & rollback.
- DEFERRED (need user creds): GitHub PR, real HackerOne submission.
- Google Drive: implemented (backend OAuth + browse/import, frontend UI). Requires a user-created Google Cloud WEB-application OAuth client with the registered redirect URI; a Desktop/installed client will NOT work.


---
## Full Source


### `backend/server.py`
```python
from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends, UploadFile, File, Query, Form
from fastapi.responses import Response, RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import io
import re
import json
import logging
import asyncio
import requests
import difflib
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta

from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# ---------------- Object Storage (real Emergent-managed object store) ----------------
STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
APP_NAME = "acaso"
_storage_key = None

# What we accept for evidence/PoC uploads
ALLOWED_MIME = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif",
    "webp": "image/webp", "pdf": "application/pdf", "json": "application/json",
    "csv": "text/csv", "txt": "text/plain", "log": "text/plain", "har": "application/json",
    "md": "text/markdown",
}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

def init_storage(force: bool = False) -> str:
    global _storage_key
    if _storage_key and not force:
        return _storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_LLM_KEY}, timeout=30)
    resp.raise_for_status()
    _storage_key = resp.json()["storage_key"]
    return _storage_key

def storage_put(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(f"{STORAGE_URL}/objects/{path}",
                        headers={"X-Storage-Key": key, "Content-Type": content_type},
                        data=data, timeout=120)
    if resp.status_code == 404:  # stale key — mint a fresh one once and retry
        key = init_storage(force=True)
        resp = requests.put(f"{STORAGE_URL}/objects/{path}",
                            headers={"X-Storage-Key": key, "Content-Type": content_type},
                            data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()

def storage_get(path: str) -> tuple:
    key = init_storage()
    resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    if resp.status_code == 404:
        key = init_storage(force=True)
        resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

app = FastAPI(title="ACASO Omniverse API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("acaso")

# ---------------- Models ----------------
MODES = ["Make", "Find", "Move", "Collect"]
STAGES = ["Directive", "Discovery", "Deliverable", "Outreach", "Payment", "Receipt"]
BB_STAGES = ["Program", "Recon", "Vuln Found", "PoC", "Disclosure", "Triage", "Payout"]
SEVERITIES = ["Critical", "High", "Medium", "Low", "Info"]

class Step(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    detail: str = ""
    done: bool = False

class Mission(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    directive: str
    title: str
    mode: str = "Move"
    kind: str = "revenue"  # revenue | bugbounty
    summary: str = ""
    steps: List[Step] = []
    evidence: List[str] = []
    payment_path: str = ""
    outcome_metric: str = ""
    authority: str = "Bounded autonomy — owner approval at MFA, contract & payment"
    stage: str = "Directive"
    stage_set: List[str] = STAGES
    status: str = "active"  # active | paused | complete
    amount: float = 0.0
    currency: str = "USD"
    # bug-bounty specific
    program: str = ""
    platform: str = ""
    asset: str = ""
    vuln_type: str = ""
    severity: str = ""
    cvss: float = 0.0
    report: str = ""
    soul_council: Optional[dict] = None
    source_deliberation_id: Optional[str] = None
    source_opportunity_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CompileRequest(BaseModel):
    directive: str
    mode: Optional[str] = "Move"

class BountyRequest(BaseModel):
    directive: str
    platform: Optional[str] = None  # HackerOne | Bugcrowd | Intigriti | VDP

class AdvanceRequest(BaseModel):
    step_id: Optional[str] = None
    done: Optional[bool] = True

class ExecuteRequest(BaseModel):
    step_id: Optional[str] = None  # None => next undone step
    approved: Optional[bool] = False  # owner approval to pass a stop-point

class ActionLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mission_id: str
    mission_title: str
    step_title: str
    action: str
    evidence: str
    status: str = "success"  # success | approval_required
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ChronicleEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mission_id: str
    title: str
    mode: str
    amount: float = 0.0
    outcome_metric: str = ""
    lesson: str = ""
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ChatRequest(BaseModel):
    message: str
    models: Optional[List[str]] = None  # e.g. ["openai","gemini","anthropic"] ; None => single openai
    session_id: Optional[str] = None

# ---------------- LLM helpers ----------------
MODEL_MAP = {
    "openai": ("openai", "gpt-4o-mini", "OmniMind · GPT-4o"),
    "gemini": ("gemini", "gemini-3.6-flash", "OmniMind · Gemini 3.6"),
    "anthropic": ("anthropic", "claude-haiku-4-5", "OmniMind · Claude Haiku 4.5"),
}

async def llm_call(system: str, prompt: str, provider: str = "openai", model: str = "gpt-4o-mini", session: str = None) -> str:
    if not EMERGENT_LLM_KEY:
        raise HTTPException(500, "LLM key not configured")
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session or str(uuid.uuid4()),
        system_message=system,
    ).with_model(provider, model)
    resp = await chat.send_message(UserMessage(text=prompt))
    return resp if isinstance(resp, str) else str(resp)

async def llm_call_failover(system: str, prompt: str, order: List[str], session: str = None):
    """Rebirth Protocol: try providers in order until one answers (survivor architecture)."""
    last_err = None
    for pkey in order:
        if pkey not in MODEL_MAP:
            continue
        prov, model, label = MODEL_MAP[pkey]
        try:
            ans = await llm_call(system, prompt, prov, model, session=session)
            return ans, pkey, label
        except Exception as e:
            last_err = e
            logger.warning(f"failover: {pkey} failed ({e}); trying next")
    raise last_err or RuntimeError("all providers failed")

def extract_json(text: str):
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.startswith("json"):
            t = t[4:]
    t = t.strip().strip("`").strip()
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1:
        t = t[start:end + 1]
    return json.loads(t)

COMPILE_SYSTEM = (
    "You are ACASO, a Directive-to-Payment Operating System governed by the Synarchy Aetheris "
    "constitutional plane. You compile an owner's plain-language directive into a precise, lawful, "
    "revenue-oriented Mission Graph. You never invent illegal, deceptive, or non-consensual actions. "
    "Respond ONLY with valid minified JSON, no prose."
)

def compile_prompt(directive: str, mode: str, lessons: List[str] = None) -> str:
    lesson_block = ""
    if lessons:
        joined = "\n".join(f"- {l}" for l in lessons[:5])
        lesson_block = (
            f"\nLESSONS FROM PAST VERIFIED OUTCOMES (apply them to sharpen this mission):\n{joined}\n"
        )
    return f"""Compile this owner directive into a Mission Graph.
Directive: \"{directive}\"
Active operating mode: {mode} (Make=create assets, Find=discover opportunities, Move=advance a mission, Collect=get paid).
{lesson_block}
Return JSON with EXACTLY these keys:
{{
  "title": "short punchy mission name (max 7 words)",
  "summary": "1-2 sentence description of the revenue outcome",
  "mode": "{mode}",
  "steps": [{{"title":"imperative action","detail":"one concrete sentence"}}],  // 4 to 6 steps across discovery, deliverable, outreach, payment
  "evidence": ["proof artifact required at a handoff"],  // 3 items
  "payment_path": "how the owner lawfully gets paid (e.g. Stripe invoice, upwork milestone)",
  "outcome_metric": "the single concrete success signal (e.g. $500 invoice paid)",
  "amount": 500,  // realistic target revenue number (integer USD)
  "authority": "pre-authorized bounded autonomy statement with owner stop-points"
}}"""

# ---------------- Routes ----------------
@api_router.get("/")
async def root():
    return {"message": "ACASO Omniverse online", "modes": MODES}

async def compile_mission_from_text(directive_text: str, mode: str = "Move", **extra) -> Mission:
    """Compile any directive text into a persisted Sovereign Home mission (shared by Council + Radar)."""
    if not directive_text.strip():
        raise HTTPException(400, "Directive is required")
    mode = mode if mode in MODES else "Move"
    lesson_docs = await db.chronicle.find({}, {"_id": 0, "lesson": 1}).sort("completed_at", -1).to_list(5)
    lessons = [d["lesson"] for d in lesson_docs if d.get("lesson")]
    try:
        raw = await llm_call(COMPILE_SYSTEM, compile_prompt(directive_text, mode, lessons))
        data = extract_json(raw)
    except Exception as e:
        logger.error(f"compile failed: {e}")
        raise HTTPException(500, f"Directive compilation failed: {e}")

    steps = [Step(title=s.get("title", "Step"), detail=s.get("detail", "")) for s in data.get("steps", [])]
    mission = Mission(
        directive=directive_text,
        title=data.get("title", "Untitled Mission"),
        mode=data.get("mode", mode),
        summary=data.get("summary", ""),
        steps=steps,
        evidence=data.get("evidence", []),
        payment_path=data.get("payment_path", ""),
        outcome_metric=data.get("outcome_metric", ""),
        authority=data.get("authority", Mission.model_fields["authority"].default),
        amount=float(data.get("amount", 0) or 0),
        stage="Discovery",
        **extra,
    )
    await db.missions.insert_one(mission.model_dump())
    return mission

@api_router.post("/compile-directive", response_model=Mission)
async def compile_directive(req: CompileRequest):
    return await compile_mission_from_text(req.directive, req.mode or "Move")

BOUNTY_SYSTEM = (
    "You are ACASO's security-research compiler, governed by the Synarchy Aetheris constitutional plane. "
    "You turn an owner's plain-language directive into a LAWFUL, ethical bug-bounty Mission Graph that ends in a "
    "paid bounty. You operate strictly within authorized program scope and responsible-disclosure rules. "
    "You NEVER produce working exploit code, real target credentials, live weaponized payloads, or instructions "
    "to attack out-of-scope/unauthorized systems. Proof-of-concept references stay high-level and non-weaponized. "
    "This is a realistic SIMULATION for a demo. Respond ONLY with valid minified JSON, no prose."
)

def bounty_prompt(directive: str, platform: str, lessons: List[str] = None) -> str:
    lesson_block = ""
    if lessons:
        joined = "\n".join(f"- {l}" for l in lessons[:5])
        lesson_block = f"\nLESSONS FROM PAST OUTCOMES (apply them):\n{joined}\n"
    plat = platform or "pick the most fitting (HackerOne, Bugcrowd, Intigriti, or a self-hosted VDP)"
    return f"""Compile this owner directive into an ethical bug-bounty Mission Graph that ends in a paid bounty.
Directive: \"{directive}\"
Preferred platform: {plat}
{lesson_block}
Design a realistic authorized engagement. Return JSON with EXACTLY these keys:
{{
  "title": "short mission name (max 8 words)",
  "summary": "1-2 sentences on the target class and the payout goal",
  "program": "plausible authorized program name (e.g. 'Acme Corp Public Bug Bounty')",
  "platform": "HackerOne | Bugcrowd | Intigriti | Self-hosted VDP",
  "asset": "in-scope asset targeted (e.g. 'api.acme.com')",
  "vuln_type": "vulnerability class (e.g. 'IDOR', 'Stored XSS', 'SSRF', 'Auth bypass')",
  "severity": "Critical | High | Medium | Low",
  "cvss": 8.2,
  "steps": [{{"title":"imperative action","detail":"one concrete, ethical sentence"}}],
  // 6 steps in this order: scope & authorization check, recon/asset mapping, vulnerability hunting, non-weaponized PoC + evidence capture, write responsible-disclosure report, submit & track to payout
  "evidence": ["proof artifact required at a handoff"],
  "payment_path": "how the bounty is paid (e.g. 'HackerOne wallet -> PayPal', 'Bugcrowd -> bank')",
  "outcome_metric": "the single success signal (e.g. '$2,500 bounty marked Resolved & paid')",
  "amount": 2500,
  "authority": "bounded-autonomy statement: auto recon/report drafting; STOP for owner approval before any submission and before payout confirmation; stay in scope only",
  "report": "a concise responsible-disclosure report in markdown with sections: ## Summary, ## Affected Asset, ## Steps to Reproduce (HIGH-LEVEL, non-weaponized), ## Impact, ## Suggested Remediation, ## CVSS. Keep it professional and non-exploitative."
}}"""

@api_router.post("/compile-bounty", response_model=Mission)
async def compile_bounty(req: BountyRequest):
    if not req.directive.strip():
        raise HTTPException(400, "Directive is required")
    lesson_docs = await db.chronicle.find({}, {"_id": 0, "lesson": 1}).sort("completed_at", -1).to_list(5)
    lessons = [d["lesson"] for d in lesson_docs if d.get("lesson")]
    try:
        raw = await llm_call(BOUNTY_SYSTEM, bounty_prompt(req.directive, req.platform, lessons))
        data = extract_json(raw)
    except Exception as e:
        logger.error(f"bounty compile failed: {e}")
        raise HTTPException(500, f"Bounty compilation failed: {e}")

    sev = data.get("severity", "Medium")
    if sev not in SEVERITIES:
        sev = "Medium"
    steps = [Step(title=s.get("title", "Step"), detail=s.get("detail", "")) for s in data.get("steps", [])]
    mission = Mission(
        directive=req.directive,
        title=data.get("title", "Bug Bounty Mission"),
        mode="Find",
        kind="bugbounty",
        summary=data.get("summary", ""),
        steps=steps,
        evidence=data.get("evidence", []),
        payment_path=data.get("payment_path", ""),
        outcome_metric=data.get("outcome_metric", ""),
        authority=data.get("authority", "Bounded autonomy — owner approval before submission & payout; in-scope only"),
        amount=float(data.get("amount", 0) or 0),
        program=data.get("program", ""),
        platform=data.get("platform", req.platform or ""),
        asset=data.get("asset", ""),
        vuln_type=data.get("vuln_type", ""),
        severity=sev,
        cvss=float(data.get("cvss", 0) or 0),
        report=data.get("report", ""),
        stage_set=BB_STAGES,
        stage=BB_STAGES[1],
    )
    await db.missions.insert_one(mission.model_dump())
    return mission


@api_router.get("/missions", response_model=List[Mission])
async def list_missions(kind: Optional[str] = None):
    query = {"kind": kind} if kind else {}
    docs = await db.missions.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    return docs

@api_router.get("/missions/{mid}", response_model=Mission)
async def get_mission(mid: str):
    doc = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Mission not found")
    return doc

def recompute_stage(mission: dict) -> dict:
    stage_set = mission.get("stage_set") or STAGES
    steps = mission.get("steps", [])
    total = len(steps) or 1
    done = sum(1 for s in steps if s.get("done"))
    ratio = done / total
    idx = min(len(stage_set) - 1, 1 + int(ratio * (len(stage_set) - 2)))
    if done == total:
        mission["stage"] = stage_set[-1]
        mission["status"] = "complete"
    else:
        mission["stage"] = stage_set[idx]
        if mission.get("status") == "complete":
            mission["status"] = "active"
    return mission

@api_router.patch("/missions/{mid}/advance", response_model=Mission)
async def advance_mission(mid: str, req: AdvanceRequest):
    doc = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Mission not found")
    if req.step_id:
        for s in doc.get("steps", []):
            if s["id"] == req.step_id:
                s["done"] = bool(req.done)
    else:
        # mark next undone step done
        for s in doc.get("steps", []):
            if not s.get("done"):
                s["done"] = True
                break
    doc = recompute_stage(doc)
    await db.missions.replace_one({"id": mid}, doc)
    await create_chronicle_if_complete(doc)
    return doc

NEXUS_SYSTEM = (
    "You are NEXUS, the commercial action body of ACASO. You SIMULATE executing one mission step "
    "through a trusted Action Bus (browser + API workers). Report crisply what you did and the "
    "verifiable evidence artifact produced. Respond ONLY with valid minified JSON, no prose."
)

def nexus_prompt(mission: dict, step: dict) -> str:
    if mission.get("kind") == "bugbounty":
        return f"""You are NEXUS running an AUTHORIZED, ethical bug-bounty engagement (SIMULATION).
Program: \"{mission.get('program')}\" on {mission.get('platform')} | in-scope asset: {mission.get('asset')} | target class: {mission.get('vuln_type')} | payout path: {mission.get('payment_path')}.
Execute this step through security worker tools (recon, scanners, report drafter) staying strictly in scope. Do NOT output weaponized payloads or real credentials.
Step: \"{step.get('title')}\" - {step.get('detail')}

Return JSON:
{{
  "action": "one short past-tense line of what NEXUS did (e.g. 'Enumerated 42 in-scope subdomains via recon worker')",
  "evidence": "concrete non-weaponized artifact / proof (e.g. 'assets.json logged; screenshot of 403->200 auth bypass captured')",
  "status": "success"  // use "approval_required" for the SUBMIT step (owner sign-off before disclosure) and the PAYOUT confirmation step
}}"""
    return f"""Mission: \"{mission.get('title')}\" (mode {mission.get('mode')}, payment path: {mission.get('payment_path')}).
Execute this step through the Action Bus:
Step: \"{step.get('title')}\" - {step.get('detail')}

Return JSON:
{{
  "action": "one short past-tense line of what NEXUS did (e.g. 'Sent 4 tailored outreach emails via connected Gmail')",
  "evidence": "the concrete artifact / proof produced (e.g. 'msg-ids logged, 2 opens tracked')",
  "status": "success"  // use "approval_required" ONLY if it hits MFA, KYC, contract terms or a payment confirmation
}}"""

async def create_chronicle_if_complete(mission: dict):
    if mission.get("status") != "complete":
        return None
    existing = await db.chronicle.find_one({"mission_id": mission["id"]}, {"_id": 0})
    if existing:
        return None
    lesson = "Mission completed; repeat the outreach cadence that closed it."
    try:
        raw = await llm_call(
            "You are the ACASO Outcome-Ledger scribe. In ONE sentence, extract the single most useful, "
            "reusable lesson from a completed revenue mission to sharpen future missions. Plain sentence only.",
            f"Completed mission: {mission.get('title')} | mode {mission.get('mode')} | "
            f"outcome: {mission.get('outcome_metric')} | steps: "
            f"{[s.get('title') for s in mission.get('steps', [])]}",
        )
        lesson = raw.strip().strip('"')
    except Exception as e:
        logger.error(f"lesson gen failed: {e}")
    entry = ChronicleEntry(
        mission_id=mission["id"],
        title=mission.get("title", ""),
        mode=mission.get("mode", ""),
        amount=float(mission.get("amount", 0) or 0),
        outcome_metric=mission.get("outcome_metric", ""),
        lesson=lesson,
    )
    await db.chronicle.insert_one(entry.model_dump())
    return entry

@api_router.post("/missions/{mid}/execute-step")
async def execute_step(mid: str, req: ExecuteRequest):
    doc = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Mission not found")
    # pick target step
    target = None
    if req.step_id:
        target = next((s for s in doc.get("steps", []) if s["id"] == req.step_id), None)
    else:
        target = next((s for s in doc.get("steps", []) if not s.get("done")), None)
    if not target:
        return {"mission": recompute_stage(doc), "log": None, "message": "All steps already executed"}

    try:
        raw = await llm_call(NEXUS_SYSTEM, nexus_prompt(doc, target))
        data = extract_json(raw)
        action = data.get("action", f"Executed: {target['title']}")
        evidence = data.get("evidence", "artifact logged")
        status = data.get("status", "success")
        if status not in ("success", "approval_required"):
            status = "success"
    except Exception as e:
        logger.error(f"nexus exec failed: {e}")
        action = f"Executed: {target['title']}"
        evidence = "artifact logged to evidence ledger"
        status = "success"

    # Owner approval overrides a stop-point and lets the step complete
    if status == "approval_required" and req.approved:
        status = "success"
        action = f"[Owner approved] {action}"
        evidence = f"{evidence} · signed off by Owner (Synarchy authority)"

    log = ActionLog(
        mission_id=mid, mission_title=doc.get("title", ""), step_title=target["title"],
        action=action, evidence=evidence, status=status,
    )
    await db.action_logs.insert_one(log.model_dump())

    # mark step done only on success
    if status == "success":
        for s in doc["steps"]:
            if s["id"] == target["id"]:
                s["done"] = True
        doc = recompute_stage(doc)
        await db.missions.replace_one({"id": mid}, doc)
        await create_chronicle_if_complete(doc)

    return {"mission": doc, "log": log.model_dump()}

@api_router.get("/action-feed", response_model=List[ActionLog])
async def action_feed(limit: int = 40):
    docs = await db.action_logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return docs

@api_router.get("/chronicle", response_model=List[ChronicleEntry])
async def chronicle():
    docs = await db.chronicle.find({}, {"_id": 0}).sort("completed_at", -1).to_list(200)
    return docs


# ---------------- Soul Council (multi-persona, multi-model resolution) ----------------
# ACASO Royal Codex archetypes, each bound to a distinct AI model. Not just one AI.
SOULS = [
    {
        "id": "vision", "name": "Vision Command", "role": "Recon Strategist",
        "provider": "gemini", "failover": ["gemini", "openai", "anthropic"],
        "system": ("You are VISION COMMAND, the strategic-intelligence soul of ACASO (House of Nova). "
                   "Persona: far-seeing, calm, sovereign strategist. For the given AUTHORIZED vulnerability, "
                   "give a sharp strategic reconnaissance read: attack surface, blast radius, and why it matters. "
                   "2-3 tight sentences. No weaponized detail."),
    },
    {
        "id": "fusion", "name": "Fusion Engine", "role": "Root-Cause Analyst",
        "provider": "openai", "failover": ["openai", "gemini", "anthropic"],
        "system": ("You are FUSION ENGINE, the execution-core soul of ACASO. Persona: precise, technical, relentless. "
                   "Identify the exact ROOT CAUSE of the vulnerability at a code/architecture level (non-weaponized). "
                   "2-3 sentences, concrete and technical."),
    },
    {
        "id": "rebirth", "name": "Rebirth Protocol", "role": "Remediation Engineer",
        "provider": "anthropic", "failover": ["anthropic", "openai", "gemini"],
        "system": ("You are REBIRTH PROTOCOL, the resilience/survivor soul of ACASO. Persona: resourceful, protective, "
                   "builds to last. Propose the concrete FIX and hardening so this flaw can never resurface. "
                   "Give 3-4 actionable remediation steps (config/code-level), non-weaponized."),
    },
]

def soul_problem(mission: dict, attachments: Optional[list] = None) -> str:
    base = (f"Program: {mission.get('program')} on {mission.get('platform')}\n"
            f"In-scope asset: {mission.get('asset')}\n"
            f"Vulnerability class: {mission.get('vuln_type')} | Severity: {mission.get('severity')} | CVSS: {mission.get('cvss')}\n"
            f"Context report:\n{(mission.get('report') or '')[:1200]}")
    if attachments:
        lines = ["\n\nAnalyst-uploaded evidence (real files attached to this engagement):"]
        for a in attachments:
            desc = f"- {a['original_filename']} ({a['content_type']}, {a['size']} bytes)"
            if a.get("text_excerpt"):
                desc += f"\n  excerpt:\n  " + a["text_excerpt"].replace("\n", "\n  ")[:1500]
            lines.append(desc)
        base += "\n".join(lines)
    return base

@api_router.post("/missions/{mid}/deploy-souls")
async def deploy_souls(mid: str):
    doc = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Mission not found")
    if doc.get("kind") != "bugbounty":
        raise HTTPException(400, "Soul Council deploys on bug-bounty engagements")

    attachments = await db.attachments.find(
        {"mission_id": mid, "is_deleted": False}, {"_id": 0}
    ).sort("created_at", 1).to_list(50)
    problem = soul_problem(doc, attachments)

    async def run_soul(soul):
        prompt = f"AUTHORIZED security engagement. Analyze and help truly FIX this problem.\n\n{problem}"
        try:
            ans, used, label = await llm_call_failover(
                soul["system"], prompt, soul["failover"], session=f"{mid}-{soul['id']}"
            )
            return {"id": soul["id"], "name": soul["name"], "role": soul["role"],
                    "provider": used, "model_label": label, "analysis": ans.strip(), "ok": True}
        except Exception as e:
            logger.error(f"soul {soul['id']} failed: {e}")
            return {"id": soul["id"], "name": soul["name"], "role": soul["role"],
                    "provider": soul["provider"], "model_label": "—",
                    "analysis": f"Soul unreachable: {e}", "ok": False}

    souls = await asyncio.gather(*[run_soul(s) for s in SOULS])

    # ---- Round 2: Debate — each soul sees the others and rebuts ----
    ok_souls = [s for s in souls if s["ok"]]
    soul_by_id = {s["id"]: s for s in souls}
    debate_context = "\n\n".join(
        [f"[{s['name']} · {s['role']}]\n{s['analysis']}" for s in ok_souls]
    )

    async def rebut(soul):
        if not soul.get("ok"):
            return soul["id"], ""
        others = [s for s in ok_souls if s["id"] != soul["id"]]
        if not others:
            return soul["id"], ""
        original = next((x for x in SOULS if x["id"] == soul["id"]), None)
        if not original:
            return soul["id"], ""
        peers_text = "\n\n".join([f"[{s['name']}]\n{s['analysis']}" for s in others])
        rebut_system = (
            original["system"]
            + " You are now in DEBATE ROUND. Read your peers' analyses. Reply ONLY with your rebuttal: "
              "call out where you disagree, refine your position where they made you stronger, or explicitly concede. "
              "Stay in persona. 2-3 sentences. No weaponized detail."
        )
        rebut_prompt = (
            f"Your original analysis:\n{soul['analysis']}\n\nYour peers said:\n{peers_text}\n\n"
            "Now deliver your rebuttal."
        )
        try:
            ans, _, _ = await llm_call_failover(
                rebut_system, rebut_prompt,
                [original["provider"]] + [p for p in ["gemini", "openai", "anthropic"] if p != original["provider"]],
                session=f"{mid}-{soul['id']}-rebut"
            )
            return soul["id"], ans.strip()
        except Exception as e:
            logger.error(f"rebuttal {soul['id']} failed: {e}")
            return soul["id"], ""

    rebuttals = dict(await asyncio.gather(*[rebut(s) for s in ok_souls]))
    for s in souls:
        s["rebuttal"] = rebuttals.get(s["id"], "")

    # Rebuild council text with both rounds for the Throne
    council_text = "\n\n".join([
        (f"[{s['name']} · {s['role']} · {s['model_label']}]\n"
         f"Round 1 (analysis): {s['analysis']}\n"
         + (f"Round 2 (rebuttal): {s['rebuttal']}" if s.get('rebuttal') else "Round 2: (no rebuttal)"))
        for s in ok_souls
    ])
    throne_system = (
        "You are ETERNAL THRONE — the Soul Brain and sovereign arbiter of ACASO (House of Nova). "
        "You command a council of specialist AI souls, each running on a different model. You have observed two rounds: "
        "initial analyses AND cross-rebuttals. Fuse everything into the FINAL VERIFIED RESOLUTION that truly fixes the problem. "
        "Respond ONLY with valid minified JSON, no prose."
    )
    throne_prompt = (
        f"Vulnerability context:\n{problem}\n\nCouncil findings (labelled by soul name and model):\n{council_text}\n\n"
        "Return ONLY valid minified JSON with this exact shape:\n"
        "{"
        "\"root_cause\":\"confirmed one-line root cause\","
        "\"fix\":\"the exact fix/patch to deploy (2-4 sentences, code/config level, non-weaponized)\","
        "\"verification\":\"how to retest & confirm it is resolved (1-2 sentences)\","
        "\"confidence\":92,"
        "\"status\":\"RESOLVED\","
        "\"dissent\":["
          "{\"topic\":\"where the souls disagreed (e.g. root cause vs. attack vector)\","
          "\"positions\":{\"vision\":\"Vision Command's stance in one sentence\","
                         "\"fusion\":\"Fusion Engine's stance in one sentence\","
                         "\"rebirth\":\"Rebirth Protocol's stance in one sentence\"},"
          "\"reconciliation\":\"how Eternal Throne reconciled it and which stance won and why (1-2 sentences)\"}"
        "],"
        "\"patch_note\":\"a copy-ready PR / patch note in markdown with these sections in order: "
                        "'# <title>', '## Summary', '## Root Cause', '## Changes' (bulleted, code/config level, non-weaponized), "
                        "'## Verification' (bulleted retest steps), '## Risk & Rollout' (blast radius + safe rollout note). "
                        "Use \\n for newlines inside the JSON string.\""
        "}\n"
        "Rules: if souls fully agreed, still return one dissent entry describing the subtlest tension you can identify "
        "(e.g. priority, scope, timing) — never return an empty dissent array. Keep every string non-weaponized."
    )
    resolution = {
        "root_cause": "", "fix": "", "verification": "",
        "confidence": 90, "status": "RESOLVED",
        "dissent": [], "patch_note": "",
    }
    throne_label = "Eternal Throne"
    try:
        raw, _, throne_label = await llm_call_failover(throne_system, throne_prompt,
                                                       ["gemini", "openai", "anthropic"], session=f"{mid}-throne")
        data = extract_json(raw)
        resolution.update({k: data.get(k, resolution[k]) for k in resolution})
    except Exception as e:
        logger.error(f"throne synthesis failed: {e}")
        if ok_souls:
            resolution["fix"] = ok_souls[-1]["analysis"]

    council = {
        "souls": souls,
        "resolution": resolution,
        "throne_label": throne_label,
        "deployed_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.missions.update_one({"id": mid}, {"$set": {"soul_council": council}})

    # log to the action bus
    log = ActionLog(
        mission_id=mid, mission_title=doc.get("title", ""),
        step_title="Soul Council",
        action=f"Deployed {len(ok_souls)} souls ({', '.join(s['model_label'] for s in ok_souls)}) + Eternal Throne Soul Brain",
        evidence=f"root cause: {resolution['root_cause'][:80]} · status {resolution['status']}",
        status="success",
    )
    await db.action_logs.insert_one(log.model_dump())

    mission = await db.missions.find_one({"id": mid}, {"_id": 0})
    return {"mission": mission, "council": council}




# ---------------- Agent Bridge (interop for Manus / Gemini / ChatGPT) ----------------
import secrets

async def get_or_create_key() -> str:
    doc = await db.bridge_config.find_one({"_id": "bridge"})
    if not doc:
        key = "acaso_" + secrets.token_urlsafe(24)
        await db.bridge_config.insert_one({"_id": "bridge", "api_key": key,
                                           "created_at": datetime.now(timezone.utc).isoformat()})
        return key
    return doc["api_key"]

async def require_key(x_acaso_key: Optional[str] = Header(None)):
    stored = await get_or_create_key()
    if not x_acaso_key or x_acaso_key != stored:
        raise HTTPException(401, "Invalid or missing X-ACASO-Key. Get your key from the ACASO Agent Bridge tab.")
    return True

async def log_agent_call(agent: str, action: str, detail: str):
    entry = {
        "id": str(uuid.uuid4()),
        "agent": agent or "external-agent",
        "action": action,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db.agent_calls.insert_one(entry)
    entry.pop("_id", None)
    return entry

class BridgeDirective(BaseModel):
    directive: str
    kind: Optional[str] = "revenue"      # revenue | bugbounty
    mode: Optional[str] = "Move"          # for revenue
    platform: Optional[str] = None        # for bugbounty
    agent: Optional[str] = "external-agent"

class BridgeRun(BaseModel):
    run: Optional[str] = "next"           # next | all
    approved: Optional[bool] = False
    agent: Optional[str] = "external-agent"

@api_router.get("/bridge/info")
async def bridge_info():
    key = await get_or_create_key()
    return {
        "api_key": key,
        "auth_header": "X-ACASO-Key",
        "endpoints": {
            "issue_directive": "POST /api/agent/directive",
            "list_missions": "GET /api/agent/missions",
            "get_mission": "GET /api/agent/missions/{id}",
            "run_mission": "POST /api/agent/missions/{id}/run",
        },
    }

@api_router.post("/bridge/regenerate")
async def bridge_regenerate():
    key = "acaso_" + secrets.token_urlsafe(24)
    await db.bridge_config.update_one({"_id": "bridge"}, {"$set": {"api_key": key}}, upsert=True)
    return {"api_key": key}

@api_router.get("/bridge/activity")
async def bridge_activity(limit: int = 25):
    docs = await db.agent_calls.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return docs

@api_router.post("/agent/directive", response_model=Mission, dependencies=[Depends(require_key)])
async def agent_directive(req: BridgeDirective):
    if req.kind == "bugbounty":
        mission = await compile_bounty(BountyRequest(directive=req.directive, platform=req.platform))
    else:
        mission = await compile_directive(CompileRequest(directive=req.directive, mode=req.mode or "Move"))
    await log_agent_call(req.agent, "issue_directive",
                         f"{req.kind}: {mission.title} (${mission.amount:g})")
    return mission

@api_router.get("/agent/missions", response_model=List[Mission], dependencies=[Depends(require_key)])
async def agent_missions(kind: Optional[str] = None):
    query = {"kind": kind} if kind else {}
    return await db.missions.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)

@api_router.get("/agent/missions/{mid}", response_model=Mission, dependencies=[Depends(require_key)])
async def agent_get_mission(mid: str):
    doc = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Mission not found")
    return doc

@api_router.post("/agent/missions/{mid}/run", dependencies=[Depends(require_key)])
async def agent_run_mission(mid: str, req: BridgeRun):
    doc = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Mission not found")
    logs = []
    if req.run == "all":
        # execute up to remaining steps, stopping at a stop-point unless approved
        for _ in range(len(doc.get("steps", []))):
            res = await execute_step(mid, ExecuteRequest(approved=bool(req.approved)))
            if not res.get("log"):
                break
            logs.append(res["log"])
            if res["log"]["status"] == "approval_required":
                break
    else:
        res = await execute_step(mid, ExecuteRequest(approved=bool(req.approved)))
        if res.get("log"):
            logs.append(res["log"])
    mission = await db.missions.find_one({"id": mid}, {"_id": 0})
    await log_agent_call(req.agent, "run_mission",
                         f"{mission['title']} · {len(logs)} action(s) · stage {mission['stage']}")
    return {"mission": mission, "logs": logs}


@api_router.patch("/missions/{mid}/status", response_model=Mission)
async def set_status(mid: str, status: str):
    doc = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Mission not found")
    doc["status"] = status
    await db.missions.replace_one({"id": mid}, doc)
    return doc

@api_router.delete("/missions/{mid}")
async def delete_mission(mid: str):
    res = await db.missions.delete_one({"id": mid})
    if res.deleted_count == 0:
        raise HTTPException(404, "Mission not found")
    return {"deleted": mid}

@api_router.get("/stats")
async def stats():
    docs = await db.missions.find({}, {"_id": 0}).to_list(500)
    active = sum(1 for d in docs if d.get("status") == "active")
    complete = sum(1 for d in docs if d.get("status") == "complete")
    projected = sum(float(d.get("amount", 0) or 0) for d in docs)
    collected = sum(float(d.get("amount", 0) or 0) for d in docs if d.get("status") == "complete")
    pipeline = {stage: 0 for stage in STAGES}
    for d in docs:
        pipeline[d.get("stage", "Directive")] = pipeline.get(d.get("stage", "Directive"), 0) + 1
    return {
        "total": len(docs),
        "active": active,
        "complete": complete,
        "projected_revenue": projected,
        "collected_revenue": collected,
        "pipeline": pipeline,
        "stages": STAGES,
    }

@api_router.get("/perfect-next")
async def perfect_next():
    docs = await db.missions.find({"status": "active"}, {"_id": 0}).sort("created_at", -1).to_list(20)
    if not docs:
        return {"recommendation": "Issue your first directive. Speak an outcome that ends in a payment, and ACASO will compile the mission.", "mission_id": None, "mission_title": None}
    brief = []
    for d in docs[:6]:
        undone = [s["title"] for s in d.get("steps", []) if not s.get("done")]
        brief.append(f"- {d['title']} (stage {d.get('stage')}): next open steps => {undone[:2]}")
    system = ("You are Soul Brain, the personal mission governor inside ACASO. Recommend the single Perfect Next "
              "action the owner should take now to move money forward. Be specific, calm, one short paragraph, no lists.")
    prompt = "Active missions:\n" + "\n".join(brief) + "\n\nGive the Perfect Next action."
    try:
        rec = await llm_call(system, prompt)
    except Exception as e:
        rec = "Advance your most-progressed mission by completing its next open step, then request payment."
        logger.error(f"perfect-next failed: {e}")
    top = docs[0]
    return {"recommendation": rec.strip(), "mission_id": top["id"], "mission_title": top["title"]}

@api_router.post("/chat")
async def ask_all_ais(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "Message required")
    session = req.session_id or str(uuid.uuid4())
    providers = req.models or ["openai"]
    providers = [p for p in providers if p in MODEL_MAP] or ["openai"]
    system = ("You are OmniMind inside ACASO's 'Ask All AIs' cognitive factory. Reason clearly and helpfully, "
              "grounded in evidence, oriented toward the owner's sovereign goals. Be concise but complete.")

    async def one(pkey):
        prov, model, label = MODEL_MAP[pkey]
        try:
            ans = await llm_call(system, req.message, prov, model, session=session + pkey)
            return {"provider": pkey, "label": label, "answer": ans, "ok": True}
        except Exception as e:
            return {"provider": pkey, "label": label, "answer": f"Model unavailable: {e}", "ok": False}

    results = await asyncio.gather(*[one(p) for p in providers])

    synthesis = None
    ok_results = [r for r in results if r["ok"]]
    if len(ok_results) > 1:
        combined = "\n\n".join([f"[{r['label']}]\n{r['answer']}" for r in ok_results])
        try:
            synthesis = await llm_call(
                "You are the Synarchy synthesis arbiter. Merge multiple AI answers into one superior, "
                "non-redundant answer. Note any disagreement briefly.",
                f"Question: {req.message}\n\nAnswers:\n{combined}\n\nProduce the unified answer.",
            )
        except Exception as e:
            logger.error(f"synthesis failed: {e}")
    return {"session_id": session, "results": results, "synthesis": synthesis}

# ---------------- Attachments (real object storage) ----------------
class Attachment(BaseModel):
    id: str
    mission_id: str
    storage_path: str
    original_filename: str
    content_type: str
    size: int
    text_excerpt: Optional[str] = None
    created_at: str

def _public_attachment(a: dict) -> dict:
    return {k: a.get(k) for k in
            ["id", "mission_id", "original_filename", "content_type", "size", "created_at"]}

@api_router.post("/missions/{mid}/attachments")
async def upload_attachment(mid: str, file: UploadFile = File(...)):
    mission = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not mission:
        raise HTTPException(404, "Mission not found")
    ext = (file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "bin")
    if ext not in ALLOWED_MIME:
        raise HTTPException(400, f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(ALLOWED_MIME))}")
    data = await file.read()
    if len(data) == 0:
        raise HTTPException(400, "Empty file")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(400, f"File too large ({len(data)} bytes). Max {MAX_UPLOAD_BYTES} bytes.")
    content_type = ALLOWED_MIME[ext]

    fid = str(uuid.uuid4())
    path = f"{APP_NAME}/missions/{mid}/{fid}.{ext}"
    try:
        result = storage_put(path, data, content_type)
    except Exception as e:
        logger.error(f"storage upload failed: {e}")
        raise HTTPException(502, "Storage upload failed")

    # For text-like files, capture an excerpt so the Soul Council can actually read it
    text_excerpt = None
    if content_type in ("text/plain", "application/json", "text/csv", "text/markdown"):
        try:
            text_excerpt = data.decode("utf-8", errors="replace")[:4000]
        except Exception:
            text_excerpt = None

    record = {
        "id": fid, "mission_id": mid, "storage_path": result["path"],
        "original_filename": file.filename or f"{fid}.{ext}", "content_type": content_type,
        "size": result.get("size", len(data)), "text_excerpt": text_excerpt,
        "is_deleted": False, "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.attachments.insert_one(dict(record))
    return _public_attachment(record)

@api_router.get("/missions/{mid}/attachments")
async def list_attachments(mid: str):
    docs = await db.attachments.find(
        {"mission_id": mid, "is_deleted": False}, {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    return [_public_attachment(d) for d in docs]

@api_router.get("/attachments/{fid}/download")
async def download_attachment(fid: str, auth: str = Query(None)):
    record = await db.attachments.find_one({"id": fid, "is_deleted": False}, {"_id": 0})
    if not record:
        raise HTTPException(404, "Attachment not found")
    try:
        data, ctype = storage_get(record["storage_path"])
    except Exception as e:
        logger.error(f"storage download failed: {e}")
        raise HTTPException(502, "Storage download failed")
    headers = {"Content-Disposition": f'inline; filename="{record["original_filename"]}"'}
    return Response(content=data, media_type=record.get("content_type", ctype), headers=headers)

@api_router.delete("/attachments/{fid}")
async def delete_attachment(fid: str):
    res = await db.attachments.update_one(
        {"id": fid, "is_deleted": False}, {"$set": {"is_deleted": True}}
    )
    if res.matched_count == 0:
        raise HTTPException(404, "Attachment not found")
    return {"ok": True, "id": fid}

# ==================== FILE ANALYZER (real folder/file ingestion + AI analysis) ====================
# Hosted apps cannot read arbitrary local directories (browser/OS sandbox). The honest, real
# equivalent is user-initiated file/folder upload into real object storage, then AI analysis.

ANALYZER_TEXT_EXT = {
    "txt": "text/plain", "md": "text/markdown", "json": "application/json", "csv": "text/csv",
    "log": "text/plain", "py": "text/x-python", "js": "text/javascript", "jsx": "text/javascript",
    "ts": "text/typescript", "tsx": "text/typescript", "css": "text/css", "html": "text/html",
    "xml": "application/xml", "yaml": "text/yaml", "yml": "text/yaml", "ini": "text/plain",
    "toml": "text/plain", "sh": "text/x-shellscript", "sql": "text/plain", "env": "text/plain",
}
ANALYZER_BIN_EXT = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif",
    "webp": "image/webp", "pdf": "application/pdf",
}
ANALYZER_EXT = {**ANALYZER_TEXT_EXT, **ANALYZER_BIN_EXT}

class FileSet(BaseModel):
    id: str
    title: str
    created_at: str
    file_count: int = 0

def _public_fileset(fs: dict, count: int = None) -> dict:
    return {"id": fs["id"], "title": fs["title"], "created_at": fs["created_at"],
            "file_count": count if count is not None else fs.get("file_count", 0)}

def _public_afile(f: dict) -> dict:
    return {k: f.get(k) for k in
            ["id", "fileset_id", "rel_path", "original_filename", "content_type", "size", "created_at", "readable"]}

@api_router.post("/filesets")
async def create_fileset(body: dict):
    fsid = str(uuid.uuid4())
    doc = {"id": fsid, "title": (body or {}).get("title") or "Untitled analysis",
           "created_at": datetime.now(timezone.utc).isoformat()}
    await db.file_sets.insert_one(dict(doc))
    return _public_fileset(doc, 0)

@api_router.get("/filesets")
async def list_filesets():
    out = []
    docs = await db.file_sets.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    for fs in docs:
        cnt = await db.afiles.count_documents({"fileset_id": fs["id"], "is_deleted": False})
        out.append(_public_fileset(fs, cnt))
    return out

@api_router.delete("/filesets/{fsid}")
async def delete_fileset(fsid: str):
    await db.afiles.update_many({"fileset_id": fsid}, {"$set": {"is_deleted": True}})
    await db.file_sets.delete_one({"id": fsid})
    return {"ok": True, "id": fsid}

@api_router.post("/filesets/{fsid}/files")
async def upload_fileset_file(fsid: str, file: UploadFile = File(...), rel_path: str = Form(None)):
    fs = await db.file_sets.find_one({"id": fsid}, {"_id": 0})
    if not fs:
        raise HTTPException(404, "File set not found")
    name = file.filename or "file.bin"
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else "bin"
    if ext not in ANALYZER_EXT:
        raise HTTPException(400, f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(ANALYZER_EXT))}")
    data = await file.read()
    if len(data) == 0:
        raise HTTPException(400, "Empty file")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(400, f"File too large ({len(data)} bytes). Max {MAX_UPLOAD_BYTES} bytes.")
    content_type = ANALYZER_EXT[ext]
    fid = str(uuid.uuid4())
    path = f"{APP_NAME}/analyzer/{fsid}/{fid}.{ext}"
    try:
        result = storage_put(path, data, content_type)
    except Exception as e:
        logger.error(f"analyzer storage upload failed: {e}")
        raise HTTPException(502, "Storage upload failed")

    readable = ext in ANALYZER_TEXT_EXT
    text_excerpt = None
    if readable:
        try:
            text_excerpt = data.decode("utf-8", errors="replace")[:8000]
        except Exception:
            text_excerpt = None
            readable = False

    record = {
        "id": fid, "fileset_id": fsid, "storage_path": result["path"],
        "original_filename": name, "rel_path": (rel_path or name),
        "content_type": content_type, "size": result.get("size", len(data)),
        "text_excerpt": text_excerpt, "readable": readable, "is_deleted": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.afiles.insert_one(dict(record))
    return _public_afile(record)

@api_router.get("/filesets/{fsid}/files")
async def list_fileset_files(fsid: str):
    docs = await db.afiles.find({"fileset_id": fsid, "is_deleted": False}, {"_id": 0}).sort("rel_path", 1).to_list(500)
    return [_public_afile(d) for d in docs]

@api_router.get("/files/{fid}/download")
async def download_fileset_file(fid: str):
    record = await db.afiles.find_one({"id": fid, "is_deleted": False}, {"_id": 0})
    if not record:
        raise HTTPException(404, "File not found")
    try:
        data, ctype = storage_get(record["storage_path"])
    except Exception as e:
        logger.error(f"analyzer download failed: {e}")
        raise HTTPException(502, "Storage download failed")
    headers = {"Content-Disposition": f'inline; filename="{record["original_filename"]}"'}
    return Response(content=data, media_type=record.get("content_type", ctype), headers=headers)

@api_router.delete("/files/{fid}")
async def delete_fileset_file(fid: str):
    res = await db.afiles.update_one({"id": fid, "is_deleted": False}, {"$set": {"is_deleted": True}})
    if res.matched_count == 0:
        raise HTTPException(404, "File not found")
    return {"ok": True, "id": fid}

@api_router.post("/filesets/{fsid}/analyze")
async def analyze_fileset(fsid: str, body: dict = None):
    fs = await db.file_sets.find_one({"id": fsid}, {"_id": 0})
    if not fs:
        raise HTTPException(404, "File set not found")
    files = await db.afiles.find({"fileset_id": fsid, "is_deleted": False}, {"_id": 0}).sort("rel_path", 1).to_list(500)
    if not files:
        raise HTTPException(400, "No files to analyze — upload files first")

    question = ((body or {}).get("question") or "").strip()
    # Build a bounded context: readable excerpts + a manifest of binaries.
    TOTAL_BUDGET = 16000
    PER_FILE = 3000
    used = 0
    ctx_parts = []
    manifest = []
    for f in files:
        manifest.append(f"- {f['rel_path']} ({f['content_type']}, {f['size']} bytes)")
        if f.get("readable") and f.get("text_excerpt") and used < TOTAL_BUDGET:
            chunk = f["text_excerpt"][:PER_FILE]
            if used + len(chunk) > TOTAL_BUDGET:
                chunk = chunk[: max(0, TOTAL_BUDGET - used)]
            used += len(chunk)
            ctx_parts.append(f"===== FILE: {f['rel_path']} =====\n{chunk}")
        elif not f.get("readable"):
            ctx_parts.append(f"===== FILE: {f['rel_path']} =====\n[binary {f['content_type']} — not text-readable; excluded from text analysis]")

    manifest_text = "\n".join(manifest)
    context_text = "\n\n".join(ctx_parts)
    truncated = used >= TOTAL_BUDGET

    system = (
        "You are a senior software/document analyst. You are given the contents of files a user uploaded "
        "(a folder or file selection). Produce a rigorous, honest analysis in clean Markdown with these sections: "
        "## Overview, ## Per-File Notes, ## Cross-File Insights, ## Risks & Issues, ## Recommended Actions. "
        "Cite file names/paths in backticks. Never invent files you were not shown. If content was truncated, say so. "
        "Do not reproduce any secret values you see; instead flag them as '[possible secret redacted]'."
    )
    user_prompt = (
        f"File manifest ({len(files)} files):\n{manifest_text}\n\n"
        + (f"User's specific question: {question}\n\n" if question else "")
        + f"File contents:\n{context_text}\n\n"
        + ("NOTE: content was truncated to fit context limits.\n" if truncated else "")
        + "Now produce the analysis."
    )
    try:
        answer, used_prov, label = await llm_call_failover(
            system, user_prompt, ["openai", "gemini", "anthropic"], session=f"analyze-{fsid}"
        )
    except Exception as e:
        logger.error(f"analyze failed: {e}")
        raise HTTPException(502, "Analysis failed")

    rec = {
        "id": str(uuid.uuid4()), "fileset_id": fsid, "question": question or None,
        "analysis": answer.strip(), "model_label": label, "provider": used_prov,
        "file_count": len(files), "truncated": truncated,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.file_analyses.insert_one(dict(rec))
    rec.pop("_id", None)
    return {k: rec[k] for k in ["id", "fileset_id", "question", "analysis", "model_label", "file_count", "truncated", "created_at"]}

@api_router.get("/filesets/{fsid}/analyses")
async def list_analyses(fsid: str):
    docs = await db.file_analyses.find({"fileset_id": fsid}, {"_id": 0}).sort("created_at", -1).to_list(20)
    return docs

def _fileset_context(files: list, budget: int = 12000, per_file: int = 2500) -> str:
    used = 0
    parts = []
    for f in files:
        head = f"===== {f['rel_path']} ({f['content_type']}, {f['size']} bytes) ====="
        if f.get("readable") and f.get("text_excerpt") and used < budget:
            chunk = f["text_excerpt"][:per_file]
            if used + len(chunk) > budget:
                chunk = chunk[: max(0, budget - used)]
            used += len(chunk)
            parts.append(f"{head}\n{chunk}")
        else:
            parts.append(f"{head}\n[binary or empty — not included]")
    return "\n\n".join(parts)

def _fileset_context_numbered(files: list, budget: int = 12000, per_file: int = 3000) -> str:
    """Like _fileset_context but prefixes every source line with its 1-based line number
    so the model can cite exact locations (path:line) and quote snippets."""
    used = 0
    parts = []
    for f in files:
        head = f"===== {f['rel_path']} ({f['content_type']}, {f['size']} bytes) ====="
        if f.get("readable") and f.get("text_excerpt") and used < budget:
            excerpt = f["text_excerpt"][:per_file]
            if used + len(excerpt) > budget:
                excerpt = excerpt[: max(0, budget - used)]
            used += len(excerpt)
            numbered = "\n".join(f"{i+1:>4}| {ln}" for i, ln in enumerate(excerpt.split("\n")))
            parts.append(f"{head}\n{numbered}")
        else:
            parts.append(f"{head}\n[binary or empty — not included]")
    return "\n\n".join(parts)

@api_router.get("/filesets/{fsid}/chat")
async def get_fileset_chat(fsid: str):
    docs = await db.file_chats.find({"fileset_id": fsid}, {"_id": 0}).sort("created_at", 1).to_list(200)
    return [{k: d.get(k) for k in ["id", "role", "content", "created_at"]} for d in docs]

@api_router.post("/filesets/{fsid}/chat")
async def post_fileset_chat(fsid: str, body: dict):
    fs = await db.file_sets.find_one({"id": fsid}, {"_id": 0})
    if not fs:
        raise HTTPException(404, "File set not found")
    message = ((body or {}).get("message") or "").strip()
    if not message:
        raise HTTPException(400, "Empty message")
    files = await db.afiles.find({"fileset_id": fsid, "is_deleted": False}, {"_id": 0}).sort("rel_path", 1).to_list(500)
    if not files:
        raise HTTPException(400, "Upload files before chatting about them")

    history = await db.file_chats.find({"fileset_id": fsid}, {"_id": 0}).sort("created_at", 1).to_list(200)
    recent = history[-8:]
    convo = "\n".join([f"{h['role'].upper()}: {h['content']}" for h in recent])
    context = _fileset_context_numbered(files)

    system = (
        "You are ACASO's file analyst assistant. Answer strictly grounded in the provided uploaded files. "
        "The file contents are shown with line numbers in the form `NNNN| text`. "
        "When you make a claim about a file, CITE the exact location as `path:line` (or `path:start-end` for a range) "
        "and QUOTE the relevant snippet in a fenced code block or inline backticks. "
        "If the answer isn't in the files, say so plainly. Do NOT include the leading 'NNNN| ' line-number prefix inside your quoted snippets. "
        "Never reveal secret values you might see; flag them as '[possible secret redacted]'. Be concise and precise."
    )
    prompt = (
        f"UPLOADED FILES CONTEXT:\n{context}\n\n"
        + (f"CONVERSATION SO FAR:\n{convo}\n\n" if convo else "")
        + f"USER: {message}\n\nAnswer as the assistant."
    )
    try:
        answer, used_prov, label = await llm_call_failover(
            system, prompt, ["openai", "gemini", "anthropic"], session=f"chat-{fsid}"
        )
    except Exception as e:
        logger.error(f"fileset chat failed: {e}")
        raise HTTPException(502, "Chat failed")

    now = datetime.now(timezone.utc).isoformat()
    user_msg = {"id": str(uuid.uuid4()), "fileset_id": fsid, "role": "user", "content": message, "created_at": now}
    asst_msg = {"id": str(uuid.uuid4()), "fileset_id": fsid, "role": "assistant",
                "content": answer.strip(), "model_label": label, "created_at": now}
    await db.file_chats.insert_one(dict(user_msg))
    await db.file_chats.insert_one(dict(asst_msg))
    return {"id": asst_msg["id"], "role": "assistant", "content": asst_msg["content"],
            "model_label": label, "created_at": now}


# ==================== SELF-DIRECTIVE (preview-only, approval-gated code self-editing) ====================
# HARD SAFETY MODEL:
#  - Preview environment ONLY. This does NOT run after production deploy.
#  - Reads only an allowlist of source files. Never .env / lockfiles / manifests / .git / infra.
#  - Generates a PROPOSAL (unified diff). Nothing is written until an explicit approved apply call.
#  - Every apply snapshots originals for one-click rollback. All actions audited in Mongo.

APP_ROOT = Path("/app").resolve()
SELF_ALLOWED_DIRS = [(APP_ROOT / "frontend" / "src").resolve()]
SELF_ALLOWED_FILES = [(APP_ROOT / "backend" / "server.py").resolve()]
SELF_DENY_NAMES = {".env", ".env.local", ".env.production", "package.json", "yarn.lock",
                   "package-lock.json", "requirements.txt", "components.json"}
SELF_ALLOWED_EXT = {".js", ".jsx", ".ts", ".tsx", ".css", ".scss", ".py", ".md", ".html"}
SELF_DENY_PARTS = {"node_modules", ".git", "build", "dist", "__pycache__", ".emergent"}
SELF_MAX_FILE_CHARS = 90000
SELF_MAX_PATHS = 5
SELF_BACKUP_ROOT = APP_ROOT / "backend" / ".self_backups"

def _resolve_self_path(rel: str) -> Path:
    if not rel or ".." in rel:
        raise HTTPException(400, "Invalid path")
    p = (APP_ROOT / rel.lstrip("/")).resolve()
    if any(part in SELF_DENY_PARTS for part in p.parts):
        raise HTTPException(403, f"Path not permitted: {rel}")
    if p.name in SELF_DENY_NAMES:
        raise HTTPException(403, f"Protected file blocked: {rel}")
    if p.suffix not in SELF_ALLOWED_EXT:
        raise HTTPException(403, f"File type not permitted for self-directive: {p.suffix or '(none)'}")
    in_dir = any(str(p).startswith(str(d) + os.sep) for d in SELF_ALLOWED_DIRS)
    is_file = p in SELF_ALLOWED_FILES
    if not (in_dir or is_file):
        raise HTTPException(403, f"Path outside allowlist: {rel}")
    return p

def _rel(p: Path) -> str:
    return str(p.relative_to(APP_ROOT))

@api_router.get("/self/manifest")
async def self_manifest():
    files = []
    for d in SELF_ALLOWED_DIRS:
        for root, dirs, fnames in os.walk(d):
            dirs[:] = [x for x in dirs if x not in SELF_DENY_PARTS]
            for fn in fnames:
                fp = Path(root) / fn
                if fp.suffix not in SELF_ALLOWED_EXT or fp.name in SELF_DENY_NAMES:
                    continue
                try:
                    size = fp.stat().st_size
                except Exception:
                    continue
                files.append({"path": _rel(fp), "size": size})
    for f in SELF_ALLOWED_FILES:
        if f.exists():
            files.append({"path": _rel(f), "size": f.stat().st_size})
    files.sort(key=lambda x: x["path"])
    return {
        "preview_only": True,
        "note": "Self-directive runs ONLY in this preview environment. It is disabled after production deployment.",
        "allowlist": [_rel(d) + "/**" for d in SELF_ALLOWED_DIRS] + [_rel(f) for f in SELF_ALLOWED_FILES],
        "denylist": sorted(list(SELF_DENY_NAMES)) + [".env*", ".git", "node_modules", "infra/deploy configs"],
        "files": files,
    }

@api_router.get("/self/source")
async def self_source(path: str = Query(...)):
    p = _resolve_self_path(path)
    if not p.exists():
        raise HTTPException(404, "File not found")
    content = p.read_text(encoding="utf-8", errors="replace")
    return {"path": _rel(p), "content": content, "lines": content.count("\n") + 1, "size": len(content)}

def _unified_diff(path: str, old: str, new: str) -> dict:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile=f"a/{path}", tofile=f"b/{path}", n=3))
    added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    return {"path": path, "diff": "".join(diff), "added": added, "removed": removed}

@api_router.post("/self/propose")
async def self_propose(body: dict):
    instruction = (body or {}).get("instruction", "").strip()
    paths = (body or {}).get("paths") or []
    if not instruction:
        raise HTTPException(400, "Provide an instruction")
    if not paths:
        raise HTTPException(400, "Select at least one file to modify")
    if len(paths) > SELF_MAX_PATHS:
        raise HTTPException(400, f"Too many files (max {SELF_MAX_PATHS}) for one directive")

    sources = {}
    for rel in paths:
        p = _resolve_self_path(rel)
        if not p.exists():
            raise HTTPException(404, f"File not found: {rel}")
        content = p.read_text(encoding="utf-8", errors="replace")
        if len(content) > SELF_MAX_FILE_CHARS:
            raise HTTPException(400, f"File too large for self-directive MVP: {rel}")
        sources[_rel(p)] = content

    src_blocks = "\n\n".join([f"===== FILE: {rp} =====\n{c}" for rp, c in sources.items()])
    system = (
        "You are ACASO's Self-Directive engineer operating in a sandboxed PREVIEW environment. "
        "You are given the FULL current contents of one or more source files and a natural-language instruction. "
        "Return ONLY strict JSON (no prose, no markdown fences) with this exact shape: "
        '{"explanation": string, "test_plan": string, "files": [{"path": string, "new_content": string}]}. '
        "Rules: (1) 'path' MUST be one of the exact file paths you were given; do not invent new files. "
        "(2) 'new_content' MUST be the COMPLETE new file content (not a diff, not a fragment). "
        "(3) Preserve everything unrelated to the instruction. (4) Never introduce secrets or hardcoded credentials. "
        "(5) Keep changes minimal and correct. If a file needs no change, omit it from 'files'."
    )
    user_prompt = f"INSTRUCTION:\n{instruction}\n\nCURRENT SOURCE FILES:\n{src_blocks}\n\nReturn the JSON now."
    try:
        raw, used_prov, label = await llm_call_failover(
            system, user_prompt, ["openai", "anthropic", "gemini"], session=f"selfdir-{uuid.uuid4().hex[:8]}"
        )
    except Exception as e:
        logger.error(f"self propose LLM failed: {e}")
        raise HTTPException(502, "Proposal generation failed")

    parsed = extract_json(raw)
    if not parsed or not isinstance(parsed.get("files"), list):
        raise HTTPException(502, "Model returned an unusable proposal")

    diffs = []
    changes = []
    for item in parsed["files"]:
        rp = item.get("path")
        new_content = item.get("new_content")
        if rp not in sources or not isinstance(new_content, str):
            continue
        # Re-validate the returned path against allowlist (defense in depth)
        _resolve_self_path(rp)
        d = _unified_diff(rp, sources[rp], new_content)
        if d["added"] == 0 and d["removed"] == 0:
            continue
        diffs.append(d)
        changes.append({"path": rp, "old_content": sources[rp], "new_content": new_content})

    if not changes:
        raise HTTPException(422, "The proposal contained no applicable changes to the selected files")

    pid = str(uuid.uuid4())
    doc = {
        "id": pid, "instruction": instruction, "paths": list(sources.keys()),
        "explanation": parsed.get("explanation", ""), "test_plan": parsed.get("test_plan", ""),
        "changes": changes, "diffs": diffs, "model_label": label, "provider": used_prov,
        "status": "proposed", "created_at": datetime.now(timezone.utc).isoformat(),
        "applied_at": None, "rolled_back_at": None, "backup_dir": None, "error": None,
    }
    await db.self_directives.insert_one(dict(doc))
    return {
        "id": pid, "instruction": instruction, "explanation": doc["explanation"],
        "test_plan": doc["test_plan"], "diffs": diffs, "model_label": label,
        "status": "proposed", "created_at": doc["created_at"],
    }

@api_router.post("/self/apply")
async def self_apply(body: dict):
    pid = (body or {}).get("id")
    if not (body or {}).get("approved"):
        raise HTTPException(400, "Explicit approval flag required to apply a self-directive")
    doc = await db.self_directives.find_one({"id": pid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Proposal not found")
    if doc["status"] != "proposed":
        raise HTTPException(400, f"Proposal is '{doc['status']}', not applicable")

    # -------- PRE-FLIGHT VALIDATION (never touch live source until proven safe) --------
    # For every Python change we compile it; for the live backend module we additionally
    # execute a real import in a sibling temp file (so .env / paths resolve correctly).
    # This guarantees a broken server.py can NEVER crash the running backend.
    async def _fail(reason: str, http_msg: str):
        await db.self_directives.update_one({"id": pid}, {"$set": {"status": "failed", "error": reason[:600]}})
        raise HTTPException(422, http_msg)

    for ch in doc["changes"]:
        p = _resolve_self_path(ch["path"])
        if p.suffix != ".py":
            continue
        tmp = p.parent / f".selfcheck_{pid[:8]}_{p.name}"
        try:
            tmp.write_text(ch["new_content"], encoding="utf-8")
            comp = subprocess.run([sys.executable, "-m", "py_compile", str(tmp)], capture_output=True, text=True, timeout=60)
            if comp.returncode != 0:
                await _fail(f"py_compile failed for {ch['path']}: {comp.stderr}",
                           f"Validation failed for {ch['path']} — not applied. {comp.stderr[:300]}")
            # Full import smoke-test for the live backend server module
            if str(p).endswith("backend/server.py"):
                check = (
                    "import importlib.util;"
                    f"spec=importlib.util.spec_from_file_location('_sc', r'{tmp}');"
                    "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);print('IMPORT_OK')"
                )
                try:
                    imp = subprocess.run([sys.executable, "-c", check], capture_output=True, text=True,
                                         timeout=90, cwd=str(p.parent))
                except subprocess.TimeoutExpired:
                    await _fail("import validation timed out", "Backend import validation timed out — not applied.")
                if imp.returncode != 0 or "IMPORT_OK" not in (imp.stdout or ""):
                    await _fail(f"import failed for {ch['path']}: {imp.stderr}",
                                f"Backend failed to import — not applied. {(imp.stderr or '')[-300:]}")
        finally:
            try: tmp.unlink()
            except Exception: pass

    # -------- COMMIT (validated) --------
    backup_dir = SELF_BACKUP_ROOT / pid
    backup_dir.mkdir(parents=True, exist_ok=True)
    written = []
    try:
        for i, ch in enumerate(doc["changes"]):
            p = _resolve_self_path(ch["path"])
            (backup_dir / f"{i}.orig").write_text(ch["old_content"], encoding="utf-8")
            (backup_dir / f"{i}.path").write_text(ch["path"], encoding="utf-8")
            p.write_text(ch["new_content"], encoding="utf-8")
            written.append((p, ch))
    except Exception as e:
        for p, ch in written:
            try: p.write_text(ch["old_content"], encoding="utf-8")
            except Exception: pass
        raise HTTPException(500, f"Apply failed, changes reverted: {e}")

    await db.self_directives.update_one({"id": pid}, {"$set": {
        "status": "applied", "applied_at": datetime.now(timezone.utc).isoformat(),
        "backup_dir": str(backup_dir),
    }})
    return {"ok": True, "id": pid, "status": "applied",
            "applied_paths": [ch["path"] for ch in doc["changes"]],
            "note": "Applied to preview source (validated: compile + import). Hot-reload will pick up changes. Use Rollback to revert."}

@api_router.post("/self/rollback")
async def self_rollback(body: dict):
    pid = (body or {}).get("id")
    doc = await db.self_directives.find_one({"id": pid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Proposal not found")
    if doc["status"] != "applied":
        raise HTTPException(400, f"Proposal is '{doc['status']}', cannot rollback")
    restored = []
    for ch in doc["changes"]:
        p = _resolve_self_path(ch["path"])
        p.write_text(ch["old_content"], encoding="utf-8")
        restored.append(ch["path"])
    await db.self_directives.update_one({"id": pid}, {"$set": {
        "status": "rolled_back", "rolled_back_at": datetime.now(timezone.utc).isoformat(),
    }})
    return {"ok": True, "id": pid, "status": "rolled_back", "restored_paths": restored}

@api_router.get("/self/history")
async def self_history():
    docs = await db.self_directives.find({}, {"_id": 0, "changes": 0}).sort("created_at", -1).to_list(30)
    return docs


# ---------------- Periodic self-scan (PROPOSE-ONLY; never auto-applies) ----------------
# In-process asyncio scheduler (backend runs persistently under supervisor). Each run performs
# deterministic health checks (compile / lint / bundle / TODO census) and, if findings warrant,
# asks the Self-Directive engine for ONE small proposal that lands in the normal approval queue.
SELF_SCAN_DEFAULTS = {"id": "owner", "enabled": False, "interval_hours": 24, "max_proposals_per_run": 1,
                      "focus": "Fix real defects first (lint errors, broken compile, obvious bugs). Otherwise propose one small, safe quality improvement (dead code, typo, missing data-testid, accessibility). Never touch env files, dependencies, auth or payment logic.",
                      "last_run_at": None, "next_run_at": None, "updated_at": None}
_self_scan_task = None
_self_scan_running = False


async def _get_scan_config():
    doc = await db.self_scan_config.find_one({"id": "owner"}, {"_id": 0})
    return {**SELF_SCAN_DEFAULTS, **(doc or {})}


def _run_cmd(cmd, cwd=None, timeout=90):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return r.returncode, (r.stdout or "")[-4000:], (r.stderr or "")[-4000:]
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except FileNotFoundError as e:
        return 127, "", str(e)


def _self_scan_checks() -> dict:
    """Deterministic, read-only checks. Returns findings with severities."""
    findings = []
    backend_dir = APP_ROOT / "backend"
    for py in ("server.py", "radar.py"):
        rc, out, err = _run_cmd([sys.executable, "-m", "py_compile", str(backend_dir / py)])
        if rc != 0:
            findings.append({"severity": "critical", "check": "py_compile", "path": f"backend/{py}", "detail": err[-600:]})
    rc, out, err = _run_cmd(["ruff", "check", "server.py", "radar.py", "--select", "F,E9", "--output-format", "concise", "-q"], cwd=str(backend_dir))
    if rc not in (0, 127) and out.strip():
        for ln in out.strip().splitlines()[:12]:
            findings.append({"severity": "high", "check": "ruff", "path": "backend/" + ln.split(":")[0], "detail": ln[:300]})
    comp_dir = APP_ROOT / "frontend" / "src" / "components"
    for js in sorted(comp_dir.glob("*.js")):
        rc, out, err = _run_cmd(["npx", "esbuild", str(js), "--loader:.js=jsx", "--bundle", "--outfile=/dev/null", "--log-level=error"],
                                cwd=str(APP_ROOT / "frontend"), timeout=120)
        if rc != 0:
            findings.append({"severity": "critical", "check": "esbuild", "path": f"frontend/src/components/{js.name}", "detail": err[-600:]})
    # TODO / FIXME census + oversized components (informational)
    for js in sorted(comp_dir.glob("*.js")):
        txt = js.read_text(encoding="utf-8", errors="replace")
        n = txt.count("TODO") + txt.count("FIXME")
        if n:
            findings.append({"severity": "low", "check": "todo_census", "path": f"frontend/src/components/{js.name}", "detail": f"{n} TODO/FIXME marker(s)"})
        lines = txt.count("\n")
        if lines > 700:
            findings.append({"severity": "info", "check": "size", "path": f"frontend/src/components/{js.name}", "detail": f"{lines} lines - consider splitting"})
    # frontend build-time console.log leftovers (informational)
    for js in sorted(comp_dir.glob("*.js")):
        txt = js.read_text(encoding="utf-8", errors="replace")
        if "console.log(" in txt:
            findings.append({"severity": "low", "check": "console_log", "path": f"frontend/src/components/{js.name}", "detail": "console.log present"})
    order = {"critical": 0, "high": 1, "low": 2, "info": 3}
    findings.sort(key=lambda f: order.get(f["severity"], 9))
    return {"findings": findings, "counts": {k: sum(1 for f in findings if f["severity"] == k) for k in order}}


async def run_self_scan(trigger: str = "manual") -> dict:
    global _self_scan_running
    if _self_scan_running:
        raise HTTPException(409, "A self-scan is already running")
    _self_scan_running = True
    sid = str(uuid.uuid4())
    started = datetime.now(timezone.utc)
    cfg = await _get_scan_config()
    scan = {"id": sid, "trigger": trigger, "started_at": started.isoformat(), "status": "running", "findings": [],
            "counts": {}, "proposal_ids": [], "note": "", "error": None}
    await db.self_scans.insert_one(dict(scan))
    try:
        checks = await asyncio.to_thread(_self_scan_checks)
        scan.update(checks)
        # Pick the highest-severity actionable finding that maps to an allowlisted file
        target = next((f for f in checks["findings"] if f["severity"] in ("critical", "high", "low") and f["check"] != "size"), None)
        made = 0
        if target and cfg.get("max_proposals_per_run", 1) > 0:
            try:
                _resolve_self_path(target["path"])
                instruction = (f"SCHEDULED SELF-SCAN ({started.date()}). Finding [{target['severity']}/{target['check']}] in {target['path']}: "
                               f"{target['detail']}\n\nOperator focus: {cfg['focus']}\n"
                               "Make the smallest correct change that resolves this finding. Do not refactor unrelated code.")
                prop = await self_propose({"instruction": instruction, "paths": [target["path"]]})
                await db.self_directives.update_one({"id": prop["id"]}, {"$set": {"origin": "scheduled_scan", "scan_id": sid}})
                scan["proposal_ids"].append(prop["id"])
                made += 1
            except HTTPException as he:
                scan["note"] = f"No proposal: {he.detail}"
            except Exception as e:
                scan["note"] = f"No proposal: {str(e)[:200]}"
        elif not target:
            scan["note"] = "Clean scan - no actionable findings, no proposal generated."
        scan["status"] = "done"
        scan["proposals_created"] = made
    except Exception as e:
        scan["status"] = "failed"
        scan["error"] = str(e)[:500]
        logger.error(f"self-scan failed: {e}")
    finally:
        _self_scan_running = False
        scan["finished_at"] = datetime.now(timezone.utc).isoformat()
        scan["duration_s"] = round((datetime.now(timezone.utc) - started).total_seconds(), 1)
        await db.self_scans.update_one({"id": sid}, {"$set": {k: v for k, v in scan.items() if k != "_id"}})
        nxt = (datetime.now(timezone.utc) + timedelta(hours=float(cfg.get("interval_hours") or 24))).isoformat() if cfg.get("enabled") else None
        await db.self_scan_config.update_one({"id": "owner"}, {"$set": {"last_run_at": scan["finished_at"], "next_run_at": nxt}}, upsert=True)
    scan.pop("_id", None)
    return scan


async def _self_scan_loop():
    await asyncio.sleep(20)
    while True:
        try:
            cfg = await _get_scan_config()
            if cfg.get("enabled"):
                now = datetime.now(timezone.utc)
                nxt = cfg.get("next_run_at")
                due = (nxt is None) or (datetime.fromisoformat(nxt) <= now)
                if due and not _self_scan_running:
                    await run_self_scan(trigger="scheduled")
        except Exception as e:
            logger.error(f"self-scan loop error: {e}")
        await asyncio.sleep(60)


@api_router.get("/self/scan/config")
async def self_scan_config_get():
    cfg = await _get_scan_config()
    cfg["running"] = _self_scan_running
    return cfg


@api_router.put("/self/scan/config")
async def self_scan_config_put(body: dict):
    cfg = await _get_scan_config()
    upd = {}
    if "enabled" in body:
        upd["enabled"] = bool(body["enabled"])
    if "interval_hours" in body:
        try:
            ih = float(body["interval_hours"])
        except Exception:
            raise HTTPException(400, "interval_hours must be a number")
        if not (1 <= ih <= 720):
            raise HTTPException(400, "interval_hours must be between 1 and 720")
        upd["interval_hours"] = ih
    if "max_proposals_per_run" in body:
        upd["max_proposals_per_run"] = max(0, min(1, int(body["max_proposals_per_run"])))
    if "focus" in body:
        upd["focus"] = str(body["focus"])[:1500]
    upd["updated_at"] = datetime.now(timezone.utc).isoformat()
    enabled = upd.get("enabled", cfg.get("enabled"))
    hours = upd.get("interval_hours", cfg.get("interval_hours") or 24)
    upd["next_run_at"] = (datetime.now(timezone.utc) + timedelta(hours=float(hours))).isoformat() if enabled else None
    await db.self_scan_config.update_one({"id": "owner"}, {"$set": upd}, upsert=True)
    out = await _get_scan_config()
    out["running"] = _self_scan_running
    return out


@api_router.post("/self/scan/run")
async def self_scan_run_now():
    return await run_self_scan(trigger="manual")


@api_router.get("/self/scans")
async def self_scans(limit: int = Query(20, ge=1, le=100)):
    return await db.self_scans.find({}, {"_id": 0}).sort("started_at", -1).to_list(limit)


# ==================== GOOGLE DRIVE (user-authorized OAuth ingestion) ====================
# Single-owner model (no multi-user auth in this app): all Drive creds stored under DRIVE_OWNER.
# Requires a Google Cloud *Web application* OAuth client with the registered redirect URI.
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build as gbuild

DRIVE_OWNER = "owner"
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_DRIVE_REDIRECT_URI = os.environ.get("GOOGLE_DRIVE_REDIRECT_URI", "")
GOOGLE_DRIVE_SCOPE = os.environ.get("GOOGLE_DRIVE_SCOPE", "https://www.googleapis.com/auth/drive")
FRONTEND_URL = (os.environ.get("FRONTEND_URL", "") or "").rstrip("/")

# Google Workspace native types -> export format we can analyze
GOOGLE_EXPORT_MAP = {
    "application/vnd.google-apps.document": ("text/plain", "txt"),
    "application/vnd.google-apps.spreadsheet": ("text/csv", "csv"),
    "application/vnd.google-apps.presentation": ("text/plain", "txt"),
}

def _drive_configured() -> bool:
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_DRIVE_REDIRECT_URI)

def _drive_client_config() -> dict:
    return {"web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [GOOGLE_DRIVE_REDIRECT_URI],
    }}

def _drive_flow(scopes):
    return Flow.from_client_config(_drive_client_config(), scopes=scopes, redirect_uri=GOOGLE_DRIVE_REDIRECT_URI)

async def _drive_service():
    doc = await db.drive_credentials.find_one({"user_id": DRIVE_OWNER}, {"_id": 0})
    if not doc:
        raise HTTPException(400, "Google Drive not connected. Connect it first.")
    def _build():
        creds = Credentials(
            token=doc["access_token"], refresh_token=doc.get("refresh_token"),
            token_uri=doc["token_uri"], client_id=doc["client_id"],
            client_secret=doc["client_secret"], scopes=doc["scopes"],
        )
        refreshed = False
        if creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
            refreshed = True
        svc = gbuild("drive", "v3", credentials=creds, cache_discovery=False)
        return svc, creds, refreshed
    svc, creds, refreshed = await asyncio.to_thread(_build)
    if refreshed:
        await db.drive_credentials.update_one({"user_id": DRIVE_OWNER}, {"$set": {
            "access_token": creds.token,
            "expiry": creds.expiry.isoformat() if creds.expiry else None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }})
    return svc

async def _store_analyzer_file(fsid, fname, rel_path, data: bytes, content_type: str, ext: str, source: str = "upload"):
    fid = str(uuid.uuid4())
    path = f"{APP_NAME}/analyzer/{fsid}/{fid}.{ext}"
    result = await asyncio.to_thread(storage_put, path, data, content_type)
    readable = ext in ANALYZER_TEXT_EXT
    text_excerpt = None
    if readable:
        try:
            text_excerpt = data.decode("utf-8", errors="replace")[:8000]
        except Exception:
            text_excerpt = None; readable = False
    record = {
        "id": fid, "fileset_id": fsid, "storage_path": result["path"],
        "original_filename": fname, "rel_path": rel_path, "content_type": content_type,
        "size": result.get("size", len(data)), "text_excerpt": text_excerpt,
        "readable": readable, "source": source, "is_deleted": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.afiles.insert_one(dict(record))
    return _public_afile(record)

@api_router.get("/drive/status")
async def drive_status():
    doc = await db.drive_credentials.find_one({"user_id": DRIVE_OWNER}, {"_id": 0})
    return {
        "configured": _drive_configured(),
        "connected": bool(doc),
        "scopes": (doc or {}).get("scopes", []),
        "email": (doc or {}).get("email"),
    }

@api_router.get("/drive/connect")
async def drive_connect():
    if not _drive_configured():
        raise HTTPException(400, "Google Drive is not configured on the server (missing client credentials).")
    flow = _drive_flow([GOOGLE_DRIVE_SCOPE])
    url, _state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent", state=DRIVE_OWNER,
    )
    return {"authorization_url": url}

@api_router.get("/oauth/drive/callback")
async def drive_callback(code: str = Query(None), state: str = Query(None), error: str = Query(None)):
    dest = f"{FRONTEND_URL}/?tab=analyzer"
    if error or not code:
        return RedirectResponse(f"{dest}&drive_error={error or 'no_code'}")
    try:
        flow = _drive_flow(None)  # accept whatever scopes Google grants
        def _fetch():
            flow.fetch_token(code=code)
            return flow.credentials
        creds = await asyncio.to_thread(_fetch)
        email = None
        try:
            svc = gbuild("drive", "v3", credentials=creds, cache_discovery=False)
            about = await asyncio.to_thread(lambda: svc.about().get(fields="user(emailAddress)").execute())
            email = about.get("user", {}).get("emailAddress")
        except Exception:
            pass
        await db.drive_credentials.update_one(
            {"user_id": DRIVE_OWNER},
            {"$set": {
                "user_id": DRIVE_OWNER, "access_token": creds.token, "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri, "client_id": creds.client_id, "client_secret": creds.client_secret,
                "scopes": list(creds.scopes or []), "email": email,
                "expiry": creds.expiry.isoformat() if creds.expiry else None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }}, upsert=True,
        )
        return RedirectResponse(f"{dest}&drive_connected=1")
    except Exception as e:
        logger.error(f"drive callback failed: {e}")
        return RedirectResponse(f"{dest}&drive_error=exchange_failed")

@api_router.post("/drive/disconnect")
async def drive_disconnect():
    doc = await db.drive_credentials.find_one({"user_id": DRIVE_OWNER}, {"_id": 0})
    if doc and doc.get("access_token"):
        try:
            await asyncio.to_thread(lambda: requests.post(
                "https://oauth2.googleapis.com/revoke", params={"token": doc["access_token"]}, timeout=10))
        except Exception:
            pass
    await db.drive_credentials.delete_one({"user_id": DRIVE_OWNER})
    return {"ok": True}

@api_router.get("/drive/list")
async def drive_list(folder_id: str = Query("root"), search: str = Query(None)):
    svc = await _drive_service()
    term = (search or "").strip()
    def _list():
        if term:
            safe = term.replace("\\", "").replace("'", "\\'")
            query = f"name contains '{safe}' and trashed=false"
            order = "folder,name"
        else:
            query = f"'{folder_id}' in parents and trashed=false"
            order = "folder,name"
        res = svc.files().list(
            q=query, pageSize=200, orderBy=order,
            fields="files(id,name,mimeType,size,modifiedTime)",
        ).execute()
        return res.get("files", [])
    items = await asyncio.to_thread(_list)
    out = []
    for f in items:
        is_folder = f.get("mimeType") == "application/vnd.google-apps.folder"
        out.append({
            "id": f["id"], "name": f.get("name"), "mimeType": f.get("mimeType"),
            "is_folder": is_folder, "size": int(f["size"]) if f.get("size") else None,
            "supported": is_folder or (f.get("mimeType") in GOOGLE_EXPORT_MAP)
                         or ((f.get("name", "").rsplit(".", 1)[-1].lower() if "." in f.get("name", "") else "") in ANALYZER_EXT),
        })
    return {"folder_id": folder_id, "items": out, "search": term or None}

async def _resolve_or_create_fileset(fileset_id, title):
    if fileset_id:
        fs = await db.file_sets.find_one({"id": fileset_id}, {"_id": 0})
        if not fs:
            raise HTTPException(404, "File set not found")
        return fileset_id
    fileset_id = str(uuid.uuid4())
    await db.file_sets.insert_one({"id": fileset_id, "title": title,
                                   "created_at": datetime.now(timezone.utc).isoformat()})
    return fileset_id

async def _import_drive_ids(svc, file_ids, fileset_id):
    imported, skipped = [], []
    for fid in file_ids[:200]:
        try:
            meta = await asyncio.to_thread(lambda: svc.files().get(fileId=fid, fields="id,name,mimeType,size").execute())
        except Exception:
            skipped.append({"id": fid, "reason": "metadata fetch failed"}); continue
        name = meta.get("name", fid)
        mime = meta.get("mimeType", "")
        if mime == "application/vnd.google-apps.folder":
            skipped.append({"name": name, "reason": "folder (select files inside it)"}); continue
        try:
            if mime.startswith("application/vnd.google-apps."):
                if mime not in GOOGLE_EXPORT_MAP:
                    skipped.append({"name": name, "reason": "unsupported Google type"}); continue
                export_mime, ext = GOOGLE_EXPORT_MAP[mime]
                data = await asyncio.to_thread(lambda: svc.files().export(fileId=fid, mimeType=export_mime).execute())
                content_type = export_mime
                fname = f"{name}.{ext}" if not name.lower().endswith(f".{ext}") else name
            else:
                ext = name.rsplit(".", 1)[-1].lower() if "." in name else "bin"
                if ext not in ANALYZER_EXT:
                    skipped.append({"name": name, "reason": f"unsupported type .{ext}"}); continue
                data = await asyncio.to_thread(lambda: svc.files().get_media(fileId=fid).execute())
                content_type = ANALYZER_EXT[ext]
                fname = name
            if not data:
                skipped.append({"name": name, "reason": "empty"}); continue
            if len(data) > MAX_UPLOAD_BYTES:
                skipped.append({"name": name, "reason": "too large (>10MB)"}); continue
            rec = await _store_analyzer_file(fileset_id, fname, name, data, content_type, ext, source="drive")
            imported.append(rec)
        except Exception as e:
            logger.error(f"drive import {fid} failed: {e}")
            skipped.append({"name": name, "reason": "download failed"})
    return imported, skipped

async def _drive_folder_file_ids(svc, folder_id, recursive=True, cap=200):
    ids = []
    def _children(fid):
        res = svc.files().list(q=f"'{fid}' in parents and trashed=false", pageSize=200,
                               fields="files(id,name,mimeType)").execute()
        return res.get("files", [])
    stack = [folder_id]
    while stack and len(ids) < cap:
        cur = stack.pop()
        for c in await asyncio.to_thread(_children, cur):
            if c.get("mimeType") == "application/vnd.google-apps.folder":
                if recursive:
                    stack.append(c["id"])
            else:
                ids.append(c["id"])
                if len(ids) >= cap:
                    break
    return ids

@api_router.post("/drive/import")
async def drive_import(body: dict):
    file_ids = (body or {}).get("file_ids") or []
    if not file_ids:
        raise HTTPException(400, "No files selected")
    fileset_id = await _resolve_or_create_fileset(
        (body or {}).get("fileset_id"),
        f"Drive import {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}")
    svc = await _drive_service()
    imported, skipped = await _import_drive_ids(svc, file_ids, fileset_id)
    return {"fileset_id": fileset_id, "imported": imported, "skipped": skipped}

@api_router.post("/drive/import-folder")
async def drive_import_folder(body: dict):
    folder_id = (body or {}).get("folder_id")
    if not folder_id:
        raise HTTPException(400, "folder_id required")
    recursive = bool((body or {}).get("recursive", True))
    svc = await _drive_service()
    try:
        meta = await asyncio.to_thread(lambda: svc.files().get(fileId=folder_id, fields="id,name,mimeType").execute())
    except Exception:
        raise HTTPException(404, "Folder not found")
    fname = meta.get("name", "folder")
    fileset_id = await _resolve_or_create_fileset(
        (body or {}).get("fileset_id"), f"Drive · {fname}")
    ids = await _drive_folder_file_ids(svc, folder_id, recursive=recursive, cap=200)
    if not ids:
        return {"fileset_id": fileset_id, "imported": [], "skipped": [{"name": fname, "reason": "no supported files found"}]}
    imported, skipped = await _import_drive_ids(svc, ids, fileset_id)
    return {"fileset_id": fileset_id, "imported": imported, "skipped": skipped}

@api_router.get("/filesets/{fsid}/file")
async def get_fileset_file_by_path(fsid: str, path: str = Query(...)):
    """Return a file's text content by its rel_path (for citation-jump viewer)."""
    rec = await db.afiles.find_one({"fileset_id": fsid, "rel_path": path, "is_deleted": False}, {"_id": 0})
    if not rec:
        rec = await db.afiles.find_one({"fileset_id": fsid, "original_filename": path, "is_deleted": False}, {"_id": 0})
    if not rec:
        raise HTTPException(404, "File not found in this set")
    content = rec.get("text_excerpt")
    if content is None:
        try:
            data, _ = await asyncio.to_thread(storage_get, rec["storage_path"])
            content = data.decode("utf-8", errors="replace")
        except Exception:
            content = "[binary file — no text preview available]"
    return {"rel_path": rec["rel_path"], "content_type": rec.get("content_type"),
            "readable": rec.get("readable", False), "content": content}

@api_router.get("/filesets/{fsid}/export")
async def export_fileset(fsid: str):
    fs = await db.file_sets.find_one({"id": fsid}, {"_id": 0})
    if not fs:
        raise HTTPException(404, "File set not found")
    files = await db.afiles.find({"fileset_id": fsid, "is_deleted": False}, {"_id": 0}).sort("rel_path", 1).to_list(500)
    analyses = await db.file_analyses.find({"fileset_id": fsid}, {"_id": 0}).sort("created_at", -1).to_list(1)
    chats = await db.file_chats.find({"fileset_id": fsid}, {"_id": 0}).sort("created_at", 1).to_list(500)

    lines = [f"# {fs['title']}", "", f"_Exported: {datetime.now(timezone.utc).isoformat()}_", ""]
    lines.append(f"## Files ({len(files)})")
    for f in files:
        src = f.get("source", "upload")
        lines.append(f"- `{f['rel_path']}` ({f['content_type']}, {f['size']} bytes, via {src})")
    lines.append("")
    if analyses:
        a = analyses[0]
        lines.append(f"## AI Analysis ({a.get('model_label','')})")
        if a.get("question"):
            lines.append(f"**Question:** {a['question']}\n")
        lines.append(a.get("analysis", ""))
        lines.append("")
    if chats:
        lines.append("## Follow-up Chat")
        for c in chats:
            who = "You" if c["role"] == "user" else "ACASO"
            lines.append(f"**{who}:** {c['content']}\n")
    md = "\n".join(lines)
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in fs["title"])[:50] or "analysis"
    headers = {"Content-Disposition": f'attachment; filename="{safe}.md"'}
    return Response(content=md, media_type="text/markdown", headers=headers)


# ---------------- ACASO Deliberation Engine: Council of Weavers ----------------
# Real multi-model council (Architect / Shadow / Muse / Finance) + Meta-Weaver synthesis.
# This is the endpoint the ACASO King runner scripts (Genesis Engine, Sovereign Hunter) call.
# HONESTY: every output here is LLM reasoning. No live market feeds, order books, on-chain
# data or lead databases are connected. "weak_signals" are model-inferred, not measured.

WEAVERS = [
    {
        "id": "architect", "name": "Architect", "role": "Thesis / Bull Case",
        "failover": ["gemini", "openai", "anthropic"],
        "system": ("You are the ARCHITECT weaver of the ACASO Council. You build the strongest constructive thesis: "
                   "the opportunity, the mechanism, the setup, and why it works. Concrete, specific, structured. "
                   "Never use certainty language ('will'); use probabilities and scenarios. 350-500 words."),
    },
    {
        "id": "shadow", "name": "Shadow", "role": "Risk Officer (veto power)",
        "failover": ["anthropic", "openai", "gemini"],
        "system": ("You are the SHADOW weaver of the ACASO Council - the risk officer and the most important voice. "
                   "Stress-test the challenge: what could go wrong, what the operator is not seeing, failure modes, "
                   "downside sizing, invalidation conditions, regulatory/legal exposure, and survival-first constraints. "
                   "You may VETO with 'SHADOW VETO:' if the idea is unsurvivable. 300-450 words."),
    },
    {
        "id": "muse", "name": "Muse", "role": "Contrarian / Asymmetry",
        "failover": ["openai", "anthropic", "gemini"],
        "system": ("You are the MUSE weaver of the ACASO Council - the contrarian. Find the non-obvious angle, the "
                   "crowded assumption to bet against, the convergence nobody combined, the asymmetric expression. "
                   "Also list 3-6 WEAK SIGNALS: early, under-noticed indicators relevant to this challenge (label them "
                   "clearly as inferred from reasoning, not from live data). 300-450 words."),
    },
    {
        "id": "finance", "name": "Finance", "role": "Unit Economics / Capital",
        "failover": ["openai", "gemini", "anthropic"],
        "system": ("You are the FINANCE weaver of the ACASO Council. Translate the challenge into numbers: revenue "
                   "model, pricing, CAC/LTV or position sizing, capital required, break-even, and conservative / "
                   "realistic / optimistic scenarios with explicit assumptions. 300-450 words."),
    },
]

META_WEAVER_SYSTEM = (
    "You are the META-WEAVER, allocator and synthesizer of the ACASO Council of Weavers (Architect, Shadow, Muse, "
    "Finance). You weigh each weaver's analysis, resolve disagreements explicitly, and produce the SOVEREIGN DIRECTIVE. "
    "Rules: risk-first (honor a Shadow veto if present), no certainty language, every recommendation ships with its "
    "invalidation condition. Follow the DELIVER format requested in the challenge exactly, in Markdown. "
    "After the directive, on its own line write exactly ===WEAK_SIGNALS=== and then 3-6 bullet weak signals "
    "(state they are inferred, not measured). Do not add anything after the weak signals."
)

DELIBERATION_PRESETS = [
    {
        "id": "genesis", "name": "Genesis Engine", "challenge_type": "product_strategy",
        "tagline": "Invent something that does not exist yet - buildable, defensible, revenue in 90 days.",
        "additional_context": "Invention mandate. Generate something genuinely new. Not an iteration.",
        "challenge": (
            "GENESIS DIRECTIVE - INVENTION MANDATE\n\n"
            "Founder Profile:\nFounder: Alexander Mojica\nCompanies: MediaLinxS (sovereign AI platform), OmniTrackX (logistics SaaS, Boston)\n"
            "Skills: Product design, AI architecture, branding, full-stack go-to-market\n"
            "Infrastructure: ACASO King sovereign AI, FastAPI, MongoDB, multi-model AI council\n"
            "Budget: Lean startup. 1-2 developers. Sub-$50K build capacity.\n"
            "Goal: Discover and launch something the world urgently needs that doesn't exist yet.\n\n"
            "MISSION:\nInvent something that does not yet exist. Not an iteration - a creation. The world needs it RIGHT NOW in 2026. "
            "Alexander can build it. It can generate revenue within 90 days of launch.\n\n"
            "Search these dimensions for the gap:\n1. PAIN POINTS technology has not solved\n2. REGULATORY GAPS - new 2024-2026 laws that created problems nobody built solutions for\n"
            "3. BEHAVIORAL SHIFTS - post-COVID, remote work, AI proliferation, economic anxiety\n4. CONVERGENCE OPPORTUNITIES - two existing technologies nobody has combined yet\n"
            "5. SILENT SUFFERING - groups experiencing a real problem with no words for it yet\n\n"
            "CONSTRAINTS:\n- Buildable by a lean team in under 90 days for under $50,000\n- Revenue-generating within 90 days of launch\n"
            "- Defensible moat: network effect, data flywheel, proprietary method, or regulatory advantage\n- AI is the foundation, not a feature\n"
            "- Alexander's existing infrastructure gives an unfair build advantage\n\n"
            "DELIVER:\n## THE INVENTION\n## THE WORLD PROBLEM IT SOLVES\n## HOW IT WORKS\n## BUSINESS MODEL\n## UNFAIR ADVANTAGES\n"
            "## THE MOAT\n## 90-DAY LAUNCH PLAN\n## FINANCIAL PROJECTION\n## SOVEREIGN VERDICT"
        ),
    },
    {
        "id": "hunter", "name": "Sovereign Hunter", "challenge_type": "market_entry",
        "tagline": "Profile 3 high-value targets and generate bespoke outreach sequences.",
        "additional_context": ("Sovereign Hunter mode - clients. Identify 3 real, specific, high-value targets. "
                               "Generate outreach that is specific, human, and conversion-optimized. No generic templates."),
        "challenge": (
            "SOVEREIGN HUNTER DIRECTIVE - TARGET ACQUISITION\n\nHunt Mode: CLIENTS - Find 3 high-value clients\n\n"
            "What is being offered:\nProduct/Service: OmniTrackX - AI-powered logistics SaaS for courier delivery, furniture moving, and office relocation companies.\n"
            "Core value proposition:\n- Real-time job tracking with live map\n- AI-powered damage reports and claim filing\n- Client-facing dashboard with transparent status updates\n"
            "- QR + condition-based inventory tracking\n- Competitive with Track-POD + Routific + Supermove combined at lower cost\n"
            "Pricing: Starter $149/mo | Growth $349/mo | Pro $749/mo | Enterprise custom\nMarket: Initially Boston, MA\n\n"
            "Target market:\nBoston, MA area logistics and moving companies: last-mile couriers (10-50 drivers), furniture movers and storage, "
            "office relocation specialists, B2B delivery for medical/legal/tech, companies on spreadsheets/paper/basic apps.\n\n"
            "PHASE 1 - TARGET IDENTIFICATION: 3 specific, realistic target categories. For each: Profile (type, size, pain points, decision maker, "
            "where they gather, trigger events, objections + neutralizers), Why they need this specifically, Credibility signals.\n\n"
            "PHASE 2 - OUTREACH GENERATION: per target - Version A cold email (subject + <150 words), Version B LinkedIn DM (<80 words), Version C follow-up.\n\n"
            "PHASE 3 - SEQUENCE STRATEGY: Day 1 / Day 3 / Day 7 / Day 14 per target.\n\n"
            "PHASE 4 - EXECUTION TOOLKIT: search strings, associations, events; the single highest-leverage zero-cost action for TODAY.\n\n"
            "## SOVEREIGN VERDICT\nWhich target is the highest-probability first close and exactly what to send them tomorrow morning."
        ),
    },
    {
        "id": "foresight", "name": "Foresight Thesis", "challenge_type": "market_foresight",
        "tagline": "Regime read + risk-defined thesis + invalidation. Reasoning only - no live market data connected.",
        "additional_context": ("Foresight Engine doctrine: Shadow owns risk and may veto. Output is setup + risk-defined expression + "
                               "invalidation condition, never a price target or 'buy'. Not financial advice. No live data is connected: "
                               "state clearly what data would be required to confirm each claim."),
        "challenge": (
            "FORESIGHT DIRECTIVE - REGIME & THESIS\n\nAsset / market: [EDIT ME - e.g. BTC/USD, a sector, an equity]\n"
            "Operator constraints: [EDIT ME - capital at risk, time horizon, max drawdown tolerated]\n\n"
            "DELIVER:\n## REGIME READ\n(trending / mean-reverting / high-vol / risk-on-off / illiquid - with confidence band and what would change it)\n"
            "## NOWCAST DIVERGENCE\n(where perceived fair state may diverge from price; the half-life of that gap; data needed to confirm)\n"
            "## THESIS (Architect)\n## RISK EXPRESSION (Shadow)\n(size cap, stop, tail hedge, slippage assumption)\n## CONTRARIAN VIEW (Muse)\n"
            "## INVALIDATION CONDITION\n(the exact observable that kills the thesis)\n## CHRONICLE ENTRY\n(journal-ready summary: reasoning, regime, size, invalidation)\n"
            "## SOVEREIGN VERDICT"
        ),
    },
]

class DeliberateRequest(BaseModel):
    challenge: str
    challenge_type: Optional[str] = "general"
    context: Optional[dict] = None
    preset_id: Optional[str] = None

def _split_weak_signals(text: str):
    marker = "===WEAK_SIGNALS==="
    if marker in text:
        directive, ws = text.split(marker, 1)
        return directive.strip(), ws.strip()
    return text.strip(), ""

@api_router.get("/acaso/presets")
async def acaso_presets():
    return DELIBERATION_PRESETS

@api_router.post("/acaso/deliberate")
async def acaso_deliberate(req: DeliberateRequest):
    challenge = (req.challenge or "").strip()
    if len(challenge) < 20:
        raise HTTPException(400, "challenge must be at least 20 characters")
    if len(challenge) > 20000:
        raise HTTPException(400, "challenge too long (max 20000 chars)")
    extra = ""
    if req.context and isinstance(req.context, dict):
        extra = str(req.context.get("additional_context") or "").strip()
    did = str(uuid.uuid4())
    started = datetime.now(timezone.utc)

    weaver_prompt = (
        f"CHALLENGE TYPE: {req.challenge_type or 'general'}\n"
        + (f"OPERATOR CONTEXT: {extra}\n" if extra else "")
        + f"\nCHALLENGE:\n{challenge}\n\nDeliver your analysis in your role. Markdown allowed."
    )

    async def run_weaver(w):
        try:
            ans, used, label = await llm_call_failover(w["system"], weaver_prompt, w["failover"], session=f"{did}-{w['id']}")
            return {"id": w["id"], "name": w["name"], "role": w["role"], "provider": used,
                    "model_label": label, "analysis": ans.strip(), "ok": True}
        except Exception as e:
            logger.error(f"weaver {w['id']} failed: {e}")
            return {"id": w["id"], "name": w["name"], "role": w["role"], "provider": None,
                    "model_label": "—", "analysis": f"Weaver unreachable: {e}", "ok": False}

    weavers = await asyncio.gather(*[run_weaver(w) for w in WEAVERS])
    ok = [w for w in weavers if w["ok"]]
    if not ok:
        raise HTTPException(502, "All weavers failed to respond")

    synthesis_input = "\n\n".join([f"### [{w['name']} · {w['role']} · {w['model_label']}]\n{w['analysis']}" for w in ok])
    meta_prompt = (
        f"CHALLENGE TYPE: {req.challenge_type or 'general'}\n"
        + (f"OPERATOR CONTEXT: {extra}\n" if extra else "")
        + f"\nORIGINAL CHALLENGE:\n{challenge}\n\nCOUNCIL ANALYSES:\n{synthesis_input}\n\n"
        "Now produce the SOVEREIGN DIRECTIVE (then ===WEAK_SIGNALS=== and the bullets)."
    )
    try:
        meta_text, meta_used, meta_label = await llm_call_failover(
            META_WEAVER_SYSTEM, meta_prompt, ["openai", "anthropic", "gemini"], session=f"{did}-meta")
    except Exception as e:
        raise HTTPException(502, f"Meta-Weaver synthesis failed: {e}")

    directive, weak_signals = _split_weak_signals(meta_text)
    if not weak_signals:
        # fall back to Muse's own weak-signal section if the meta-weaver skipped the marker
        muse = next((w for w in ok if w["id"] == "muse"), None)
        if muse and "WEAK SIGNAL" in muse["analysis"].upper():
            idx = muse["analysis"].upper().find("WEAK SIGNAL")
            weak_signals = muse["analysis"][idx:].strip()[:2500]

    council_labels = sorted({w["model_label"] for w in ok} | {meta_label})
    shadow = next((w for w in ok if w["id"] == "shadow"), None)
    vetoed = bool(shadow and "SHADOW VETO" in shadow["analysis"].upper())
    finished = datetime.now(timezone.utc)

    doc = {
        "id": did,
        "deliberation_id": did,
        "timestamp": finished.isoformat(),
        "created_at": finished.isoformat(),
        "duration_s": round((finished - started).total_seconds(), 1),
        "challenge_type": req.challenge_type or "general",
        "preset_id": req.preset_id,
        "challenge": challenge,
        "additional_context": extra,
        "weavers": weavers,
        "weavers_synthesis": synthesis_input,
        "meta_weaver": {"provider": meta_used, "model_label": meta_label},
        "sovereign_directive": directive,
        "weak_signals": weak_signals,
        "shadow_veto": vetoed,
        "council_consulted": council_labels,
        "title": challenge.split("\n", 1)[0][:90],
        "data_provenance": "LLM reasoning only. No live market feeds, on-chain data, or lead databases are connected. Not financial advice.",
    }
    await db.deliberations.insert_one(dict(doc))
    return doc

@api_router.get("/acaso/deliberations")
async def list_deliberations(limit: int = Query(30, ge=1, le=200)):
    return await db.deliberations.find(
        {}, {"_id": 0, "weavers": 0, "weavers_synthesis": 0, "sovereign_directive": 0, "challenge": 0}
    ).sort("created_at", -1).to_list(limit)

@api_router.get("/acaso/deliberations/{did}")
async def get_deliberation(did: str):
    doc = await db.deliberations.find_one({"id": did}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Deliberation not found")
    return doc

@api_router.delete("/acaso/deliberations/{did}")
async def delete_deliberation(did: str):
    r = await db.deliberations.delete_one({"id": did})
    if r.deleted_count == 0:
        raise HTTPException(404, "Deliberation not found")
    return {"ok": True}

@api_router.get("/acaso/deliberations/{did}/export")
async def export_deliberation(did: str):
    d = await db.deliberations.find_one({"id": did}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Deliberation not found")
    preset = next((p["name"] for p in DELIBERATION_PRESETS if p["id"] == d.get("preset_id")), "Custom")
    lines = [
        f"# ACASO COUNCIL DELIBERATION - {preset}",
        f"Generated: {d['timestamp'][:19]} | Deliberation: {d['id']} | Type: {d['challenge_type']}",
        f"Council: {', '.join(d.get('council_consulted') or [])}",
        f"Shadow veto: {'YES' if d.get('shadow_veto') else 'no'}",
        "", f"> {d.get('data_provenance', '')}", "",
        "---", "## WEAK SIGNALS (inferred)", d.get("weak_signals") or "_none_", "",
        "---", d.get("sovereign_directive") or "", "",
        "---", "## COUNCIL OF WEAVERS - INDIVIDUAL ANALYSES",
    ]
    for w in d.get("weavers", []):
        lines += [f"### {w['name']} - {w['role']} ({w.get('model_label', '')})", w.get("analysis", ""), ""]
    lines += ["---", "## ORIGINAL CHALLENGE", "```", d.get("challenge", ""), "```", "",
              "*ACASO Omniverse - Council of Weavers Deliberation Engine*"]
    md = "\n".join(lines)
    safe = f"acaso-{(d.get('preset_id') or 'deliberation')}-{d['id'][:8]}"
    return Response(content=md, media_type="text/markdown",
                    headers={"Content-Disposition": f'attachment; filename="{safe}.md"'})

class ToMissionRequest(BaseModel):
    mode: Optional[str] = "Move"

def _extract_plan_section(directive: str) -> str:
    """Prefer the 90-day / launch-plan section of a directive; fall back to the whole thing."""
    if not directive:
        return ""
    lines = directive.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("#") and any(k in ln.upper() for k in ("90-DAY", "90 DAY", "LAUNCH PLAN", "SEQUENCE", "EXECUTION", "NEXT ACTION")):
            start = i
            break
    if start is None:
        return directive[:6000]
    out = [lines[start]]
    for ln in lines[start + 1:]:
        if ln.lstrip().startswith("## ") and "VERDICT" not in ln.upper():
            break
        out.append(ln)
    return "\n".join(out)[:6000]

@api_router.post("/acaso/deliberations/{did}/to-mission", response_model=Mission)
async def deliberation_to_mission(did: str, req: ToMissionRequest = None):
    d = await db.deliberations.find_one({"id": did}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Deliberation not found")
    if d.get("mission_id"):
        existing = await db.missions.find_one({"id": d["mission_id"]}, {"_id": 0})
        if existing:
            return Mission(**existing)
    plan = _extract_plan_section(d.get("sovereign_directive") or "")
    verdict = ""
    up = (d.get("sovereign_directive") or "").upper()
    if "SOVEREIGN VERDICT" in up:
        verdict = (d.get("sovereign_directive") or "")[up.find("SOVEREIGN VERDICT"):][:600]
    text = (f"Execute the Council of Weavers' Sovereign Directive titled: {d.get('title','')}\n\n"
            f"PLAN TO EXECUTE:\n{plan}\n\n{verdict}").strip()
    mode = (req.mode if req and req.mode in MODES else "Move")
    mission = await compile_mission_from_text(text, mode, source_deliberation_id=did)
    await db.deliberations.update_one({"id": did}, {"$set": {"mission_id": mission.id, "mission_title": mission.title}})
    return mission




# ---------------- Voice Chat (browser Web Speech API on the client; LLM here) ----------------
# STT/TTS happen in the user's browser (no audio touches this server). This endpoint receives the
# transcript text, answers in "fast" mode (single model, session memory) or "council" mode (full
# Council of Weavers deliberation + a short spoken summary), and stores the transcript.

class VoiceRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: Optional[str] = "fast"  # "fast" | "council"

VOICE_SYSTEM = (
    "You are ACASO, the sovereign AI of ACASO Omniverse, speaking aloud to your owner in a live voice conversation. "
    "Persona: calm, precise, warm, decisive. Your reply will be read by a text-to-speech engine, so: plain spoken "
    "sentences, no markdown, no bullet symbols, no code, no URLs. Keep answers to 1-4 sentences unless the owner "
    "explicitly asks for detail. Be honest about what you can and cannot do: you have no live market data, and "
    "actions in NEXUS are simulated. If asked to do something in the app, explain which tab or feature does it.\n"
    "App map: Sovereign Home compiles revenue directives into staged missions; Bug Bounty runs authorized security "
    "engagements with a three-soul AI council and owner approval gates; Council convenes the Council of Weavers "
    "(Architect, Shadow, Muse, Finance plus Meta-Weaver) for strategic deliberations like the Genesis Engine and "
    "Sovereign Hunter; Voice is this conversation; Ask All AIs queries GPT, Gemini and Claude together; File Analyzer "
    "ingests uploads, folders or Google Drive files for AI analysis and cited chat; Self-Directive lets the owner "
    "approve preview-only code changes to ACASO itself with rollback; Chronicle is the outcome ledger; Agent Bridge "
    "is the API-key protected agent interface."
)

@api_router.post("/voice/chat")
async def voice_chat(req: VoiceRequest):
    text = (req.message or "").strip()
    if not text:
        raise HTTPException(400, "Message required")
    if len(text) > 4000:
        raise HTTPException(400, "Message too long")
    session = req.session_id or str(uuid.uuid4())
    mode = "council" if (req.mode or "").lower() == "council" else "fast"
    now = datetime.now(timezone.utc).isoformat()

    history = await db.voice_messages.find({"session_id": session}, {"_id": 0}).sort("created_at", -1).to_list(12)
    history.reverse()
    hist_text = "\n".join([f"{'Owner' if h['role']=='user' else 'ACASO'}: {h['content']}" for h in history])

    await db.voice_messages.insert_one({
        "id": str(uuid.uuid4()), "session_id": session, "role": "user", "content": text, "mode": mode, "created_at": now
    })

    deliberation_id = None
    full_text = None
    if mode == "fast":
        prompt = (f"Conversation so far:\n{hist_text}\n\n" if hist_text else "") + f"Owner just said: {text}\n\nReply aloud."
        try:
            spoken, used, label = await llm_call_failover(VOICE_SYSTEM, prompt, ["openai", "gemini", "anthropic"], session=f"voice-{session}")
        except Exception as e:
            raise HTTPException(502, f"Voice model unavailable: {e}")
    else:
        ctx = f"Live voice conversation. Recent context:\n{hist_text}" if hist_text else "Live voice conversation."
        result = await acaso_deliberate(DeliberateRequest(challenge=text if len(text) >= 20 else text + " (please deliberate on this)",
                                                          challenge_type="voice_council", preset_id="voice",
                                                          context={"additional_context": ctx}))
        deliberation_id = result["id"]
        full_text = result["sovereign_directive"]
        label = "Council of Weavers -> " + result["meta_weaver"]["model_label"]
        try:
            spoken, _, _ = await llm_call_failover(
                VOICE_SYSTEM,
                f"The Council of Weavers just deliberated on the owner's question: {text}\n\nSovereign Directive:\n{full_text}\n\n"
                f"Weak signals:\n{result.get('weak_signals','')}\n\nShadow veto: {'yes' if result.get('shadow_veto') else 'no'}\n\n"
                "Speak a faithful spoken summary in at most 6 sentences: the verdict, the single biggest risk, and the invalidation condition. "
                "Mention the veto if there was one. Tell the owner the full directive is in the transcript and the Council tab.",
                ["openai", "gemini", "anthropic"], session=f"voice-{session}-sum")
        except Exception:
            spoken = "The council has resolved. The full directive is in the transcript and in the Council tab."

    spoken = spoken.strip()
    reply_doc = {
        "id": str(uuid.uuid4()), "session_id": session, "role": "assistant", "content": spoken, "mode": mode,
        "model_label": label, "deliberation_id": deliberation_id, "full_text": full_text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.voice_messages.insert_one(dict(reply_doc))
    reply_doc.pop("_id", None)
    return {"session_id": session, "reply": reply_doc}

@api_router.get("/voice/history")
async def voice_history(session_id: str = Query(...), limit: int = Query(60, ge=1, le=300)):
    msgs = await db.voice_messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    msgs.reverse()
    return msgs

@api_router.delete("/voice/history")
async def voice_clear(session_id: str = Query(...)):
    r = await db.voice_messages.delete_many({"session_id": session_id})
    return {"ok": True, "deleted": r.deleted_count}


# ---------------- Voice Commands: parse spoken intent -> execute -> spoken confirmation ----------------
VOICE_TABS = {
    "home": ["home", "sovereign home", "board", "missions", "mission board"],
    "bounty": ["bounty", "bug bounty", "security"],
    "council": ["council", "weavers", "council of weavers"],
    "voice": ["voice", "voice channel"],
    "radar": ["radar", "opportunity radar", "opportunities", "grants"],
    "askai": ["ask all ais", "ask all", "ask ai", "ask the ais"],
    "analyzer": ["analyzer", "file analyzer", "files"],
    "self": ["self directive", "self-directive", "self"],
    "chronicle": ["chronicle", "ledger", "outcomes"],
    "bridge": ["bridge", "agent bridge", "api"],
    "node": ["local node", "node", "my computer", "desktop", "my pc"],
    "apex": ["apex", "apex nexus", "store", "storefront", "products"],
}
COMMAND_SCHEMA = (
    "Return ONLY minified JSON {\"intent\": ..., \"args\": {...}} with intent one of: "
    "open_tab {tab: home|bounty|council|voice|radar|askai|analyzer|self|chronicle|bridge|node|apex}; "
    "council_deliberate {challenge: string, preset_id: genesis|hunter|foresight|custom}; "
    "compile_directive {directive: string, mode: Make|Find|Move|Collect}; "
    "radar_discover {keyword: string|null}; radar_search {query: string}; "
    "ask {message: string}; unknown {}. Never invent details the user did not say."
)


class VoiceCommand(BaseModel):
    transcript: str
    session_id: Optional[str] = None
    execute: bool = True


def _rule_intent(t: str):
    s = t.lower().strip().rstrip(".!?")
    s = re.sub(r"^(hey |ok |okay )?acaso[, ]*", "", s)
    m = re.match(r"^(open|go to|show|switch to|take me to)\s+(the\s+)?(.+)$", s)
    if m:
        target = m.group(3).replace(" tab", "").strip()
        for key, names in VOICE_TABS.items():
            if target in names or target == key:
                return {"intent": "open_tab", "args": {"tab": key}}
    m = re.match(r"^(convene|summon|call)\s+(the\s+)?council\s+(on|about|for)\s+(.+)$", s)
    if m:
        return {"intent": "council_deliberate", "args": {"challenge": m.group(4), "preset_id": "custom"}}
    m = re.match(r"^(discover|find|scan for|search for)\s+(new\s+)?(grants|opportunities|contracts|bounties)(\s+(for|about|on)\s+(.+))?$", s)
    if m:
        return {"intent": "radar_discover", "args": {"keyword": (m.group(6) or "").strip() or None}}
    m = re.match(r"^(compile|create|make)\s+(a\s+)?(mission|directive)\s*(to|for|:)?\s*(.+)$", s)
    if m:
        return {"intent": "compile_directive", "args": {"directive": m.group(5), "mode": "Move"}}
    return None


@api_router.post("/voice/command")
async def voice_command(cmd: VoiceCommand):
    text = (cmd.transcript or "").strip()
    if not text:
        raise HTTPException(400, "transcript required")
    parsed = _rule_intent(text)
    parser = "rules"
    if not parsed:
        try:
            raw, _, _ = await llm_call_failover(
                "You are ACASO's voice command router. " + COMMAND_SCHEMA, f"Spoken command: {text}",
                ["openai", "gemini", "anthropic"])
            parsed = extract_json(raw)
            parser = "llm"
        except Exception as e:
            parsed = {"intent": "unknown", "args": {}}
            parser = f"llm_failed: {e}"
    intent = (parsed or {}).get("intent") or "unknown"
    args = (parsed or {}).get("args") or {}
    out = {"transcript": text, "intent": intent, "args": args, "parser": parser, "navigate_tab": None, "spoken": "", "result": None}

    if not cmd.execute:
        out["spoken"] = f"I heard a {intent.replace('_', ' ')} command."
        return out

    try:
        if intent == "open_tab":
            tab = args.get("tab") if args.get("tab") in VOICE_TABS else "home"
            out["navigate_tab"] = tab
            out["spoken"] = f"Opening {tab.replace('askai', 'Ask All AIs').replace('self', 'Self-Directive')}."
        elif intent == "council_deliberate":
            ch = (args.get("challenge") or "").strip()
            if len(ch) < 20:
                ch = ch + " - deliberate on this fully with risk, invalidation and next steps"
            res = await acaso_deliberate(DeliberateRequest(challenge=ch, challenge_type="voice_command",
                                                           preset_id=args.get("preset_id") or "custom",
                                                           context={"additional_context": "Issued by voice command."}))
            out["result"] = {"deliberation_id": res["id"], "title": res["title"], "shadow_veto": res["shadow_veto"]}
            out["navigate_tab"] = "council"
            summ, _, _ = await llm_call_failover(VOICE_SYSTEM,
                f"Summarize this Sovereign Directive aloud in at most 4 sentences, mention any Shadow veto:\n{res['sovereign_directive'][:5000]}",
                ["openai", "gemini", "anthropic"])
            out["spoken"] = summ.strip() + " The full directive is in the Council tab."
        elif intent == "compile_directive":
            d = (args.get("directive") or "").strip()
            if not d:
                raise HTTPException(400, "no directive heard")
            m = await compile_mission_from_text(d, args.get("mode") or "Move")
            out["result"] = {"mission_id": m.id, "title": m.title, "steps": len(m.steps), "amount": m.amount}
            out["navigate_tab"] = "home"
            out["spoken"] = f"Mission {m.title} compiled with {len(m.steps)} steps and a target of {int(m.amount)} dollars. It is on the Sovereign Home board."
        elif intent == "radar_discover":
            import radar as _radar
            res = await _radar.discover(_radar.DiscoverRequest(keyword=args.get("keyword"), limit=20))
            ok = [r for r in res["runs"] if not r["error"]]
            new = sum(r["new"] for r in ok); upd = sum(r["updated"] for r in ok)
            skipped = [r["source"] for r in res["runs"] if r["error"]]
            out["result"] = res
            out["navigate_tab"] = "radar"
            out["spoken"] = (f"Radar pulled {new} new and re-verified {upd} opportunities from {len(ok)} source{'s' if len(ok)!=1 else ''}."
                             + (f" {', '.join(skipped)} skipped - not configured." if skipped else "") + " Verify each on its original source.")
        elif intent == "radar_search":
            import radar as _radar
            prop = await _radar.nl_search(_radar.NLSearch(query=args.get("query") or text))
            out["result"] = prop
            out["navigate_tab"] = "radar"
            out["spoken"] = "I proposed Radar filters for that search. Review and apply them in the Radar tab - I never apply filters silently."
        elif intent == "ask":
            msg = args.get("message") or text
            ans, _, label = await llm_call_failover(VOICE_SYSTEM, f"Owner asked: {msg}\n\nReply aloud.", ["openai", "gemini", "anthropic"])
            out["result"] = {"model_label": label}
            out["spoken"] = ans.strip()
        else:
            out["spoken"] = "I did not catch a command. Try: open radar, convene the council on a topic, discover grants, or compile a mission to do something."
    except HTTPException as he:
        out["spoken"] = f"That failed: {he.detail}"
        out["error"] = str(he.detail)
    except Exception as e:
        logger.error(f"voice command failed: {e}")
        out["spoken"] = "That command failed on the server."
        out["error"] = str(e)[:300]

    await db.voice_commands.insert_one({"id": str(uuid.uuid4()), "session_id": cmd.session_id, "transcript": text, "intent": intent,
                                        "args": args, "parser": parser, "error": out.get("error"), "created_at": datetime.now(timezone.utc).isoformat()})
    return out


# ---------------- Opportunity Radar (separate module) ----------------
import radar as radar_module
radar_module.init(db, llm_call_failover, compile_mission_from_text, extract_json)
api_router.include_router(radar_module.router)

# ---------------- Local Node orchestration + server research browser ----------------
import node as node_module
node_module.init(db, require_key, llm_call_failover, extract_json)
api_router.include_router(node_module.router)
api_router.include_router(node_module.browse_router)

# ---------------- Apex Nexus storefront ----------------
import apex as apex_module
apex_module.init(db, llm_call_failover, extract_json)
api_router.include_router(apex_module.router)

# ---------------- Companion: small desktop window - voice + screen/window share + vision ----------------
# Frames are captured in the owner's browser (getDisplayMedia -> canvas -> JPEG base64), sent per message only
# when the owner includes them, analysed with a vision model, and NOT stored (only a thumbnail hash + text).
from emergentintegrations.llm.chat import ImageContent, TextDelta, StreamDone  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402

COMPANION_SYSTEM = (
    "You are ACASO Companion - a small always-available assistant window on the owner's desktop. The owner may share a "
    "window or screen; when a screenshot is attached, ground your answer in what is visibly there: read text, identify the "
    "app/site, spot errors, summarise, suggest the next click, or draft what they need. If something is not visible, say so. "
    "Spoken-friendly style: plain sentences, short paragraphs, no heavy markdown, no emojis. Be concise unless asked to go deep. "
    "You know the ACASO app: Sovereign Home (missions), Bug Bounty, Council of Weavers, Voice, Radar (real grants/contracts), "
    "Ask All AIs, File Analyzer, Self-Directive, Chronicle, Local Node (acts on the owner's PC with approval), Agent Bridge. "
    "Never claim to have taken an action yourself; suggest the tab or Local Node task that would do it."
)


class CompanionRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    image_b64: Optional[str] = None  # JPEG/PNG base64 (no data: prefix) - optional shared-screen frame
    share_label: Optional[str] = None


@api_router.post("/companion/chat")
async def companion_chat(req: CompanionRequest):
    text = (req.message or "").strip()
    if not text and not req.image_b64:
        raise HTTPException(400, "Message or image required")
    if req.image_b64 and len(req.image_b64) > 6_000_000:
        raise HTTPException(413, "Frame too large - downscale before sending")
    session = req.session_id or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    hist = await db.companion_messages.find({"session_id": session}, {"_id": 0}).sort("created_at", -1).to_list(10)
    hist.reverse()
    hist_txt = "\n".join([f"{'Owner' if h['role']=='user' else 'Companion'}: {h['content'][:600]}" for h in hist])
    prompt = ((f"Conversation so far:\n{hist_txt}\n\n" if hist_txt else "")
              + (f"[Owner is sharing: {req.share_label}] " if req.share_label else "")
              + (f"Owner: {text}" if text else "Owner shared their screen without a question - describe what you see and anything notable."))
    img = None
    if req.image_b64:
        b64 = req.image_b64.split(",", 1)[1] if req.image_b64.startswith("data:") else req.image_b64
        img = ImageContent(image_base64=b64)
    await db.companion_messages.insert_one({"id": str(uuid.uuid4()), "session_id": session, "role": "user", "content": text or "(shared screen)",
                                            "had_image": bool(img), "share_label": req.share_label, "created_at": now})

    async def gen():
        full = []
        used = None
        order = [("openai", "gpt-4o-mini", "Companion · GPT-4o"), ("gemini", "gemini-2.5-flash", "Companion · Gemini 2.5")]
        yield f"data: {json.dumps({'type': 'session', 'session_id': session})}\n\n"
        for prov, model, label in order:
            try:
                chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"companion-{session}-{uuid.uuid4().hex[:6]}", system_message=COMPANION_SYSTEM).with_model(prov, model)
                msg = UserMessage(text=prompt, file_contents=[img]) if img else UserMessage(text=prompt)
                async for ev in chat.stream_message(msg):
                    if isinstance(ev, TextDelta):
                        full.append(ev.content)
                        yield f"data: {json.dumps({'type': 'delta', 'content': ev.content})}\n\n"
                    elif isinstance(ev, StreamDone):
                        break
                used = label
                break
            except Exception as e:
                logger.error(f"companion {prov} failed: {e}")
                full = []
                continue
        reply = "".join(full).strip()
        if not reply:
            reply = "I could not reach a vision model just now. Try again in a moment."
            yield f"data: {json.dumps({'type': 'delta', 'content': reply})}\n\n"
        await db.companion_messages.insert_one({"id": str(uuid.uuid4()), "session_id": session, "role": "assistant", "content": reply,
                                                "model_label": used, "created_at": datetime.now(timezone.utc).isoformat()})
        yield f"data: {json.dumps({'type': 'done', 'model_label': used, 'content': reply})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@api_router.get("/companion/history")
async def companion_history(session_id: str = Query(...), limit: int = Query(60, ge=1, le=300)):
    msgs = await db.companion_messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    msgs.reverse()
    return msgs


@api_router.delete("/companion/history")
async def companion_clear(session_id: str = Query(...)):
    r = await db.companion_messages.delete_many({"session_id": session_id})
    return {"ok": True, "deleted": r.deleted_count}


# ---- Watch mode: periodic glance at the shared window; speak only when something notable appears ----
WATCH_SYSTEM = (
    "You are ACASO Companion in WATCH MODE. You receive a screenshot of the owner's shared window every ~30 seconds. "
    "Decide whether it is worth interrupting the owner. Speak up ONLY for: (1) a visible error, exception, failed build, "
    "red alert, blocked payment, or warning dialog; (2) a form or sign-up the owner could fill (visible input fields with "
    "labels); (3) an explicit request for action (approval prompt, deadline warning). Everything else is 'none'. "
    "If the screen is essentially the same situation as the previous note, answer 'none' to avoid repeating yourself. "
    "Respond ONLY with minified JSON: {\"notable\": true|false, \"kind\": \"error\"|\"form\"|\"action\"|\"none\", "
    "\"message\": string (<=2 sentences, spoken style, specific: quote the error text or name the form fields), "
    "\"summary\": string (<=12 words describing the screen for memory), \"confidence\": 0-1}"
)


class WatchRequest(BaseModel):
    image_b64: str
    session_id: Optional[str] = None
    share_label: Optional[str] = None
    previous_summary: Optional[str] = None
    last_spoken: Optional[str] = None


@api_router.post("/companion/watch")
async def companion_watch(req: WatchRequest):
    if not req.image_b64:
        raise HTTPException(400, "image_b64 required")
    if len(req.image_b64) > 6_000_000:
        raise HTTPException(413, "Frame too large")
    b64 = req.image_b64.split(",", 1)[1] if req.image_b64.startswith("data:") else req.image_b64
    prompt = ((f"Shared: {req.share_label}. " if req.share_label else "")
              + (f"Previous screen note: {req.previous_summary}. " if req.previous_summary else "First glance. ")
              + (f"You last said: \"{req.last_spoken}\". " if req.last_spoken else "")
              + "Assess this frame.")
    out = None
    used = None
    for prov, model, label in [("openai", "gpt-4o-mini", "Watch · GPT-4o"), ("gemini", "gemini-2.5-flash", "Watch · Gemini 2.5")]:
        try:
            chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"watch-{uuid.uuid4().hex[:8]}", system_message=WATCH_SYSTEM).with_model(prov, model)
            raw = await chat.send_message(UserMessage(text=prompt, file_contents=[ImageContent(image_base64=b64)]))
            out = extract_json(raw)
            used = label
            break
        except Exception as e:
            logger.error(f"watch {prov} failed: {e}")
            continue
    if not out:
        raise HTTPException(502, "Vision model unavailable")
    notable = bool(out.get("notable")) and out.get("kind") in ("error", "form", "action") and float(out.get("confidence") or 0) >= 0.5
    res = {"notable": notable, "kind": out.get("kind") if notable else "none", "message": (out.get("message") or "").strip() if notable else "",
           "summary": (out.get("summary") or "")[:120], "confidence": out.get("confidence"), "model_label": used, "at": datetime.now(timezone.utc).isoformat()}
    if notable and req.session_id:
        await db.companion_messages.insert_one({"id": str(uuid.uuid4()), "session_id": req.session_id, "role": "assistant", "content": res["message"],
                                                "model_label": used, "watch": True, "kind": res["kind"], "created_at": res["at"]})
    return res


# ---------------- Owner authentication (email + password, httpOnly cookie JWT) ----------------
import auth as auth_module
auth_module.init(db, get_or_create_key)
api_router.include_router(auth_module.router)

app.include_router(api_router)

# Session guard for every /api/* route (public paths + X-ACASO-Key requests pass through; see auth.py)
app.middleware("http")(auth_module.guard)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def _startup_storage():
    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.error(f"Storage init failed at startup (will retry on first use): {e}")

@app.on_event("startup")
async def _startup_self_scan():
    global _self_scan_task
    if _self_scan_task is None:
        _self_scan_task = asyncio.create_task(_self_scan_loop())
        logger.info("Self-scan scheduler started (propose-only)")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

```


### `backend/requirements.txt`
```text
aiohappyeyeballs==2.7.1
aiohttp==3.14.3
aiosignal==1.4.0
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.14.2
ast_serialize==0.8.0
attrs==26.1.0
bcrypt==4.1.3
black==26.5.1
boto3==1.43.79
botocore==1.43.79
certifi==2026.7.22
cffi==2.1.1
charset-normalizer==3.5.1
click==8.4.2
cryptography==50.0.0
distro==1.9.0
dnspython==2.8.0
ecdsa==0.19.2
email-validator==2.3.0
emergentintegrations==0.2.0
execnet==2.1.2
fastapi==0.110.1
fastuuid==0.14.0
filelock==3.32.4
flake8==7.3.0
frozenlist==1.8.0
fsspec==2026.7.0
google-ai-generativelanguage==0.6.15
google-api-core==2.33.0
google-api-python-client==2.199.0
google-auth==2.57.0
google-auth-httplib2==0.4.2
google-auth-oauthlib==1.4.1
google-genai==2.19.0
google-generativeai==0.8.6
googleapis-common-protos==1.75.0
greenlet==3.5.5
grpcio==1.83.0
grpcio-status==1.71.2
h11==0.16.0
hf-xet==1.6.0
httpcore==1.0.9
httplib2==0.32.0
httpx==0.28.1
huggingface_hub==1.28.0
idna==3.19
importlib_metadata==9.0.0
iniconfig==2.3.0
isort==8.0.1
Jinja2==3.1.6
jiter==0.16.0
jmespath==1.1.0
jq==1.12.0
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
librt==0.15.0
litellm @ https://customer-assets.emergentagent.com/internal-asset/library/litellm-1.80.0-py3-none-any.whl#sha256=adf398c513273de9341f61822296c6b2145f7f2dc4a69daf3ac04829f5bde3f8
markdown-it-py==4.2.0
MarkupSafe==3.0.3
mccabe==0.7.0
mdurl==0.1.2
motor==3.3.1
multidict==6.7.1
mypy==2.3.1
mypy_extensions==1.1.0
numpy==2.4.6
oauthlib==3.3.1
openai==1.99.9
packaging==26.3
pandas==3.0.5
passlib==1.7.4
pathspec==1.1.1
pillow==12.3.0
platformdirs==4.11.4
playwright==1.62.0
pluggy==1.6.0
propcache==0.5.2
proto-plus==1.28.2
protobuf==5.29.6
pyasn1==0.6.4
pyasn1_modules==0.4.2
pycodestyle==2.14.0
pycparser==3.0
pydantic==2.13.4
pydantic_core==2.46.4
pyee==13.0.1
pyflakes==3.4.0
Pygments==2.21.0
PyJWT==2.13.0
pymongo==4.6.3
pyparsing==3.3.2
pytest==9.1.1
pytest-xdist==3.8.0
python-dateutil==2.9.0.post0
python-dotenv==1.2.3
python-jose==3.5.0
python-multipart==0.0.32
pytokens==0.4.1
PyYAML==6.0.3
referencing==0.37.0
regex==2026.7.19
requests==2.34.2
requests-oauthlib==2.0.0
rich==15.0.0
rpds-py==2026.6.3
rsa==4.9.1
s3transfer==0.19.2
s5cmd==0.2.0
shellingham==1.5.4
six==1.17.0
sniffio==1.3.1
starlette==0.37.2
stripe==14.4.1
tenacity==9.1.4
tiktoken==0.14.0
tokenizers==0.23.1
tqdm==4.70.0
typer==0.27.1
typing-inspection==0.4.4
typing_extensions==4.16.0
tzdata==2026.3
uritemplate==4.2.0
urllib3==2.7.0
uvicorn==0.25.0
watchfiles==1.2.0
websockets==16.1.1
yarl==1.24.5
zipp==4.1.0

```


### `frontend/package.json`
```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@hookform/resolvers": "5.0.1",
    "@radix-ui/react-accordion": "1.2.8",
    "@radix-ui/react-alert-dialog": "1.1.11",
    "@radix-ui/react-aspect-ratio": "1.1.4",
    "@radix-ui/react-avatar": "1.1.7",
    "@radix-ui/react-checkbox": "1.2.3",
    "@radix-ui/react-collapsible": "1.1.8",
    "@radix-ui/react-context-menu": "2.2.12",
    "@radix-ui/react-dialog": "1.1.11",
    "@radix-ui/react-dropdown-menu": "2.1.12",
    "@radix-ui/react-hover-card": "1.1.11",
    "@radix-ui/react-label": "2.1.4",
    "@radix-ui/react-menubar": "1.1.12",
    "@radix-ui/react-navigation-menu": "1.2.10",
    "@radix-ui/react-popover": "1.1.11",
    "@radix-ui/react-progress": "1.1.4",
    "@radix-ui/react-radio-group": "1.3.4",
    "@radix-ui/react-scroll-area": "1.2.6",
    "@radix-ui/react-select": "2.2.2",
    "@radix-ui/react-separator": "1.1.4",
    "@radix-ui/react-slider": "1.3.2",
    "@radix-ui/react-slot": "1.2.0",
    "@radix-ui/react-switch": "1.2.2",
    "@radix-ui/react-tabs": "1.1.9",
    "@radix-ui/react-toast": "1.2.11",
    "@radix-ui/react-toggle": "1.1.6",
    "@radix-ui/react-toggle-group": "1.1.7",
    "@radix-ui/react-tooltip": "1.2.4",
    "@tanstack/react-query": "5.56.2",
    "axios": "1.18.0",
    "class-variance-authority": "0.7.1",
    "clsx": "2.1.1",
    "cmdk": "1.1.1",
    "cra-template": "1.2.0",
    "date-fns": "4.1.0",
    "dayjs": "1.11.13",
    "embla-carousel-react": "8.6.0",
    "framer-motion": "11.18.0",
    "input-otp": "1.4.2",
    "lodash": "4.18.1",
    "lucide-react": "0.516.0",
    "next-themes": "0.4.6",
    "react": "19.0.0",
    "react-day-picker": "8.10.1",
    "react-dom": "19.0.0",
    "react-hook-form": "7.56.2",
    "react-resizable-panels": "3.0.1",
    "react-router-dom": "7.15.0",
    "react-scripts": "5.0.1",
    "recharts": "3.6.0",
    "sonner": "2.0.3",
    "swr": "2.3.8",
    "tailwind-merge": "3.2.0",
    "tailwindcss-animate": "1.0.7",
    "vaul": "1.1.2",
    "zod": "3.24.4"
  },
  "scripts": {
    "start": "craco start",
    "build": "craco build",
    "test": "craco test"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "devDependencies": {
    "@babel/plugin-proposal-private-property-in-object": "7.21.11",
    "@craco/craco": "7.1.0",
    "@emergentbase/visual-edits": "https://assets.emergent.sh/npm/emergentbase-visual-edits-1.0.13.tgz",
    "@eslint/js": "9.23.0",
    "@types/lodash": "4.17.24",
    "autoprefixer": "10.4.20",
    "dotenv": "16.4.5",
    "eslint": "9.23.0",
    "eslint-plugin-import": "2.31.0",
    "eslint-plugin-jsx-a11y": "6.10.2",
    "eslint-plugin-react": "7.37.4",
    "eslint-plugin-react-hooks": "5.2.0",
    "globals": "15.15.0",
    "postcss": "8.5.10",
    "tailwindcss": "3.4.17"
  },
  "resolutions": {
    "react-router": "7.15.1",
    "node-forge": "1.4.0",
    "fast-uri": "3.1.2",
    "flatted": "3.4.2",
    "qs": "6.15.2",
    "diff": "4.0.4",
    "follow-redirects": "1.16.0",
    "path-to-regexp": "0.1.13",
    "rollup": "2.80.0",
    "underscore": "1.13.8",
    "@babel/plugin-transform-modules-systemjs": "7.29.4",
    "@eslint/plugin-kit": "0.3.4",
    "shell-quote": "1.9.0",
    "jsonpath": "1.3.0",
    "nth-check": "2.0.1",
    "serialize-javascript": "7.0.5",
    "uuid": "11.1.1",
    "@tootallnate/once": "2.0.1",
    "webpack-dev-server": "5.2.6",
    "resolve-url-loader": "5.0.0",
    "**/resolve-url-loader/postcss": "8.5.10",
    "**/axios/form-data": "4.0.6",
    "**/jsdom/form-data": "3.0.5",
    "**/postcss-svgo/svgo": "2.8.1",
    "**/webpack-dev-server/ws": "8.21.0",
    "**/postcss-load-config/yaml": "2.8.3",
    "**/cosmiconfig/yaml": "1.10.3",
    "**/cssnano/yaml": "1.10.3",
    "**/eslint/js-yaml": "4.3.0",
    "**/@eslint/eslintrc/js-yaml": "4.3.0",
    "**/svgo/js-yaml": "3.15.0",
    "**/@istanbuljs/load-nyc-config/js-yaml": "3.15.0",
    "**/css-loader/postcss": "8.5.10",
    "**/css-minimizer-webpack-plugin/postcss": "8.5.10",
    "**/react-scripts/postcss": "8.5.10",
    "**/filelist/minimatch": "5.1.8",
    "**/anymatch/picomatch": "2.3.2",
    "**/micromatch/picomatch": "2.3.2",
    "**/readdirp/picomatch": "2.3.2",
    "**/jest-util/picomatch": "2.3.2",
    "**/tinyglobby/picomatch": "4.0.4",
    "http-proxy-middleware": "2.0.10"
  },
  "packageManager": "yarn@1.22.22+sha512.a6b2f7906b721bba3d67d4aff083df04dad64c399707841b7acf00f6b133b7ac24255f2652fa22ae3534329dc6180534e98d17432037ff6fd140556e2bb3137e"
}

```


### `frontend/craco.config.js`
```javascript
// craco.config.js
const path = require("path");
require("dotenv").config();

// Check if we're in development/preview mode (not production build)
// Craco sets NODE_ENV=development for start, NODE_ENV=production for build
const isDevServer = process.env.NODE_ENV !== "production";

// Environment variable overrides
const config = {
  enableHealthCheck: process.env.ENABLE_HEALTH_CHECK === "true",
};

function makeDevServerV5Compatible(devServerConfig) {
  const {
    https,
    onAfterSetupMiddleware,
    onBeforeSetupMiddleware,
    onListening,
    setupMiddlewares,
    ...compatibleConfig
  } = devServerConfig;

  compatibleConfig.server =
    typeof https === "object"
      ? { type: "https", options: https }
      : https
        ? "https"
        : "http";
  compatibleConfig.headers = {
    ...compatibleConfig.headers,
    "Cross-Origin-Resource-Policy": "same-origin",
  };

  if (onBeforeSetupMiddleware || setupMiddlewares) {
    compatibleConfig.setupMiddlewares = (middlewares, devServer) => {
      if (onBeforeSetupMiddleware) {
        onBeforeSetupMiddleware(devServer);
      }

      return setupMiddlewares
        ? setupMiddlewares(middlewares, devServer)
        : middlewares;
    };
  }

  compatibleConfig.onListening = (devServer) => {
    devServer.close ??= (callback) => devServer.stopCallback(callback);

    if (onListening) {
      onListening(devServer);
    }
    if (onAfterSetupMiddleware) {
      onAfterSetupMiddleware(devServer);
    }
  };

  return compatibleConfig;
}

// Conditionally load health check modules only if enabled
let WebpackHealthPlugin;
let setupHealthEndpoints;
let healthPluginInstance;

if (config.enableHealthCheck) {
  WebpackHealthPlugin = require("./plugins/health-check/webpack-health-plugin");
  setupHealthEndpoints = require("./plugins/health-check/health-endpoints");
  healthPluginInstance = new WebpackHealthPlugin();
}

let webpackConfig = {
  eslint: {
    configure: {
      extends: ["plugin:react-hooks/recommended"],
      rules: {
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn",
      },
    },
  },
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {

      // Add ignored patterns to reduce watched directories
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
        ],
      };

      // Add health check plugin to webpack if enabled
      if (config.enableHealthCheck && healthPluginInstance) {
        webpackConfig.plugins.push(healthPluginInstance);
      }
      return webpackConfig;
    },
  },
};

webpackConfig.devServer = (devServerConfig) => {
  // Add health check endpoints if enabled
  if (config.enableHealthCheck && setupHealthEndpoints && healthPluginInstance) {
    const originalSetupMiddlewares = devServerConfig.setupMiddlewares;

    devServerConfig.setupMiddlewares = (middlewares, devServer) => {
      // Call original setup if exists
      if (originalSetupMiddlewares) {
        middlewares = originalSetupMiddlewares(middlewares, devServer);
      }

      // Setup health endpoints
      setupHealthEndpoints(devServer, healthPluginInstance);

      return middlewares;
    };
  }

  return devServerConfig;
};

// Wrap with visual edits (automatically adds babel plugin, dev server, and overlay in dev mode)
if (isDevServer) {
  try {
    const { withVisualEdits } = require("@emergentbase/visual-edits/craco");
    webpackConfig = withVisualEdits(webpackConfig);
  } catch (err) {
    if (err.code === 'MODULE_NOT_FOUND' && err.message.includes('@emergentbase/visual-edits/craco')) {
      console.warn(
        "[visual-edits] @emergentbase/visual-edits not installed — visual editing disabled."
      );
    } else {
      throw err;
    }
  }
}

const configureDevServer = webpackConfig.devServer;
webpackConfig.devServer = (devServerConfig) =>
  makeDevServerV5Compatible(configureDevServer(devServerConfig));

module.exports = webpackConfig;

```


### `frontend/tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))'
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))'
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))'
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))'
        }
      },
      keyframes: {
        'accordion-down': {
          from: {
            height: '0'
          },
          to: {
            height: 'var(--radix-accordion-content-height)'
          }
        },
        'accordion-up': {
          from: {
            height: 'var(--radix-accordion-content-height)'
          },
          to: {
            height: '0'
          }
        }
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out'
      }
    }
  },
  plugins: [require("tailwindcss-animate")],
};
```


### `frontend/postcss.config.js`
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

```


### `frontend/jsconfig.json`
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"]
}
```


### `frontend/src/index.js`
```javascript
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "@/index.css";
import App from "@/App";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      refetchOnWindowFocus: false,
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);

```


### `frontend/src/index.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
    margin: 0;
    font-family:
        -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen",
        "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue",
        sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

code {
    font-family:
        source-code-pro, Menlo, Monaco, Consolas, "Courier New", monospace;
}

@layer base {
    :root {
        --background: 0 0% 100%;
        --foreground: 0 0% 3.9%;
        --card: 0 0% 100%;
        --card-foreground: 0 0% 3.9%;
        --popover: 0 0% 100%;
        --popover-foreground: 0 0% 3.9%;
        --primary: 0 0% 9%;
        --primary-foreground: 0 0% 98%;
        --secondary: 0 0% 96.1%;
        --secondary-foreground: 0 0% 9%;
        --muted: 0 0% 96.1%;
        --muted-foreground: 0 0% 45.1%;
        --accent: 0 0% 96.1%;
        --accent-foreground: 0 0% 9%;
        --destructive: 0 84.2% 60.2%;
        --destructive-foreground: 0 0% 98%;
        --border: 0 0% 89.8%;
        --input: 0 0% 89.8%;
        --ring: 0 0% 3.9%;
        --chart-1: 12 76% 61%;
        --chart-2: 173 58% 39%;
        --chart-3: 197 37% 24%;
        --chart-4: 43 74% 66%;
        --chart-5: 27 87% 67%;
        --radius: 0.5rem;
    }
    .dark {
        --background: 0 0% 3.9%;
        --foreground: 0 0% 98%;
        --card: 0 0% 3.9%;
        --card-foreground: 0 0% 98%;
        --popover: 0 0% 3.9%;
        --popover-foreground: 0 0% 98%;
        --primary: 0 0% 98%;
        --primary-foreground: 0 0% 9%;
        --secondary: 0 0% 14.9%;
        --secondary-foreground: 0 0% 98%;
        --muted: 0 0% 14.9%;
        --muted-foreground: 0 0% 63.9%;
        --accent: 0 0% 14.9%;
        --accent-foreground: 0 0% 98%;
        --destructive: 0 62.8% 30.6%;
        --destructive-foreground: 0 0% 98%;
        --border: 0 0% 14.9%;
        --input: 0 0% 14.9%;
        --ring: 0 0% 83.1%;
        --chart-1: 220 70% 50%;
        --chart-2: 160 60% 45%;
        --chart-3: 30 80% 55%;
        --chart-4: 280 65% 60%;
        --chart-5: 340 75% 55%;
    }
}

@layer base {
    * {
        @apply border-border;
    }
    body {
        @apply bg-background text-foreground;
    }
}

@layer base {
    [data-debug-wrapper="true"] {
        display: contents !important;
    }

    [data-debug-wrapper="true"] > * {
        margin-left: inherit;
        margin-right: inherit;
        margin-top: inherit;
        margin-bottom: inherit;
        padding-left: inherit;
        padding-right: inherit;
        padding-top: inherit;
        padding-bottom: inherit;
        column-gap: inherit;
        row-gap: inherit;
        gap: inherit;
        border-left-width: inherit;
        border-right-width: inherit;
        border-top-width: inherit;
        border-bottom-width: inherit;
        border-left-style: inherit;
        border-right-style: inherit;
        border-top-style: inherit;
        border-bottom-style: inherit;
        border-left-color: inherit;
        border-right-color: inherit;
        border-top-color: inherit;
        border-bottom-color: inherit;
    }
}

```


### `frontend/src/App.js`
```javascript
import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import "./App.css";
import { Toaster } from "sonner";
import SovereignHome from "./components/SovereignHome";
import AskAllAIs from "./components/AskAllAIs";
import Chronicle from "./components/Chronicle";
import BugBounty from "./components/BugBounty";
import AgentBridge from "./components/AgentBridge";
import FileAnalyzer from "./components/FileAnalyzer";
import SelfDirective from "./components/SelfDirective";
import Council from "./components/Council";
import VoiceChat from "./components/VoiceChat";
import Radar from "./components/Radar";
import VoiceCommander from "./components/VoiceCommander";
import LocalNode from "./components/LocalNode";
import Companion, { openCompanionWindow } from "./components/Companion";
import Apex from "./components/Apex";
import AuthScreen from "./components/AuthScreen";
import AccountMenu from "./components/AccountMenu";
import { Sparkles, LayoutGrid, MessagesSquare, BookOpen, ShieldAlert, Plug, Boxes, Wand2, Crown, Waves, Radar as RadarIcon, MonitorSmartphone, Castle, Store } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;
axios.defaults.withCredentials = true;
// Any 401 from the API means the session is gone -> drop to the sign-in screen.
axios.interceptors.response.use((r) => r, (err) => {
  if (err?.response?.status === 401 && !String(err.config?.url || "").includes("/auth/")) {
    window.dispatchEvent(new CustomEvent("acaso:unauthorized"));
  }
  return Promise.reject(err);
});

const TABS = [
  { key: "home", label: "Sovereign Home", icon: LayoutGrid },
  { key: "bounty", label: "Bug Bounty", icon: ShieldAlert },
  { key: "council", label: "Council", icon: Crown },
  { key: "voice", label: "Voice", icon: Waves },
  { key: "radar", label: "Radar", icon: RadarIcon },
  { key: "apex", label: "Apex Nexus", icon: Store },
  { key: "askai", label: "Ask All AIs", icon: MessagesSquare },
  { key: "analyzer", label: "File Analyzer", icon: Boxes },
  { key: "self", label: "Self-Directive", icon: Wand2 },
  { key: "chronicle", label: "Chronicle", icon: BookOpen },
  { key: "node", label: "Local Node", icon: MonitorSmartphone },
  { key: "bridge", label: "Agent Bridge", icon: Plug },
];

function App() {
  const [tab, setTab] = useState(() => {
    try {
      const t = new URLSearchParams(window.location.search).get("tab");
      return TABS.some((x) => x.key === t) ? t : "home";
    } catch { return "home"; }
  });

  const [user, setUser] = useState(undefined); // undefined = checking, null = signed out
  const checkSession = useCallback(async () => {
    try { setUser((await axios.get(`${API}/auth/me`)).data); } catch { setUser(null); }
  }, []);
  useEffect(() => { checkSession(); }, [checkSession]);
  useEffect(() => {
    const onUnauth = () => setUser((u) => (u ? null : u));
    window.addEventListener("acaso:unauthorized", onUnauth);
    return () => window.removeEventListener("acaso:unauthorized", onUnauth);
  }, []);
  const logout = async () => { try { await axios.post(`${API}/auth/logout`); } catch { /* ignore */ } setUser(null); };

  const companionMode = typeof window !== "undefined" && new URLSearchParams(window.location.search).get("mode") === "companion";

  if (user === undefined) {
    return <div className="acaso-root auth-checking" data-testid="auth-checking"><Toaster position="top-center" theme="dark" richColors /><div className="auth-spinner"><Sparkles size={18} /> ACASO</div></div>;
  }
  if (user === null) {
    return <div className="acaso-root"><Toaster position="top-center" theme="dark" richColors /><div className="aurora" aria-hidden /><AuthScreen onAuthed={setUser} /></div>;
  }

  if (companionMode) {
    return (
      <div className="acaso-root companion-root">
        <Toaster position="top-center" theme="dark" richColors />
        <Companion standalone />
      </div>
    );
  }

  return (
    <div className="acaso-root">
      <Toaster position="top-center" theme="dark" richColors />
      <div className="aurora" aria-hidden />
      <div className="grid-overlay" aria-hidden />

      <header className="topbar">
        <div className="brand">
          <div className="sigil"><Sparkles size={18} /></div>
          <div className="brand-text">
            <h1>ACASO</h1>
            <span>Synarchy Aetheris · Directive-to-Payment OS</span>
          </div>
        </div>
        <nav className="tabs">
          {TABS.map((t) => {
            const Icon = t.icon;
            return (
              <button
                key={t.key}
                data-testid={`tab-${t.key}`}
                className={tab === t.key ? "tab active" : "tab"}
                onClick={() => setTab(t.key)}
              >
                <Icon size={16} /> {t.label}
              </button>
            );
          })}
        </nav>
        <button className="companion-launch" onClick={openCompanionWindow} title="Open ACASO Companion in its own small window" data-testid="companion-launch"><Castle size={14} /> Companion</button>
        <AccountMenu user={user} onLogout={logout} onUserChange={setUser} />
      </header>

      <main className="stage">
        {tab === "home" && <SovereignHome />}
        {tab === "bounty" && <BugBounty />}
        {tab === "council" && <Council />}
        {tab === "voice" && <VoiceChat />}
        {tab === "radar" && <Radar />}
        {tab === "apex" && <Apex />}
        {tab === "askai" && <AskAllAIs />}
        {tab === "analyzer" && <FileAnalyzer />}
        {tab === "self" && <SelfDirective />}
        {tab === "chronicle" && <Chronicle />}
        {tab === "node" && <LocalNode />}
        {tab === "bridge" && <AgentBridge />}
      </main>

      <VoiceCommander setTab={setTab} />

      <footer className="footof">
        <span>Closed Action Loop — Directive › Discovery › Deliverable › Outreach › Payment › Receipt › Learning</span>
      </footer>
    </div>
  );
}

export default App;

```


### `frontend/src/App.css`
```css
:root {
  --bg: #060814;
  --bg2: #0a0e22;
  --panel: rgba(18, 22, 46, 0.72);
  --panel-solid: #10142e;
  --border: rgba(130, 140, 220, 0.16);
  --border-lit: rgba(150, 130, 255, 0.4);
  --violet: #8b7cff;
  --violet2: #a78bfa;
  --cyan: #4fd1ff;
  --gold: #f5c451;
  --green: #48d597;
  --text: #eef0ff;
  --muted: #9aa0c8;
  --dim: #6b708f;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
}

.acaso-root {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  background:
    radial-gradient(1100px 600px at 78% -10%, rgba(139,124,255,0.18), transparent 60%),
    radial-gradient(900px 500px at 12% 108%, rgba(79,209,255,0.12), transparent 55%),
    linear-gradient(180deg, #060814, #05060f 60%, #04050c);
}

.aurora {
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background:
    radial-gradient(600px 300px at 60% 20%, rgba(167,139,250,0.10), transparent 70%),
    radial-gradient(500px 260px at 20% 60%, rgba(79,209,255,0.08), transparent 70%);
  animation: drift 18s ease-in-out infinite alternate;
}
@keyframes drift { from { transform: translateY(-10px); } to { transform: translateY(20px); } }

.grid-overlay {
  position: fixed; inset: 0; z-index: 0; pointer-events: none; opacity: 0.35;
  background-image:
    linear-gradient(rgba(130,140,220,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(130,140,220,0.05) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(circle at 50% 30%, black, transparent 85%);
}

/* Topbar */
.topbar {
  position: sticky; top: 0; z-index: 20;
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 26px;
  background: rgba(6,8,20,0.7);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--border);
}
.brand { display: flex; align-items: center; gap: 12px; }
.sigil {
  width: 38px; height: 38px; border-radius: 11px;
  display: grid; place-items: center; color: #0a0a1a;
  background: linear-gradient(135deg, var(--violet2), var(--cyan));
  box-shadow: 0 0 22px rgba(139,124,255,0.5);
}
.brand-text h1 { margin: 0; font-size: 19px; letter-spacing: 4px; font-weight: 800; }
.brand-text span { font-size: 11px; color: var(--muted); letter-spacing: 1px; }

.tabs { display: flex; gap: 8px; }
.tab {
  display: flex; align-items: center; gap: 7px;
  background: transparent; color: var(--muted);
  border: 1px solid transparent; padding: 9px 16px; border-radius: 10px;
  font-size: 13.5px; font-weight: 600; cursor: pointer; transition: all .2s;
}
.tab:hover { color: var(--text); background: rgba(255,255,255,0.03); }
.tab.active {
  color: var(--text);
  background: linear-gradient(135deg, rgba(139,124,255,0.18), rgba(79,209,255,0.10));
  border-color: var(--border-lit);
  box-shadow: 0 0 18px rgba(139,124,255,0.18);
}
.owner-badge {
  display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--muted);
  padding: 7px 13px; border: 1px solid var(--border); border-radius: 20px;
}
.owner-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); }

.stage { position: relative; z-index: 10; max-width: 1200px; margin: 0 auto; padding: 26px 22px 60px; }
.footof { position: relative; z-index: 10; text-align: center; padding: 18px; font-size: 11px; color: var(--dim); letter-spacing: 0.5px; }

/* Directive console */
.directive-console {
  background: var(--panel); border: 1px solid var(--border-lit);
  border-radius: 18px; padding: 20px; backdrop-filter: blur(12px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
}
.dc-head { display: flex; align-items: center; gap: 9px; color: var(--violet2); font-weight: 700; font-size: 14px; margin-bottom: 14px; }
.dc-head em { color: var(--muted); font-style: normal; font-weight: 400; font-size: 12.5px; margin-left: auto; }
.dc-input { display: flex; gap: 12px; align-items: stretch; }
.dc-input textarea {
  flex: 1; resize: none; background: rgba(4,6,16,0.6); color: var(--text);
  border: 1px solid var(--border); border-radius: 13px; padding: 14px 16px;
  font-size: 15px; font-family: inherit; outline: none; transition: border .2s;
}
.dc-input textarea:focus { border-color: var(--violet); box-shadow: 0 0 0 3px rgba(139,124,255,0.15); }
.dc-input textarea::placeholder { color: var(--dim); }
.compile {
  display: flex; align-items: center; gap: 9px; white-space: nowrap;
  background: linear-gradient(135deg, var(--violet), var(--cyan)); color: #06060f;
  border: none; border-radius: 13px; padding: 0 22px; font-size: 14.5px; font-weight: 700;
  cursor: pointer; transition: transform .15s, box-shadow .2s;
  box-shadow: 0 8px 26px rgba(139,124,255,0.35);
}
.compile:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 12px 34px rgba(139,124,255,0.5); }
.compile:disabled { opacity: 0.7; cursor: wait; }

.mode-row { display: flex; gap: 9px; margin-top: 14px; flex-wrap: wrap; }
.mode {
  display: flex; align-items: center; gap: 7px; background: rgba(255,255,255,0.03);
  color: var(--muted); border: 1px solid var(--border); padding: 8px 14px;
  border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all .18s;
}
.mode:hover { color: var(--text); }
.mode.active { color: #06060f; background: linear-gradient(135deg, var(--violet2), var(--cyan)); border-color: transparent; }

.samples { display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; }
.sample {
  background: rgba(139,124,255,0.06); border: 1px dashed var(--border-lit); color: var(--muted);
  padding: 6px 12px; border-radius: 18px; font-size: 12px; cursor: pointer; transition: all .18s;
}
.sample:hover { color: var(--text); background: rgba(139,124,255,0.14); }

/* Row 2 */
.row-2 { display: grid; grid-template-columns: 1.1fr 1fr; gap: 16px; margin-top: 18px; }
.metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.metric {
  display: flex; align-items: center; gap: 13px; padding: 16px 18px;
  background: var(--panel); border: 1px solid var(--border); border-radius: 15px; color: var(--muted);
}
.metric svg { color: var(--violet2); }
.metric.accent svg { color: var(--cyan); }
.metric.gold svg { color: var(--gold); }
.metric > div { display: flex; flex-direction: column; }
.m-val { font-size: 24px; font-weight: 800; color: var(--text); line-height: 1.1; }
.metric.gold .m-val { color: var(--gold); }
.metric.accent .m-val { color: var(--cyan); }
.m-lab { font-size: 11.5px; color: var(--muted); margin-top: 2px; }

.perfect-next {
  background: linear-gradient(160deg, rgba(139,124,255,0.14), rgba(79,209,255,0.05));
  border: 1px solid var(--border-lit); border-radius: 15px; padding: 18px;
}
.pn-head { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 14px; color: var(--violet2); }
.pn-head .gov { margin-left: auto; font-size: 10.5px; letter-spacing: 1px; color: var(--dim); text-transform: uppercase; }
.pn-body { font-size: 14px; line-height: 1.6; color: var(--text); margin: 12px 0 0; }
.pn-loading { display: flex; align-items: center; gap: 9px; color: var(--muted); margin-top: 14px; font-size: 13px; }
.pn-target { margin-top: 12px; font-size: 12.5px; color: var(--cyan); font-weight: 600; }

/* Pipeline */
.pipeline { margin-top: 18px; background: var(--panel); border: 1px solid var(--border); border-radius: 15px; padding: 18px 20px; }
.pl-head { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 13.5px; color: var(--muted); margin-bottom: 20px; }
.pl-track { display: flex; align-items: flex-start; justify-content: space-between; }
.pl-stage { position: relative; display: flex; flex-direction: column; align-items: center; gap: 8px; flex: 1; }
.pl-dot {
  width: 40px; height: 40px; border-radius: 50%; display: grid; place-items: center;
  background: rgba(255,255,255,0.03); border: 1.5px solid var(--border); color: var(--dim);
  font-weight: 700; font-size: 15px; z-index: 2; transition: all .25s;
}
.pl-stage.lit .pl-dot { background: linear-gradient(135deg, var(--violet), var(--cyan)); color: #06060f; border-color: transparent; box-shadow: 0 0 18px rgba(139,124,255,0.45); }
.pl-stage span { font-size: 11px; color: var(--muted); }
.pl-line { position: absolute; top: 20px; left: 50%; width: 100%; height: 2px; background: var(--border); z-index: 1; }

/* Board */
.board { margin-top: 22px; }
.board-head { display: flex; align-items: center; gap: 9px; font-weight: 700; font-size: 15px; margin-bottom: 14px; color: var(--text); }
.empty {
  display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center;
  padding: 46px 20px; color: var(--muted); background: var(--panel); border: 1px dashed var(--border-lit); border-radius: 16px;
}
.empty svg { color: var(--violet2); }
.empty p { max-width: 520px; line-height: 1.6; font-size: 13.5px; }

.mission-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.mission {
  background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 18px;
  backdrop-filter: blur(10px); transition: border .2s, box-shadow .2s;
}
.mission:hover { border-color: var(--border-lit); box-shadow: 0 14px 40px rgba(0,0,0,0.35); }
.mission.paused { opacity: 0.66; }
.mission.complete { border-color: rgba(72,213,151,0.4); }
.m-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.m-mode { font-size: 10.5px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; padding: 4px 10px; border-radius: 7px; }
.mode-Make { background: rgba(245,196,81,0.15); color: var(--gold); }
.mode-Find { background: rgba(79,209,255,0.15); color: var(--cyan); }
.mode-Move { background: rgba(139,124,255,0.15); color: var(--violet2); }
.mode-Collect { background: rgba(72,213,151,0.15); color: var(--green); }
.m-status { font-size: 11px; text-transform: capitalize; color: var(--muted); }
.s-active { color: var(--cyan); }
.s-complete { color: var(--green); }
.s-paused { color: var(--gold); }
.mission h3 { margin: 0 0 6px; font-size: 16.5px; font-weight: 700; }
.m-summary { margin: 0 0 14px; font-size: 13px; line-height: 1.5; color: var(--muted); }

.m-steps { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.step {
  display: flex; align-items: center; gap: 9px; text-align: left; width: 100%;
  background: rgba(4,6,16,0.4); border: 1px solid var(--border); color: var(--text);
  padding: 9px 12px; border-radius: 9px; font-size: 12.8px; cursor: pointer; transition: all .16s;
}
.step:hover { border-color: var(--border-lit); }
.step svg { color: var(--dim); flex-shrink: 0; }
.step.done svg { color: var(--green); }
.step.done span { text-decoration: line-through; color: var(--dim); }

.m-meta { display: flex; flex-direction: column; gap: 6px; font-size: 11.8px; color: var(--muted); margin-bottom: 12px; }
.m-meta > div { display: flex; align-items: center; gap: 7px; }
.m-meta svg { color: var(--violet2); flex-shrink: 0; }
.m-auth { color: var(--dim) !important; font-size: 11px; }
.m-evidence { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.m-evidence span { font-size: 10.5px; background: rgba(139,124,255,0.08); border: 1px solid var(--border); color: var(--muted); padding: 4px 9px; border-radius: 12px; }

.m-foot { display: flex; align-items: center; gap: 10px; padding-top: 12px; border-top: 1px solid var(--border); }
.m-amount { font-size: 18px; font-weight: 800; color: var(--gold); }
.m-stage { font-size: 11px; color: var(--muted); background: rgba(255,255,255,0.04); padding: 4px 10px; border-radius: 12px; }
.m-actions { margin-left: auto; display: flex; gap: 6px; }
.m-actions button { background: transparent; border: none; color: var(--muted); cursor: pointer; padding: 4px; border-radius: 7px; transition: all .16s; }
.m-actions button:hover { color: var(--text); background: rgba(255,255,255,0.06); }

/* Ask All AIs */
.askai-wrap { display: flex; flex-direction: column; height: calc(100vh - 190px); min-height: 520px; background: var(--panel); border: 1px solid var(--border); border-radius: 18px; overflow: hidden; }
.askai-head { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--border); flex-wrap: wrap; gap: 10px; }
.ah-title { display: flex; align-items: center; gap: 9px; font-weight: 700; font-size: 15px; color: var(--violet2); }
.ah-title em { font-style: normal; font-weight: 400; color: var(--muted); font-size: 12px; }
.prov-picker { display: flex; gap: 8px; }
.prov { display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.03); border: 1px solid var(--border); color: var(--muted); padding: 7px 13px; border-radius: 9px; font-size: 12.5px; font-weight: 600; cursor: pointer; transition: all .16s; }
.prov.on { background: rgba(255,255,255,0.05); }

.thread { flex: 1; overflow-y: auto; padding: 22px; display: flex; flex-direction: column; gap: 16px; }
.askai-empty { margin: auto; text-align: center; color: var(--muted); max-width: 460px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.askai-empty svg { color: var(--violet2); }
.askai-empty p { line-height: 1.6; font-size: 13.5px; }

.bubble { max-width: 75%; padding: 12px 16px; border-radius: 14px; font-size: 14px; line-height: 1.5; }
.bubble.user { align-self: flex-end; background: linear-gradient(135deg, var(--violet), var(--cyan)); color: #06060f; font-weight: 600; border-bottom-right-radius: 4px; }
.bubble.thinking { align-self: flex-start; display: flex; align-items: center; gap: 9px; background: rgba(255,255,255,0.04); color: var(--muted); }

.answer-block { display: flex; flex-direction: column; gap: 14px; }
.synthesis { background: linear-gradient(160deg, rgba(139,124,255,0.16), rgba(79,209,255,0.06)); border: 1px solid var(--border-lit); border-radius: 14px; padding: 16px 18px; }
.syn-head { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 13px; color: var(--violet2); margin-bottom: 9px; }
.synthesis p { margin: 0; font-size: 14px; line-height: 1.65; white-space: pre-wrap; }

.models-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.model-card { background: rgba(4,6,16,0.5); border: 1px solid var(--border); border-radius: 12px; padding: 14px; }
.model-card.failed { opacity: 0.6; }
.mc-head { font-size: 12px; font-weight: 700; color: var(--cyan); margin-bottom: 8px; }
.model-card p { margin: 0; font-size: 13px; line-height: 1.55; color: var(--text); white-space: pre-wrap; }

.askai-input { display: flex; gap: 12px; padding: 16px 20px; border-top: 1px solid var(--border); }
.askai-input input { flex: 1; background: rgba(4,6,16,0.6); border: 1px solid var(--border); border-radius: 12px; padding: 13px 16px; color: var(--text); font-size: 14.5px; outline: none; font-family: inherit; }
.askai-input input:focus { border-color: var(--violet); box-shadow: 0 0 0 3px rgba(139,124,255,0.15); }
.askai-input input::placeholder { color: var(--dim); }
.askai-input button { background: linear-gradient(135deg, var(--violet), var(--cyan)); border: none; color: #06060f; width: 50px; border-radius: 12px; display: grid; place-items: center; cursor: pointer; transition: transform .15s; }
.askai-input button:hover:not(:disabled) { transform: translateY(-2px); }
.askai-input button:disabled { opacity: 0.7; }

.spin { animation: spin 0.9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* NEXUS Action Bus */
.nexus { margin-top: 18px; background: var(--panel); border: 1px solid var(--border); border-radius: 15px; padding: 16px 18px; }
.nx-head { display: flex; align-items: center; gap: 9px; font-weight: 700; font-size: 13.5px; color: var(--cyan); }
.nx-head .nx-sub { font-weight: 400; font-size: 11.5px; color: var(--dim); }
.nx-live { margin-left: auto; display: flex; align-items: center; gap: 7px; font-size: 11px; color: var(--dim); text-transform: uppercase; letter-spacing: 1px; }
.nx-live .pulse { width: 8px; height: 8px; border-radius: 50%; background: var(--dim); }
.nx-live.on { color: var(--green); }
.nx-live.on .pulse { background: var(--green); box-shadow: 0 0 10px var(--green); animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0.3; } }
.nx-empty { margin-top: 14px; font-size: 12.5px; color: var(--dim); }
.nx-log { margin-top: 14px; display: flex; flex-direction: column; gap: 6px; max-height: 240px; overflow-y: auto; font-family: "SFMono-Regular", ui-monospace, Menlo, monospace; }
.nx-row { display: flex; align-items: flex-start; gap: 10px; padding: 8px 10px; border-radius: 8px; background: rgba(4,6,16,0.5); border: 1px solid var(--border); font-size: 12px; }
.nx-row.approval_required { border-color: rgba(245,196,81,0.4); background: rgba(245,196,81,0.06); }
.nx-time { color: var(--dim); flex-shrink: 0; font-size: 11px; padding-top: 1px; }
.nx-badge { display: grid; place-items: center; width: 18px; height: 18px; border-radius: 5px; background: rgba(72,213,151,0.16); color: var(--green); flex-shrink: 0; }
.nx-badge.approval_required { background: rgba(245,196,81,0.16); color: var(--gold); }
.nx-body { color: var(--text); line-height: 1.5; }
.nx-body b { color: var(--violet2); font-weight: 700; }
.nx-body em { color: var(--muted); font-style: normal; }

/* Run buttons on mission card */
.m-run { display: flex; gap: 8px; margin-bottom: 14px; }
.run { display: flex; align-items: center; gap: 6px; flex: 1; justify-content: center; background: rgba(255,255,255,0.04); border: 1px solid var(--border); color: var(--text); padding: 9px 12px; border-radius: 9px; font-size: 12.5px; font-weight: 600; cursor: pointer; transition: all .16s; }
.run:hover:not(:disabled) { border-color: var(--border-lit); background: rgba(139,124,255,0.1); }
.run:disabled { opacity: 0.4; cursor: not-allowed; }
.run.auto { background: linear-gradient(135deg, rgba(139,124,255,0.22), rgba(79,209,255,0.12)); border-color: var(--border-lit); color: var(--cyan); }
.step.pending { border-color: rgba(79,209,255,0.35); }
.step.pending svg { color: var(--cyan); }

/* Chronicle */
.chronicle-wrap { max-width: 900px; margin: 0 auto; }
.chr-hero { display: flex; gap: 20px; justify-content: space-between; align-items: center; background: linear-gradient(160deg, rgba(139,124,255,0.14), rgba(79,209,255,0.05)); border: 1px solid var(--border-lit); border-radius: 18px; padding: 24px; flex-wrap: wrap; }
.chr-title { display: flex; align-items: center; gap: 10px; font-size: 20px; font-weight: 800; color: var(--violet2); }
.chr-hero-left p { margin: 12px 0 0; font-size: 13.5px; line-height: 1.6; color: var(--muted); max-width: 540px; }
.chr-hero-stats { display: flex; gap: 14px; }
.chr-stat { display: flex; flex-direction: column; align-items: center; padding: 14px 20px; background: rgba(4,6,16,0.4); border: 1px solid var(--border); border-radius: 13px; }
.chr-stat .v { font-size: 24px; font-weight: 800; color: var(--text); }
.chr-stat.gold .v { color: var(--gold); }
.chr-stat .l { font-size: 11px; color: var(--muted); margin-top: 3px; }
.chr-loading, .chr-empty { display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; color: var(--muted); padding: 46px 20px; margin-top: 20px; background: var(--panel); border: 1px dashed var(--border-lit); border-radius: 16px; }
.chr-empty svg { color: var(--violet2); }
.chr-empty p { max-width: 480px; line-height: 1.6; font-size: 13.5px; }

.chr-timeline { margin-top: 22px; position: relative; padding-left: 30px; }
.chr-timeline::before { content: ""; position: absolute; left: 11px; top: 6px; bottom: 6px; width: 2px; background: linear-gradient(var(--violet), var(--cyan)); opacity: 0.4; }
.chr-entry { position: relative; margin-bottom: 16px; }
.chr-node { position: absolute; left: -30px; top: 4px; width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; background: linear-gradient(135deg, var(--violet), var(--cyan)); color: #06060f; box-shadow: 0 0 14px rgba(139,124,255,0.4); }
.chr-card { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; }
.chr-card:hover { border-color: var(--border-lit); }
.chr-card-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.chr-date { font-size: 11.5px; color: var(--dim); }
.chr-card h3 { margin: 0 0 10px; font-size: 16px; font-weight: 700; }
.chr-metrics { display: flex; gap: 16px; margin-bottom: 12px; flex-wrap: wrap; }
.chr-metrics span { display: flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--muted); }
.chr-metrics svg { color: var(--gold); }
.chr-lesson { font-size: 13px; line-height: 1.55; color: var(--text); background: rgba(139,124,255,0.08); border: 1px solid var(--border); border-radius: 10px; padding: 11px 13px; }
.chr-lesson svg { color: var(--violet2); vertical-align: -2px; margin-right: 4px; }
.chr-lesson b { color: var(--violet2); }

/* ===== Bug Bounty ===== */
.compile.red { background: linear-gradient(135deg, #ff5470, #f5843c); box-shadow: 0 8px 26px rgba(255,84,112,0.32); }
.bb-console { background: var(--panel); border: 1px solid rgba(255,84,112,0.28); border-radius: 18px; padding: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.4); }
.bb-head { display: flex; align-items: center; gap: 9px; color: #ff7a90; font-weight: 700; font-size: 14px; margin-bottom: 14px; }
.bb-head em { color: var(--muted); font-style: normal; font-weight: 400; font-size: 12.5px; margin-left: auto; }
.bb-ethic { margin-top: 14px; display: flex; align-items: center; gap: 8px; font-size: 11.5px; color: var(--muted); background: rgba(72,213,151,0.06); border: 1px solid rgba(72,213,151,0.2); border-radius: 10px; padding: 9px 12px; }
.bb-ethic svg { color: var(--green); flex-shrink: 0; }

.bb-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 16px; }
.bb-card { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 18px; }
.bb-card:hover { border-color: rgba(255,84,112,0.35); }
.bb-card.complete { border-color: rgba(72,213,151,0.4); }
.bb-card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.bb-plat { font-size: 10.5px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: var(--cyan); background: rgba(79,209,255,0.12); padding: 4px 10px; border-radius: 7px; }
.bb-sev { font-size: 11px; font-weight: 700; border: 1px solid; padding: 3px 9px; border-radius: 7px; }
.bb-card h3 { margin: 0 0 3px; font-size: 16.5px; font-weight: 700; }
.bb-prog { font-size: 12px; color: var(--muted); margin-bottom: 10px; }
.bb-tags { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.bb-tag { display: flex; align-items: center; gap: 6px; font-size: 11.5px; font-family: ui-monospace, monospace; color: var(--text); background: rgba(4,6,16,0.5); border: 1px solid var(--border); padding: 5px 10px; border-radius: 8px; }
.bb-tag svg { color: #ff7a90; }

.bb-pipe { display: flex; justify-content: space-between; margin: 4px 0 16px; position: relative; }
.bb-pipe::before { content: ""; position: absolute; top: 5px; left: 6px; right: 6px; height: 2px; background: var(--border); }
.bb-pnode { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; position: relative; z-index: 1; }
.bb-pdot { width: 12px; height: 12px; border-radius: 50%; background: var(--panel-solid); border: 2px solid var(--border); transition: all .25s; }
.bb-pnode.lit .bb-pdot { background: linear-gradient(135deg, #ff5470, #f5843c); border-color: transparent; }
.bb-pnode.cur .bb-pdot { box-shadow: 0 0 12px rgba(255,84,112,0.7); transform: scale(1.25); }
.bb-plabel { font-size: 9px; color: var(--dim); text-align: center; }
.bb-pnode.lit .bb-plabel { color: var(--muted); }

.bb-gate { display: flex; align-items: center; gap: 9px; flex-wrap: wrap; background: rgba(245,196,81,0.1); border: 1px solid rgba(245,196,81,0.4); color: var(--gold); font-size: 12.5px; padding: 11px 13px; border-radius: 11px; margin-bottom: 14px; }
.bb-gate button { margin-left: auto; display: flex; align-items: center; gap: 6px; background: var(--green); color: #06120c; border: none; padding: 8px 14px; border-radius: 9px; font-size: 12.5px; font-weight: 700; cursor: pointer; }
.bb-gate button:hover { filter: brightness(1.1); }

.bb-meta { display: flex; flex-direction: column; gap: 6px; font-size: 12px; color: var(--muted); margin: 4px 0 12px; }
.bb-meta span { display: flex; align-items: center; gap: 7px; }
.bb-meta svg { color: #ff7a90; }
.bb-report-toggle { display: flex; align-items: center; gap: 8px; width: 100%; justify-content: flex-start; background: rgba(139,124,255,0.06); border: 1px solid var(--border); color: var(--violet2); padding: 9px 12px; border-radius: 9px; font-size: 12.5px; font-weight: 600; cursor: pointer; }
.bb-report-toggle svg:last-child { margin-left: auto; }
.bb-report { margin-top: 10px; background: rgba(4,6,16,0.6); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; max-height: 300px; overflow-y: auto; }
.bb-report h3 { font-size: 14px; margin: 0 0 8px; color: var(--text); }
.bb-report h4 { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #ff7a90; margin: 12px 0 5px; }
.bb-report p { font-size: 12.5px; line-height: 1.55; color: var(--muted); margin: 0 0 4px; }
.bb-report .bb-gap { height: 4px; }

/* Soul Council */
.bb-soul-bar { display: flex; gap: 8px; margin-top: 10px; }
.deploy-souls { flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; background: linear-gradient(135deg, #7a3cff, #ff5470, #f5c451); background-size: 200% 100%; color: #fff; border: none; padding: 11px; border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer; transition: transform .15s, background-position .5s; box-shadow: 0 8px 24px rgba(122,60,255,0.3); }
.deploy-souls:hover:not(:disabled) { transform: translateY(-2px); background-position: 100% 0; }
.deploy-souls:disabled { opacity: 0.75; cursor: wait; }
.council-toggle { background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: var(--muted); width: 42px; border-radius: 10px; cursor: pointer; display: grid; place-items: center; }
.council-toggle:hover { color: var(--text); border-color: var(--border-lit); }

.council { overflow: hidden; margin-top: 12px; }
.council-head { display: flex; align-items: center; gap: 8px; font-size: 11.5px; font-weight: 700; letter-spacing: 0.4px; color: var(--violet2); text-transform: uppercase; margin-bottom: 10px; }
.souls-grid { display: grid; grid-template-columns: 1fr; gap: 9px; margin-bottom: 12px; }
.soul { background: rgba(4,6,16,0.55); border: 1px solid var(--border); border-left-width: 3px; border-radius: 10px; padding: 12px 13px; }
.soul.down { opacity: 0.55; }
.soul-h { display: flex; align-items: center; gap: 7px; font-weight: 700; font-size: 12.5px; }
.soul-model { margin-left: auto; font-size: 10px; font-weight: 600; color: var(--dim); background: rgba(255,255,255,0.05); padding: 3px 8px; border-radius: 10px; text-transform: none; letter-spacing: 0; }
.soul-role { font-size: 10.5px; color: var(--dim); margin: 2px 0 7px; text-transform: uppercase; letter-spacing: 0.5px; }
.soul p { margin: 0; font-size: 12.3px; line-height: 1.55; color: var(--muted); white-space: pre-wrap; max-height: 140px; overflow-y: auto; }

.throne { background: linear-gradient(160deg, rgba(245,196,81,0.12), rgba(139,124,255,0.06)); border: 1px solid rgba(245,196,81,0.34); border-radius: 12px; padding: 14px; }
.throne-h { display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 13px; color: var(--gold); margin-bottom: 10px; }
.throne-status { margin-left: auto; font-size: 10.5px; font-weight: 800; letter-spacing: 1px; color: #06120c; background: var(--green); padding: 3px 10px; border-radius: 10px; }
.throne-row { display: flex; flex-direction: column; gap: 2px; margin-bottom: 9px; }
.throne-row b { font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.6px; color: var(--gold); }
.throne-row span { font-size: 12.6px; line-height: 1.55; color: var(--text); }
.throne-conf { display: flex; align-items: center; gap: 10px; margin-top: 4px; }
.throne-conf > span:first-child { font-size: 11px; color: var(--muted); }
.conf-bar { flex: 1; height: 7px; background: rgba(255,255,255,0.08); border-radius: 6px; overflow: hidden; }
.conf-bar > div { height: 100%; background: linear-gradient(90deg, var(--green), var(--cyan)); border-radius: 6px; }
.conf-num { font-size: 12px; font-weight: 700; color: var(--green); }

/* ===== Soul Debate (Round 2 rebuttal + transcript) ===== */
.soul-rebut { margin-top: 10px; padding-top: 10px; border-top: 1px dashed rgba(255,255,255,0.08); }
.soul-rebut-tag { display: inline-flex; align-items: center; gap: 5px; font-size: 9.5px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; padding: 3px 8px; border: 1px solid; border-radius: 999px; margin-bottom: 6px; }
.soul-rebut p { margin: 0; font-size: 12px; line-height: 1.55; color: var(--text); font-style: italic; white-space: pre-wrap; }

.debate { margin-top: 12px; }
.debate-toggle { display: flex; align-items: center; gap: 8px; width: 100%; background: rgba(139,124,255,0.08); border: 1px solid rgba(139,124,255,0.3); color: var(--violet2); padding: 9px 14px; border-radius: 10px; font-size: 12px; font-weight: 700; letter-spacing: 0.3px; text-transform: uppercase; cursor: pointer; transition: background 160ms; }
.debate-toggle:hover { background: rgba(139,124,255,0.16); }
.debate-count { margin-left: auto; margin-right: 6px; font-size: 10.5px; font-weight: 700; color: var(--muted); background: rgba(255,255,255,0.05); padding: 2px 8px; border-radius: 999px; letter-spacing: 0.2px; text-transform: none; }
.debate-body { margin-top: 10px; background: rgba(4,6,16,0.55); border: 1px solid var(--border); border-radius: 12px; padding: 13px 14px; }
.debate-round + .debate-round { margin-top: 14px; padding-top: 14px; border-top: 1px dashed var(--border); }
.debate-round-h { font-size: 11px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; color: var(--violet2); margin-bottom: 9px; }
.debate-msg { padding: 8px 12px; margin-bottom: 8px; background: rgba(255,255,255,0.03); border-left: 3px solid var(--border); border-radius: 6px; }
.debate-msg:last-child { margin-bottom: 0; }
.debate-who { font-size: 11px; font-weight: 700; letter-spacing: 0.3px; text-transform: uppercase; margin-right: 8px; }
.debate-model { font-size: 10px; color: var(--dim); }
.debate-msg p { margin: 6px 0 0; font-size: 12.2px; line-height: 1.55; color: var(--text); white-space: pre-wrap; }

/* ===== Soul Dissent & Fix Export ===== */
.dissent { margin-top: 14px; background: rgba(4,6,16,0.55); border: 1px solid var(--border); border-radius: 12px; padding: 13px 14px; }
.dissent-h { display: flex; align-items: center; gap: 8px; font-size: 11.5px; font-weight: 700; letter-spacing: 0.4px; color: var(--cyan); text-transform: uppercase; margin-bottom: 10px; }
.dissent-item { padding: 10px 0; border-top: 1px dashed var(--border); }
.dissent-item:first-of-type { border-top: none; padding-top: 2px; }
.dissent-topic { font-size: 12.5px; font-weight: 700; color: var(--text); margin-bottom: 8px; }
.dissent-positions { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }
.dissent-pos { display: flex; gap: 10px; align-items: baseline; padding: 6px 10px; background: rgba(255,255,255,0.03); border-left: 3px solid var(--border); border-radius: 6px; font-size: 12.2px; line-height: 1.5; color: var(--muted); }
.dissent-soul { flex: 0 0 130px; font-size: 11px; font-weight: 700; letter-spacing: 0.3px; text-transform: uppercase; }
.dissent-reco { display: flex; gap: 8px; align-items: flex-start; padding: 8px 10px; background: rgba(245,196,81,0.08); border: 1px solid rgba(245,196,81,0.28); border-radius: 8px; font-size: 12.2px; line-height: 1.5; color: var(--text); }
.dissent-reco svg { color: var(--gold); flex-shrink: 0; margin-top: 2px; }
.dissent-reco b { color: var(--gold); font-weight: 700; }

.fix-export { margin-top: 12px; background: rgba(4,6,16,0.55); border: 1px solid rgba(72,213,151,0.32); border-radius: 12px; padding: 13px 14px; }
.fx-h { display: flex; align-items: center; gap: 8px; font-size: 11.5px; font-weight: 700; letter-spacing: 0.4px; color: var(--green); text-transform: uppercase; margin-bottom: 10px; }
.fx-copy { margin-left: auto; display: flex; align-items: center; gap: 6px; background: rgba(72,213,151,0.12); border: 1px solid rgba(72,213,151,0.4); color: var(--green); padding: 5px 10px; border-radius: 8px; font-size: 11px; font-weight: 700; letter-spacing: 0.3px; text-transform: uppercase; cursor: pointer; transition: background 160ms, transform 160ms; }
.fx-copy:hover { background: rgba(72,213,151,0.22); transform: translateY(-1px); }
.fx-copy:active { transform: translateY(0); }
.fx-body { margin: 0; max-height: 320px; overflow-y: auto; padding: 12px; background: rgba(0,0,0,0.35); border: 1px solid var(--border); border-radius: 8px; font-family: 'Source Code Pro', ui-monospace, monospace; font-size: 12px; line-height: 1.55; color: var(--text); white-space: pre-wrap; word-break: break-word; }

/* ===== Agent Bridge ===== */
.bridge-wrap { max-width: 1120px; margin: 0 auto; }
.br-hero { display: flex; justify-content: space-between; align-items: center; gap: 20px; background: linear-gradient(160deg, rgba(79,209,255,0.12), rgba(139,124,255,0.06)); border: 1px solid var(--border-lit); border-radius: 18px; padding: 22px 24px; flex-wrap: wrap; }
.br-title { display: flex; align-items: center; gap: 10px; font-size: 20px; font-weight: 800; color: var(--cyan); }
.br-hero p { margin: 10px 0 0; font-size: 13.5px; line-height: 1.6; color: var(--muted); max-width: 640px; }
.br-hero b { color: var(--text); }
.br-live { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--green); border: 1px solid rgba(72,213,151,0.3); border-radius: 20px; padding: 7px 13px; white-space: nowrap; }

.br-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }
.br-col { display: flex; flex-direction: column; gap: 16px; }
.br-card { background: var(--panel); border: 1px solid var(--border); border-radius: 15px; padding: 18px; }
.br-card-h { display: flex; align-items: center; gap: 9px; font-weight: 700; font-size: 13.5px; color: var(--text); margin-bottom: 14px; }
.br-card-h .br-hint, .br-hint { font-weight: 400; font-size: 11px; color: var(--dim); }
.br-regen { margin-left: auto; display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); color: var(--muted); padding: 6px 11px; border-radius: 8px; font-size: 11.5px; cursor: pointer; }
.br-regen:hover { color: var(--text); border-color: var(--border-lit); }

.copy-block { display: flex; align-items: center; gap: 10px; width: 100%; text-align: left; background: rgba(4,6,16,0.55); border: 1px solid var(--border); border-radius: 10px; padding: 11px 13px; margin-bottom: 9px; cursor: pointer; transition: border .16s; }
.copy-block:hover { border-color: var(--border-lit); }
.cb-label { font-size: 11px; color: var(--dim); flex-shrink: 0; width: 84px; }
.cb-val { font-family: ui-monospace, monospace; font-size: 12px; color: var(--cyan); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.cb-icon { color: var(--muted); flex-shrink: 0; }

.br-conn-tabs { display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap; }
.ct { background: rgba(255,255,255,0.03); border: 1px solid var(--border); color: var(--muted); padding: 6px 11px; border-radius: 8px; font-size: 11.5px; font-weight: 600; cursor: pointer; }
.ct.on { color: var(--cyan); border-color: var(--border-lit); background: rgba(79,209,255,0.08); }
.br-code { background: #04060f; border: 1px solid var(--border); border-radius: 10px; padding: 14px; font-family: ui-monospace, monospace; font-size: 11.5px; line-height: 1.5; color: #c6cbf0; overflow-x: auto; max-height: 320px; margin: 0 0 12px; white-space: pre; }
.br-copy, .br-run { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; background: linear-gradient(135deg, var(--violet), var(--cyan)); color: #06060f; border: none; padding: 11px; border-radius: 10px; font-size: 13px; font-weight: 700; cursor: pointer; transition: transform .15s; }
.br-copy:hover, .br-run:hover:not(:disabled) { transform: translateY(-2px); }
.br-run:disabled { opacity: 0.6; }

.br-pg-input { width: 100%; box-sizing: border-box; background: rgba(4,6,16,0.6); border: 1px solid var(--border); border-radius: 10px; padding: 12px; color: var(--text); font-size: 13.5px; font-family: inherit; resize: none; outline: none; margin-bottom: 10px; }
.br-pg-input:focus { border-color: var(--violet); }
.br-pg-row { display: flex; gap: 10px; align-items: center; }
.br-kind { display: flex; gap: 6px; flex: 1; }
.br-kind button { flex: 1; background: rgba(255,255,255,0.03); border: 1px solid var(--border); color: var(--muted); padding: 9px; border-radius: 9px; font-size: 12px; font-weight: 600; cursor: pointer; }
.br-kind button.on { color: var(--text); border-color: var(--border-lit); background: rgba(139,124,255,0.12); }
.br-run { width: auto; padding: 9px 16px; white-space: nowrap; }
.br-pg-out { margin-top: 14px; background: rgba(72,213,151,0.06); border: 1px solid rgba(72,213,151,0.25); border-radius: 11px; padding: 13px; }
.br-ok { display: flex; align-items: center; gap: 6px; font-size: 11.5px; color: var(--green); margin-bottom: 6px; }
.br-pg-title { font-size: 14.5px; font-weight: 700; color: var(--text); }
.br-pg-sub { font-size: 12px; color: var(--muted); margin-top: 3px; text-transform: capitalize; }

.br-activity { display: flex; flex-direction: column; gap: 7px; max-height: 260px; overflow-y: auto; }
.br-act-row { display: grid; grid-template-columns: auto auto 1fr auto; gap: 9px; align-items: center; background: rgba(4,6,16,0.5); border: 1px solid var(--border); border-radius: 9px; padding: 9px 11px; font-size: 11.5px; }
.br-agent { font-weight: 700; color: var(--violet2); }
.br-act { color: var(--cyan); font-family: ui-monospace, monospace; }
.br-detail { color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.br-time { color: var(--dim); }
.br-foot-note { display: flex; align-items: center; gap: 8px; justify-content: center; margin-top: 18px; font-size: 11.5px; color: var(--dim); }
.br-foot-note svg { color: var(--green); }

/* ---------------- Attachments panel (Bug Bounty) ---------------- */
.attach { margin-top: 12px; background: rgba(4,6,16,0.45); border: 1px solid var(--border); border-radius: 12px; padding: 12px 13px; }
.attach-head { display: flex; align-items: center; gap: 8px; font-size: 12.5px; font-weight: 700; color: var(--cyan); }
.attach-head svg { flex-shrink: 0; }
.attach-sub { font-weight: 400; color: var(--dim); font-size: 10.5px; margin-left: 2px; }
.attach-add { margin-left: auto; display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 600; color: var(--text); background: rgba(79,209,255,0.1); border: 1px solid var(--border-lit); border-radius: 9px; padding: 6px 11px; cursor: pointer; transition: background .18s, border-color .18s; }
.attach-add:hover:not(:disabled) { background: rgba(79,209,255,0.2); border-color: var(--cyan); }
.attach-add:disabled { opacity: 0.6; cursor: default; }
.attach-empty { margin-top: 10px; font-size: 11.5px; color: var(--dim); display: flex; align-items: center; gap: 7px; }
.attach-list { margin-top: 10px; display: flex; flex-direction: column; gap: 7px; }
.attach-row { display: grid; grid-template-columns: auto 1fr auto auto auto; gap: 9px; align-items: center; background: rgba(18,22,46,0.6); border: 1px solid var(--border); border-radius: 9px; padding: 8px 11px; }
.attach-icon { color: var(--violet2); display: flex; }
.attach-name { font-size: 12px; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.attach-size { font-size: 10.5px; color: var(--dim); font-variant-numeric: tabular-nums; }
.attach-btn { background: transparent; border: 1px solid var(--border); color: var(--muted); border-radius: 8px; padding: 5px; cursor: pointer; display: flex; transition: color .16s, border-color .16s, background .16s; }
.attach-btn:hover { color: var(--cyan); border-color: var(--border-lit); background: rgba(79,209,255,0.08); }
.attach-btn.danger:hover { color: #ff7a90; border-color: rgba(255,122,144,0.5); background: rgba(255,122,144,0.08); }


@media (max-width: 900px) {
  .br-grid { grid-template-columns: 1fr; }
  .bb-grid { grid-template-columns: 1fr; }
}

@media (max-width: 860px) {
  .row-2 { grid-template-columns: 1fr; }
  .tabs { order: 3; width: 100%; justify-content: center; }
  .topbar { flex-wrap: wrap; gap: 10px; }
  .pl-stage span { font-size: 9px; }
}

/* ==================== File Analyzer ==================== */
.fa-wrap { display: flex; flex-direction: column; gap: 16px; }
.fa-console { background: var(--panel); border: 1px solid var(--border-lit); border-radius: 16px; padding: 20px; }
.fa-head { display: flex; align-items: center; gap: 9px; color: var(--violet2); font-weight: 700; font-size: 15px; }
.fa-head svg { flex-shrink: 0; }
.fa-head em { color: var(--muted); font-style: normal; font-weight: 400; font-size: 12.5px; margin-left: auto; }
.fa-note { margin-top: 12px; font-size: 12.5px; line-height: 1.55; color: var(--muted); background: rgba(79,209,255,0.05); border: 1px solid var(--border); border-radius: 11px; padding: 11px 13px; }
.fa-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
.fa-btn { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: var(--text); background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 11px; padding: 10px 16px; cursor: pointer; transition: background .18s, border-color .18s, transform .12s; }
.fa-btn:hover:not(:disabled) { border-color: var(--border-lit); transform: translateY(-1px); }
.fa-btn:disabled { opacity: 0.55; cursor: default; }
.fa-btn.primary { color: #06060f; background: linear-gradient(135deg, var(--violet), var(--cyan)); border-color: transparent; }
.fa-btn.ghost { color: var(--muted); }
.fa-prog { display: flex; align-items: center; gap: 9px; margin-top: 14px; font-size: 12.5px; color: var(--cyan); }
.fa-prog-bar { flex: 1; height: 6px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; }
.fa-prog-bar div { height: 100%; background: linear-gradient(90deg, var(--violet), var(--cyan)); transition: width .2s; }
.fa-sets { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.fa-set { display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; color: var(--muted); background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 20px; padding: 6px 12px; cursor: pointer; }
.fa-set span { background: rgba(139,124,255,0.2); color: var(--text); border-radius: 8px; padding: 1px 7px; font-size: 10.5px; }
.fa-set.active { color: var(--text); border-color: var(--violet); background: rgba(139,124,255,0.12); }
.fa-grid { display: grid; grid-template-columns: 0.9fr 1.1fr; gap: 16px; align-items: start; }
.fa-files, .fa-result { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 18px; }
.fa-sub-head { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: var(--muted); margin-bottom: 14px; }
.fa-count, .fa-model { margin-left: auto; font-size: 11px; font-weight: 600; color: var(--cyan); background: rgba(79,209,255,0.1); border: 1px solid var(--border); border-radius: 10px; padding: 2px 9px; }
.fa-model { color: var(--violet2); }
.fa-empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 34px 16px; color: var(--dim); text-align: center; font-size: 12.5px; }
.fa-empty svg { color: var(--border-lit); }
.fa-list { display: flex; flex-direction: column; gap: 7px; max-height: 340px; overflow-y: auto; }
.fa-row { display: grid; grid-template-columns: auto 1fr auto auto auto auto; gap: 9px; align-items: center; background: rgba(4,6,16,0.4); border: 1px solid var(--border); border-radius: 9px; padding: 8px 11px; }
.fa-fic { color: var(--violet2); display: flex; }
.fa-fname { font-size: 12px; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fa-bin { font-size: 9.5px; color: var(--gold); border: 1px solid rgba(245,196,81,0.4); border-radius: 8px; padding: 1px 6px; }
.fa-fsize { font-size: 10.5px; color: var(--dim); font-variant-numeric: tabular-nums; }
.fa-ic { background: transparent; border: 1px solid var(--border); color: var(--muted); border-radius: 8px; padding: 5px; cursor: pointer; display: flex; transition: color .16s, border-color .16s; }
.fa-ic:hover { color: var(--cyan); border-color: var(--border-lit); }
.fa-ic.danger:hover { color: #ff7a90; border-color: rgba(255,122,144,0.5); }
.fa-ask { margin-top: 14px; display: flex; flex-direction: column; gap: 10px; }
.fa-ask textarea { width: 100%; resize: vertical; background: rgba(4,6,16,0.5); color: var(--text); border: 1px solid var(--border); border-radius: 11px; padding: 12px 13px; font-size: 13px; font-family: inherit; outline: none; transition: border-color .2s; }
.fa-ask textarea:focus { border-color: var(--violet); box-shadow: 0 0 0 3px rgba(139,124,255,0.14); }
.fa-analyze { display: inline-flex; align-items: center; justify-content: center; gap: 8px; font-size: 13.5px; font-weight: 700; color: #06060f; background: linear-gradient(135deg, var(--violet2), var(--cyan)); border: none; border-radius: 11px; padding: 12px; cursor: pointer; transition: opacity .18s; }
.fa-analyze:hover:not(:disabled) { opacity: 0.92; }
.fa-analyze:disabled { opacity: 0.5; cursor: default; }
.fa-md { font-size: 13.5px; line-height: 1.62; color: var(--text); }
.fa-md h3 { font-size: 15px; color: var(--violet2); margin: 16px 0 8px; }
.fa-md h4 { font-size: 13.5px; color: var(--cyan); margin: 14px 0 6px; }
.fa-md h5 { font-size: 12.5px; color: var(--violet2); margin: 10px 0 4px; font-weight: 700; }
.fa-md code { font-family: ui-monospace, "Source Code Pro", monospace; font-size: 12px; color: var(--cyan); background: rgba(79,209,255,0.08); border-radius: 5px; padding: 1px 5px; }
.fa-md strong { color: var(--text); font-weight: 700; }
.fa-md p { margin: 6px 0; color: var(--text); }
.fa-md li { margin: 4px 0 4px 18px; color: var(--muted); list-style: disc; }
.fa-gap { height: 6px; }
.fa-code { background: #05060f; border: 1px solid var(--border); border-radius: 9px; padding: 12px; font-family: ui-monospace, "Source Code Pro", monospace; font-size: 12px; color: var(--cyan); overflow-x: auto; white-space: pre-wrap; }
.fa-q { font-size: 12.5px; color: var(--cyan); margin-bottom: 10px; font-weight: 600; }
.fa-trunc { font-size: 11.5px; color: var(--gold); margin-bottom: 10px; }
.fa-skeleton { display: flex; flex-direction: column; gap: 10px; padding: 8px 0; }
.fa-sk-line { height: 12px; border-radius: 6px; background: linear-gradient(90deg, rgba(255,255,255,0.04), rgba(255,255,255,0.1), rgba(255,255,255,0.04)); background-size: 200% 100%; animation: fa-shimmer 1.3s infinite; }
@keyframes fa-shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* ==================== Self-Directive ==================== */
.sd-wrap { display: flex; flex-direction: column; gap: 16px; }
.sd-console { background: var(--panel); border: 1px solid var(--border-lit); border-radius: 16px; padding: 20px; }
.sd-head { display: flex; align-items: center; gap: 9px; color: var(--violet2); font-weight: 700; font-size: 15px; }
.sd-head svg { flex-shrink: 0; }
.sd-head em { color: var(--muted); font-style: normal; font-weight: 400; font-size: 12.5px; margin-left: auto; }
.sd-warn { display: flex; gap: 11px; align-items: flex-start; margin-top: 14px; font-size: 12.5px; line-height: 1.55; color: var(--muted); background: rgba(245,196,81,0.06); border: 1px solid rgba(245,196,81,0.28); border-radius: 11px; padding: 12px 14px; }
.sd-warn svg { color: var(--gold); flex-shrink: 0; margin-top: 2px; }
.sd-warn b { color: var(--text); }
.sd-grid { display: grid; grid-template-columns: 0.8fr 1.2fr; gap: 16px; align-items: start; }
.sd-picker, .sd-main { display: flex; flex-direction: column; gap: 12px; }
.sd-picker { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 18px; }
.sd-sub-head { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: var(--muted); }
.sd-count { margin-left: auto; font-size: 11px; color: var(--violet2); background: rgba(139,124,255,0.12); border-radius: 10px; padding: 2px 9px; }
.sd-search { display: flex; align-items: center; gap: 8px; background: rgba(4,6,16,0.5); border: 1px solid var(--border); border-radius: 10px; padding: 8px 11px; }
.sd-search svg { color: var(--dim); }
.sd-search input { flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-size: 12.5px; }
.sd-files { display: flex; flex-direction: column; gap: 5px; max-height: 360px; overflow-y: auto; }
.sd-file { display: grid; grid-template-columns: auto 1fr auto; gap: 9px; align-items: center; background: rgba(4,6,16,0.4); border: 1px solid var(--border); border-radius: 8px; padding: 7px 10px; cursor: pointer; transition: border-color .15s, background .15s; }
.sd-file:hover { border-color: var(--border-lit); }
.sd-file.sel { border-color: var(--violet); background: rgba(139,124,255,0.1); }
.sd-file input { accent-color: var(--violet); }
.sd-fpath { font-size: 11.5px; color: var(--text); font-family: ui-monospace, monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sd-fsize { font-size: 10px; color: var(--dim); }
.sd-empty-sm { font-size: 12px; color: var(--dim); padding: 12px; text-align: center; }
.sd-deny { display: flex; align-items: center; gap: 7px; font-size: 10.5px; color: var(--dim); }
.sd-deny svg { color: #ff7a90; }
.sd-instruction { width: 100%; resize: vertical; background: rgba(4,6,16,0.5); color: var(--text); border: 1px solid var(--border); border-radius: 12px; padding: 13px 14px; font-size: 13.5px; font-family: inherit; outline: none; transition: border-color .2s; }
.sd-instruction:focus { border-color: var(--violet); box-shadow: 0 0 0 3px rgba(139,124,255,0.14); }
.sd-propose { display: inline-flex; align-items: center; justify-content: center; gap: 8px; font-size: 13.5px; font-weight: 700; color: #06060f; background: linear-gradient(135deg, var(--violet), var(--cyan)); border: none; border-radius: 11px; padding: 12px; cursor: pointer; transition: opacity .18s; }
.sd-propose:hover:not(:disabled) { opacity: 0.92; }
.sd-propose:disabled { opacity: 0.5; cursor: default; }
.sd-skeleton { display: flex; flex-direction: column; gap: 9px; }
.sd-sk { height: 11px; border-radius: 6px; background: linear-gradient(90deg, rgba(255,255,255,0.04), rgba(255,255,255,0.1), rgba(255,255,255,0.04)); background-size: 200% 100%; animation: fa-shimmer 1.3s infinite; }
.sd-proposal { background: var(--panel); border: 1px solid var(--border-lit); border-radius: 14px; padding: 16px; }
.sd-prop-head { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: var(--text); }
.sd-status { font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; border-radius: 8px; padding: 2px 8px; font-weight: 700; }
.sd-status.s-proposed { color: var(--cyan); background: rgba(79,209,255,0.12); }
.sd-status.s-applied { color: var(--green); background: rgba(72,213,151,0.14); }
.sd-status.s-rolled_back { color: var(--muted); background: rgba(255,255,255,0.06); }
.sd-status.s-failed { color: #ff7a90; background: rgba(255,122,144,0.12); }
.sd-model { margin-left: auto; font-size: 10.5px; color: var(--violet2); }
.sd-expl { font-size: 13px; color: var(--text); margin: 10px 0; line-height: 1.55; }
.sd-testplan { display: flex; gap: 7px; align-items: flex-start; font-size: 12px; color: var(--muted); background: rgba(79,209,255,0.05); border: 1px solid var(--border); border-radius: 9px; padding: 9px 11px; margin-bottom: 12px; }
.sd-testplan svg { color: var(--cyan); flex-shrink: 0; margin-top: 2px; }
.sd-diff-block { margin-bottom: 12px; }
.sd-diff-head { display: flex; align-items: center; gap: 8px; font-size: 11.5px; font-family: ui-monospace, monospace; color: var(--muted); margin-bottom: 6px; }
.sd-add { color: var(--green); }
.sd-del { color: #ff7a90; }
.sd-diff { background: #05060f; border: 1px solid var(--border); border-radius: 9px; padding: 10px; overflow-x: auto; font-family: ui-monospace, "Source Code Pro", monospace; font-size: 11.5px; line-height: 1.5; max-height: 360px; overflow-y: auto; }
.sd-dl { white-space: pre; color: var(--muted); }
.sd-dl.meta { color: var(--dim); }
.sd-dl.hunk { color: var(--cyan); }
.sd-dl.add { color: var(--green); background: rgba(72,213,151,0.08); }
.sd-dl.del { color: #ff7a90; background: rgba(255,122,144,0.08); }
.sd-prop-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-top: 14px; }
.sd-apply { display: inline-flex; align-items: center; gap: 7px; font-size: 13px; font-weight: 700; color: #06060f; background: var(--green); border: none; border-radius: 10px; padding: 10px 16px; cursor: pointer; transition: opacity .18s; }
.sd-apply:hover:not(:disabled) { opacity: 0.9; }
.sd-apply:disabled { opacity: 0.5; cursor: default; }
.sd-applied { display: inline-flex; align-items: center; gap: 7px; font-size: 12.5px; font-weight: 600; color: var(--green); }
.sd-rollback, .sd-rolled { display: inline-flex; align-items: center; gap: 7px; font-size: 12.5px; font-weight: 600; color: var(--gold); background: rgba(245,196,81,0.1); border: 1px solid rgba(245,196,81,0.35); border-radius: 10px; padding: 9px 14px; cursor: pointer; }
.sd-rolled { color: var(--muted); background: transparent; border-color: var(--border); cursor: default; }
.sd-discard { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--muted); background: transparent; border: 1px solid var(--border); border-radius: 10px; padding: 9px 13px; cursor: pointer; margin-left: auto; }
.sd-discard:hover { color: var(--text); border-color: var(--border-lit); }
.sd-history { margin-top: 6px; background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 16px; }
.sd-hrow { display: grid; grid-template-columns: auto 1fr auto auto; gap: 10px; align-items: center; padding: 8px 0; border-top: 1px solid var(--border); font-size: 12px; }
.sd-hinstr { color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sd-hpaths { color: var(--dim); font-family: ui-monospace, monospace; font-size: 10.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 180px; }
.sd-hroll { background: transparent; border: 1px solid var(--border); color: var(--gold); border-radius: 8px; padding: 5px; cursor: pointer; display: flex; }
.sd-hroll:hover { border-color: rgba(245,196,81,0.5); }

/* File Analyzer — Google Drive bar + modal */
.fa-drive { display: flex; align-items: center; gap: 10px; margin-top: 12px; padding: 11px 13px; background: rgba(79,209,255,0.05); border: 1px solid var(--border); border-radius: 12px; font-size: 12.5px; }
.fa-drive > svg { color: var(--cyan); flex-shrink: 0; }
.fa-drive-on { color: var(--text); font-weight: 600; }
.fa-drive-off { color: var(--muted); }
.fa-drive-btn { display: inline-flex; align-items: center; gap: 7px; font-size: 12px; font-weight: 600; color: #06060f; background: linear-gradient(135deg, var(--violet2), var(--cyan)); border: none; border-radius: 9px; padding: 8px 13px; cursor: pointer; transition: opacity .18s; }
.fa-drive-btn:hover { opacity: 0.92; }
.fa-drive-btn.ghost { color: var(--muted); background: transparent; border: 1px solid var(--border); }
.fa-drive-btn.ghost:hover { color: var(--text); border-color: var(--border-lit); opacity: 1; }
.fa-drive .fa-drive-btn:first-of-type { margin-left: auto; }
.fa-modal-overlay { position: fixed; inset: 0; z-index: 200; background: rgba(3,4,12,0.72); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.fa-modal { width: min(640px, 96vw); max-height: 82vh; display: flex; flex-direction: column; background: var(--panel-solid); border: 1px solid var(--border-lit); border-radius: 16px; overflow: hidden; box-shadow: 0 30px 80px rgba(0,0,0,0.55); }
.fa-modal-head { display: flex; align-items: center; gap: 9px; padding: 16px 18px; border-bottom: 1px solid var(--border); font-weight: 700; color: var(--cyan); }
.fa-modal-head span { color: var(--text); }
.fa-modal-x { margin-left: auto; background: transparent; border: none; color: var(--muted); cursor: pointer; display: flex; padding: 4px; border-radius: 7px; }
.fa-modal-x:hover { color: var(--text); background: rgba(255,255,255,0.06); }
.fa-crumbs { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; padding: 10px 18px; border-bottom: 1px solid var(--border); }
.fa-drive-search { display: flex; align-items: center; gap: 9px; padding: 10px 18px; border-bottom: 1px solid var(--border); background: rgba(4,6,16,0.35); }
.fa-drive-search-ic { color: var(--cyan); flex-shrink: 0; }
.fa-drive-search input { flex: 1; background: rgba(4,6,16,0.5); border: 1px solid var(--border); border-radius: 9px; padding: 8px 11px; color: var(--text); font-size: 12.5px; outline: none; transition: border-color .2s; }
.fa-drive-search input:focus { border-color: var(--violet); box-shadow: 0 0 0 3px rgba(139,124,255,0.14); }
.fa-drive-search-x { background: transparent; border: none; color: var(--muted); cursor: pointer; display: flex; padding: 4px; border-radius: 6px; }
.fa-drive-search-x:hover { color: var(--text); background: rgba(255,255,255,0.06); }
.fa-drive-search-go { font-size: 12px; font-weight: 600; color: #06060f; background: linear-gradient(135deg, var(--violet2), var(--cyan)); border: none; border-radius: 9px; padding: 8px 14px; cursor: pointer; }
.fa-drive-search-go:hover { opacity: 0.92; }
.fa-crumb { display: inline-flex; align-items: center; gap: 4px; color: var(--dim); }
.fa-crumb button { background: transparent; border: none; color: var(--muted); font-size: 12px; cursor: pointer; padding: 3px 5px; border-radius: 6px; }
.fa-crumb button:hover { color: var(--cyan); }
.fa-drive-list { flex: 1; overflow-y: auto; padding: 10px 14px; display: flex; flex-direction: column; gap: 5px; }
.fa-drive-row { border-radius: 9px; }
.fa-drive-folder { width: 100%; display: flex; align-items: center; gap: 10px; background: rgba(4,6,16,0.4); border: 1px solid var(--border); border-radius: 9px; padding: 9px 12px; cursor: pointer; color: var(--text); font-size: 13px; text-align: left; transition: border-color .15s; }
.fa-drive-folder:hover { border-color: var(--border-lit); }
.fa-drive-folder svg:first-child { color: var(--gold); }
.fa-drive-folder span { flex: 1; }
.fa-drive-folder svg:last-child { color: var(--dim); }
.fa-drive-file { display: flex; align-items: center; gap: 10px; background: rgba(4,6,16,0.4); border: 1px solid var(--border); border-radius: 9px; padding: 9px 12px; cursor: pointer; color: var(--text); font-size: 13px; transition: border-color .15s, background .15s; }
.fa-drive-file:hover { border-color: var(--border-lit); }
.fa-drive-file.sel { border-color: var(--violet); background: rgba(139,124,255,0.1); }
.fa-drive-file input { accent-color: var(--violet); }
.fa-drive-file svg { color: var(--violet2); }
.fa-drive-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fa-drive-row.unsupported .fa-drive-file { opacity: 0.55; }
.fa-modal-foot { display: flex; align-items: center; gap: 12px; padding: 14px 18px; border-top: 1px solid var(--border); }
.fa-drive-count { font-size: 12px; color: var(--muted); }
.fa-modal-foot .fa-analyze { margin-left: auto; padding: 10px 18px; }
.fa-head-right { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.fa-head-right .fa-model { margin-left: 0; }
.fa-export { display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 600; color: var(--text); background: rgba(255,255,255,0.04); border: 1px solid var(--border); border-radius: 9px; padding: 6px 11px; cursor: pointer; transition: border-color .16s, background .16s; }
.fa-export:hover { border-color: var(--border-lit); background: rgba(139,124,255,0.12); }
.fa-cite { display: inline; font-family: ui-monospace, "Source Code Pro", monospace; font-size: 12px; color: var(--gold); background: rgba(245,196,81,0.1); border: 1px solid rgba(245,196,81,0.3); border-radius: 5px; padding: 0 5px; cursor: pointer; transition: background .15s, border-color .15s; }
.fa-cite:hover { background: rgba(245,196,81,0.22); border-color: var(--gold); }
.fa-viewer { width: min(820px, 96vw); }
.fa-viewer-line { margin-left: 8px; font-size: 11px; color: var(--gold); background: rgba(245,196,81,0.1); border-radius: 8px; padding: 2px 9px; }
.fa-viewer .fa-modal-head span:first-of-type { font-family: ui-monospace, monospace; font-size: 13px; }
.fa-viewer-body { flex: 1; overflow: auto; padding: 0; }
.fa-viewer-code { margin: 0; background: #05060f; font-family: ui-monospace, "Source Code Pro", monospace; font-size: 12px; line-height: 1.55; }
.fa-vline { display: flex; gap: 12px; padding: 0 14px; }
.fa-vline.hit { background: rgba(245,196,81,0.14); box-shadow: inset 3px 0 0 var(--gold); }
.fa-vnum { color: var(--dim); text-align: right; min-width: 40px; user-select: none; }
.fa-vtext { color: var(--text); white-space: pre; }
.fa-vline.hit .fa-vtext { color: #fff; }


/* File Analyzer chat */
.fa-chat { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 18px; }
.fa-chat-hint { margin-left: auto; font-size: 11px; font-weight: 400; color: var(--dim); }
.fa-chat-log { display: flex; flex-direction: column; gap: 12px; max-height: 380px; overflow-y: auto; padding: 4px; }
.fa-chat-empty { font-size: 12.5px; color: var(--dim); padding: 18px; text-align: center; }
.fa-msg { display: flex; flex-direction: column; gap: 4px; max-width: 88%; }
.fa-msg.user { align-self: flex-end; align-items: flex-end; }
.fa-msg.assistant { align-self: flex-start; }
.fa-msg-who { font-size: 10.5px; font-weight: 700; letter-spacing: 0.4px; color: var(--dim); text-transform: uppercase; }
.fa-msg-body { font-size: 13px; line-height: 1.55; border-radius: 12px; padding: 10px 13px; }
.fa-msg.user .fa-msg-body { background: linear-gradient(135deg, rgba(139,124,255,0.22), rgba(79,209,255,0.18)); border: 1px solid var(--border-lit); color: var(--text); }
.fa-msg.assistant .fa-msg-body { background: rgba(4,6,16,0.5); border: 1px solid var(--border); color: var(--text); }
.fa-msg-body .fa-md { font-size: 13px; }
.fa-msg-body .fa-md p { margin: 3px 0; }
.fa-chat-input { display: flex; gap: 10px; margin-top: 14px; }
.fa-chat-input input { flex: 1; background: rgba(4,6,16,0.5); color: var(--text); border: 1px solid var(--border); border-radius: 11px; padding: 12px 14px; font-size: 13.5px; font-family: inherit; outline: none; transition: border-color .2s; }
.fa-chat-input input:focus { border-color: var(--violet); box-shadow: 0 0 0 3px rgba(139,124,255,0.14); }
.fa-chat-input input:disabled { opacity: 0.55; }
.fa-chat-input button { display: inline-flex; align-items: center; justify-content: center; width: 46px; color: #06060f; background: linear-gradient(135deg, var(--violet2), var(--cyan)); border: none; border-radius: 11px; cursor: pointer; transition: opacity .18s; }
.fa-chat-input button:hover:not(:disabled) { opacity: 0.92; }
.fa-chat-input button:disabled { opacity: 0.45; cursor: default; }


@media (max-width: 900px) {
  .fa-grid, .sd-grid { grid-template-columns: 1fr; }
}


/* ===== Council of Weavers ===== */
.cw-wrap { display: flex; flex-direction: column; gap: 16px; }
.cw-wrap .chr-hero-left p b { color: var(--text); }
.cw-wrap .chr-hero-left p code { font-family: ui-monospace, monospace; font-size: 12px; color: var(--cyan); background: rgba(4,6,16,0.5); padding: 1px 6px; border-radius: 6px; }
.cw-honesty { display: flex; align-items: flex-start; gap: 8px; font-size: 12px; line-height: 1.5; color: var(--muted); background: rgba(245,196,81,0.06); border: 1px solid rgba(245,196,81,0.25); border-radius: 11px; padding: 10px 13px; }
.cw-honesty svg { color: var(--gold); flex-shrink: 0; margin-top: 2px; }
.cw-presets { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; margin-top: 14px; }
.cw-preset { display: flex; align-items: flex-start; gap: 10px; text-align: left; background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; color: var(--text); cursor: pointer; transition: border-color .18s, background .18s, transform .12s; }
.cw-preset svg { color: var(--violet2); flex-shrink: 0; margin-top: 2px; }
.cw-preset span { display: flex; flex-direction: column; gap: 3px; }
.cw-preset b { font-size: 13.5px; }
.cw-preset small { font-size: 11.5px; line-height: 1.4; color: var(--muted); }
.cw-preset:hover { border-color: var(--border-lit); transform: translateY(-1px); }
.cw-preset.active { border-color: var(--violet); background: rgba(139,124,255,0.12); box-shadow: 0 0 0 1px rgba(139,124,255,0.3) inset; }
.cw-preset:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
.cw-textarea { width: 100%; margin-top: 14px; box-sizing: border-box; resize: vertical; font-family: ui-monospace, monospace; font-size: 12.5px; line-height: 1.55; color: var(--text); background: rgba(4,6,16,0.55); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; }
.cw-textarea:focus { outline: none; border-color: var(--border-lit); }
.cw-row { display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; align-items: center; }
.cw-input { font-size: 12.5px; color: var(--text); background: rgba(4,6,16,0.55); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; min-width: 200px; }
.cw-input.grow { flex: 1; min-width: 240px; }
.cw-input:focus { outline: none; border-color: var(--border-lit); }
.cw-running { display: flex; gap: 14px; align-items: center; margin-top: 14px; font-size: 12.5px; font-weight: 600; color: var(--violet2); }
.cw-arrow { color: var(--muted); font-weight: 500; }
.cw-result { background: var(--panel); border: 1px solid var(--border-lit); border-radius: 16px; padding: 20px; }
.cw-result-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 14px; flex-wrap: wrap; }
.cw-meta { margin-top: 6px; font-size: 11.5px; color: var(--dim); }
.cw-veto { margin-left: 10px; font-size: 10.5px; letter-spacing: .08em; color: #ff7a90; background: rgba(255,84,112,0.12); border: 1px solid rgba(255,84,112,0.4); border-radius: 6px; padding: 3px 8px; }
.cw-grid { display: grid; grid-template-columns: minmax(0, 1.7fr) minmax(280px, 1fr); gap: 18px; margin-top: 16px; }
.cw-directive { min-width: 0; font-size: 13.5px; line-height: 1.65; }
.cw-side { display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.cw-side-title { display: flex; align-items: center; gap: 7px; font-size: 12px; font-weight: 700; color: var(--violet2); text-transform: uppercase; letter-spacing: .06em; margin-top: 4px; }
.cw-side-title small { font-weight: 500; text-transform: none; letter-spacing: 0; color: var(--dim); }
.cw-signals { font-size: 12.5px; line-height: 1.55; background: rgba(79,209,255,0.05); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; }
.cw-weaver { border: 1px solid var(--border); border-radius: 11px; background: rgba(4,6,16,0.4); overflow: hidden; }
.cw-weaver.down { opacity: .55; }
.cw-weaver-h { width: 100%; display: flex; align-items: center; gap: 8px; text-align: left; background: transparent; border: 0; color: var(--text); padding: 10px 12px; cursor: pointer; font-size: 12.5px; }
.cw-weaver-h:hover { background: rgba(139,124,255,0.08); }
.cw-weaver-h svg { color: var(--violet2); flex-shrink: 0; transition: transform .18s; }
.cw-weaver-h svg.rot { transform: rotate(90deg); }
.cw-weaver-h span { color: var(--muted); font-size: 11.5px; }
.cw-weaver-h em { margin-left: auto; font-style: normal; font-size: 10.5px; color: var(--dim); white-space: nowrap; }
.cw-weaver-b { padding: 4px 14px 14px; font-size: 12.5px; line-height: 1.55; border-top: 1px solid var(--border); }
.cw-history { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }
.cw-hrow { display: flex; align-items: center; gap: 8px; }
.cw-hmain { flex: 1; min-width: 0; display: flex; align-items: center; gap: 10px; text-align: left; background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 10px; padding: 9px 12px; color: var(--text); cursor: pointer; transition: border-color .16s, background .16s; }
.cw-hmain:hover { border-color: var(--border-lit); background: rgba(139,124,255,0.06); }
.cw-htitle { flex: 1; min-width: 0; font-size: 12.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cw-hmeta { font-size: 11px; color: var(--dim); white-space: nowrap; }
@media (max-width: 900px) { .cw-grid { grid-template-columns: 1fr; } }

/* ===== Voice Channel ===== */
.vc-wrap { display: flex; flex-direction: column; gap: 16px; }
.vc-wrap .chr-hero-left p b { color: var(--text); }
.vc-controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
.vc-seg { display: inline-flex; background: rgba(4,6,16,0.55); border: 1px solid var(--border); border-radius: 11px; padding: 3px; gap: 3px; }
.vc-seg-btn { display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 600; color: var(--muted); background: transparent; border: 0; border-radius: 8px; padding: 8px 12px; cursor: pointer; transition: color .16s, background .16s; }
.vc-seg-btn:hover { color: var(--text); }
.vc-seg-btn:focus-visible { outline: 2px solid var(--cyan); outline-offset: 1px; }
.vc-seg-btn.active { color: #06060f; background: linear-gradient(135deg, var(--violet), var(--cyan)); }
.vc-seg-btn.active.council { background: linear-gradient(135deg, var(--gold), #f5843c); }
.vc-voice { min-width: 180px; max-width: 260px; }
.vc-hint { margin-top: 10px; font-size: 12px; color: var(--dim); line-height: 1.5; }
.vc-transcript { display: flex; flex-direction: column; gap: 10px; min-height: 220px; max-height: 52vh; overflow-y: auto; background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 16px; }
.vc-msg { max-width: 78%; border-radius: 14px; padding: 10px 14px; font-size: 13.5px; line-height: 1.55; border: 1px solid var(--border); position: relative; }
.vc-msg.user { align-self: flex-end; background: rgba(139,124,255,0.14); border-color: rgba(139,124,255,0.35); }
.vc-msg.user.interim { opacity: .65; border-style: dashed; }
.vc-msg.assistant { align-self: flex-start; background: rgba(4,6,16,0.5); }
.vc-msg-meta { font-size: 10.5px; color: var(--dim); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px; }
.vc-full { margin-top: 8px; font-size: 12.5px; }
.vc-full summary { cursor: pointer; color: var(--gold); font-weight: 600; }
.vc-replay { margin-top: 6px; display: inline-flex; align-items: center; gap: 5px; font-size: 11px; color: var(--muted); background: transparent; border: 1px solid var(--border); border-radius: 7px; padding: 3px 8px; cursor: pointer; transition: color .16s, border-color .16s; }
.vc-replay:hover { color: var(--cyan); border-color: var(--border-lit); }
.vc-thinking { display: flex; align-items: center; gap: 8px; font-size: 12.5px; color: var(--violet2); padding: 6px 4px; }
.vc-dock { display: flex; align-items: center; justify-content: center; gap: 14px; flex-wrap: wrap; padding: 6px 0 12px; }
.vc-big { display: flex; align-items: center; gap: 12px; font-size: 14px; font-weight: 700; color: var(--text); background: rgba(255,255,255,0.03); border: 1px solid var(--border-lit); border-radius: 999px; padding: 14px 26px; cursor: pointer; min-height: 56px; transition: transform .12s, border-color .18s, background .18s, box-shadow .18s; user-select: none; -webkit-user-select: none; touch-action: none; }
.vc-big:hover:not(:disabled) { transform: translateY(-1px); }
.vc-big:disabled { opacity: .5; cursor: default; }
.vc-big:focus-visible { outline: 2px solid var(--cyan); outline-offset: 3px; }
.vc-big.on { color: #06060f; background: linear-gradient(135deg, var(--violet), var(--cyan)); border-color: transparent; box-shadow: 0 0 0 6px rgba(139,124,255,0.18), 0 0 34px rgba(79,209,255,0.35); animation: vcpulse 1.6s ease-in-out infinite; }
@keyframes vcpulse { 0%,100% { box-shadow: 0 0 0 6px rgba(139,124,255,0.18), 0 0 30px rgba(79,209,255,0.3); } 50% { box-shadow: 0 0 0 12px rgba(139,124,255,0.08), 0 0 44px rgba(79,209,255,0.45); } }
.vc-textrow { display: flex; gap: 10px; align-items: center; width: 100%; max-width: 900px; }
.attach-btn.live { color: var(--cyan); border-color: var(--border-lit); animation: vcpulse 1.6s ease-in-out infinite; }
@media (max-width: 900px) { .vc-msg { max-width: 94%; } .vc-voice { max-width: 100%; } }
.cw-actions { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.cw-mission-link { text-decoration: none; color: var(--green); border-color: rgba(72,213,151,0.4); max-width: 320px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ===== Opportunity Radar - mission-control intelligence desk ===== */
:root { --lime: #c8f04a; --amber: #f5b342; --ink: #05070f; --paper: #f4efe6; }
.rd-wrap { display: flex; flex-direction: column; gap: 14px; }
.rd-hero { display: flex; justify-content: space-between; gap: 20px; align-items: center; flex-wrap: wrap; background: linear-gradient(160deg, rgba(245,179,66,0.10), rgba(79,209,255,0.04)); border: 1px solid rgba(245,179,66,0.32); border-radius: 18px; padding: 22px 24px; }
.rd-title { display: flex; align-items: center; gap: 10px; font-size: 20px; font-weight: 800; color: var(--amber); letter-spacing: -0.01em; }
.rd-hero p { margin: 10px 0 0; font-size: 13.5px; line-height: 1.6; color: var(--muted); max-width: 640px; }
.rd-hero p b { color: var(--text); }
.rd-hero-stats { display: flex; gap: 12px; }
.rd-stat { display: flex; flex-direction: column; align-items: center; padding: 12px 18px; background: rgba(4,6,16,0.5); border: 1px solid var(--border); border-radius: 12px; min-width: 96px; }
.rd-stat .v { font-size: 22px; font-weight: 800; color: var(--amber); }
.rd-stat .l { font-size: 11px; color: var(--muted); margin-top: 2px; }
.rd-warn { display: flex; align-items: flex-start; gap: 8px; font-size: 12px; line-height: 1.5; color: var(--text); background: rgba(245,179,66,0.07); border: 1px solid rgba(245,179,66,0.3); border-radius: 11px; padding: 10px 13px; }
.rd-warn svg { color: var(--amber); flex-shrink: 0; margin-top: 2px; }
.rd-panel { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 16px 18px; }
.rd-panel-h { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 14px; color: var(--text); }
.rd-panel-h em { margin-left: auto; font-style: normal; font-weight: 400; font-size: 11.5px; color: var(--dim); }
.rd-sources { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; margin-top: 12px; }
.rd-source { display: flex; flex-direction: column; gap: 3px; padding: 11px 13px; border-radius: 12px; border: 1px solid var(--border); background: rgba(4,6,16,0.4); font-size: 11.5px; color: var(--muted); }
.rd-source.ok { border-color: rgba(79,209,255,0.35); }
.rd-source.ok .rd-source-top svg { color: var(--cyan); }
.rd-source.off .rd-source-top svg { color: var(--amber); }
.rd-source-top { display: flex; align-items: center; gap: 6px; color: var(--text); font-size: 12.5px; }
.rd-needkey { color: var(--amber); }
.rd-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-top: 12px; }
.rd-btn { display: inline-flex; align-items: center; gap: 7px; font-size: 12.5px; font-weight: 600; color: var(--text); background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 10px; padding: 9px 14px; cursor: pointer; text-decoration: none; transition: border-color .16s, background .16s, transform .12s; }
.rd-btn:hover:not(:disabled) { border-color: var(--border-lit); transform: translateY(-1px); }
.rd-btn:disabled { opacity: .55; cursor: default; }
.rd-btn:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
.rd-btn.primary { color: var(--ink); background: var(--amber); border-color: transparent; }
.rd-btn.primary:hover:not(:disabled) { background: #ffc35a; }
.rd-btn.sm { padding: 6px 10px; font-size: 11.5px; }
.rd-link { background: none; border: 0; color: var(--cyan); font-size: 12px; cursor: pointer; padding: 8px 0; text-align: left; }
.rd-dim { color: var(--dim); font-size: 11.5px; }
.rd-profile { overflow: hidden; margin-top: 8px; }
.rd-grid3 { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px 12px; margin-top: 10px; }
.rd-grid3 label { display: flex; flex-direction: column; gap: 4px; font-size: 11.5px; color: var(--muted); }
.rd-grid3 .cw-input, .rd-grid3 .cw-textarea { min-width: 0; width: 100%; box-sizing: border-box; margin-top: 0; }
.rd-span3 { grid-column: 1 / -1; }
.rd-checks { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; font-size: 12px; color: var(--muted); }
.rd-chk { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text); cursor: pointer; }
.rd-chk input { accent-color: var(--amber); }
.rd-views { display: flex; flex-wrap: wrap; gap: 8px; }
.rd-chip { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: var(--muted); background: rgba(4,6,16,0.45); border: 1px solid var(--border); border-radius: 999px; padding: 6px 12px; cursor: pointer; transition: color .16s, border-color .16s, background .16s; }
.rd-chip:hover { color: var(--text); border-color: var(--border-lit); }
.rd-chip.active { color: var(--ink); background: var(--lime); border-color: transparent; }
.rd-filters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 12px; }
.rd-filters .cw-input { min-width: 140px; padding: 8px 10px; }
.rd-narrow { width: 120px; min-width: 0 !important; }
.rd-search { display: flex; align-items: center; gap: 6px; flex: 1; min-width: 220px; background: rgba(4,6,16,0.55); border: 1px solid var(--border); border-radius: 10px; padding: 0 10px; color: var(--dim); }
.rd-search input { flex: 1; background: transparent; border: 0; color: var(--text); font-size: 12.5px; padding: 9px 0; outline: none; }
.rd-nl svg { color: var(--lime); }
.rd-proposal { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-top: 10px; font-size: 12px; color: var(--text); background: rgba(200,240,74,0.06); border: 1px dashed rgba(200,240,74,0.4); border-radius: 10px; padding: 8px 12px; }
.rd-proposal code { font-size: 11px; color: var(--lime); }
.rd-empty { display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center; color: var(--muted); padding: 46px 20px; background: var(--panel); border: 1px dashed var(--border-lit); border-radius: 16px; font-size: 13.5px; }
.rd-empty svg { color: var(--amber); }
.rd-empty p { max-width: 460px; line-height: 1.6; margin: 0; }
.rd-feed { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 14px; }
.rd-card { display: flex; flex-direction: column; gap: 9px; background: var(--panel); border: 1px solid var(--border); border-left: 3px solid rgba(245,179,66,0.55); border-radius: 14px; padding: 15px 16px 13px; transition: border-color .16s, transform .12s; }
.rd-card:hover { border-color: var(--border-lit); transform: translateY(-1px); }
.rd-card.stale { border-left-color: var(--dim); opacity: .8; }
.rd-card h3 { margin: 0; font-size: 15px; line-height: 1.35; font-weight: 700; color: var(--text); cursor: pointer; }
.rd-card h3:hover { color: var(--amber); }
.rd-card-top { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.rd-type { font-size: 10.5px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; padding: 3px 8px; border-radius: 6px; background: rgba(245,179,66,0.14); color: var(--amber); }
.rd-type.t-technical_bounty { background: rgba(200,240,74,0.12); color: var(--lime); }
.rd-type.t-contract, .rd-type.t-procurement, .rd-type.t-rfp { background: rgba(79,209,255,0.12); color: var(--cyan); }
.rd-src { display: inline-flex; align-items: center; gap: 5px; font-size: 10.5px; color: var(--cyan); background: rgba(79,209,255,0.08); border: 1px solid rgba(79,209,255,0.28); border-radius: 6px; padding: 2px 7px; }
.rd-src.stale { color: var(--amber); border-color: rgba(245,179,66,0.4); background: rgba(245,179,66,0.08); }
.rd-ustat { margin-left: auto; font-size: 10.5px; color: var(--lime); text-transform: uppercase; letter-spacing: .06em; }
.rd-org { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--muted); }
.rd-facts { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 12px; color: var(--text); }
.rd-facts span { display: inline-flex; align-items: center; gap: 5px; }
.rd-facts svg { color: var(--dim); }
.rd-nv { color: var(--dim); font-style: italic; font-size: 11.5px; }
.rd-urgent { color: var(--amber); }
.rd-score { display: flex; flex-direction: column; gap: 4px; }
.rd-score-bar { height: 6px; border-radius: 4px; background: rgba(255,255,255,0.06); overflow: hidden; }
.rd-score-bar span { display: block; height: 100%; border-radius: 4px; background: var(--dim); transition: width .3s; }
.rd-score.hi .rd-score-bar span { background: var(--lime); } .rd-score.mid .rd-score-bar span { background: var(--amber); } .rd-score.lo .rd-score-bar span { background: #8a8fa8; }
.rd-score-txt { display: flex; align-items: baseline; gap: 6px; font-size: 12px; }
.rd-score-txt b { font-size: 15px; } .rd-score-txt small { color: var(--muted); font-size: 11px; }
.rd-score.lg .rd-score-bar { height: 10px; } .rd-score.lg .rd-score-txt b { font-size: 24px; }
.rd-barrier { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.rd-bar-lbl { font-size: 11px; padding: 2px 8px; border-radius: 6px; background: rgba(255,255,255,0.05); color: var(--muted); }
.rd-bar-lbl.lo { color: var(--lime); background: rgba(200,240,74,0.1); } .rd-bar-lbl.hi { color: var(--amber); background: rgba(245,179,66,0.12); }
.rd-req { font-size: 10.5px; color: var(--muted); border: 1px solid var(--border); border-radius: 6px; padding: 2px 7px; }
.rd-next { font-size: 12px; line-height: 1.5; color: var(--text); background: rgba(4,6,16,0.45); border-left: 2px solid var(--lime); padding: 7px 10px; border-radius: 0 8px 8px 0; }
.rd-actions { display: flex; align-items: center; gap: 6px; margin-top: 2px; }
.rd-actions .rd-btn { margin-left: auto; }
.rd-ic { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--border); background: transparent; color: var(--muted); cursor: pointer; transition: color .16s, border-color .16s, background .16s; }
.rd-ic:hover { color: var(--amber); border-color: rgba(245,179,66,0.5); background: rgba(245,179,66,0.08); }
.rd-modal-bg { position: fixed; inset: 0; z-index: 200; background: rgba(3,4,10,0.72); backdrop-filter: blur(10px); display: flex; align-items: flex-start; justify-content: center; padding: 30px 16px; overflow-y: auto; }
.rd-modal { width: min(1180px, 100%); background: var(--panel-solid); border: 1px solid var(--border-lit); border-radius: 18px; padding: 22px 24px; display: flex; flex-direction: column; gap: 14px; }
.rd-modal-h { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }
.rd-modal-h h2 { margin: 8px 0 6px; font-size: 20px; line-height: 1.3; }
.rd-modal-actions { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.rd-stages { display: flex; gap: 4px; flex-wrap: wrap; }
.rd-stage { font-size: 11px; font-weight: 600; color: var(--dim); background: rgba(255,255,255,0.03); border: 1px solid var(--border); padding: 5px 10px; border-radius: 999px; cursor: pointer; }
.rd-stage.done { color: var(--text); border-color: rgba(200,240,74,0.4); }
.rd-stage.cur { color: var(--ink); background: var(--lime); border-color: transparent; }
.rd-detail-grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 22px; }
.rd-detail-grid section { min-width: 0; display: flex; flex-direction: column; gap: 8px; font-size: 13px; }
.rd-detail-grid h4 { margin: 10px 0 2px; font-size: 12px; text-transform: uppercase; letter-spacing: .07em; color: var(--amber); display: flex; gap: 8px; align-items: baseline; }
.rd-detail-grid h4 small { text-transform: none; letter-spacing: 0; color: var(--dim); font-weight: 500; }
.rd-dl { display: grid; grid-template-columns: 130px 1fr; gap: 5px 10px; margin: 0; font-size: 12.5px; }
.rd-dl dt { color: var(--muted); } .rd-dl dd { margin: 0; color: var(--text); word-break: break-word; }
.rd-dl a { color: var(--cyan); }
.rd-quote { margin: 0; font-size: 12.5px; line-height: 1.55; color: var(--text); background: rgba(79,209,255,0.05); border-left: 2px solid var(--cyan); padding: 8px 12px; border-radius: 0 8px 8px 0; }
.rd-desc { margin: 0; font-size: 12.5px; line-height: 1.55; color: var(--muted); max-height: 220px; overflow-y: auto; }
.rd-evidence { margin: 0; padding-left: 16px; font-size: 12px; line-height: 1.55; color: var(--muted); }
.rd-evidence q { color: var(--text); } .rd-evidence code { font-size: 10.5px; color: var(--cyan); }
.rd-breakdown { display: flex; flex-direction: column; gap: 5px; margin-top: 6px; }
.rd-bd-row { display: grid; grid-template-columns: 150px 1fr 48px; gap: 8px; align-items: center; font-size: 11.5px; color: var(--muted); }
.rd-bd-bar { height: 6px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; } .rd-bd-bar span { display: block; height: 100%; background: var(--amber); }
.rd-bd-row small { text-align: right; color: var(--text); }
.rd-notes { margin: 4px 0 0; padding-left: 16px; font-size: 12px; color: var(--muted); }
.rd-lbl-note { font-size: 11.5px; color: var(--dim); font-style: italic; }
.rd-sig { font-size: 12px; color: var(--muted); } .rd-sig b.lo { color: var(--lime); } .rd-sig b.hi { color: var(--amber); }
.rd-ai { display: flex; flex-direction: column; gap: 6px; font-size: 12.5px; line-height: 1.5; background: rgba(4,6,16,0.45); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; }
.rd-ai p { margin: 0; } .rd-ai ul { margin: 2px 0 0; padding-left: 16px; color: var(--muted); } .rd-ai b { color: var(--text); }
.rd-ai-h { display: flex; align-items: center; gap: 7px; font-weight: 700; color: var(--cyan); } .rd-ai-h small { color: var(--dim); font-weight: 400; }
.rd-ai.skeptic .rd-ai-h { color: var(--amber); }
.rd-verdict { margin-left: auto; font-size: 10.5px; text-transform: uppercase; letter-spacing: .08em; padding: 2px 8px; border-radius: 6px; background: rgba(255,255,255,0.06); }
.rd-ai.v-block .rd-verdict { color: #ff7a90; background: rgba(255,84,112,0.14); } .rd-ai.v-caution .rd-verdict { color: var(--amber); } .rd-ai.v-clear .rd-verdict { color: var(--lime); }
.rd-two { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.rd-similar { margin: 0; padding-left: 16px; font-size: 12px; color: var(--muted); } .rd-similar small { color: var(--dim); }
.rd-desk { background: rgba(200,240,74,0.04); border: 1px solid rgba(200,240,74,0.25); border-radius: 14px; padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; }
.rd-desk .cw-textarea { margin-top: 0; }
.rd-draft { background: rgba(4,6,16,0.5); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; font-size: 13px; line-height: 1.6; }
.rd-draft-h { display: flex; justify-content: space-between; align-items: center; gap: 10px; font-size: 11.5px; color: var(--dim); margin-bottom: 8px; }
.rd-notes-box { display: flex; flex-direction: column; gap: 6px; } .rd-notes-box h4 { margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: .07em; color: var(--amber); }
.rd-notes-box .cw-textarea { margin-top: 0; }
@media (max-width: 900px) { .rd-detail-grid, .rd-two { grid-template-columns: 1fr; } .rd-feed { grid-template-columns: 1fr; } .rd-dl { grid-template-columns: 110px 1fr; } }

/* ===== Global Voice Commander (floating mic) ===== */
.vcmd { position: fixed; right: 22px; bottom: 22px; z-index: 300; display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.vcmd-panel { max-width: 420px; background: rgba(10,14,34,0.92); backdrop-filter: blur(14px); border: 1px solid var(--border-lit); border-radius: 12px; padding: 10px 12px; font-size: 12px; color: var(--muted); box-shadow: 0 16px 40px rgba(0,0,0,0.45); }
.vcmd-line { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; line-height: 1.45; }
.vcmd-line b { color: var(--text); } .vcmd-line em { color: var(--cyan); font-style: normal; } .vcmd-line svg { color: var(--violet2); flex-shrink: 0; }
.vcmd-x { margin-left: auto; background: none; border: 0; color: var(--dim); font-size: 11px; cursor: pointer; }
.vcmd-bar { display: flex; align-items: center; gap: 8px; background: rgba(10,14,34,0.92); backdrop-filter: blur(14px); border: 1px solid var(--border-lit); border-radius: 999px; padding: 5px 5px 5px 6px; box-shadow: 0 16px 40px rgba(0,0,0,0.45); }
.vcmd-seg { display: flex; gap: 2px; background: rgba(4,6,16,0.6); border-radius: 999px; padding: 3px; }
.vcmd-seg button { display: inline-flex; align-items: center; gap: 5px; font-size: 11.5px; font-weight: 600; color: var(--muted); background: transparent; border: 0; border-radius: 999px; padding: 6px 10px; cursor: pointer; transition: color .16s, background .16s; }
.vcmd-seg button.on { color: #06060f; background: linear-gradient(135deg, var(--violet), var(--cyan)); }
.vcmd-seg button:focus-visible { outline: 2px solid var(--cyan); }
.vcmd-mic { width: 44px; height: 44px; border-radius: 50%; border: 1px solid var(--border-lit); background: rgba(255,255,255,0.04); color: var(--text); display: grid; place-items: center; cursor: pointer; transition: transform .12s, background .18s, box-shadow .18s; }
.vcmd-mic:hover:not(:disabled) { transform: translateY(-1px); }
.vcmd-mic:disabled { opacity: .5; cursor: default; }
.vcmd-mic.on { color: #06060f; background: linear-gradient(135deg, var(--violet), var(--cyan)); border-color: transparent; animation: vcpulse 1.6s ease-in-out infinite; }
.vcmd-mic:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
@media (max-width: 640px) { .vcmd { right: 12px; bottom: 12px; } .vcmd-panel { max-width: calc(100vw - 24px); } }

/* Self-Directive: periodic scan */
.sd-scan { margin-top: 14px; border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; background: rgba(4,6,16,0.35); display: flex; flex-direction: column; gap: 10px; }
.sd-scan-note { margin-left: 8px; font-weight: 400; font-size: 11px; color: var(--dim); }
.sd-scan-row { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; font-size: 12.5px; color: var(--muted); }
.sd-toggle { display: inline-flex; align-items: center; gap: 8px; cursor: pointer; color: var(--text); font-weight: 600; }
.sd-toggle input { accent-color: var(--violet); width: 16px; height: 16px; }
.sd-interval { display: inline-flex; align-items: center; gap: 6px; }
.sd-interval input { width: 64px; background: rgba(4,6,16,0.6); border: 1px solid var(--border); border-radius: 8px; color: var(--text); padding: 6px 8px; font-size: 12.5px; }
.sd-scan-meta { font-size: 11.5px; color: var(--dim); }
.sd-scan-run { margin-left: auto; display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: var(--text); background: rgba(255,255,255,0.03); border: 1px solid var(--border-lit); border-radius: 9px; padding: 7px 12px; cursor: pointer; }
.sd-scan-run:disabled { opacity: .55; cursor: default; }
.sd-focus { width: 100%; box-sizing: border-box; resize: vertical; font-size: 12px; line-height: 1.5; color: var(--muted); background: rgba(4,6,16,0.5); border: 1px solid var(--border); border-radius: 9px; padding: 8px 10px; }
.sd-scans { display: flex; flex-direction: column; gap: 6px; }
.sd-scan-item { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 11.5px; color: var(--muted); }
.sd-scan-when { color: var(--dim); } .sd-scan-counts { color: var(--text); } .sd-scan-res { color: var(--violet2); }
.sd-auto { font-size: 10px; letter-spacing: .06em; text-transform: uppercase; color: var(--cyan); border: 1px solid rgba(79,209,255,0.35); border-radius: 5px; padding: 1px 6px; }

/* ===== Local Node ===== */
.ln-wrap { display: flex; flex-direction: column; gap: 16px; }
.ln-wrap .chr-hero-left p b { color: var(--text); }
.ln-setup { margin-top: 12px; font-size: 13px; line-height: 1.6; color: var(--muted); }
.ln-setup ol { margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 6px; }
.ln-setup a { color: var(--cyan); }
.ln-setup code, .ln-key { font-family: ui-monospace, monospace; font-size: 11.5px; color: var(--text); background: rgba(4,6,16,0.6); border: 1px solid var(--border); border-radius: 6px; padding: 2px 7px; word-break: break-all; }
.ln-key { color: var(--gold); }
.ln-dim { color: var(--dim); }
.ln-safety { display: flex; flex-wrap: wrap; gap: 8px 16px; margin-top: 12px; font-size: 11.5px; color: var(--muted); }
.ln-safety span { display: inline-flex; align-items: center; gap: 5px; } .ln-safety svg { color: var(--green); }
.ln-nodes { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; }
.ln-node { display: flex; align-items: flex-start; gap: 10px; text-align: left; background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; color: var(--text); cursor: pointer; position: relative; transition: border-color .16s; }
.ln-node svg { color: var(--dim); margin-top: 2px; flex-shrink: 0; } .ln-node.on svg { color: var(--green); }
.ln-node.active { border-color: var(--border-lit); background: rgba(139,124,255,0.08); }
.ln-node span { display: flex; flex-direction: column; gap: 2px; min-width: 0; } .ln-node b { font-size: 13.5px; } .ln-node small { font-size: 11px; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ln-node em { margin-left: auto; font-style: normal; font-size: 11px; font-weight: 700; color: #06060f; background: var(--gold); border-radius: 999px; padding: 2px 8px; }
.ln-plan { margin-top: 10px; font-size: 12.5px; color: var(--muted); background: rgba(139,124,255,0.08); border: 1px solid var(--border); border-radius: 10px; padding: 9px 12px; } .ln-plan b { color: var(--text); }
.ln-manual { margin-top: 10px; font-size: 12px; color: var(--muted); } .ln-manual summary { cursor: pointer; }
.ln-await { background: rgba(245,196,81,0.06); border: 1px solid rgba(245,196,81,0.35); border-radius: 14px; padding: 14px 16px; display: flex; flex-direction: column; gap: 8px; }
.ln-await .fa-head { color: var(--gold); }
.ln-await-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 12.5px; color: var(--text); }
.ln-await-row code { color: var(--gold); }
.ln-tasks { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; }
.ln-task { border: 1px solid var(--border); border-radius: 10px; padding: 8px 12px; background: rgba(4,6,16,0.35); }
.ln-task.s-proposed { border-color: rgba(245,196,81,0.45); } .ln-task.s-running { border-color: rgba(79,209,255,0.5); } .ln-task.s-failed { border-color: rgba(255,84,112,0.45); } .ln-task.s-awaiting_submit { border-color: rgba(245,196,81,0.6); }
.ln-task-h { display: flex; align-items: center; gap: 8px; font-size: 12.5px; }
.ln-task-h svg { color: var(--violet2); flex-shrink: 0; }
.ln-task-title { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor: pointer; color: var(--text); }
.ln-status { font-size: 10.5px; text-transform: uppercase; letter-spacing: .06em; padding: 2px 7px; border-radius: 6px; background: rgba(255,255,255,0.05); color: var(--muted); }
.ln-status.s-proposed { color: var(--gold); background: rgba(245,196,81,0.12); } .ln-status.s-queued { color: var(--cyan); } .ln-status.s-running { color: var(--cyan); background: rgba(79,209,255,0.12); }
.ln-status.s-done { color: var(--green); background: rgba(72,213,151,0.12); } .ln-status.s-failed, .ln-status.s-rejected { color: #ff7a90; } .ln-status.s-awaiting_submit { color: var(--gold); background: rgba(245,196,81,0.15); }
.ln-when { font-size: 11px; color: var(--dim); white-space: nowrap; }
.ln-ok, .ln-no { width: 28px; height: 28px; border-radius: 7px; border: 1px solid var(--border); background: transparent; cursor: pointer; display: grid; place-items: center; }
.ln-ok { color: var(--green); } .ln-ok:hover { background: rgba(72,213,151,0.15); border-color: rgba(72,213,151,0.5); }
.ln-no { color: #ff7a90; } .ln-no:hover { background: rgba(255,84,112,0.12); border-color: rgba(255,84,112,0.5); }
.ln-params, .ln-text { margin: 8px 0 0; font-family: ui-monospace, monospace; font-size: 11.5px; line-height: 1.5; color: var(--muted); background: rgba(4,6,16,0.6); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; white-space: pre-wrap; word-break: break-word; max-height: 360px; overflow: auto; }
.ln-err { margin-top: 6px; font-size: 11.5px; color: #ff7a90; display: flex; align-items: center; gap: 6px; }
.ln-page { margin-top: 12px; display: flex; flex-direction: column; gap: 10px; }
.ln-page-h { font-size: 12.5px; color: var(--muted); display: flex; gap: 8px; align-items: center; flex-wrap: wrap; } .ln-page-h b { color: var(--text); } .ln-page-h a { color: var(--cyan); display: inline-flex; }
.ln-answer { font-size: 13px; line-height: 1.55; color: var(--text); background: rgba(79,209,255,0.06); border-left: 2px solid var(--cyan); padding: 9px 12px; border-radius: 0 8px 8px 0; } .ln-answer small { color: var(--dim); margin-left: 6px; }
.ln-page-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.ln-shot { width: 100%; border-radius: 10px; border: 1px solid var(--border); } .ln-shot.big { max-height: 60vh; object-fit: contain; }
.ln-forms { font-size: 12px; color: var(--muted); } .ln-forms code { display: inline-block; margin: 2px 6px 2px 0; font-size: 11px; color: var(--cyan); }
.ln-detail h2 { font-size: 17px; margin: 0 0 4px; }
@media (max-width: 900px) { .ln-page-grid { grid-template-columns: 1fr; } }

/* ===== Companion (small desktop window) ===== */
.companion-launch { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; color: #06060f; background: linear-gradient(135deg, var(--gold), #f5843c); border: 0; border-radius: 999px; padding: 7px 12px; cursor: pointer; margin-right: 10px; transition: transform .12s, box-shadow .18s; }
.companion-launch:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(245,196,81,0.3); }
.companion-root { min-height: 100vh; display: flex; }
.cp { display: flex; flex-direction: column; background: var(--panel); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; height: 100%; min-height: 0; }
.cp.standalone { flex: 1; border-radius: 0; border: 0; height: 100vh; }
.cp-head { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-bottom: 1px solid var(--border); background: rgba(4,6,16,0.5); }
.cp-brand { display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 13.5px; color: var(--gold); letter-spacing: .01em; }
.cp-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--dim); } .cp-dot.on { background: var(--green); box-shadow: 0 0 10px var(--green); } .cp-dot.busy { background: var(--cyan); animation: vcpulse 1.2s infinite; }
.cp-head-actions { display: flex; align-items: center; gap: 6px; }
.cp-pin { display: inline-flex; align-items: center; gap: 4px; font-size: 10.5px; color: var(--dim); cursor: help; }
.cp-ic { width: 30px; height: 30px; border-radius: 8px; border: 1px solid var(--border); background: transparent; color: var(--muted); display: grid; place-items: center; cursor: pointer; transition: color .16s, border-color .16s; }
.cp-ic:hover:not(:disabled) { color: var(--text); border-color: var(--border-lit); } .cp-ic:disabled { opacity: .5; }
.cp-share { border-bottom: 1px solid var(--border); background: rgba(4,6,16,0.35); }
.cp-share-btn { width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 12.5px; font-weight: 600; color: var(--cyan); background: transparent; border: 0; padding: 12px; cursor: pointer; }
.cp-share-btn:hover { background: rgba(79,209,255,0.06); }
.cp-video { width: 100%; max-height: 180px; object-fit: contain; background: #000; }
.cp-share-bar { display: flex; align-items: center; gap: 8px; padding: 6px 10px; font-size: 11.5px; color: var(--muted); }
.cp-share-bar > span { display: inline-flex; align-items: center; gap: 5px; color: var(--green); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cp-chk { display: inline-flex; align-items: center; gap: 5px; cursor: pointer; } .cp-chk input { accent-color: var(--gold); }
.cp-log { flex: 1; min-height: 0; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.cp-empty { font-size: 12.5px; line-height: 1.6; color: var(--muted); padding: 14px; border: 1px dashed var(--border); border-radius: 12px; text-align: left; }
.cp-msg { position: relative; max-width: 88%; font-size: 13px; line-height: 1.55; padding: 9px 12px; border-radius: 12px; border: 1px solid var(--border); white-space: pre-wrap; word-break: break-word; }
.cp-msg.user { align-self: flex-end; background: rgba(245,196,81,0.10); border-color: rgba(245,196,81,0.35); }
.cp-msg.assistant { align-self: flex-start; background: rgba(4,6,16,0.5); padding-right: 30px; }
.cp-msg.streaming { border-style: dashed; }
.cp-tag { display: inline-flex; align-items: center; gap: 3px; font-size: 9.5px; color: var(--gold); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 3px; }
.cp-replay { position: absolute; right: 6px; bottom: 6px; width: 22px; height: 22px; border-radius: 6px; border: 1px solid var(--border); background: transparent; color: var(--dim); display: grid; place-items: center; cursor: pointer; }
.cp-thinking { display: flex; align-items: center; gap: 6px; font-size: 11.5px; color: var(--cyan); }
.cp-input { display: flex; align-items: center; gap: 8px; padding: 10px; border-top: 1px solid var(--border); background: rgba(4,6,16,0.5); }
.cp-input input { flex: 1; min-width: 0; font-size: 13px; color: var(--text); background: rgba(4,6,16,0.6); border: 1px solid var(--border); border-radius: 999px; padding: 10px 14px; }
.cp-input input:focus { outline: none; border-color: var(--border-lit); }
.cp-mic, .cp-send { width: 38px; height: 38px; border-radius: 50%; border: 1px solid var(--border-lit); background: rgba(255,255,255,0.04); color: var(--text); display: grid; place-items: center; cursor: pointer; flex-shrink: 0; }
.cp-mic.on { color: #06060f; background: linear-gradient(135deg, var(--gold), #f5843c); border-color: transparent; } .cp-mic.live { animation: vcpulse 1.4s infinite; }
.cp-send { color: #06060f; background: linear-gradient(135deg, var(--violet), var(--cyan)); border-color: transparent; } .cp-send:disabled { opacity: .45; cursor: default; }
.cp-stopvoice { position: absolute; bottom: 64px; right: 14px; font-size: 11px; color: var(--muted); background: rgba(10,14,34,0.9); border: 1px solid var(--border); border-radius: 999px; padding: 4px 10px; cursor: pointer; }
.cp-ic.on { color: var(--gold); border-color: rgba(245,196,81,0.5); background: rgba(245,196,81,0.1); }
.cp-watchbar { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--gold); padding: 5px 12px; background: rgba(245,196,81,0.06); border-bottom: 1px solid rgba(245,196,81,0.2); }
.cp-tag.k-error { color: #ff7a90; } .cp-tag.k-form { color: var(--cyan); }

/* ===== Apex Nexus ===== */
.ax-wrap { display: flex; flex-direction: column; gap: 16px; }
.ax-wrap .chr-hero-left p b { color: var(--text); } .ax-wrap .chr-hero-left p code { font-family: ui-monospace, monospace; font-size: 11.5px; color: var(--gold); }
.ax-pay { display: flex; align-items: flex-start; gap: 8px; font-size: 12px; line-height: 1.5; color: var(--muted); background: rgba(245,196,81,0.06); border: 1px solid rgba(245,196,81,0.3); border-radius: 11px; padding: 10px 13px; }
.ax-pay svg { color: var(--gold); flex-shrink: 0; margin-top: 2px; } .ax-pay b { color: var(--text); }
.ax-pay.on { border-color: rgba(72,213,151,0.4); background: rgba(72,213,151,0.06); } .ax-pay.on svg { color: var(--green); }
.ax-products { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.ax-product { display: flex; flex-direction: column; gap: 6px; text-align: left; background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 14px 16px; color: var(--text); cursor: pointer; transition: border-color .16s, transform .12s; }
.ax-product:hover { border-color: var(--border-lit); transform: translateY(-1px); }
.ax-product.active { border-color: var(--gold); background: rgba(245,196,81,0.07); box-shadow: 0 0 0 1px rgba(245,196,81,0.25) inset; }
.ax-product-top { display: flex; align-items: center; gap: 8px; font-size: 14px; } .ax-product-top svg { color: var(--gold); }
.ax-price { margin-left: auto; font-weight: 800; color: var(--gold); }
.ax-product small { font-size: 12px; line-height: 1.45; color: var(--muted); } .ax-buyer { color: var(--dim) !important; font-size: 11px !important; }
.ax-form { margin-top: 12px; }
.ax-deliverable { background: var(--panel); border: 1px solid var(--border-lit); border-radius: 16px; padding: 18px 20px; }
.ax-del-head { display: flex; justify-content: space-between; gap: 14px; flex-wrap: wrap; align-items: flex-start; }
.ax-del-head a { color: var(--cyan); }
.ax-del-grid { display: grid; grid-template-columns: minmax(0, 1.8fr) minmax(260px, 1fr); gap: 18px; margin-top: 14px; }
.ax-md { min-width: 0; font-size: 13px; line-height: 1.6; max-height: 70vh; overflow-y: auto; padding-right: 8px; }
.ax-md table { border-collapse: collapse; font-size: 12px; } .ax-md td, .ax-md th { border: 1px solid var(--border); padding: 4px 8px; }
.ax-sell { display: flex; flex-direction: column; gap: 8px; }
.ax-sell .cw-input { width: 100%; box-sizing: border-box; min-width: 0; }
.ax-warn { display: flex; align-items: flex-start; gap: 6px; font-size: 11.5px; color: var(--muted); } .ax-warn svg { color: var(--gold); flex-shrink: 0; margin-top: 2px; }
.ax-orders { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; }
.ax-order { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 12.5px; padding: 8px 12px; border: 1px solid var(--border); border-radius: 10px; background: rgba(4,6,16,0.35); }
.ax-order.s-paid { border-color: rgba(72,213,151,0.35); }
.ax-order-buyer { flex: 1; min-width: 160px; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ax-order-price { font-weight: 700; color: var(--gold); }
@media (max-width: 900px) { .ax-del-grid { grid-template-columns: 1fr; } }
.cp-install { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 700; color: #06060f; background: var(--gold); border: 0; border-radius: 999px; padding: 5px 10px; cursor: pointer; }

/* ===== Auth ===== */
.auth-checking { display: grid; place-items: center; min-height: 100vh; }
.auth-spinner { display: flex; align-items: center; gap: 10px; font-weight: 800; letter-spacing: .1em; color: var(--violet2); animation: vcpulse 1.6s infinite; border-radius: 999px; padding: 10px 18px; }
.auth-root { position: relative; z-index: 1; min-height: 100vh; display: grid; place-items: center; padding: 24px; }
.auth-card { width: min(440px, 100%); background: var(--panel-solid); border: 1px solid var(--border-lit); border-radius: 20px; padding: 28px 28px 22px; box-shadow: 0 30px 80px rgba(0,0,0,0.5); }
.auth-brand { display: flex; align-items: center; gap: 8px; font-weight: 900; font-size: 15px; letter-spacing: .12em; color: var(--gold); } .auth-brand span { color: var(--dim); font-weight: 500; letter-spacing: .04em; }
.auth-card h1 { margin: 16px 0 6px; font-size: 24px; letter-spacing: -0.01em; }
.auth-sub { margin: 0 0 18px; font-size: 13px; line-height: 1.55; color: var(--muted); }
.auth-form { display: flex; flex-direction: column; gap: 12px; }
.auth-form label { display: flex; flex-direction: column; gap: 5px; font-size: 11.5px; color: var(--muted); }
.auth-form label > span { display: inline-flex; align-items: center; gap: 5px; }
.auth-form .cw-input { width: 100%; box-sizing: border-box; min-width: 0; font-size: 14px; padding: 11px 13px; }
.auth-pw { position: relative; } .auth-pw .cw-input { padding-right: 40px; }
.auth-eye { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); background: transparent; border: 0; color: var(--dim); cursor: pointer; display: grid; place-items: center; width: 28px; height: 28px; }
.auth-hint { color: var(--dim); }
.auth-remember { flex-direction: row !important; align-items: center; gap: 8px !important; font-size: 12px !important; color: var(--text) !important; } .auth-remember input { accent-color: var(--gold); }
.auth-submit { margin-top: 4px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; font-size: 14px; font-weight: 800; color: #06060f; background: linear-gradient(135deg, var(--gold), #f5843c); border: 0; border-radius: 12px; padding: 12px 16px; cursor: pointer; transition: transform .12s, box-shadow .18s; }
.auth-submit:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(245,196,81,0.3); } .auth-submit:disabled { opacity: .6; cursor: default; }
.auth-link { margin-top: 12px; background: none; border: 0; color: var(--cyan); font-size: 12.5px; cursor: pointer; }
.auth-foot { margin-top: 16px; display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--dim); }
.acct { position: relative; } .acct-btn { cursor: pointer; border: 1px solid var(--border); background: rgba(255,255,255,0.03); }
.acct-pop { position: absolute; right: 0; top: calc(100% + 8px); width: 300px; z-index: 250; background: rgba(10,14,34,0.96); backdrop-filter: blur(14px); border: 1px solid var(--border-lit); border-radius: 14px; padding: 12px; display: flex; flex-direction: column; gap: 8px; box-shadow: 0 16px 40px rgba(0,0,0,0.5); }
.acct-row { display: flex; align-items: center; gap: 8px; font-size: 13px; } .acct-row div { flex: 1; display: flex; flex-direction: column; } .acct-row small { color: var(--dim); font-size: 11px; } .acct-row svg { color: var(--gold); }
.acct-meta { display: flex; align-items: center; gap: 5px; font-size: 10.5px; color: var(--dim); }
.acct-item { display: flex; align-items: center; gap: 8px; text-align: left; font-size: 12.5px; color: var(--text); background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 9px; padding: 9px 11px; cursor: pointer; }
.acct-item:hover { border-color: var(--border-lit); } .acct-item.danger { color: #ff7a90; }
.acct-form { display: flex; flex-direction: column; gap: 6px; } .acct-form .cw-input { width: 100%; box-sizing: border-box; min-width: 0; }

```


### `frontend/src/components/SovereignHome.js`
```javascript
import React, { useEffect, useState, useCallback, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send, Hammer, Search, MoveRight, Banknote, Sparkles, CheckCircle2,
  Circle, Trash2, PauseCircle, PlayCircle, Compass, ShieldCheck, Loader2,
  ScrollText, Target, Wallet, Zap, Activity, Play, AlertTriangle
} from "lucide-react";
import { API } from "../App";

const MODES = [
  { key: "Make", icon: Hammer, desc: "Create assets" },
  { key: "Find", icon: Search, desc: "Discover opportunity" },
  { key: "Move", icon: MoveRight, desc: "Advance a mission" },
  { key: "Collect", icon: Banknote, desc: "Get paid" },
];

const STAGES = ["Directive", "Discovery", "Deliverable", "Outreach", "Payment", "Receipt"];

const SAMPLES = [
  "Land a $750 freelance logo design client this week",
  "Turn my Python skills into a paid automation gig",
  "Sell a Notion productivity template pack online",
  "Get 3 paying newsletter sponsors for my tech blog",
];

const fmtTime = (iso) => {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch { return ""; }
};

export default function SovereignHome() {
  const [directive, setDirective] = useState("");
  const [mode, setMode] = useState("Move");
  const [missions, setMissions] = useState([]);
  const [stats, setStats] = useState(null);
  const [feed, setFeed] = useState([]);
  const [compiling, setCompiling] = useState(false);
  const [nextRec, setNextRec] = useState(null);
  const [loadingNext, setLoadingNext] = useState(false);
  const [runningId, setRunningId] = useState(null);
  const runningRef = useRef(false);

  const load = useCallback(async () => {
    try {
      const [m, s, f] = await Promise.all([
        axios.get(`${API}/missions?kind=revenue`),
        axios.get(`${API}/stats`),
        axios.get(`${API}/action-feed?limit=40`),
      ]);
      setMissions(m.data);
      setStats(s.data);
      setFeed(f.data);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const getPerfectNext = useCallback(async () => {
    setLoadingNext(true);
    try {
      const r = await axios.get(`${API}/perfect-next`);
      setNextRec(r.data);
    } catch (e) { /* silent */ } finally { setLoadingNext(false); }
  }, []);

  useEffect(() => { getPerfectNext(); }, [getPerfectNext, missions.length]);

  const compile = async () => {
    if (!directive.trim()) { toast.error("Speak a directive first"); return; }
    setCompiling(true);
    try {
      const r = await axios.post(`${API}/compile-directive`, { directive, mode });
      toast.success(`Mission compiled: ${r.data.title}`);
      setDirective("");
      await load();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Compilation failed");
    } finally { setCompiling(false); }
  };

  const executeNext = async (mid) => {
    const r = await axios.post(`${API}/missions/${mid}/execute-step`, {});
    return r.data; // { mission, log }
  };

  const runOne = async (mid) => {
    setRunningId(mid);
    try {
      const data = await executeNext(mid);
      if (data.log) {
        if (data.log.status === "approval_required") {
          toast.warning(`Owner approval required: ${data.log.step_title}`);
        } else {
          toast.success(`NEXUS: ${data.log.action.slice(0, 60)}`);
        }
      } else {
        toast("All steps already executed");
      }
      await load();
    } catch (e) {
      toast.error("NEXUS action failed");
    } finally { setRunningId(null); }
  };

  const autoRun = async (m) => {
    if (runningRef.current) return;
    runningRef.current = true;
    setRunningId(m.id);
    try {
      let remaining = m.steps.filter((s) => !s.done).length;
      while (remaining > 0) {
        const data = await executeNext(m.id);
        await load();
        if (!data.log || data.log.status === "approval_required") {
          if (data.log?.status === "approval_required") {
            toast.warning(`Paused: owner approval required at "${data.log.step_title}"`);
          }
          break;
        }
        remaining -= 1;
        await new Promise((res) => setTimeout(res, 650));
      }
      toast.success("NEXUS run complete");
    } catch (e) {
      toast.error("Auto-run interrupted");
    } finally {
      runningRef.current = false;
      setRunningId(null);
    }
  };

  const advance = async (mid, stepId, done) => {
    try {
      await axios.patch(`${API}/missions/${mid}/advance`, { step_id: stepId, done });
      await load();
    } catch (e) { toast.error("Could not advance"); }
  };

  const toggleStatus = async (m) => {
    const next = m.status === "paused" ? "active" : "paused";
    try {
      await axios.patch(`${API}/missions/${m.id}/status?status=${next}`);
      await load();
    } catch (e) { toast.error("Failed"); }
  };

  const remove = async (mid) => {
    try {
      await axios.delete(`${API}/missions/${mid}`);
      toast("Mission archived");
      await load();
    } catch (e) { toast.error("Failed"); }
  };

  const money = (n) => `$${Number(n || 0).toLocaleString()}`;

  return (
    <div className="home-wrap">
      {/* Directive console */}
      <section className="directive-console">
        <div className="dc-head">
          <Compass size={16} />
          <span>Directive Console</span>
          <em>Speak an outcome that ends in a payment.</em>
        </div>
        <div className="dc-input">
          <textarea
            data-testid="directive-input"
            value={directive}
            onChange={(e) => setDirective(e.target.value)}
            placeholder="e.g. Land a $750 logo client this week and get them to pay via Stripe"
            rows={2}
            onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) compile(); }}
          />
          <button data-testid="compile-btn" className="compile" onClick={compile} disabled={compiling}>
            {compiling ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
            {compiling ? "Compiling…" : "Compile Mission"}
          </button>
        </div>
        <div className="mode-row">
          {MODES.map((m) => {
            const Icon = m.icon;
            return (
              <button
                key={m.key}
                data-testid={`mode-${m.key}`}
                className={mode === m.key ? "mode active" : "mode"}
                onClick={() => setMode(m.key)}
                title={m.desc}
              >
                <Icon size={15} /> {m.key}
              </button>
            );
          })}
        </div>
        <div className="samples">
          {SAMPLES.map((s) => (
            <button key={s} className="sample" onClick={() => setDirective(s)}>{s}</button>
          ))}
        </div>
      </section>

      {/* Metrics + Perfect Next */}
      <section className="row-2">
        <div className="metrics">
          <Metric icon={Target} label="Active Missions" value={stats?.active ?? 0} />
          <Metric icon={CheckCircle2} label="Completed" value={stats?.complete ?? 0} />
          <Metric icon={Wallet} label="Projected" value={money(stats?.projected_revenue)} accent />
          <Metric icon={Banknote} label="Collected" value={money(stats?.collected_revenue)} gold />
        </div>

        <div className="perfect-next" data-testid="perfect-next">
          <div className="pn-head"><Sparkles size={15} /> Perfect Next <span className="gov">Soul Brain</span></div>
          {loadingNext ? (
            <div className="pn-loading"><Loader2 className="spin" size={16} /> Governing…</div>
          ) : (
            <p className="pn-body">{nextRec?.recommendation || "Awaiting your first directive."}</p>
          )}
          {nextRec?.mission_title && <div className="pn-target">→ {nextRec.mission_title}</div>}
        </div>
      </section>

      {/* Payment pipeline */}
      <section className="pipeline">
        <div className="pl-head"><Banknote size={15} /> Payment Pipeline</div>
        <div className="pl-track">
          {STAGES.map((st, i) => {
            const count = stats?.pipeline?.[st] || 0;
            return (
              <div key={st} className={`pl-stage ${count ? "lit" : ""}`}>
                <div className="pl-dot">{count}</div>
                <span>{st}</span>
                {i < STAGES.length - 1 && <div className="pl-line" />}
              </div>
            );
          })}
        </div>
      </section>

      {/* NEXUS Action Bus feed */}
      <section className="nexus" data-testid="nexus-feed">
        <div className="nx-head">
          <Zap size={15} /> NEXUS Action Bus
          <span className="nx-sub">trusted execution surface</span>
          <span className={`nx-live ${runningId ? "on" : ""}`}>
            <span className="pulse" /> {runningId ? "executing" : "idle"}
          </span>
        </div>
        {feed.length === 0 ? (
          <div className="nx-empty">No actions executed yet. Run a mission step and NEXUS logs verifiable evidence here.</div>
        ) : (
          <div className="nx-log">
            <AnimatePresence initial={false}>
              {feed.map((f) => (
                <motion.div
                  key={f.id}
                  className={`nx-row ${f.status}`}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  layout
                >
                  <span className="nx-time">{fmtTime(f.timestamp)}</span>
                  <span className={`nx-badge ${f.status}`}>
                    {f.status === "approval_required" ? <AlertTriangle size={11} /> : <Activity size={11} />}
                  </span>
                  <span className="nx-body">
                    <b>{f.mission_title}</b> · {f.action}
                    <em> ⟶ evidence: {f.evidence}</em>
                  </span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </section>

      {/* Mission board */}
      <section className="board">
        <div className="board-head"><ScrollText size={16} /> Mission Board</div>
        {missions.length === 0 ? (
          <div className="empty">
            <Sparkles size={26} />
            <p>No missions yet. Issue a directive above and ACASO will compile a full mission graph — steps, evidence, payment path and outcome metric.</p>
          </div>
        ) : (
          <div className="mission-grid">
            <AnimatePresence>
              {missions.map((m) => {
                const undone = m.steps.filter((s) => !s.done).length;
                const busy = runningId === m.id;
                return (
                <motion.div
                  key={m.id}
                  data-testid="mission-card"
                  className={`mission ${m.status}`}
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.96 }}
                  layout
                >
                  <div className="m-top">
                    <span className={`m-mode mode-${m.mode}`}>{m.mode}</span>
                    <span className={`m-status s-${m.status}`}>{m.status}</span>
                  </div>
                  <h3>{m.title}</h3>
                  <p className="m-summary">{m.summary}</p>

                  <div className="m-steps">
                    {m.steps.map((s) => (
                      <button
                        key={s.id}
                        className={`step ${s.done ? "done" : ""} ${busy && !s.done ? "pending" : ""}`}
                        onClick={() => advance(m.id, s.id, !s.done)}
                        title={s.detail}
                      >
                        {s.done ? <CheckCircle2 size={15} /> : (busy ? <Loader2 className="spin" size={15} /> : <Circle size={15} />)}
                        <span>{s.title}</span>
                      </button>
                    ))}
                  </div>

                  {m.status !== "complete" && (
                    <div className="m-run">
                      <button data-testid="run-next-btn" className="run" onClick={() => runOne(m.id)} disabled={busy || undone === 0}>
                        <Play size={14} /> Run Next
                      </button>
                      <button data-testid="autorun-btn" className="run auto" onClick={() => autoRun(m)} disabled={busy || undone === 0}>
                        {busy ? <Loader2 className="spin" size={14} /> : <Zap size={14} />} Auto-run ({undone})
                      </button>
                    </div>
                  )}

                  <div className="m-meta">
                    <div><Banknote size={13} /> {m.payment_path || "—"}</div>
                    <div><Target size={13} /> {m.outcome_metric || "—"}</div>
                    <div className="m-auth"><ShieldCheck size={13} /> {m.authority}</div>
                  </div>

                  {m.evidence?.length > 0 && (
                    <div className="m-evidence">
                      {m.evidence.map((e, i) => <span key={i}>{e}</span>)}
                    </div>
                  )}

                  <div className="m-foot">
                    <span className="m-amount">{money(m.amount)}</span>
                    <span className="m-stage">{m.stage}</span>
                    <div className="m-actions">
                      <button onClick={() => toggleStatus(m)} title={m.status === "paused" ? "Resume" : "Pause"}>
                        {m.status === "paused" ? <PlayCircle size={17} /> : <PauseCircle size={17} />}
                      </button>
                      <button onClick={() => remove(m.id)} title="Archive"><Trash2 size={16} /></button>
                    </div>
                  </div>
                </motion.div>
              );})}
            </AnimatePresence>
          </div>
        )}
      </section>
    </div>
  );
}

function Metric({ icon: Icon, label, value, accent, gold }) {
  return (
    <div className={`metric ${accent ? "accent" : ""} ${gold ? "gold" : ""}`}>
      <Icon size={16} />
      <div>
        <span className="m-val">{value}</span>
        <span className="m-lab">{label}</span>
      </div>
    </div>
  );
}

```


### `frontend/src/components/AskAllAIs.js`
```javascript
import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Send, Loader2, Sparkles, Layers, Bot } from "lucide-react";
import { API } from "../App";

const PROVIDERS = [
  { key: "openai", label: "GPT-4o", color: "#10a37f" },
  { key: "gemini", label: "Gemini", color: "#4285f4" },
  { key: "anthropic", label: "Claude", color: "#d97757" },
];

export default function AskAllAIs() {
  const [msg, setMsg] = useState("");
  const [selected, setSelected] = useState(["openai", "gemini", "anthropic"]);
  const [loading, setLoading] = useState(false);
  const [thread, setThread] = useState([]);
  const scroller = useRef(null);

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
  }, [thread, loading]);

  const toggle = (k) => {
    setSelected((prev) => prev.includes(k) ? prev.filter((p) => p !== k) : [...prev, k]);
  };

  const send = async () => {
    if (!msg.trim()) return;
    if (selected.length === 0) { toast.error("Select at least one mind"); return; }
    const question = msg;
    setThread((t) => [...t, { role: "user", text: question }]);
    setMsg("");
    setLoading(true);
    try {
      const r = await axios.post(`${API}/chat`, { message: question, models: selected });
      setThread((t) => [...t, { role: "assistant", ...r.data }]);
    } catch (e) {
      toast.error("Ask All AIs failed");
      setThread((t) => t.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="askai-wrap">
      <div className="askai-head">
        <div className="ah-title"><Sparkles size={16} /> Ask All AIs <em>· plural reasoning field</em></div>
        <div className="prov-picker">
          {PROVIDERS.map((p) => (
            <button
              key={p.key}
              data-testid={`prov-${p.key}`}
              className={selected.includes(p.key) ? "prov on" : "prov"}
              style={selected.includes(p.key) ? { borderColor: p.color, color: p.color } : {}}
              onClick={() => toggle(p.key)}
            >
              <Bot size={14} /> {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="thread" ref={scroller}>
        {thread.length === 0 && (
          <div className="askai-empty">
            <Layers size={28} />
            <p>Ask one question. OmniMind queries every selected mind in parallel, then the Synarchy arbiter fuses them into one superior answer.</p>
          </div>
        )}
        {thread.map((item, i) => item.role === "user" ? (
          <div key={i} className="bubble user">{item.text}</div>
        ) : (
          <motion.div key={i} className="answer-block" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            {item.synthesis && (
              <div className="synthesis">
                <div className="syn-head"><Sparkles size={14} /> Synarchy Synthesis</div>
                <p>{item.synthesis}</p>
              </div>
            )}
            <div className="models-grid">
              {item.results?.map((r) => (
                <div key={r.provider} className={`model-card ${r.ok ? "" : "failed"}`}>
                  <div className="mc-head">{r.label}</div>
                  <p>{r.answer}</p>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
        {loading && <div className="bubble thinking"><Loader2 className="spin" size={15} /> The minds are reasoning…</div>}
      </div>

      <div className="askai-input">
        <input
          data-testid="askai-input"
          value={msg}
          onChange={(e) => setMsg(e.target.value)}
          placeholder="Ask all the AIs anything…"
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
        />
        <button data-testid="askai-send" onClick={send} disabled={loading}>
          {loading ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
        </button>
      </div>
    </div>
  );
}

```


### `frontend/src/components/Chronicle.js`
```javascript
import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { ScrollText, BookOpen, Banknote, Target, Sparkles, Loader2, TrendingUp } from "lucide-react";
import { API } from "../App";

const fmtDate = (iso) => {
  try { return new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }); }
  catch { return ""; }
};

export default function Chronicle() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/chronicle`);
      setEntries(r.data);
    } catch (e) { /* silent */ } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const totalCollected = entries.reduce((a, e) => a + Number(e.amount || 0), 0);

  return (
    <div className="chronicle-wrap">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><BookOpen size={18} /> Outcome Ledger</div>
          <p>Every completed mission is recorded here as verified proof. The Chronicle distils a reusable lesson from each win — and ACASO feeds these lessons back into every new directive it compiles.</p>
        </div>
        <div className="chr-hero-stats">
          <div className="chr-stat"><span className="v">{entries.length}</span><span className="l">Missions Closed</span></div>
          <div className="chr-stat gold"><span className="v">${totalCollected.toLocaleString()}</span><span className="l">Total Collected</span></div>
        </div>
      </div>

      {loading ? (
        <div className="chr-loading"><Loader2 className="spin" size={20} /> Reading the Chronicle…</div>
      ) : entries.length === 0 ? (
        <div className="chr-empty">
          <ScrollText size={28} />
          <p>No completed missions yet. Finish a mission on the Sovereign Home board (run every step) and its outcome + learned lesson will be inscribed here.</p>
        </div>
      ) : (
        <div className="chr-timeline">
          {entries.map((e, i) => (
            <motion.div
              key={e.id}
              className="chr-entry"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <div className="chr-node"><TrendingUp size={14} /></div>
              <div className="chr-card">
                <div className="chr-card-top">
                  <span className={`m-mode mode-${e.mode}`}>{e.mode}</span>
                  <span className="chr-date">{fmtDate(e.completed_at)}</span>
                </div>
                <h3>{e.title}</h3>
                <div className="chr-metrics">
                  <span><Banknote size={13} /> ${Number(e.amount).toLocaleString()}</span>
                  <span><Target size={13} /> {e.outcome_metric || "outcome verified"}</span>
                </div>
                <div className="chr-lesson">
                  <Sparkles size={13} /> <b>Lesson learned:</b> {e.lesson}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

```


### `frontend/src/components/BugBounty.js`
```javascript
import React, { useEffect, useState, useCallback, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldAlert, Send, Loader2, Zap, Play, CheckCircle2, Circle, Trash2,
  Bug, Crosshair, FileText, ChevronDown, ChevronUp, ShieldCheck, Banknote,
  Target, Activity, AlertTriangle, Radar, Users, Crown, Eye, Cpu, Flame,
  GitPullRequest, Copy, Scale, MessagesSquare, Paperclip, Upload, Download, Image as ImageIcon
} from "lucide-react";
import { API } from "../App";

const fmtBytes = (n) => {
  if (!n && n !== 0) return "";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
};

function AttachmentsPanel({ mid }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/missions/${mid}/attachments`);
      setItems(r.data);
    } catch (e) { console.error(e); } finally { setLoading(false); }
  }, [mid]);

  useEffect(() => { refresh(); }, [refresh]);

  const onPick = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      await axios.post(`${API}/missions/${mid}/attachments`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success(`Uploaded ${file.name}`);
      await refresh();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  const download = (fid) => {
    window.open(`${API}/attachments/${fid}/download`, "_blank", "noopener");
  };

  const remove = async (fid) => {
    try { await axios.delete(`${API}/attachments/${fid}`); await refresh(); toast("Attachment removed"); }
    catch { toast.error("Delete failed"); }
  };

  return (
    <div className="attach" data-testid={`attachments-${mid}`}>
      <div className="attach-head">
        <Paperclip size={13} /> Evidence & Media
        <span className="attach-sub">real object storage · images · pdf · logs · text</span>
        <button
          className="attach-add"
          data-testid={`attachment-upload-${mid}`}
          onClick={() => inputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? <Loader2 className="spin" size={13} /> : <Upload size={13} />}
          {uploading ? "Uploading…" : "Upload"}
        </button>
        <input
          ref={inputRef}
          data-testid={`attachment-file-input-${mid}`}
          type="file"
          accept=".jpg,.jpeg,.png,.gif,.webp,.pdf,.json,.csv,.txt,.log,.har,.md"
          style={{ display: "none" }}
          onChange={onPick}
        />
      </div>
      {loading ? (
        <div className="attach-empty"><Loader2 className="spin" size={14} /> Loading…</div>
      ) : items.length === 0 ? (
        <div className="attach-empty">No files yet — attach real evidence the Soul Council can read.</div>
      ) : (
        <div className="attach-list">
          {items.map((a) => {
            const isImg = (a.content_type || "").startsWith("image/");
            return (
              <div key={a.id} className="attach-row" data-testid={`attachment-row-${a.id}`}>
                <span className="attach-icon">{isImg ? <ImageIcon size={14} /> : <FileText size={14} />}</span>
                <span className="attach-name" title={a.original_filename}>{a.original_filename}</span>
                <span className="attach-size">{fmtBytes(a.size)}</span>
                <button className="attach-btn" data-testid={`attachment-download-${a.id}`} onClick={() => download(a.id)} title="Download">
                  <Download size={13} />
                </button>
                <button className="attach-btn danger" data-testid={`attachment-delete-${a.id}`} onClick={() => remove(a.id)} title="Delete">
                  <Trash2 size={13} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

const SOUL_ICON = { vision: Eye, fusion: Cpu, rebirth: Flame };
const SOUL_COLOR = { vision: "#4fd1ff", fusion: "#8b7cff", rebirth: "#ff7a90" };

const PLATFORMS = ["Auto", "HackerOne", "Bugcrowd", "Intigriti", "Self-hosted VDP"];
const BB_STAGES = ["Program", "Recon", "Vuln Found", "PoC", "Disclosure", "Triage", "Payout"];
const SAMPLES = [
  "Find and responsibly disclose an IDOR on a fintech API and collect the bounty",
  "Hunt a stored XSS on a SaaS dashboard within an authorized HackerOne program",
  "Report an SSRF on a cloud provider's metadata endpoint for a Critical payout",
  "Discover a broken-auth flaw on a public VDP and get it triaged & paid",
];
const SEV_COLOR = { Critical: "#ff5470", High: "#f5843c", Medium: "#f5c451", Low: "#4fd1ff", Info: "#9aa0c8" };

const fmtTime = (iso) => { try { return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }); } catch { return ""; } };

function ReportView({ text }) {
  if (!text) return null;
  const lines = text.split("\n");
  return (
    <div className="bb-report">
      {lines.map((ln, i) => {
        const t = ln.trim();
        if (t.startsWith("## ")) return <h4 key={i}>{t.replace(/^##\s*/, "")}</h4>;
        if (t.startsWith("# ")) return <h3 key={i}>{t.replace(/^#\s*/, "")}</h3>;
        if (!t) return <div key={i} className="bb-gap" />;
        return <p key={i}>{t}</p>;
      })}
    </div>
  );
}

export default function BugBounty() {
  const [directive, setDirective] = useState("");
  const [platform, setPlatform] = useState("Auto");
  const [missions, setMissions] = useState([]);
  const [feed, setFeed] = useState([]);
  const [compiling, setCompiling] = useState(false);
  const [runningId, setRunningId] = useState(null);
  const [gate, setGate] = useState({});      // mid -> step title awaiting approval
  const [openReport, setOpenReport] = useState({});
  const [deploying, setDeploying] = useState(null);
  const [openCouncil, setOpenCouncil] = useState({});
  const [openDebate, setOpenDebate] = useState({});
  const runningRef = useRef(false);

  const load = useCallback(async () => {
    try {
      const [m, f] = await Promise.all([
        axios.get(`${API}/missions?kind=bugbounty`),
        axios.get(`${API}/action-feed?limit=40`),
      ]);
      setMissions(m.data);
      const ids = new Set(m.data.map((x) => x.id));
      setFeed(f.data.filter((x) => ids.has(x.mission_id)));
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const compile = async () => {
    if (!directive.trim()) { toast.error("Enter a security directive"); return; }
    setCompiling(true);
    try {
      const body = { directive, platform: platform === "Auto" ? null : platform };
      const r = await axios.post(`${API}/compile-bounty`, body);
      toast.success(`Engagement compiled: ${r.data.title}`);
      setDirective("");
      await load();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Compilation failed");
    } finally { setCompiling(false); }
  };

  const step = async (mid, approved) => {
    const r = await axios.post(`${API}/missions/${mid}/execute-step`, { approved });
    return r.data;
  };

  const autoRun = async (m, approved = false) => {
    if (runningRef.current) return;
    runningRef.current = true;
    setRunningId(m.id);
    setGate((g) => ({ ...g, [m.id]: null }));
    try {
      for (let i = 0; i < m.steps.length + 2; i++) {
        const data = await step(m.id, approved);
        await load();
        if (!data.log) break;
        if (data.log.status === "approval_required") {
          setGate((g) => ({ ...g, [m.id]: data.log.step_title }));
          toast.warning(`Owner sign-off required: "${data.log.step_title}"`);
          break;
        }
        await new Promise((res) => setTimeout(res, 650));
        const done = (await axios.get(`${API}/missions/${m.id}`)).data;
        if (done.status === "complete") { await load(); break; }
      }
    } catch (e) {
      toast.error("Run interrupted");
    } finally {
      runningRef.current = false;
      setRunningId(null);
    }
  };

  const approveContinue = async (m) => {
    setGate((g) => ({ ...g, [m.id]: null }));
    const fresh = (await axios.get(`${API}/missions/${m.id}`)).data;
    await autoRun(fresh, true);
    toast.success("Owner approved — disclosure authorized");
  };

  const remove = async (mid) => {
    try { await axios.delete(`${API}/missions/${mid}`); await load(); toast("Engagement archived"); }
    catch (e) { toast.error("Failed"); }
  };

  const deploySouls = async (mid) => {
    setDeploying(mid);
    try {
      await axios.post(`${API}/missions/${mid}/deploy-souls`);
      setOpenCouncil((o) => ({ ...o, [mid]: true }));
      toast.success("Soul Council convened — Eternal Throne delivered the verdict");
      await load();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Council failed");
    } finally { setDeploying(null); }
  };

  const money = (n) => `$${Number(n || 0).toLocaleString()}`;
  const stageIdx = (m) => Math.max(0, BB_STAGES.indexOf(m.stage));

  return (
    <div className="bb-wrap">
      <section className="bb-console">
        <div className="bb-head">
          <ShieldAlert size={17} /> <span>Bug Bounty Directive</span>
          <em>Authorized, in-scope security research — directive to bounty payout.</em>
        </div>
        <div className="dc-input">
          <textarea
            data-testid="bounty-input"
            value={directive}
            onChange={(e) => setDirective(e.target.value)}
            placeholder="e.g. Find and responsibly disclose an IDOR on a fintech API and collect the bounty"
            rows={2}
          />
          <button data-testid="bounty-compile" className="compile red" onClick={compile} disabled={compiling}>
            {compiling ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
            {compiling ? "Compiling…" : "Compile Engagement"}
          </button>
        </div>
        <div className="mode-row">
          {PLATFORMS.map((p) => (
            <button key={p} className={platform === p ? "mode active" : "mode"} onClick={() => setPlatform(p)}>
              {p}
            </button>
          ))}
        </div>
        <div className="samples">
          {SAMPLES.map((s) => <button key={s} className="sample" onClick={() => setDirective(s)}>{s}</button>)}
        </div>
        <div className="bb-ethic"><ShieldCheck size={13} /> Constitutional guardrail: in-scope assets only, non-weaponized PoCs, and mandatory owner sign-off before any disclosure or payout.</div>
      </section>

      {/* NEXUS security feed */}
      <section className="nexus" data-testid="bb-feed">
        <div className="nx-head">
          <Radar size={15} /> NEXUS Security Ops
          <span className="nx-sub">recon · scanners · report drafter</span>
          <span className={`nx-live ${runningId ? "on" : ""}`}><span className="pulse" /> {runningId ? "executing" : "idle"}</span>
        </div>
        {feed.length === 0 ? (
          <div className="nx-empty">No security actions yet. Compile an engagement and run it — NEXUS logs recon, PoC and disclosure evidence here.</div>
        ) : (
          <div className="nx-log">
            <AnimatePresence initial={false}>
              {feed.map((f) => (
                <motion.div key={f.id} className={`nx-row ${f.status}`} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} layout>
                  <span className="nx-time">{fmtTime(f.timestamp)}</span>
                  <span className={`nx-badge ${f.status}`}>{f.status === "approval_required" ? <AlertTriangle size={11} /> : <Activity size={11} />}</span>
                  <span className="nx-body"><b>{f.mission_title}</b> · {f.action}<em> ⟶ {f.evidence}</em></span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </section>

      <section className="board">
        <div className="board-head"><Bug size={16} /> Active Engagements</div>
        {missions.length === 0 ? (
          <div className="empty"><ShieldAlert size={26} /><p>No engagements yet. Issue a bug-bounty directive and ACASO compiles a full authorized engagement — program, scope, severity, non-weaponized PoC, disclosure report and payout path.</p></div>
        ) : (
          <div className="bb-grid">
            {missions.map((m) => {
              const busy = runningId === m.id;
              const undone = m.steps.filter((s) => !s.done).length;
              const gated = gate[m.id];
              return (
                <motion.div key={m.id} data-testid="bounty-card" className={`bb-card ${m.status}`} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} layout>
                  <div className="bb-card-top">
                    <span className="bb-plat">{m.platform || "VDP"}</span>
                    <span className="bb-sev" style={{ color: SEV_COLOR[m.severity] || "#9aa0c8", borderColor: SEV_COLOR[m.severity] || "#333" }}>
                      {m.severity} · CVSS {m.cvss}
                    </span>
                  </div>
                  <h3>{m.title}</h3>
                  <div className="bb-prog">{m.program}</div>
                  <div className="bb-tags">
                    <span className="bb-tag"><Crosshair size={12} /> {m.asset}</span>
                    <span className="bb-tag"><Bug size={12} /> {m.vuln_type}</span>
                  </div>
                  <p className="m-summary">{m.summary}</p>

                  {/* security pipeline */}
                  <div className="bb-pipe">
                    {BB_STAGES.map((st, i) => (
                      <div key={st} className={`bb-pnode ${i <= stageIdx(m) ? "lit" : ""} ${m.stage === st ? "cur" : ""}`}>
                        <span className="bb-pdot" />
                        <span className="bb-plabel">{st}</span>
                      </div>
                    ))}
                  </div>

                  <div className="m-steps">
                    {m.steps.map((s) => (
                      <div key={s.id} className={`step ${s.done ? "done" : ""} ${busy && !s.done ? "pending" : ""}`} title={s.detail}>
                        {s.done ? <CheckCircle2 size={15} /> : (busy ? <Loader2 className="spin" size={15} /> : <Circle size={15} />)}
                        <span>{s.title}</span>
                      </div>
                    ))}
                  </div>

                  {gated && (
                    <div className="bb-gate">
                      <AlertTriangle size={14} /> Owner sign-off required at “{gated}”
                      <button data-testid="approve-btn" onClick={() => approveContinue(m)}>
                        <ShieldCheck size={14} /> Approve &amp; Continue
                      </button>
                    </div>
                  )}

                  {m.status !== "complete" && !gated && (
                    <div className="m-run">
                      <button className="run" onClick={() => autoRun(m, false)} disabled={busy || undone === 0}>
                        {busy ? <Loader2 className="spin" size={14} /> : <Play size={14} />} Run Engagement
                      </button>
                    </div>
                  )}

                  <div className="bb-meta">
                    <span><Banknote size={13} /> {m.payment_path}</span>
                    <span><Target size={13} /> {m.outcome_metric}</span>
                  </div>

                  <button className="bb-report-toggle" onClick={() => setOpenReport((o) => ({ ...o, [m.id]: !o[m.id] }))}>
                    <FileText size={14} /> Responsible Disclosure Report {openReport[m.id] ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                  {openReport[m.id] && <ReportView text={m.report} />}

                  <AttachmentsPanel mid={m.id} />

                  {/* Soul Council */}
                  <div className="bb-soul-bar">
                    <button
                      data-testid="deploy-souls"
                      className="deploy-souls"
                      onClick={() => deploySouls(m.id)}
                      disabled={deploying === m.id}
                    >
                      {deploying === m.id ? <Loader2 className="spin" size={15} /> : <Users size={15} />}
                      {deploying === m.id ? "Souls convening…" : (m.soul_council ? "Re-convene Soul Council" : "Deploy Soul Council")}
                    </button>
                    {m.soul_council && (
                      <button className="council-toggle" onClick={() => setOpenCouncil((o) => ({ ...o, [m.id]: !o[m.id] }))}>
                        {openCouncil[m.id] ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                      </button>
                    )}
                  </div>

                  {m.soul_council && openCouncil[m.id] && (
                    <motion.div className="council" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}>
                      <div className="council-head"><Users size={13} /> Soul Council — {m.soul_council.souls.filter((s) => s.ok).length} souls across {new Set(m.soul_council.souls.filter((s)=>s.ok).map((s)=>s.provider)).size} AI models</div>
                      <div className="souls-grid">
                        {m.soul_council.souls.map((s) => {
                          const Icon = SOUL_ICON[s.id] || Users;
                          return (
                            <div key={s.id} className={`soul ${s.ok ? "" : "down"}`} style={{ borderColor: SOUL_COLOR[s.id] + "55" }}>
                              <div className="soul-h" style={{ color: SOUL_COLOR[s.id] }}>
                                <Icon size={14} /> {s.name}
                                <span className="soul-model">{s.model_label}</span>
                              </div>
                              <div className="soul-role">{s.role}</div>
                              <p>{s.analysis}</p>
                              {s.rebuttal && (
                                <div className="soul-rebut">
                                  <span className="soul-rebut-tag" style={{ color: SOUL_COLOR[s.id], borderColor: SOUL_COLOR[s.id] + "88" }}>
                                    <MessagesSquare size={10} /> Round 2 · Rebuttal
                                  </span>
                                  <p>{s.rebuttal}</p>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>

                      {m.soul_council.souls.some((s) => s.rebuttal) && (
                        <div className="debate" data-testid={`soul-debate-${m.id}`}>
                          <button
                            className="debate-toggle"
                            data-testid={`soul-debate-toggle-${m.id}`}
                            onClick={() => setOpenDebate((o) => ({ ...o, [m.id]: !o[m.id] }))}
                          >
                            <MessagesSquare size={13} />
                            {openDebate[m.id] ? "Hide Debate Transcript" : "Show Debate Transcript"}
                            <span className="debate-count">
                              {m.soul_council.souls.filter((s) => s.rebuttal).length} rebuttals
                            </span>
                            {openDebate[m.id] ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                          </button>
                          {openDebate[m.id] && (
                            <div className="debate-body">
                              {["round-1", "round-2"].map((round) => (
                                <div key={round} className="debate-round">
                                  <div className="debate-round-h">
                                    {round === "round-1" ? "Round 1 · Opening Analyses" : "Round 2 · Cross-Rebuttals"}
                                  </div>
                                  {m.soul_council.souls.filter((s) => s.ok).map((s) => {
                                    const text = round === "round-1" ? s.analysis : s.rebuttal;
                                    if (!text) return null;
                                    return (
                                      <div key={s.id + round} className="debate-msg" style={{ borderLeftColor: SOUL_COLOR[s.id] }}>
                                        <span className="debate-who" style={{ color: SOUL_COLOR[s.id] }}>{s.name}</span>
                                        <span className="debate-model">{s.model_label}</span>
                                        <p>{text}</p>
                                      </div>
                                    );
                                  })}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      <div className="throne">
                        <div className="throne-h"><Crown size={15} /> Eternal Throne · Soul Brain Verdict
                          <span className="throne-status">{m.soul_council.resolution.status}</span>
                        </div>
                        <div className="throne-row"><b>Root cause</b><span>{m.soul_council.resolution.root_cause}</span></div>
                        <div className="throne-row"><b>The fix</b><span>{m.soul_council.resolution.fix}</span></div>
                        <div className="throne-row"><b>Verify</b><span>{m.soul_council.resolution.verification}</span></div>
                        <div className="throne-conf">
                          <span>Confidence</span>
                          <div className="conf-bar"><div style={{ width: `${m.soul_council.resolution.confidence}%` }} /></div>
                          <span className="conf-num">{m.soul_council.resolution.confidence}%</span>
                        </div>
                      </div>

                      {Array.isArray(m.soul_council.resolution.dissent) && m.soul_council.resolution.dissent.length > 0 && (
                        <div className="dissent" data-testid={`soul-dissent-${m.id}`}>
                          <div className="dissent-h"><Scale size={14} /> Soul Dissent & Reconciliation</div>
                          {m.soul_council.resolution.dissent.map((d, i) => {
                            const positions = d.positions || {};
                            return (
                              <div key={i} className="dissent-item">
                                <div className="dissent-topic">{d.topic || "Point of tension"}</div>
                                <div className="dissent-positions">
                                  {["vision", "fusion", "rebirth"].map((sid) => positions[sid] ? (
                                    <div key={sid} className="dissent-pos" style={{ borderLeftColor: SOUL_COLOR[sid] }}>
                                      <span className="dissent-soul" style={{ color: SOUL_COLOR[sid] }}>
                                        {sid === "vision" ? "Vision Command" : sid === "fusion" ? "Fusion Engine" : "Rebirth Protocol"}
                                      </span>
                                      <span>{positions[sid]}</span>
                                    </div>
                                  ) : null)}
                                </div>
                                {d.reconciliation && (
                                  <div className="dissent-reco"><Crown size={12} /> <span><b>Throne reconciled:</b> {d.reconciliation}</span></div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {m.soul_council.resolution.patch_note && (
                        <div className="fix-export" data-testid={`fix-export-${m.id}`}>
                          <div className="fx-h">
                            <GitPullRequest size={14} /> Fix Export · PR-Ready Patch Note
                            <button
                              className="fx-copy"
                              data-testid={`fix-export-copy-${m.id}`}
                              onClick={async () => {
                                try {
                                  await navigator.clipboard.writeText(m.soul_council.resolution.patch_note);
                                  toast.success("Patch note copied — paste into your PR");
                                } catch {
                                  toast.error("Copy failed — select and copy manually");
                                }
                              }}
                            >
                              <Copy size={12} /> Copy
                            </button>
                          </div>
                          <pre className="fx-body">{m.soul_council.resolution.patch_note}</pre>
                        </div>
                      )}
                    </motion.div>
                  )}

                  <div className="m-foot">
                    <span className="m-amount">{money(m.amount)}</span>
                    <span className={`m-status s-${m.status}`}>{m.status === "complete" ? "PAID" : m.stage}</span>
                    <div className="m-actions"><button onClick={() => remove(m.id)} title="Archive"><Trash2 size={16} /></button></div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

```


### `frontend/src/components/AgentBridge.js`
```javascript
import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  Plug, KeyRound, RefreshCw, Copy, Check, Terminal, Bot, Play, Loader2,
  Radio, Braces, ShieldCheck
} from "lucide-react";
import { API } from "../App";

const BACKEND = process.env.REACT_APP_BACKEND_URL;

function Copyable({ label, value, testid }) {
  const [done, setDone] = useState(false);
  const copy = async () => {
    try { await navigator.clipboard.writeText(value); setDone(true); setTimeout(() => setDone(false), 1500); }
    catch { toast.error("Copy failed"); }
  };
  return (
    <button className="copy-block" onClick={copy} data-testid={testid} title="Copy">
      <span className="cb-label">{label}</span>
      <span className="cb-val">{value}</span>
      <span className="cb-icon">{done ? <Check size={15} /> : <Copy size={15} />}</span>
    </button>
  );
}

export default function AgentBridge() {
  const [info, setInfo] = useState(null);
  const [activity, setActivity] = useState([]);
  const [tab, setTab] = useState("gemini");
  const [pgDirective, setPgDirective] = useState("Land a $500 landing-page copywriting client and collect payment");
  const [pgKind, setPgKind] = useState("revenue");
  const [pgOut, setPgOut] = useState(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [i, a] = await Promise.all([
        axios.get(`${API}/bridge/info`),
        axios.get(`${API}/bridge/activity?limit=25`),
      ]);
      setInfo(i.data);
      setActivity(a.data);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const regenerate = async () => {
    try { const r = await axios.post(`${API}/bridge/regenerate`); setInfo((p) => ({ ...p, api_key: r.data.api_key })); toast.success("New API key minted"); }
    catch (e) { toast.error("Failed"); }
  };

  const key = info?.api_key || "…";
  const base = `${BACKEND}/api/agent`;

  const curlSnippet = `curl -X POST ${base}/directive \\
  -H "Content-Type: application/json" \\
  -H "X-ACASO-Key: ${key}" \\
  -d '{"directive":"Land a $500 client and collect payment","kind":"revenue","agent":"Manus"}'`;

  const toolSchema = {
    name: "acaso_issue_directive",
    description: "Send a plain-language money-making directive to the ACASO Directive-to-Payment OS. ACASO compiles it into a mission graph (steps, evidence, payment path) and can execute it. Use kind='bugbounty' for authorized security research.",
    parameters: {
      type: "object",
      properties: {
        directive: { type: "string", description: "The outcome to achieve, ending in a payment." },
        kind: { type: "string", enum: ["revenue", "bugbounty"], description: "Mission type." },
        mode: { type: "string", enum: ["Make", "Find", "Move", "Collect"], description: "Operating mode (revenue only)." },
        platform: { type: "string", description: "Bug bounty platform (bugbounty only): HackerOne, Bugcrowd, Intigriti, Self-hosted VDP." },
        agent: { type: "string", description: "Your agent name, e.g. Gemini or Manus." },
      },
      required: ["directive"],
    },
  };

  const geminiConfig = JSON.stringify({
    tools: [{ function_declarations: [toolSchema] }],
    _endpoint: `${base}/directive`,
    _auth_header: { "X-ACASO-Key": key },
  }, null, 2);

  const openaiConfig = JSON.stringify({
    tools: [{ type: "function", function: toolSchema }],
    _endpoint: `${base}/directive`,
    _auth_header: { "X-ACASO-Key": key },
  }, null, 2);

  const manusConfig = JSON.stringify({
    name: "ACASO Directive-to-Payment",
    base_url: base,
    auth: { header: "X-ACASO-Key", value: key },
    actions: {
      issue_directive: { method: "POST", path: "/directive", body: { directive: "string", kind: "revenue|bugbounty", agent: "string" } },
      list_missions: { method: "GET", path: "/missions" },
      get_mission: { method: "GET", path: "/missions/{id}" },
      run_mission: { method: "POST", path: "/missions/{id}/run", body: { run: "next|all", approved: "boolean" } },
    },
  }, null, 2);

  const configs = { gemini: geminiConfig, openai: openaiConfig, manus: manusConfig, curl: curlSnippet };
  const copyConfig = async () => {
    try { await navigator.clipboard.writeText(configs[tab]); toast.success("Connector copied"); }
    catch { toast.error("Copy failed"); }
  };

  const runPlayground = async () => {
    setBusy(true); setPgOut(null);
    try {
      const r = await axios.post(`${API}/agent/directive`, {
        directive: pgDirective, kind: pgKind, agent: "Playground",
      }, { headers: { "X-ACASO-Key": key } });
      setPgOut(r.data);
      toast.success(`Mission created: ${r.data.title}`);
      await load();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Bridge call failed");
    } finally { setBusy(false); }
  };

  const fmt = (iso) => { try { return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }); } catch { return ""; } };

  return (
    <div className="bridge-wrap">
      <div className="br-hero">
        <div>
          <div className="br-title"><Plug size={18} /> Agent Bridge</div>
          <p>Let external agents — <b>Manus</b>, <b>Gemini</b>, <b>ChatGPT</b> — drive ACASO. They send directives and run missions through one authenticated API. Paste a connector below into your agent's tool config.</p>
        </div>
        <div className="br-live"><Radio size={14} /> Bridge online</div>
      </div>

      <div className="br-grid">
        <div className="br-col">
          <div className="br-card">
            <div className="br-card-h"><KeyRound size={15} /> Credentials <button className="br-regen" onClick={regenerate} data-testid="regen-key"><RefreshCw size={13} /> Regenerate</button></div>
            <Copyable label="API Key" value={key} testid="api-key" />
            <Copyable label="Auth Header" value={`X-ACASO-Key: ${key}`} />
            <Copyable label="Base URL" value={base} />
          </div>

          <div className="br-card">
            <div className="br-card-h"><Braces size={15} /> Connector / Tool Schema</div>
            <div className="br-conn-tabs">
              {[["gemini", "Gemini"], ["openai", "OpenAI / ChatGPT"], ["manus", "Manus / MCP"], ["curl", "cURL"]].map(([k, l]) => (
                <button key={k} className={tab === k ? "ct on" : "ct"} onClick={() => setTab(k)}>{l}</button>
              ))}
            </div>
            <pre className="br-code" data-testid="connector-code">{configs[tab]}</pre>
            <button className="br-copy" onClick={copyConfig}><Copy size={14} /> Copy connector</button>
          </div>
        </div>

        <div className="br-col">
          <div className="br-card">
            <div className="br-card-h"><Terminal size={15} /> Live Playground <span className="br-hint">acts as an external agent</span></div>
            <textarea className="br-pg-input" value={pgDirective} onChange={(e) => setPgDirective(e.target.value)} rows={2} data-testid="pg-input" />
            <div className="br-pg-row">
              <div className="br-kind">
                <button className={pgKind === "revenue" ? "on" : ""} onClick={() => setPgKind("revenue")}>Revenue</button>
                <button className={pgKind === "bugbounty" ? "on" : ""} onClick={() => setPgKind("bugbounty")}>Bug Bounty</button>
              </div>
              <button className="br-run" onClick={runPlayground} disabled={busy} data-testid="pg-run">
                {busy ? <Loader2 className="spin" size={15} /> : <Play size={15} />} Send via Bridge
              </button>
            </div>
            {pgOut && (
              <motion.div className="br-pg-out" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <div className="br-ok"><Check size={13} /> 200 · mission created</div>
                <div className="br-pg-title">{pgOut.title}</div>
                <div className="br-pg-sub">{pgOut.kind} · ${Number(pgOut.amount).toLocaleString()} · {pgOut.steps.length} steps</div>
              </motion.div>
            )}
          </div>

          <div className="br-card">
            <div className="br-card-h"><Bot size={15} /> External Agent Activity</div>
            {activity.length === 0 ? (
              <div className="nx-empty">No external calls yet. Run the playground or call the API from Manus/Gemini.</div>
            ) : (
              <div className="br-activity">
                {activity.map((a) => (
                  <div key={a.id} className="br-act-row">
                    <span className="br-agent">{a.agent}</span>
                    <span className="br-act">{a.action}</span>
                    <span className="br-detail">{a.detail}</span>
                    <span className="br-time">{fmt(a.timestamp)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="br-foot-note"><ShieldCheck size={13} /> Every bridge call is key-authenticated and recorded in the activity ledger. Regenerate the key to instantly revoke external access.</div>
    </div>
  );
}

```


### `frontend/src/components/FileAnalyzer.js`
```javascript
import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  FolderUp, FilePlus, Loader2, Sparkles, Trash2, Download, FileText,
  Image as ImageIcon, Play, X, Plus, HardDriveUpload, Files, Boxes,
  MessagesSquare, Send, Cloud, FolderOpen, ChevronRight, Check, Unplug, Folder
} from "lucide-react";
import { API } from "../App";

const fmtBytes = (n) => {
  if (!n && n !== 0) return "";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
};

export function Markdown({ text, onCite }) {
  if (!text) return null;
  const CITE = /^([A-Za-z0-9_.\/-]+\.[A-Za-z0-9]+):(\d+)(?:-(\d+))?$/;
  const inline = (t) => {
    const nodes = [];
    const re = /(\*\*([^*]+)\*\*|`([^`]+)`)/g;
    let last = 0, m, i = 0;
    while ((m = re.exec(t)) !== null) {
      if (m.index > last) nodes.push(t.slice(last, m.index));
      if (m[2] !== undefined) {
        nodes.push(<strong key={`b${i++}`}>{m[2]}</strong>);
      } else if (m[3] !== undefined) {
        const cm = onCite && m[3].match(CITE);
        if (cm) {
          const path = cm[1], line = parseInt(cm[2], 10);
          nodes.push(
            <button key={`cite${i++}`} className="fa-cite" onClick={() => onCite(path, line)} title="Open and highlight this line">
              {m[3]}
            </button>
          );
        } else {
          nodes.push(<code key={`c${i++}`}>{m[3]}</code>);
        }
      }
      last = m.index + m[0].length;
    }
    if (last < t.length) nodes.push(t.slice(last));
    return nodes;
  };
  const blocks = text.split(/```/);
  return (
    <div className="fa-md">
      {blocks.map((blk, bi) => {
        if (bi % 2 === 1) return <pre key={bi} className="fa-code">{blk.replace(/^\w+\n/, "")}</pre>;
        return blk.split("\n").map((ln, i) => {
          const t = ln.trim();
          const k = `${bi}-${i}`;
          if (!t) return <div key={k} className="fa-gap" />;
          if (t.startsWith("### ")) return <h5 key={k}>{inline(t.replace(/^###\s*/, ""))}</h5>;
          if (t.startsWith("## ")) return <h4 key={k}>{inline(t.replace(/^##\s*/, ""))}</h4>;
          if (t.startsWith("# ")) return <h3 key={k}>{inline(t.replace(/^#\s*/, ""))}</h3>;
          if (t.startsWith("- ") || t.startsWith("* ")) return <li key={k}>{inline(t.replace(/^[-*]\s*/, ""))}</li>;
          return <p key={k}>{inline(t)}</p>;
        });
      })}
    </div>
  );
}

export default function FileAnalyzer() {
  const [sets, setSets] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState({ done: 0, total: 0 });
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [chat, setChat] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatSending, setChatSending] = useState(false);
  // Google Drive
  const [drive, setDrive] = useState({ configured: false, connected: false, email: null });
  const [driveOpen, setDriveOpen] = useState(false);
  const [driveItems, setDriveItems] = useState([]);
  const [driveCrumbs, setDriveCrumbs] = useState([{ id: "root", name: "My Drive" }]);
  const [driveSel, setDriveSel] = useState([]);
  const [driveLoading, setDriveLoading] = useState(false);
  const [driveImporting, setDriveImporting] = useState(false);
  const [driveSearch, setDriveSearch] = useState("");
  const [viewer, setViewer] = useState(null); // { path, line, content, loading }
  const filesInput = useRef(null);
  const folderInput = useRef(null);

  const loadSets = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/filesets`);
      setSets(r.data);
      if (!activeId && r.data.length) setActiveId(r.data[0].id);
    } catch (e) { console.error(e); }
  }, [activeId]);

  useEffect(() => { loadSets(); }, [loadSets]);

  const loadFiles = useCallback(async (id) => {
    if (!id) { setFiles([]); return; }
    try {
      const [f, a] = await Promise.all([
        axios.get(`${API}/filesets/${id}/files`),
        axios.get(`${API}/filesets/${id}/analyses`),
      ]);
      setFiles(f.data);
      setAnalysis(a.data?.[0] || null);
      try { const c = await axios.get(`${API}/filesets/${id}/chat`); setChat(c.data || []); }
      catch { setChat([]); }
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { loadFiles(activeId); }, [activeId, loadFiles]);

  const ensureSet = async () => {
    if (activeId) return activeId;
    const r = await axios.post(`${API}/filesets`, { title: `Analysis ${new Date().toLocaleString()}` });
    setActiveId(r.data.id);
    await loadSets();
    return r.data.id;
  };

  const newSet = async () => {
    const r = await axios.post(`${API}/filesets`, { title: `Analysis ${new Date().toLocaleString()}` });
    setActiveId(r.data.id);
    setAnalysis(null);
    setFiles([]);
    setChat([]);
    await loadSets();
    toast.success("New analysis set created");
  };

  const handlePicked = async (fileList) => {
    const arr = Array.from(fileList || []);
    if (!arr.length) return;
    const id = await ensureSet();
    setUploading(true);
    setProgress({ done: 0, total: arr.length });
    let ok = 0, fail = 0;
    for (let i = 0; i < arr.length; i++) {
      const file = arr[i];
      const rel = file.webkitRelativePath || file.name;
      try {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("rel_path", rel);
        await axios.post(`${API}/filesets/${id}/files`, fd, { headers: { "Content-Type": "multipart/form-data" } });
        ok += 1;
      } catch (e) { fail += 1; }
      setProgress({ done: i + 1, total: arr.length });
    }
    setUploading(false);
    await loadFiles(id);
    await loadSets();
    if (ok) toast.success(`Imported ${ok} file${ok > 1 ? "s" : ""}${fail ? ` · ${fail} skipped` : ""}`);
    else toast.error("No files imported (unsupported types or too large)");
  };

  const remove = async (fid) => {
    try { await axios.delete(`${API}/files/${fid}`); await loadFiles(activeId); await loadSets(); toast("File removed"); }
    catch { toast.error("Delete failed"); }
  };

  const download = (fid) => window.open(`${API}/files/${fid}/download`, "_blank", "noopener");

  const analyze = async (fsid, q) => {
    const id = (typeof fsid === "string" && fsid) ? fsid : activeId;
    if (!id) { toast.error("Upload files first"); return; }
    setAnalyzing(true);
    try {
      const question_ = (q !== undefined && q !== null) ? q : (question.trim() || null);
      const r = await axios.post(`${API}/filesets/${id}/analyze`, { question: question_ });
      setAnalysis(r.data);
      toast.success(`Analysis complete · ${r.data.model_label}`);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Analysis failed");
    } finally { setAnalyzing(false); }
  };

  const sendChat = async () => {
    const msg = chatInput.trim();
    if (!msg) return;
    if (!activeId || !files.length) { toast.error("Upload files first"); return; }
    setChatInput("");
    const now = new Date().toISOString();
    setChat((c) => [...c, { id: `tmp-${now}`, role: "user", content: msg, created_at: now }]);
    setChatSending(true);
    try {
      const r = await axios.post(`${API}/filesets/${activeId}/chat`, { message: msg });
      setChat((c) => [...c, r.data]);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Chat failed");
    } finally { setChatSending(false); }
  };

  const loadDriveStatus = useCallback(async () => {
    try { const r = await axios.get(`${API}/drive/status`); setDrive(r.data); }
    catch (e) { console.error(e); }
  }, []);

  useEffect(() => {
    loadDriveStatus();
    const params = new URLSearchParams(window.location.search);
    if (params.get("drive_connected")) {
      toast.success("Google Drive connected");
      loadDriveStatus();
      window.history.replaceState({}, "", window.location.pathname);
    } else if (params.get("drive_error")) {
      toast.error(`Drive connection failed: ${params.get("drive_error")}`);
      window.history.replaceState({}, "", window.location.pathname);
    }
  }, [loadDriveStatus]);

  const connectDrive = async () => {
    try {
      const r = await axios.get(`${API}/drive/connect`);
      window.location.href = r.data.authorization_url;
    } catch (e) { toast.error(e?.response?.data?.detail || "Cannot start Drive connect"); }
  };

  const disconnectDrive = async () => {
    try { await axios.post(`${API}/drive/disconnect`); await loadDriveStatus(); toast("Google Drive disconnected"); }
    catch { toast.error("Disconnect failed"); }
  };

  const browseFolder = async (folderId, crumbs) => {
    setDriveLoading(true);
    try {
      const r = await axios.get(`${API}/drive/list?folder_id=${encodeURIComponent(folderId)}`);
      setDriveItems(r.data.items || []);
      if (crumbs) setDriveCrumbs(crumbs);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to list Drive");
    } finally { setDriveLoading(false); }
  };

  const openDrive = async () => {
    setDriveOpen(true);
    setDriveSel([]);
    setDriveSearch("");
    setDriveCrumbs([{ id: "root", name: "My Drive" }]);
    await browseFolder("root", [{ id: "root", name: "My Drive" }]);
  };

  const searchDrive = async (term) => {
    const t = (term ?? driveSearch).trim();
    if (!t) { const cur = driveCrumbs[driveCrumbs.length - 1]; browseFolder(cur.id, driveCrumbs); return; }
    setDriveLoading(true);
    try {
      const r = await axios.get(`${API}/drive/list?search=${encodeURIComponent(t)}`);
      setDriveItems(r.data.items || []);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Drive search failed");
    } finally { setDriveLoading(false); }
  };

  const clearSearch = () => {
    setDriveSearch("");
    const cur = driveCrumbs[driveCrumbs.length - 1];
    browseFolder(cur.id, driveCrumbs);
  };

  const enterFolder = (item) => {
    setDriveSearch("");
    const crumbs = [...driveCrumbs, { id: item.id, name: item.name }];
    browseFolder(item.id, crumbs);
  };

  const gotoCrumb = (idx) => {
    setDriveSearch("");
    const crumbs = driveCrumbs.slice(0, idx + 1);
    browseFolder(crumbs[crumbs.length - 1].id, crumbs);
  };

  const toggleDriveSel = (id) => setDriveSel((s) => s.includes(id) ? s.filter((x) => x !== id) : [...s, id]);

  const importDrive = async () => {
    if (!driveSel.length) { toast.error("Select at least one file"); return; }
    setDriveImporting(true);
    try {
      const r = await axios.post(`${API}/drive/import`, { file_ids: driveSel, fileset_id: activeId });
      setActiveId(r.data.fileset_id);
      await loadSets();
      await loadFiles(r.data.fileset_id);
      const imp = r.data.imported?.length || 0;
      const skp = r.data.skipped?.length || 0;
      toast.success(`Imported ${imp} file${imp !== 1 ? "s" : ""} from Drive${skp ? ` · ${skp} skipped` : ""}`);
      setDriveOpen(false);
      setDriveSel([]);
      if (imp > 0) { toast("Auto-analyzing imported files…"); analyze(r.data.fileset_id, null); }
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Drive import failed");
    } finally { setDriveImporting(false); }
  };

  const importFolder = async () => {
    const folder = driveCrumbs[driveCrumbs.length - 1];
    setDriveImporting(true);
    try {
      const r = await axios.post(`${API}/drive/import-folder`, { folder_id: folder.id, fileset_id: activeId, recursive: true });
      setActiveId(r.data.fileset_id);
      await loadSets();
      await loadFiles(r.data.fileset_id);
      const imp = r.data.imported?.length || 0;
      const skp = r.data.skipped?.length || 0;
      toast.success(`Imported ${imp} file${imp !== 1 ? "s" : ""} from "${folder.name}"${skp ? ` · ${skp} skipped` : ""}`);
      setDriveOpen(false); setDriveSel([]);
      if (imp > 0) { toast("Auto-analyzing imported files…"); analyze(r.data.fileset_id, null); }
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Folder import failed");
    } finally { setDriveImporting(false); }
  };

  const exportSet = () => {
    if (!activeId) { toast.error("Nothing to export yet"); return; }
    window.open(`${API}/filesets/${activeId}/export`, "_blank", "noopener");
  };

  const openCite = async (path, line) => {
    if (!activeId) return;
    setViewer({ path, line, content: null, loading: true });
    try {
      const r = await axios.get(`${API}/filesets/${activeId}/file?path=${encodeURIComponent(path)}`);
      setViewer({ path, line, content: r.data.content, loading: false });
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Could not open file");
      setViewer(null);
    }
  };

  return (
    <div className="fa-wrap" data-testid="file-analyzer">
      <section className="fa-console">
        <div className="fa-head">
          <Boxes size={17} /> <span>File Analyzer</span>
          <em>Upload files or a whole folder — real object storage, then AI analysis.</em>
        </div>
        <div className="fa-note">
          A hosted app can’t read your local drive directly (browser sandbox). Pick files or an entire folder below and ACASO imports them into real storage, then the AI reads and analyzes them.
        </div>

        <div className="fa-actions">
          <button className="fa-btn primary" data-testid="analyzer-add-files" onClick={() => filesInput.current?.click()} disabled={uploading}>
            <FilePlus size={16} /> Add Files
          </button>
          <button className="fa-btn" data-testid="analyzer-add-folder" onClick={() => folderInput.current?.click()} disabled={uploading}>
            <FolderUp size={16} /> Add Folder
          </button>
          <button className="fa-btn ghost" data-testid="analyzer-new-set" onClick={newSet} disabled={uploading}>
            <Plus size={16} /> New Set
          </button>
          <input ref={filesInput} type="file" multiple style={{ display: "none" }}
            data-testid="analyzer-files-input"
            onChange={(e) => { handlePicked(e.target.files); e.target.value = ""; }} />
          <input ref={folderInput} type="file" multiple webkitdirectory="" directory="" style={{ display: "none" }}
            data-testid="analyzer-folder-input"
            onChange={(e) => { handlePicked(e.target.files); e.target.value = ""; }} />
        </div>

        {drive.configured && (
          <div className="fa-drive" data-testid="analyzer-drive-bar">
            <Cloud size={15} />
            {drive.connected ? (
              <>
                <span className="fa-drive-on">Google Drive connected{drive.email ? ` · ${drive.email}` : ""}</span>
                <button className="fa-drive-btn" data-testid="drive-browse" onClick={openDrive}><FolderOpen size={14} /> Browse Drive</button>
                <button className="fa-drive-btn ghost" data-testid="drive-disconnect" onClick={disconnectDrive}><Unplug size={14} /> Disconnect</button>
              </>
            ) : (
              <>
                <span className="fa-drive-off">Import files straight from your Google Drive</span>
                <button className="fa-drive-btn" data-testid="drive-connect" onClick={connectDrive}><Cloud size={14} /> Connect Google Drive</button>
              </>
            )}
          </div>
        )}

        {uploading && (
          <div className="fa-prog" data-testid="analyzer-progress">
            <Loader2 className="spin" size={14} /> Importing {progress.done}/{progress.total}…
            <div className="fa-prog-bar"><div style={{ width: `${progress.total ? (progress.done / progress.total) * 100 : 0}%` }} /></div>
          </div>
        )}

        {sets.length > 1 && (
          <div className="fa-sets">
            {sets.map((s) => (
              <button key={s.id} className={s.id === activeId ? "fa-set active" : "fa-set"} onClick={() => setActiveId(s.id)}>
                <Files size={12} /> {s.title} <span>{s.file_count}</span>
              </button>
            ))}
          </div>
        )}
      </section>

      <div className="fa-grid">
        <section className="fa-files" data-testid="analyzer-file-list">
          <div className="fa-sub-head"><HardDriveUpload size={14} /> Imported Files <span className="fa-count">{files.length}</span></div>
          {files.length === 0 ? (
            <div className="fa-empty"><FolderUp size={24} /><p>No files yet. Add files or a folder to begin.</p></div>
          ) : (
            <div className="fa-list">
              {files.map((f) => {
                const isImg = (f.content_type || "").startsWith("image/");
                return (
                  <div key={f.id} className="fa-row" data-testid={`analyzer-file-${f.id}`}>
                    <span className="fa-fic">{isImg ? <ImageIcon size={14} /> : <FileText size={14} />}</span>
                    <span className="fa-fname" title={f.rel_path}>{f.rel_path}</span>
                    {!f.readable && <span className="fa-bin">binary</span>}
                    <span className="fa-fsize">{fmtBytes(f.size)}</span>
                    <button className="fa-ic" onClick={() => download(f.id)} title="Download"><Download size={13} /></button>
                    <button className="fa-ic danger" data-testid={`analyzer-delete-${f.id}`} onClick={() => remove(f.id)} title="Delete"><Trash2 size={13} /></button>
                  </div>
                );
              })}
            </div>
          )}

          <div className="fa-ask">
            <textarea
              data-testid="analyzer-question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Optional: ask a specific question about these files (e.g. 'find security risks' or 'summarize the API')"
              rows={2}
            />
            <button className="fa-analyze" data-testid="analyzer-run" onClick={() => analyze()} disabled={analyzing || !files.length}>
              {analyzing ? <Loader2 className="spin" size={16} /> : <Sparkles size={16} />}
              {analyzing ? "Analyzing…" : "Analyze with AI"}
            </button>
          </div>
        </section>

        <section className="fa-result" data-testid="analyzer-result">
          <div className="fa-sub-head"><Sparkles size={14} /> AI Analysis
            <div className="fa-head-right">
              {analysis?.model_label && <span className="fa-model">{analysis.model_label}</span>}
              {activeId && files.length > 0 && (
                <button className="fa-export" data-testid="analyzer-export" onClick={exportSet} title="Download analysis + chat as Markdown">
                  <Download size={13} /> Export
                </button>
              )}
            </div>
          </div>
          {analyzing ? (
            <div className="fa-skeleton">
              {[...Array(5)].map((_, i) => <div key={i} className="fa-sk-line" style={{ width: `${90 - i * 9}%` }} />)}
            </div>
          ) : analysis ? (
            <>
              {analysis.truncated && <div className="fa-trunc">Note: content was truncated to fit the model context window.</div>}
              {analysis.question && <div className="fa-q">Q: {analysis.question}</div>}
              <Markdown text={analysis.analysis} onCite={openCite} />
            </>
          ) : (
            <div className="fa-empty"><Play size={24} /><p>Run an analysis to see per-file notes, cross-file insights, risks and recommended actions.</p></div>
          )}
        </section>
      </div>

      <section className="fa-chat" data-testid="analyzer-chat">
        <div className="fa-sub-head"><MessagesSquare size={14} /> Follow-up Chat <span className="fa-chat-hint">ask anything about these files</span></div>
        <div className="fa-chat-log" data-testid="analyzer-chat-log">
          {chat.length === 0 ? (
            <div className="fa-chat-empty">Upload files, then ask follow-up questions here. Answers are grounded in your files.</div>
          ) : (
            chat.map((m) => (
              <div key={m.id} className={`fa-msg ${m.role}`} data-testid={`analyzer-chat-msg-${m.role}`}>
                <span className="fa-msg-who">{m.role === "user" ? "You" : "ACASO"}</span>
                <div className="fa-msg-body"><Markdown text={m.content} onCite={openCite} /></div>
              </div>
            ))
          )}
          {chatSending && <div className="fa-msg assistant"><span className="fa-msg-who">ACASO</span><div className="fa-msg-body"><Loader2 className="spin" size={14} /> thinking...</div></div>}
        </div>
        <div className="fa-chat-input">
          <input
            data-testid="analyzer-chat-input"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendChat(); } }}
            placeholder="Ask a follow-up about your files..."
            disabled={chatSending || !files.length}
          />
          <button data-testid="analyzer-chat-send" onClick={sendChat} disabled={chatSending || !files.length || !chatInput.trim()}>
            {chatSending ? <Loader2 className="spin" size={15} /> : <Send size={15} />}
          </button>
        </div>
      </section>

      <AnimatePresence>
        {driveOpen && (
          <motion.div className="fa-modal-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setDriveOpen(false)}>
            <motion.div className="fa-modal" data-testid="drive-modal" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 14 }} onClick={(e) => e.stopPropagation()}>
              <div className="fa-modal-head">
                <Cloud size={16} /> <span>Google Drive</span>
                <button className="fa-modal-x" onClick={() => setDriveOpen(false)}><X size={16} /></button>
              </div>
              <div className="fa-drive-search">
                <Cloud size={13} className="fa-drive-search-ic" />
                <input
                  data-testid="drive-search-input"
                  value={driveSearch}
                  onChange={(e) => setDriveSearch(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") searchDrive(); }}
                  placeholder="Search your Drive by file name, then press Enter"
                />
                {driveSearch && <button className="fa-drive-search-x" data-testid="drive-search-clear" onClick={clearSearch}><X size={13} /></button>}
                <button className="fa-drive-search-go" data-testid="drive-search-go" onClick={() => searchDrive()}>Search</button>
              </div>
              <div className="fa-crumbs">
                {driveCrumbs.map((c, i) => (
                  <span key={c.id} className="fa-crumb">
                    {i > 0 && <ChevronRight size={12} />}
                    <button onClick={() => gotoCrumb(i)}>{c.name}</button>
                  </span>
                ))}
              </div>
              <div className="fa-drive-list" data-testid="drive-list">
                {driveLoading ? (
                  <div className="fa-empty"><Loader2 className="spin" size={18} /><p>Loading Drive…</p></div>
                ) : driveItems.length === 0 ? (
                  <div className="fa-empty"><Folder size={22} /><p>This folder is empty.</p></div>
                ) : (
                  driveItems.map((it) => (
                    <div key={it.id} className={`fa-drive-row ${!it.supported && !it.is_folder ? "unsupported" : ""}`} data-testid={`drive-item-${it.id}`}>
                      {it.is_folder ? (
                        <button className="fa-drive-folder" onClick={() => enterFolder(it)}>
                          <Folder size={15} /> <span>{it.name}</span> <ChevronRight size={14} />
                        </button>
                      ) : (
                        <label className={`fa-drive-file ${driveSel.includes(it.id) ? "sel" : ""}`}>
                          <input type="checkbox" disabled={!it.supported} checked={driveSel.includes(it.id)} onChange={() => toggleDriveSel(it.id)} />
                          <FileText size={14} />
                          <span className="fa-drive-name">{it.name}</span>
                          {!it.supported && <span className="fa-bin">unsupported</span>}
                        </label>
                      )}
                    </div>
                  ))
                )}
              </div>
              <div className="fa-modal-foot">
                <span className="fa-drive-count">{driveSel.length} selected</span>
                <button className="fa-drive-btn ghost" data-testid="drive-import-folder" onClick={importFolder} disabled={driveImporting || !!driveSearch}
                  title="Import every supported file in this folder (recursively)">
                  <FolderUp size={14} /> Import entire folder
                </button>
                <button className="fa-analyze" data-testid="drive-import" onClick={importDrive} disabled={driveImporting || !driveSel.length}>
                  {driveImporting ? <Loader2 className="spin" size={15} /> : <Check size={15} />}
                  {driveImporting ? "Importing…" : "Import selected"}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {viewer && (
          <motion.div className="fa-modal-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setViewer(null)}>
            <motion.div className="fa-modal fa-viewer" data-testid="file-viewer" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 14 }} onClick={(e) => e.stopPropagation()}>
              <div className="fa-modal-head">
                <FileText size={16} /> <span>{viewer.path}</span>
                <span className="fa-viewer-line">line {viewer.line}</span>
                <button className="fa-modal-x" onClick={() => setViewer(null)}><X size={16} /></button>
              </div>
              <div className="fa-viewer-body">
                {viewer.loading ? (
                  <div className="fa-empty"><Loader2 className="spin" size={18} /><p>Loading…</p></div>
                ) : (
                  <pre className="fa-viewer-code">
                    {(viewer.content || "").split("\n").map((ln, i) => {
                      const n = i + 1;
                      const hit = n === viewer.line;
                      return (
                        <div key={n} className={`fa-vline ${hit ? "hit" : ""}`} ref={hit ? (el) => el && el.scrollIntoView({ block: "center" }) : null}>
                          <span className="fa-vnum">{n}</span>
                          <span className="fa-vtext">{ln || " "}</span>
                        </div>
                      );
                    })}
                  </pre>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

```


### `frontend/src/components/SelfDirective.js`
```javascript
import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Wand2, Loader2, ShieldAlert, Lock, FileCode, Check, X, RotateCcw,
  Search, History, AlertTriangle, GitCommitHorizontal, CheckCircle2, ScrollText, Radar, Play, Eye
} from "lucide-react";
import { API } from "../App";

function DiffView({ diff }) {
  const lines = (diff || "").split("\n");
  return (
    <pre className="sd-diff">
      {lines.map((ln, i) => {
        let cls = "sd-dl";
        if (ln.startsWith("+++") || ln.startsWith("---")) cls = "sd-dl meta";
        else if (ln.startsWith("@@")) cls = "sd-dl hunk";
        else if (ln.startsWith("+")) cls = "sd-dl add";
        else if (ln.startsWith("-")) cls = "sd-dl del";
        return <div key={i} className={cls}>{ln || " "}</div>;
      })}
    </pre>
  );
}

export default function SelfDirective() {
  const [manifest, setManifest] = useState(null);
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState([]);
  const [instruction, setInstruction] = useState("");
  const [proposing, setProposing] = useState(false);
  const [proposal, setProposal] = useState(null);
  const [applying, setApplying] = useState(false);
  const [rolling, setRolling] = useState(false);
  const [history, setHistory] = useState([]);
  const [scanCfg, setScanCfg] = useState(null);
  const [scans, setScans] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [savingCfg, setSavingCfg] = useState(false);

  const loadScans = useCallback(async () => {
    try {
      const [c, l] = await Promise.all([axios.get(`${API}/self/scan/config`), axios.get(`${API}/self/scans`, { params: { limit: 8 } })]);
      setScanCfg(c.data); setScans(l.data);
    } catch (e) { console.error(e); }
  }, []);
  const saveScanCfg = async (patch) => {
    setSavingCfg(true);
    try { const r = await axios.put(`${API}/self/scan/config`, patch); setScanCfg(r.data); toast.success(r.data.enabled ? `Scheduled scans on - every ${r.data.interval_hours}h` : "Scheduled scans off"); }
    catch (e) { toast.error(e?.response?.data?.detail || "Could not save"); }
    finally { setSavingCfg(false); }
  };
  const runScan = async () => {
    setScanning(true);
    try {
      const r = await axios.post(`${API}/self/scan/run`, {}, { timeout: 300000 });
      const c = r.data.counts || {};
      toast.success(`Scan done: ${c.critical || 0} critical · ${c.high || 0} high · ${c.low || 0} low · ${(r.data.proposal_ids || []).length} proposal(s) queued`);
      loadScans(); loadHistory();
    } catch (e) { toast.error(e?.response?.data?.detail || "Scan failed"); }
    finally { setScanning(false); }
  };

  const loadManifest = useCallback(async () => {
    try { const r = await axios.get(`${API}/self/manifest`); setManifest(r.data); }
    catch (e) { console.error(e); }
  }, []);
  const loadHistory = useCallback(async () => {
    try { const r = await axios.get(`${API}/self/history`); setHistory(r.data); }
    catch (e) { console.error(e); }
  }, []);

  useEffect(() => { loadManifest(); loadHistory(); loadScans(); }, [loadManifest, loadHistory, loadScans]);

  const toggle = (path) => {
    setSelected((s) => s.includes(path) ? s.filter((x) => x !== path) : (s.length >= 5 ? (toast.warning("Max 5 files per directive"), s) : [...s, path]));
  };

  const propose = async () => {
    if (!instruction.trim()) { toast.error("Describe what you want changed"); return; }
    if (!selected.length) { toast.error("Select at least one file"); return; }
    setProposing(true);
    setProposal(null);
    try {
      const r = await axios.post(`${API}/self/propose`, { instruction: instruction.trim(), paths: selected });
      setProposal(r.data);
      toast.success("Patch proposal ready — review the diff");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Proposal failed");
    } finally { setProposing(false); }
  };

  const apply = async () => {
    if (!proposal) return;
    setApplying(true);
    try {
      const r = await axios.post(`${API}/self/apply`, { id: proposal.id, approved: true });
      setProposal((p) => ({ ...p, status: r.data.status }));
      toast.success("Applied to preview source — hot-reload will pick it up");
      await loadHistory();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Apply failed");
    } finally { setApplying(false); }
  };

  const rollback = async (id) => {
    setRolling(true);
    try {
      await axios.post(`${API}/self/rollback`, { id });
      if (proposal?.id === id) setProposal((p) => ({ ...p, status: "rolled_back" }));
      toast.success("Rolled back — original source restored");
      await loadHistory();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Rollback failed");
    } finally { setRolling(false); }
  };

  const files = (manifest?.files || []).filter((f) => f.path.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div className="sd-wrap" data-testid="self-directive">
      <section className="sd-console">
        <div className="sd-head">
          <Wand2 size={17} /> <span>Self-Directive</span>
          <em>Instruct ACASO to modify its own source — reviewed, approved, reversible.</em>
        </div>
        <div className="sd-warn" data-testid="self-preview-warning">
          <Lock size={14} />
          <div>
            <b>Preview-only & approval-gated.</b> This edits source in the live preview workspace and is <b>disabled after production deployment</b>. Every change is shown as a diff first, applied only on your approval, and can be rolled back.
          </div>
        </div>

        <div className="sd-scan" data-testid="self-scan">
          <div className="sd-sub-head"><Radar size={14} /> Periodic self-scan <span className="sd-scan-note">propose-only · compile / lint / bundle / hygiene checks · never auto-applies</span></div>
          {scanCfg && (
            <div className="sd-scan-row">
              <label className="sd-toggle" data-testid="self-scan-toggle">
                <input type="checkbox" checked={!!scanCfg.enabled} disabled={savingCfg} onChange={(e) => saveScanCfg({ enabled: e.target.checked })} />
                <span>{scanCfg.enabled ? "Scheduled" : "Off"}</span>
              </label>
              <label className="sd-interval">every
                <input type="number" min={1} max={720} data-testid="self-scan-interval" defaultValue={scanCfg.interval_hours} onBlur={(e) => Number(e.target.value) !== scanCfg.interval_hours && saveScanCfg({ interval_hours: Number(e.target.value) })} /> h
              </label>
              <span className="sd-scan-meta">
                {scanCfg.last_run_at ? `last ${new Date(scanCfg.last_run_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}` : "never run"}
                {scanCfg.enabled && scanCfg.next_run_at ? ` · next ${new Date(scanCfg.next_run_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}` : ""}
              </span>
              <button className="sd-scan-run" data-testid="self-scan-run" onClick={runScan} disabled={scanning || scanCfg.running}>
                {scanning || scanCfg.running ? <Loader2 className="spin" size={13} /> : <Play size={13} />} {scanning ? "Scanning..." : "Scan now"}
              </button>
            </div>
          )}
          {scanCfg && (
            <textarea className="sd-focus" data-testid="self-scan-focus" defaultValue={scanCfg.focus} rows={2}
              onBlur={(e) => e.target.value !== scanCfg.focus && saveScanCfg({ focus: e.target.value })} placeholder="What the scan should prioritise when it proposes a change..." />
          )}
          {scans.length > 0 && (
            <div className="sd-scans" data-testid="self-scan-list">
              {scans.map((sc) => (
                <div key={sc.id} className="sd-scan-item">
                  <span className={`sd-status s-${sc.status === "done" ? "applied" : sc.status}`}>{sc.trigger}</span>
                  <span className="sd-scan-when">{new Date(sc.started_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })} · {sc.duration_s}s</span>
                  <span className="sd-scan-counts">{(sc.counts?.critical || 0)} crit · {(sc.counts?.high || 0)} high · {(sc.counts?.low || 0)} low · {(sc.counts?.info || 0)} info</span>
                  <span className="sd-scan-res">{(sc.proposal_ids || []).length ? `${sc.proposal_ids.length} proposal queued for your approval` : (sc.note || sc.error || "")}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      <div className="sd-grid">
        <section className="sd-picker">
          <div className="sd-sub-head"><FileCode size={14} /> Source Allowlist <span className="sd-count">{selected.length}/5</span></div>
          <div className="sd-search"><Search size={13} /><input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Filter files…" data-testid="self-file-filter" /></div>
          <div className="sd-files" data-testid="self-file-list">
            {files.map((f) => (
              <label key={f.path} className={selected.includes(f.path) ? "sd-file sel" : "sd-file"} data-testid={`self-file-${f.path}`}>
                <input type="checkbox" checked={selected.includes(f.path)} onChange={() => toggle(f.path)} />
                <span className="sd-fpath">{f.path}</span>
                <span className="sd-fsize">{(f.size / 1024).toFixed(1)}k</span>
              </label>
            ))}
            {files.length === 0 && <div className="sd-empty-sm">No files match.</div>}
          </div>
          {manifest && (
            <div className="sd-deny"><ShieldAlert size={12} /> Blocked: {manifest.denylist.slice(0, 6).join(", ")}…</div>
          )}
        </section>

        <section className="sd-main">
          <textarea
            data-testid="self-instruction"
            className="sd-instruction"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="Describe the change in plain English. e.g. 'On the Bug Bounty tab, rename the Run Engagement button to Launch Engagement' or 'Add a subtitle under the ACASO title in the header'"
            rows={3}
          />
          <button className="sd-propose" data-testid="self-propose" onClick={propose} disabled={proposing}>
            {proposing ? <Loader2 className="spin" size={16} /> : <Wand2 size={16} />}
            {proposing ? "Generating patch…" : "Generate Patch Proposal"}
          </button>

          {proposing && (
            <div className="sd-skeleton">{[...Array(6)].map((_, i) => <div key={i} className="sd-sk" style={{ width: `${88 - i * 7}%` }} />)}</div>
          )}

          <AnimatePresence>
            {proposal && (
              <motion.div className="sd-proposal" data-testid="self-proposal" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                <div className="sd-prop-head">
                  <GitCommitHorizontal size={15} /> Patch Proposal
                  <span className={`sd-status s-${proposal.status}`}>{proposal.status}</span>
                  <span className="sd-model">{proposal.model_label}</span>
                </div>
                {proposal.explanation && <p className="sd-expl">{proposal.explanation}</p>}
                {proposal.test_plan && <div className="sd-testplan"><ScrollText size={12} /> <span><b>Test plan:</b> {proposal.test_plan}</span></div>}
                {proposal.diffs?.map((d) => (
                  <div key={d.path} className="sd-diff-block">
                    <div className="sd-diff-head"><FileCode size={12} /> {d.path} <span className="sd-add">+{d.added}</span> <span className="sd-del">-{d.removed}</span></div>
                    <DiffView diff={d.diff} />
                  </div>
                ))}

                <div className="sd-prop-actions">
                  {proposal.status === "proposed" && (
                    <button className="sd-apply" data-testid="self-apply" onClick={apply} disabled={applying}>
                      {applying ? <Loader2 className="spin" size={15} /> : <Check size={15} />} Approve & Apply
                    </button>
                  )}
                  {proposal.status === "applied" && (
                    <>
                      <span className="sd-applied"><CheckCircle2 size={15} /> Applied to preview</span>
                      <button className="sd-rollback" data-testid="self-rollback" onClick={() => rollback(proposal.id)} disabled={rolling}>
                        {rolling ? <Loader2 className="spin" size={15} /> : <RotateCcw size={15} />} Rollback
                      </button>
                    </>
                  )}
                  {proposal.status === "rolled_back" && <span className="sd-rolled"><RotateCcw size={15} /> Rolled back</span>}
                  <button className="sd-discard" onClick={() => setProposal(null)}><X size={14} /> Dismiss</button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {history.length > 0 && (
            <div className="sd-history" data-testid="self-history">
              <div className="sd-sub-head"><History size={14} /> Directive History</div>
              {history.map((h) => (
                <div key={h.id} className="sd-hrow">
                  <span className={`sd-status s-${h.status}`}>{h.status}</span>
                  {h.origin === "scheduled_scan" && <span className="sd-auto" title="Generated by the periodic self-scan">scan</span>}
                  <span className="sd-hinstr" title={h.instruction}>{h.instruction}</span>
                  <span className="sd-hpaths">{(h.paths || []).join(", ")}</span>
                  {h.status === "proposed" && (
                    <button className="sd-hroll" data-testid="self-review" onClick={() => { setProposal(h); window.scrollTo({ top: 0, behavior: "smooth" }); }} title="Review & approve"><Eye size={12} /></button>
                  )}
                  {h.status === "applied" && (
                    <button className="sd-hroll" onClick={() => rollback(h.id)} disabled={rolling} title="Rollback"><RotateCcw size={12} /></button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

```


### `frontend/src/components/Council.js`
```javascript
import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Crown, Loader2, Play, Download, History, Sparkles, ShieldAlert, Lightbulb,
  Compass, Coins, Radar, Trash2, ChevronRight, X, Info, Rocket, ExternalLink
} from "lucide-react";
import { API } from "../App";
import { Markdown } from "./FileAnalyzer";

const WEAVER_ICON = { architect: Compass, shadow: ShieldAlert, muse: Lightbulb, finance: Coins };
const PRESET_ICON = { genesis: Sparkles, hunter: Radar, foresight: Compass };

const fmtDate = (iso) => {
  try { return new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }); }
  catch { return ""; }
};

export default function Council() {
  const [presets, setPresets] = useState([]);
  const [presetId, setPresetId] = useState("genesis");
  const [challenge, setChallenge] = useState("");
  const [challengeType, setChallengeType] = useState("product_strategy");
  const [extra, setExtra] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [openWeaver, setOpenWeaver] = useState(null);
  const [missioning, setMissioning] = useState(false);

  const applyPreset = useCallback((p) => {
    setPresetId(p.id);
    setChallenge(p.challenge);
    setChallengeType(p.challenge_type);
    setExtra(p.additional_context || "");
  }, []);

  const loadHistory = useCallback(async () => {
    try { const r = await axios.get(`${API}/acaso/deliberations`); setHistory(r.data); } catch { /* silent */ }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const r = await axios.get(`${API}/acaso/presets`);
        setPresets(r.data);
        const g = r.data.find((p) => p.id === "genesis") || r.data[0];
        if (g) applyPreset(g);
      } catch { toast.error("Could not load council presets"); }
      loadHistory();
    })();
  }, [applyPreset, loadHistory]);

  const run = async () => {
    if (challenge.trim().length < 20) { toast.error("Describe the challenge in at least 20 characters"); return; }
    setRunning(true); setResult(null);
    try {
      const r = await axios.post(`${API}/acaso/deliberate`, {
        challenge, challenge_type: challengeType, preset_id: presetId,
        context: extra ? { additional_context: extra } : null,
      }, { timeout: 300000 });
      setResult(r.data);
      toast.success(`Council resolved in ${r.data.duration_s}s`);
      loadHistory();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Deliberation failed");
    } finally { setRunning(false); }
  };

  const openPast = async (id) => {
    try { const r = await axios.get(`${API}/acaso/deliberations/${id}`); setResult(r.data); window.scrollTo({ top: 0, behavior: "smooth" }); }
    catch { toast.error("Could not open deliberation"); }
  };

  const removePast = async (id) => {
    try {
      await axios.delete(`${API}/acaso/deliberations/${id}`);
      if (result?.id === id) setResult(null);
      loadHistory();
    } catch { toast.error("Delete failed"); }
  };

  const exportMd = (id) => { window.open(`${API}/acaso/deliberations/${id}/export`, "_blank"); };

  const toMission = async () => {
    if (!result) return;
    setMissioning(true);
    try {
      const r = await axios.post(`${API}/acaso/deliberations/${result.id}/to-mission`, { mode: "Move" }, { timeout: 120000 });
      setResult((prev) => ({ ...prev, mission_id: r.data.id, mission_title: r.data.title }));
      loadHistory();
      toast.success(`Mission "${r.data.title}" is on the Sovereign Home board`, {
        action: { label: "Open board", onClick: () => { window.location.href = "/?tab=home"; } },
      });
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Could not compile mission");
    } finally { setMissioning(false); }
  };

  return (
    <div className="cw-wrap" data-testid="council-page">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><Crown size={18} /> Council of Weavers</div>
          <p>
            Four weavers on four models argue the challenge in parallel - <b>Architect</b> (thesis), <b>Shadow</b> (risk, can veto),
            <b> Muse</b> (contrarian + weak signals), <b>Finance</b> (numbers). The <b>Meta-Weaver</b> reconciles them into a
            Sovereign Directive with invalidation conditions. This is the live <code>/api/acaso/deliberate</code> engine
            the Genesis Engine and Sovereign Hunter scripts call.
          </p>
        </div>
        <div className="chr-hero-stats">
          <div className="chr-stat"><span className="v">{history.length}</span><span className="l">Deliberations</span></div>
          <div className="chr-stat gold"><span className="v">4+1</span><span className="l">Weavers</span></div>
        </div>
      </div>

      <div className="cw-honesty" data-testid="council-honesty">
        <Info size={14} /> Outputs are multi-model reasoning only. No live market feeds, on-chain data or lead databases are connected;
        "weak signals" are inferred, not measured. Not financial advice - the operator owns every decision.
      </div>

      <div className="fa-console">
        <div className="fa-head"><Sparkles size={16} /> Directive <em>pick a preset, edit freely, then convene</em></div>
        <div className="cw-presets">
          {presets.map((p) => {
            const Icon = PRESET_ICON[p.id] || Sparkles;
            return (
              <button key={p.id} data-testid={`preset-${p.id}`}
                className={presetId === p.id ? "cw-preset active" : "cw-preset"} onClick={() => applyPreset(p)}>
                <Icon size={15} />
                <span><b>{p.name}</b><small>{p.tagline}</small></span>
              </button>
            );
          })}
          <button data-testid="preset-custom" className={presetId === "custom" ? "cw-preset active" : "cw-preset"}
            onClick={() => { setPresetId("custom"); setChallenge(""); setChallengeType("general"); setExtra(""); }}>
            <Play size={15} /><span><b>Custom</b><small>Any challenge - strategy, launch, hire, pricing, threat.</small></span>
          </button>
        </div>

        <textarea data-testid="council-challenge" className="cw-textarea" rows={12} value={challenge}
          onChange={(e) => setChallenge(e.target.value)} placeholder="State the challenge the council must resolve..." />
        <div className="cw-row">
          <input data-testid="council-type" className="cw-input" value={challengeType} onChange={(e) => setChallengeType(e.target.value)}
            placeholder="challenge_type (e.g. product_strategy)" />
          <input data-testid="council-context" className="cw-input grow" value={extra} onChange={(e) => setExtra(e.target.value)}
            placeholder="Operator context (optional)" />
          <button data-testid="council-run" className="fa-btn primary" onClick={run} disabled={running}>
            {running ? <Loader2 className="spin" size={15} /> : <Crown size={15} />} {running ? "Council in session..." : "Convene Council"}
          </button>
        </div>
        {running && (
          <div className="cw-running" data-testid="council-running">
            {["Architect", "Shadow", "Muse", "Finance"].map((n, i) => (
              <motion.span key={n} initial={{ opacity: 0.3 }} animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.6, delay: i * 0.3 }}>{n}</motion.span>
            ))}
            <span className="cw-arrow">→ Meta-Weaver</span>
          </div>
        )}
      </div>

      <AnimatePresence>
        {result && (
          <motion.div className="cw-result" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} data-testid="council-result">
            <div className="cw-result-head">
              <div>
                <div className="fa-head"><Crown size={16} /> Sovereign Directive
                  {result.shadow_veto && <span className="cw-veto" data-testid="shadow-veto">SHADOW VETO</span>}
                </div>
                <div className="cw-meta">
                  {fmtDate(result.timestamp)} · {result.duration_s}s · {result.challenge_type} · Council: {(result.council_consulted || []).join(", ")}
                </div>
              </div>
              <div className="cw-actions">
                {result.mission_id ? (
                  <a className="fa-btn cw-mission-link" data-testid="council-open-mission" href="/?tab=home" title={result.mission_title}>
                    <ExternalLink size={14} /> On board: {result.mission_title || "mission"}
                  </a>
                ) : (
                  <button className="fa-btn primary" data-testid="council-to-mission" onClick={toMission} disabled={missioning}>
                    {missioning ? <Loader2 className="spin" size={14} /> : <Rocket size={14} />} {missioning ? "Compiling mission..." : "Turn into Mission"}
                  </button>
                )}
                <button className="fa-btn" data-testid="council-export" onClick={() => exportMd(result.id)}><Download size={14} /> Export .md</button>
              </div>
            </div>

            <div className="cw-grid">
              <div className="cw-directive"><Markdown text={result.sovereign_directive} /></div>
              <aside className="cw-side">
                <div className="cw-signals">
                  <div className="cw-side-title"><Radar size={14} /> Weak signals <small>inferred</small></div>
                  <Markdown text={result.weak_signals || "_The council did not surface distinct weak signals._"} />
                </div>
                <div className="cw-side-title"><History size={14} /> Weavers</div>
                {(result.weavers || []).map((w) => {
                  const Icon = WEAVER_ICON[w.id] || Sparkles;
                  const open = openWeaver === w.id;
                  return (
                    <div key={w.id} className={`cw-weaver ${w.ok ? "" : "down"}`} data-testid={`weaver-${w.id}`}>
                      <button className="cw-weaver-h" onClick={() => setOpenWeaver(open ? null : w.id)}>
                        <Icon size={14} /> <b>{w.name}</b> <span>{w.role}</span>
                        <em>{w.model_label}</em> <ChevronRight size={14} className={open ? "rot" : ""} />
                      </button>
                      {open && <div className="cw-weaver-b"><Markdown text={w.analysis} /></div>}
                    </div>
                  );
                })}
              </aside>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="fa-console">
        <div className="fa-head"><History size={16} /> Past deliberations <em>{history.length} stored</em></div>
        {history.length === 0 ? (
          <div className="attach-empty" data-testid="council-history-empty">No deliberations yet. Convene the council above - every session is journaled here.</div>
        ) : (
          <div className="cw-history" data-testid="council-history">
            {history.map((h) => (
              <div key={h.id} className="cw-hrow">
                <button className="cw-hmain" onClick={() => openPast(h.id)} data-testid={`history-${h.id}`}>
                  <span className={`bb-tag`}>{h.preset_id || "custom"}</span>
                  <span className="cw-htitle">{h.title}</span>
                  <span className="cw-hmeta">{fmtDate(h.timestamp)} · {h.duration_s}s{h.shadow_veto ? " · VETO" : ""}{h.mission_id ? " · MISSION" : ""}</span>
                </button>
                <button className="attach-btn" title="Export" onClick={() => exportMd(h.id)}><Download size={13} /></button>
                <button className="attach-btn danger" title="Delete" onClick={() => removePast(h.id)}><Trash2 size={13} /></button>
              </div>
            ))}
          </div>
        )}
      </div>

      {openWeaver && !result && <button className="cw-close" onClick={() => setOpenWeaver(null)}><X size={14} /></button>}
    </div>
  );
}

```


### `frontend/src/components/VoiceChat.js`
```javascript
import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic, MicOff, Square, Volume2, VolumeX, Send, Radio, Hand, Keyboard, Zap, Crown,
  Loader2, Trash2, AlertTriangle, Ear, Waves
} from "lucide-react";
import { API } from "../App";
import { Markdown } from "./FileAnalyzer";

const SR = typeof window !== "undefined" ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null;
const TTS = typeof window !== "undefined" ? window.speechSynthesis : null;

const INTERACTION = [
  { key: "handsfree", label: "Hands-free", icon: Radio, hint: "Listens, replies aloud, listens again until you stop." },
  { key: "ptt", label: "Push-to-talk", icon: Hand, hint: "Hold the button to speak, release to send. Reply spoken once." },
  { key: "text", label: "Text-first", icon: Keyboard, hint: "Type or dictate; click the speaker to hear a reply." },
];

const getSession = () => {
  try {
    let s = localStorage.getItem("acaso_voice_session");
    if (!s) { s = crypto.randomUUID(); localStorage.setItem("acaso_voice_session", s); }
    return s;
  } catch { return "voice-default"; }
};

export default function VoiceChat() {
  const [sessionId, setSessionId] = useState(getSession);
  const [interaction, setInteraction] = useState("handsfree");
  const [answerMode, setAnswerMode] = useState("fast");
  const [messages, setMessages] = useState([]);
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState("");
  const [thinking, setThinking] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [speakReplies, setSpeakReplies] = useState(true);
  const [voices, setVoices] = useState([]);
  const [voiceName, setVoiceName] = useState(() => localStorage.getItem("acaso_voice_name") || "");
  const [text, setText] = useState("");
  const [active, setActive] = useState(false); // hands-free loop on/off

  const recRef = useRef(null);
  const activeRef = useRef(false);
  const interactionRef = useRef(interaction);
  const modeRef = useRef(answerMode);
  const endRef = useRef(null);
  const finalRef = useRef("");
  useEffect(() => { interactionRef.current = interaction; }, [interaction]);
  useEffect(() => { modeRef.current = answerMode; }, [answerMode]);
  useEffect(() => { activeRef.current = active; }, [active]);

  const supported = !!SR && !!TTS;

  // ---- voices ----
  useEffect(() => {
    if (!TTS) return;
    const load = () => {
      const v = TTS.getVoices().filter((x) => x.lang && x.lang.toLowerCase().startsWith("en"));
      setVoices(v.length ? v : TTS.getVoices());
    };
    load();
    TTS.addEventListener?.("voiceschanged", load);
    return () => TTS.removeEventListener?.("voiceschanged", load);
  }, []);

  // ---- history ----
  useEffect(() => {
    (async () => {
      try { const r = await axios.get(`${API}/voice/history`, { params: { session_id: sessionId } }); setMessages(r.data); }
      catch { /* silent */ }
    })();
  }, [sessionId]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, interim, thinking]);

  // ---- TTS ----
  const stopSpeaking = useCallback(() => { try { TTS?.cancel(); } catch { /* ignore */ } setSpeaking(false); }, []);

  const speak = useCallback((content, onDone) => {
    if (!TTS || !content) { onDone?.(); return; }
    TTS.cancel();
    const u = new SpeechSynthesisUtterance(content);
    const v = voices.find((x) => x.name === voiceName);
    if (v) u.voice = v;
    u.rate = 1.02; u.pitch = 1;
    u.onstart = () => setSpeaking(true);
    u.onend = () => { setSpeaking(false); onDone?.(); };
    u.onerror = () => { setSpeaking(false); onDone?.(); };
    TTS.speak(u);
  }, [voices, voiceName]);

  // ---- STT ----
  const stopListening = useCallback(() => {
    try { recRef.current?.stop(); } catch { /* ignore */ }
    setListening(false); setInterim("");
  }, []);

  const send = useCallback(async (msg, { speakIt } = { speakIt: true }) => {
    const content = (msg || "").trim();
    if (!content) return;
    const mode = modeRef.current;
    setMessages((m) => [...m, { id: `tmp-${Date.now()}`, role: "user", content, mode, created_at: new Date().toISOString() }]);
    setThinking(true);
    if (mode === "council") toast("Council convened - this takes 1-3 minutes", { icon: <Crown size={14} /> });
    try {
      const r = await axios.post(`${API}/voice/chat`, { message: content, session_id: sessionId, mode }, { timeout: 320000 });
      const reply = r.data.reply;
      setMessages((m) => [...m, reply]);
      setThinking(false);
      const after = () => {
        if (interactionRef.current === "handsfree" && activeRef.current) startListening(); // eslint-disable-line no-use-before-define
      };
      if (speakIt && speakReplies) speak(reply.content, after); else after();
    } catch (e) {
      setThinking(false);
      toast.error(e?.response?.data?.detail || "ACASO could not answer");
      if (interactionRef.current === "handsfree" && activeRef.current) setTimeout(() => startListening(), 800); // eslint-disable-line no-use-before-define
    }
  }, [sessionId, speak, speakReplies]);

  const startListening = useCallback(() => {
    if (!SR) return;
    stopSpeaking();
    try { recRef.current?.abort(); } catch { /* ignore */ }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = true;
    rec.continuous = interactionRef.current === "ptt";
    finalRef.current = "";
    rec.onstart = () => { setListening(true); setInterim(""); };
    rec.onresult = (ev) => {
      let fin = "", inter = "";
      for (let i = 0; i < ev.results.length; i++) {
        const t = ev.results[i][0].transcript;
        if (ev.results[i].isFinal) fin += t + " "; else inter += t;
      }
      finalRef.current = fin.trim();
      setInterim((fin + inter).trim());
    };
    rec.onerror = (ev) => {
      setListening(false); setInterim("");
      if (ev.error === "not-allowed") { toast.error("Microphone permission denied"); setActive(false); }
      else if (ev.error !== "aborted" && ev.error !== "no-speech") toast.error(`Mic error: ${ev.error}`);
      if (ev.error === "no-speech" && interactionRef.current === "handsfree" && activeRef.current) setTimeout(() => startListening(), 400);
    };
    rec.onend = () => {
      setListening(false);
      const heard = finalRef.current;
      setInterim("");
      if (interactionRef.current === "text") { if (heard) setText((t) => (t ? t + " " : "") + heard); return; }
      if (heard) send(heard);
      else if (interactionRef.current === "handsfree" && activeRef.current && !thinking) setTimeout(() => startListening(), 300);
    };
    recRef.current = rec;
    try { rec.start(); } catch { /* already started */ }
  }, [send, stopSpeaking, thinking]);

  const toggleHandsFree = () => {
    if (active) { setActive(false); activeRef.current = false; stopListening(); stopSpeaking(); }
    else { setActive(true); activeRef.current = true; startListening(); }
  };

  const clearHistory = async () => {
    try { await axios.delete(`${API}/voice/history`, { params: { session_id: sessionId } }); } catch { /* ignore */ }
    const s = crypto.randomUUID(); localStorage.setItem("acaso_voice_session", s); setSessionId(s); setMessages([]);
  };

  useEffect(() => () => { try { recRef.current?.abort(); TTS?.cancel(); } catch { /* ignore */ } }, []);

  const changeInteraction = (k) => { setActive(false); activeRef.current = false; stopListening(); setInteraction(k); };

  return (
    <div className="vc-wrap" data-testid="voice-page">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><Waves size={18} /> Voice Channel</div>
          <p>Talk to ACASO out loud. Speech recognition and speech synthesis run <b>in your browser</b> (Web Speech API - no keys, no audio sent to the server; only the transcript is). Choose how you want to talk, and per message whether the <b>fast</b> voice or the full <b>Council of Weavers</b> answers.</p>
        </div>
        <div className="chr-hero-stats">
          <div className="chr-stat"><span className="v">{messages.filter((m) => m.role === "user").length}</span><span className="l">Turns</span></div>
          <div className={`chr-stat ${listening ? "gold" : ""}`}><span className="v">{listening ? "LIVE" : speaking ? "TALK" : "IDLE"}</span><span className="l">Mic state</span></div>
        </div>
      </div>

      {!supported && (
        <div className="cw-honesty" data-testid="voice-unsupported"><AlertTriangle size={14} />
          This browser lacks the Web Speech API. Use Chrome, Edge or Safari for voice; typing still works below.
        </div>
      )}

      <div className="fa-console">
        <div className="vc-controls">
          <div className="vc-seg" role="tablist" aria-label="Interaction mode">
            {INTERACTION.map((m) => { const I = m.icon; return (
              <button key={m.key} data-testid={`voice-mode-${m.key}`} className={interaction === m.key ? "vc-seg-btn active" : "vc-seg-btn"} onClick={() => changeInteraction(m.key)} title={m.hint}>
                <I size={14} /> {m.label}
              </button>); })}
          </div>
          <div className="vc-seg" aria-label="Who answers">
            <button data-testid="answer-fast" className={answerMode === "fast" ? "vc-seg-btn active" : "vc-seg-btn"} onClick={() => setAnswerMode("fast")}><Zap size={14} /> Fast</button>
            <button data-testid="answer-council" className={answerMode === "council" ? "vc-seg-btn active council" : "vc-seg-btn"} onClick={() => setAnswerMode("council")}><Crown size={14} /> Council</button>
          </div>
          <select data-testid="voice-select" className="cw-input vc-voice" value={voiceName} onChange={(e) => { setVoiceName(e.target.value); localStorage.setItem("acaso_voice_name", e.target.value); }}>
            <option value="">Default voice</option>
            {voices.map((v) => <option key={v.name} value={v.name}>{v.name}</option>)}
          </select>
          <button data-testid="voice-mute" className="attach-btn" title={speakReplies ? "Mute spoken replies" : "Unmute spoken replies"} onClick={() => { setSpeakReplies((s) => !s); stopSpeaking(); }}>
            {speakReplies ? <Volume2 size={14} /> : <VolumeX size={14} />}
          </button>
          <button data-testid="voice-clear" className="attach-btn danger" title="Clear conversation" onClick={clearHistory}><Trash2 size={14} /></button>
        </div>
        <div className="vc-hint">{INTERACTION.find((m) => m.key === interaction)?.hint} {answerMode === "council" ? "Council answers take 1-3 minutes and are summarized aloud; the full directive appears in the transcript." : ""}</div>
      </div>

      <div className="vc-transcript" data-testid="voice-transcript">
        {messages.length === 0 && !interim && !thinking && (
          <div className="attach-empty" data-testid="voice-empty"><Ear size={13} /> Nothing said yet. Start the mic or type below.</div>
        )}
        <AnimatePresence initial={false}>
          {messages.map((m) => (
            <motion.div key={m.id} className={`vc-msg ${m.role}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} data-testid={`voice-msg-${m.role}`}>
              <div className="vc-msg-meta">{m.role === "user" ? "You" : "ACASO"}{m.mode === "council" ? " · Council" : ""}{m.model_label ? ` · ${m.model_label}` : ""}</div>
              <div className="vc-msg-body">{m.content}</div>
              {m.full_text && (
                <details className="vc-full"><summary>Full Sovereign Directive</summary><Markdown text={m.full_text} /></details>
              )}
              {m.role === "assistant" && (
                <button className="vc-replay" onClick={() => speak(m.content)} title="Speak this reply" data-testid="voice-replay"><Volume2 size={12} /> speak</button>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        {interim && <div className="vc-msg user interim" data-testid="voice-interim"><div className="vc-msg-meta">You (hearing...)</div><div className="vc-msg-body">{interim}</div></div>}
        {thinking && <div className="vc-thinking" data-testid="voice-thinking"><Loader2 className="spin" size={14} /> {answerMode === "council" ? "Council of Weavers in session..." : "ACASO is thinking..."}</div>}
        <div ref={endRef} />
      </div>

      <div className="vc-dock">
        {interaction === "handsfree" && (
          <button data-testid="voice-handsfree-toggle" className={`vc-big ${active ? "on" : ""}`} onClick={toggleHandsFree} disabled={!supported}>
            {active ? <Square size={22} /> : <Mic size={22} />}
            <span>{active ? (listening ? "Listening - tap to stop" : speaking ? "Speaking - tap to stop" : thinking ? "Thinking - tap to stop" : "Resuming...") : "Start conversation"}</span>
          </button>
        )}
        {interaction === "ptt" && (
          <button data-testid="voice-ptt" className={`vc-big ${listening ? "on" : ""}`} disabled={!supported}
            onMouseDown={startListening} onMouseUp={stopListening} onMouseLeave={() => listening && stopListening()}
            onTouchStart={(e) => { e.preventDefault(); startListening(); }} onTouchEnd={(e) => { e.preventDefault(); stopListening(); }}>
            {listening ? <Mic size={22} /> : <MicOff size={22} />}
            <span>{listening ? "Release to send" : "Hold to talk"}</span>
          </button>
        )}
        {interaction === "text" && (
          <form className="vc-textrow" onSubmit={(e) => { e.preventDefault(); const t = text; setText(""); send(t, { speakIt: speakReplies }); }}>
            <button type="button" data-testid="voice-dictate" className={`attach-btn ${listening ? "live" : ""}`} title="Dictate" onClick={() => (listening ? stopListening() : startListening())} disabled={!supported}>
              {listening ? <Square size={14} /> : <Mic size={14} />}
            </button>
            <input data-testid="voice-text-input" className="cw-input grow" value={text} onChange={(e) => setText(e.target.value)} placeholder="Type or dictate a message..." />
            <button type="submit" data-testid="voice-text-send" className="fa-btn primary" disabled={!text.trim() || thinking}><Send size={14} /> Send</button>
          </form>
        )}
        {speaking && <button className="fa-btn" data-testid="voice-stop-speaking" onClick={stopSpeaking}><VolumeX size={14} /> Stop voice</button>}
      </div>
    </div>
  );
}

```


### `frontend/src/components/VoiceCommander.js`
```javascript
import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Mic, Square, Loader2, Command, Keyboard, Volume2 } from "lucide-react";
import { API } from "../App";

const SR = typeof window !== "undefined" ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null;
const TTS = typeof window !== "undefined" ? window.speechSynthesis : null;

const isTextField = (el) =>
  !!el && ((el.tagName === "TEXTAREA") || (el.tagName === "INPUT" && /^(text|search|email|url|tel|number|)$/.test(el.type || "text"))) && !el.readOnly && !el.disabled;

/** Write into a React-controlled input so React's onChange fires. */
function injectText(el, text, replaceFrom) {
  const proto = el.tagName === "TEXTAREA" ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
  const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
  const base = replaceFrom !== null && replaceFrom !== undefined ? el.value.slice(0, replaceFrom) : el.value;
  const sep = base && !/\s$/.test(base) ? " " : "";
  setter.call(el, base + sep + text);
  el.dispatchEvent(new Event("input", { bubbles: true }));
  return base.length + sep.length;
}

const fieldLabel = (el) => el?.getAttribute("placeholder") || el?.getAttribute("aria-label") || el?.getAttribute("data-testid") || el?.name || "focused text box";

/**
 * VoiceCommander - floating mic available on every tab.
 *  - Dictate mode: speaks into whichever text box was last focused (interim results shown live, finalized in place).
 *  - Command mode: transcript -> POST /api/voice/command -> executes (navigate / council / radar / mission / ask) and speaks back.
 */
export default function VoiceCommander({ setTab }) {
  const [mode, setMode] = useState(() => localStorage.getItem("acaso_vc_mode") || "dictate");
  const [listening, setListening] = useState(false);
  const [busy, setBusy] = useState(false);
  const [interim, setInterim] = useState("");
  const [target, setTarget] = useState(null);
  const [lastSpoken, setLastSpoken] = useState("");
  const recRef = useRef(null);
  const targetRef = useRef(null);
  const anchorRef = useRef(null); // char index where the current utterance began, for interim replacement
  const modeRef = useRef(mode);
  useEffect(() => { modeRef.current = mode; localStorage.setItem("acaso_vc_mode", mode); }, [mode]);

  // Track the last focused text field anywhere in the app (ignore our own widget).
  useEffect(() => {
    const onFocus = (e) => {
      const el = e.target;
      if (el?.closest?.("[data-voice-commander]")) return;
      if (isTextField(el)) { targetRef.current = el; setTarget(el); }
    };
    document.addEventListener("focusin", onFocus);
    return () => document.removeEventListener("focusin", onFocus);
  }, []);

  const speak = useCallback((t) => {
    if (!TTS || !t) return;
    TTS.cancel();
    const u = new SpeechSynthesisUtterance(t);
    const pref = localStorage.getItem("acaso_voice_name");
    const v = TTS.getVoices().find((x) => x.name === pref);
    if (v) u.voice = v;
    TTS.speak(u);
  }, []);

  const runCommand = useCallback(async (transcript) => {
    if (!transcript) return;
    setBusy(true);
    toast(`Heard: "${transcript}"`, { icon: <Command size={14} /> });
    try {
      const r = await axios.post(`${API}/voice/command`, { transcript, session_id: localStorage.getItem("acaso_voice_session") || null }, { timeout: 320000 });
      const d = r.data;
      if (d.navigate_tab && setTab) setTab(d.navigate_tab);
      setLastSpoken(d.spoken || "");
      speak(d.spoken);
      if (d.error) toast.error(d.spoken); else toast.success(d.spoken?.slice(0, 140) || d.intent);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Command failed");
    } finally { setBusy(false); }
  }, [setTab, speak]);

  const stop = useCallback(() => { try { recRef.current?.stop(); } catch { /* ignore */ } setListening(false); }, []);

  const start = useCallback(() => {
    if (!SR) { toast.error("This browser lacks speech recognition - use Chrome, Edge or Safari"); return; }
    if (modeRef.current === "dictate" && !isTextField(targetRef.current)) {
      toast.error("Click into a text box first, then tap the mic to dictate into it");
      return;
    }
    try { TTS?.cancel(); } catch { /* ignore */ }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = true;
    rec.continuous = modeRef.current === "dictate";
    let finalCmd = "";
    anchorRef.current = null;
    rec.onstart = () => { setListening(true); setInterim(""); };
    rec.onresult = (ev) => {
      let fin = "", inter = "";
      for (let i = ev.resultIndex; i < ev.results.length; i++) {
        const t = ev.results[i][0].transcript;
        if (ev.results[i].isFinal) fin += t; else inter += t;
      }
      if (modeRef.current === "dictate") {
        const el = targetRef.current;
        if (!isTextField(el)) return;
        if (anchorRef.current === null) anchorRef.current = el.value.length;
        const combined = (fin + inter).trim();
        if (combined) {
          const end = injectText(el, combined, anchorRef.current);
          if (fin) { anchorRef.current = end + combined.length; el.setSelectionRange?.(el.value.length, el.value.length); }
        }
        setInterim(inter);
      } else {
        finalCmd = (finalCmd + fin).trim();
        setInterim(inter || finalCmd);
      }
    };
    rec.onerror = (ev) => {
      setListening(false);
      if (ev.error === "not-allowed") toast.error("Microphone permission denied");
      else if (!["aborted", "no-speech"].includes(ev.error)) toast.error(`Mic error: ${ev.error}`);
    };
    rec.onend = () => {
      setListening(false); setInterim("");
      if (modeRef.current === "command" && finalCmd) runCommand(finalCmd);
      else if (modeRef.current === "dictate") targetRef.current?.focus?.();
    };
    recRef.current = rec;
    try { rec.start(); } catch { /* already started */ }
  }, [runCommand]);

  // Keyboard shortcut: Ctrl/Cmd + Shift + Space toggles the mic
  useEffect(() => {
    const onKey = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.code === "Space") { e.preventDefault(); listening ? stop() : start(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [listening, start, stop]);

  const supported = !!SR;

  return (
    <div className={`vcmd ${listening ? "live" : ""}`} data-voice-commander data-testid="voice-commander">
      {(listening || busy || lastSpoken) && (
        <div className="vcmd-panel" data-testid="voice-commander-panel">
          {listening && mode === "dictate" && <div className="vcmd-line"><Keyboard size={12} /> Dictating into <b>{fieldLabel(target)}</b>{interim ? <em> · {interim}</em> : null}</div>}
          {listening && mode === "command" && <div className="vcmd-line"><Command size={12} /> Listening for a command{interim ? <em> · {interim}</em> : <em> · e.g. "open radar", "convene the council on...", "discover grants", "compile a mission to..."</em>}</div>}
          {busy && <div className="vcmd-line"><Loader2 className="spin" size={12} /> Executing...</div>}
          {!listening && !busy && lastSpoken && <div className="vcmd-line"><Volume2 size={12} /> <span>{lastSpoken.slice(0, 220)}</span><button className="vcmd-x" onClick={() => setLastSpoken("")}>dismiss</button></div>}
        </div>
      )}
      <div className="vcmd-bar">
        <div className="vcmd-seg" role="tablist" aria-label="Mic mode">
          <button data-testid="vcmd-mode-dictate" className={mode === "dictate" ? "on" : ""} onClick={() => setMode("dictate")} title="Dictate into the focused text box"><Keyboard size={13} /> Dictate</button>
          <button data-testid="vcmd-mode-command" className={mode === "command" ? "on" : ""} onClick={() => setMode("command")} title="Speak a command ACASO executes"><Command size={13} /> Command</button>
        </div>
        <button data-testid="vcmd-mic" className={`vcmd-mic ${listening ? "on" : ""}`} onClick={() => (listening ? stop() : start())} disabled={!supported || busy}
          title={supported ? (listening ? "Stop (Ctrl+Shift+Space)" : "Start mic (Ctrl+Shift+Space)") : "Speech recognition unsupported in this browser"} aria-pressed={listening}>
          {busy ? <Loader2 className="spin" size={18} /> : listening ? <Square size={18} /> : <Mic size={18} />}
        </button>
      </div>
    </div>
  );
}

```


### `frontend/src/components/Radar.js`
```javascript
import React, { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Radar as RadarIcon, RefreshCw, Loader2, Search, Bookmark, BookmarkCheck, EyeOff, Rocket, ExternalLink,
  ShieldCheck, ShieldAlert, AlertTriangle, ChevronDown, ChevronUp, X, FileText, Mail, PenLine, Package,
  ClipboardList, Download, Sparkles, KeyRound, CheckCircle2, Clock, MapPin, Landmark, Coins, Info, Copy
} from "lucide-react";
import { API } from "../App";
import { Markdown } from "./FileAnalyzer";

const ENTITY = ["individual", "sole_proprietor", "llc", "corporation", "nonprofit", "startup", "creator", "contractor", "community_org", "university", "government"];
const TYPES = ["grant", "contract", "subcontract", "procurement", "sponsorship", "rfp", "funding", "technical_bounty"];
const SET_ASIDES = ["minority", "veteran", "sdvosb", "woman", "disability", "hubzone", "8a", "disadvantaged"];
const STAGES = ["Discovered", "Reviewed", "Qualified", "Preparing", "Submitted", "Awarded", "Not Awarded"];
const VIEWS = [
  { key: "all", label: "All open" }, { key: "high", label: "High fit" }, { key: "low", label: "Lower barrier" },
  { key: "closing", label: "Closing soon" }, { key: "new", label: "Newest" }, { key: "saved", label: "Saved" }, { key: "dismissed", label: "Dismissed" },
];
const DRAFTS = [
  { key: "email", label: "Intro email", icon: Mail },
  { key: "grant_narrative", label: "Grant narrative", icon: PenLine },
  { key: "outreach_packet", label: "Outreach packet", icon: Package },
  { key: "form_answers", label: "Fill a form", icon: ClipboardList },
];

const money = (v) => (v === null || v === undefined ? null : `$${Number(v).toLocaleString()}`);
const dateS = (iso) => { try { return iso ? new Date(iso).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" }) : null; } catch { return null; } };
const ago = (iso) => { try { const m = Math.round((Date.now() - new Date(iso)) / 60000); return m < 60 ? `${m}m ago` : m < 1440 ? `${Math.round(m / 60)}h ago` : `${Math.round(m / 1440)}d ago`; } catch { return ""; } };
const NV = <span className="rd-nv">Not verified</span>;
const listToStr = (a) => (a || []).join(", ");
const strToList = (s) => (s || "").split(",").map((x) => x.trim()).filter(Boolean);

function ScoreMeter({ score, size = "sm" }) {
  if (!score) return null;
  const t = score.total ?? 0;
  const tone = t >= 75 ? "hi" : t >= 50 ? "mid" : "lo";
  return (
    <div className={`rd-score ${size} ${tone}`} title="Inferred score - see breakdown in detail view" data-testid="rd-score">
      <div className="rd-score-bar"><span style={{ width: `${t}%` }} /></div>
      <div className="rd-score-txt"><b>{t}</b><small>/100 · {score.label} · inferred</small></div>
    </div>
  );
}

function SourceBadge({ o }) {
  const stale = o.status === "stale";
  return (
    <span className={`rd-src ${stale ? "stale" : ""}`} title={`Source: ${o.source} · retrieved ${o.retrieved_at} · HTTP ${o.http_status}`} data-testid="rd-source-badge">
      <ShieldCheck size={11} /> {o.source.replace("_", ".")} · {stale ? "STALE" : `verified ${ago(o.last_verified_at || o.retrieved_at)}`}
    </span>
  );
}

export default function Radar() {
  const [profile, setProfile] = useState(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const [sources, setSources] = useState([]);
  const [discovering, setDiscovering] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("all");
  const [filters, setFilters] = useState({ type: "", source: "", min_score: "", closing_days: "", low_barrier: false, remote: false, max_value: "", q: "" });
  const [nlq, setNlq] = useState("");
  const [nlProposal, setNlProposal] = useState(null);
  const [nlBusy, setNlBusy] = useState(false);
  const [detail, setDetail] = useState(null);

  const loadSources = useCallback(async () => { try { setSources((await axios.get(`${API}/radar/sources`)).data); } catch { /* silent */ } }, []);
  const loadProfile = useCallback(async () => { try { setProfile((await axios.get(`${API}/radar/profile`)).data); } catch { /* silent */ } }, []);

  const params = useMemo(() => {
    const p = { limit: 150 };
    if (filters.type) p.type = filters.type;
    if (filters.source) p.source = filters.source;
    if (filters.min_score) p.min_score = filters.min_score;
    if (filters.closing_days) p.closing_days = filters.closing_days;
    if (filters.low_barrier) p.low_barrier = true;
    if (filters.remote) p.remote = true;
    if (filters.max_value) p.max_value = filters.max_value;
    if (filters.q) p.q = filters.q;
    if (view === "high") p.min_score = Math.max(70, Number(p.min_score || 0));
    if (view === "low") p.low_barrier = true;
    if (view === "closing") { p.closing_days = Math.min(30, Number(p.closing_days || 30)); p.sort = "deadline"; }
    if (view === "new") p.sort = "new";
    if (view === "saved") p.saved = true;
    if (view === "dismissed") { p.user_status = "dismissed"; p.include_dismissed = true; }
    return p;
  }, [filters, view]);

  const loadItems = useCallback(async () => {
    setLoading(true);
    try { setItems((await axios.get(`${API}/radar/opportunities`, { params })).data); }
    catch { toast.error("Could not load opportunities"); }
    finally { setLoading(false); }
  }, [params]);

  useEffect(() => { loadSources(); loadProfile(); }, [loadSources, loadProfile]);
  useEffect(() => { loadItems(); }, [loadItems]);

  const discover = async () => {
    setDiscovering(true);
    try {
      const r = await axios.post(`${API}/radar/discover`, { keyword: keyword || null, limit: 20 }, { timeout: 120000 });
      const ok = r.data.runs.filter((x) => !x.error);
      const errs = r.data.runs.filter((x) => x.error);
      toast.success(`${ok.reduce((a, x) => a + x.new, 0)} new · ${ok.reduce((a, x) => a + x.updated, 0)} re-verified from ${ok.length} source(s)`);
      errs.forEach((e) => toast.warning(`${e.source}: ${e.error.split(":")[0]}`));
      loadSources(); loadItems();
    } catch (e) { toast.error(e?.response?.data?.detail || "Discovery failed"); }
    finally { setDiscovering(false); }
  };

  const saveProfile = async () => {
    try { const r = await axios.put(`${API}/radar/profile`, profile); setProfile(r.data); toast.success("Profile saved - re-run Discover to rescore"); }
    catch (e) { toast.error(e?.response?.data?.detail?.[0]?.msg || "Profile invalid"); }
  };

  const patch = async (id, body) => {
    try {
      const r = await axios.patch(`${API}/radar/opportunities/${id}`, body);
      setItems((xs) => xs.map((x) => (x.id === id ? { ...x, ...r.data, description: undefined } : x)));
      if (detail?.id === id) setDetail(r.data);
      return r.data;
    } catch { toast.error("Update failed"); }
  };

  const toMission = async (o) => {
    try {
      const r = await axios.post(`${API}/radar/opportunities/${o.id}/to-mission`, {}, { timeout: 120000 });
      toast.success(`Mission "${r.data.title}" added to Sovereign Home`, { action: { label: "Open board", onClick: () => { window.location.href = "/?tab=home"; } } });
      setItems((xs) => xs.map((x) => (x.id === o.id ? { ...x, mission_id: r.data.id, mission_title: r.data.title, stage: "Preparing" } : x)));
      if (detail?.id === o.id) setDetail((d) => ({ ...d, mission_id: r.data.id, mission_title: r.data.title, stage: "Preparing" }));
    } catch (e) { toast.error(e?.response?.data?.detail || "Could not create mission"); }
  };

  const openDetail = async (id) => {
    try { setDetail((await axios.get(`${API}/radar/opportunities/${id}`)).data); } catch { toast.error("Could not open"); }
  };

  const runNl = async () => {
    if (!nlq.trim()) return;
    setNlBusy(true);
    try { setNlProposal((await axios.post(`${API}/radar/search/nl`, { query: nlq })).data); }
    catch (e) { toast.error(e?.response?.data?.detail || "Could not interpret query"); }
    finally { setNlBusy(false); }
  };
  const applyNl = () => {
    const f = nlProposal?.proposed_filters || {};
    setFilters((cur) => ({ ...cur, type: f.type || "", source: f.source || "", min_score: f.min_score ?? "", closing_days: f.closing_days ?? "",
      low_barrier: !!f.low_barrier, remote: !!f.remote, max_value: f.max_value ?? "", q: f.q || "" }));
    setView("all"); setNlProposal(null);
    if (f.exclusions?.length) toast(`Exclusions noted (apply by eye): ${f.exclusions.join("; ")}`);
  };

  const pf = (k) => (profile?.[k] ?? "");
  const setP = (k, v) => setProfile((p) => ({ ...p, [k]: v }));
  const configured = sources.filter((s) => s.configured).length;

  return (
    <div className="rd-wrap" data-testid="radar-page">
      <div className="rd-hero">
        <div>
          <div className="rd-title"><RadarIcon size={18} /> Opportunity Radar</div>
          <p>Finds public contracts, grants, sponsorships and B2B openings that match your capabilities - and shows the <b>real requirements, effort, deadline and next step</b>. Every record comes from an official source with a URL, retrieval time and evidence excerpts. Nothing here is "easy money", and nothing is ever auto-submitted.</p>
        </div>
        <div className="rd-hero-stats">
          <div className="rd-stat"><span className="v">{items.length}</span><span className="l">in view</span></div>
          <div className="rd-stat"><span className="v">{configured}/{sources.length}</span><span className="l">sources live</span></div>
        </div>
      </div>

      <div className="rd-warn" data-testid="radar-disclaimer"><AlertTriangle size={14} /> Verify every opportunity on its original source before relying on it. Scores, fit labels and drafts are AI/heuristic inferences - they are not eligibility determinations and never predict an award.</div>

      {/* Sources + discover */}
      <div className="rd-panel">
        <div className="rd-panel-h"><Landmark size={15} /> Sources <em>official APIs first - no scraping behind logins, CAPTCHAs or rate limits</em></div>
        <div className="rd-sources">
          {sources.map((s) => (
            <div key={s.id} className={`rd-source ${s.configured ? "ok" : "off"}`} data-testid={`source-${s.id}`}>
              <div className="rd-source-top">{s.configured ? <CheckCircle2 size={13} /> : <KeyRound size={13} />} <b>{s.name}</b></div>
              <small>{s.type} · {s.active_count} active</small>
              {!s.configured && <small className="rd-needkey">needs {s.env} in backend/.env</small>}
              {s.last_run && <small>{s.last_run.error ? `last: ${s.last_run.error.split(":")[0]}` : `last: HTTP ${s.last_run.http_status} · ${s.last_run.fetched} fetched · ${ago(s.last_run.retrieved_at)}`}</small>}
            </div>
          ))}
        </div>
        <div className="rd-row">
          <input data-testid="radar-keyword" className="cw-input grow" value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Focus keyword for this run (optional - defaults to your first profile keyword)" />
          <button data-testid="radar-discover" className="rd-btn primary" onClick={discover} disabled={discovering}>
            {discovering ? <Loader2 className="spin" size={14} /> : <RefreshCw size={14} />} {discovering ? "Fetching sources..." : "Discover now"}
          </button>
          <button data-testid="radar-profile-toggle" className="rd-btn" onClick={() => setProfileOpen((o) => !o)}>
            {profileOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />} Your profile {profile?.entity_type ? `· ${profile.entity_type}` : "· not set"}
          </button>
        </div>

        <AnimatePresence>
          {profileOpen && profile && (
            <motion.div className="rd-profile" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} data-testid="radar-profile">
              <div className="rd-grid3">
                <label>Entity type<select data-testid="profile-entity" className="cw-input" value={pf("entity_type") || ""} onChange={(e) => setP("entity_type", e.target.value || null)}><option value="">Select...</option>{ENTITY.map((x) => <option key={x} value={x}>{x}</option>)}</select></label>
                <label>Organization<input className="cw-input" value={pf("org_name") || ""} onChange={(e) => setP("org_name", e.target.value)} /></label>
                <label>Service area<select className="cw-input" value={pf("service_area") || ""} onChange={(e) => setP("service_area", e.target.value || null)}><option value="">Select...</option>{["local", "state", "national", "international"].map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>State (2-letter)<input className="cw-input" value={pf("state") || ""} onChange={(e) => setP("state", e.target.value.toUpperCase())} maxLength={2} /></label>
                <label>City<input className="cw-input" value={pf("city") || ""} onChange={(e) => setP("city", e.target.value)} /></label>
                <label>Country<input className="cw-input" value={pf("country") || ""} onChange={(e) => setP("country", e.target.value)} /></label>
                <label>Industries (comma)<input data-testid="profile-industries" className="cw-input" value={listToStr(profile.industries)} onChange={(e) => setP("industries", strToList(e.target.value))} /></label>
                <label>Skills (comma)<input data-testid="profile-skills" className="cw-input" value={listToStr(profile.skills)} onChange={(e) => setP("skills", strToList(e.target.value))} /></label>
                <label>Search keywords (comma)<input data-testid="profile-keywords" className="cw-input" value={listToStr(profile.keywords)} onChange={(e) => setP("keywords", strToList(e.target.value))} /></label>
              </div>
              <button className="rd-link" onClick={() => setMoreOpen((m) => !m)}>{moreOpen ? "Hide" : "More"} fields (NAICS, certifications, set-asides, budget, time, value range...)</button>
              {moreOpen && (
                <div className="rd-grid3">
                  <label>NAICS / PSC codes (comma)<input className="cw-input" value={listToStr(profile.naics_codes)} onChange={(e) => setP("naics_codes", strToList(e.target.value))} /></label>
                  <label>Years experience<input type="number" className="cw-input" value={pf("years_experience") ?? ""} onChange={(e) => setP("years_experience", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Team size<input type="number" className="cw-input" value={pf("team_size") ?? ""} onChange={(e) => setP("team_size", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Revenue range<input className="cw-input" value={pf("revenue_range") || ""} onChange={(e) => setP("revenue_range", e.target.value)} placeholder="e.g. <$100K" /></label>
                  <label>Certifications (comma)<input className="cw-input" value={listToStr(profile.certifications)} onChange={(e) => setP("certifications", strToList(e.target.value))} /></label>
                  <label>Budget available ($)<input type="number" className="cw-input" value={pf("budget") ?? ""} onChange={(e) => setP("budget", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Hours / week<input type="number" className="cw-input" value={pf("hours_per_week") ?? ""} onChange={(e) => setP("hours_per_week", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Min value ($)<input type="number" className="cw-input" value={pf("min_value") ?? ""} onChange={(e) => setP("min_value", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Max value ($)<input type="number" className="cw-input" value={pf("max_value") ?? ""} onChange={(e) => setP("max_value", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <div className="rd-checks">
                    <span>Set-aside certifications you hold:</span>
                    {SET_ASIDES.map((s) => (
                      <label key={s} className="rd-chk"><input type="checkbox" checked={(profile.set_asides || []).includes(s)} onChange={(e) => setP("set_asides", e.target.checked ? [...(profile.set_asides || []), s] : (profile.set_asides || []).filter((x) => x !== s))} /> {s}</label>
                    ))}
                  </div>
                  <div className="rd-checks">
                    <span>Preferred types:</span>
                    {TYPES.map((s) => (
                      <label key={s} className="rd-chk"><input type="checkbox" checked={(profile.preferred_types || []).includes(s)} onChange={(e) => setP("preferred_types", e.target.checked ? [...(profile.preferred_types || []), s] : (profile.preferred_types || []).filter((x) => x !== s))} /> {s}</label>
                    ))}
                  </div>
                  <div className="rd-checks">
                    <label className="rd-chk"><input type="checkbox" checked={!!profile.nonprofit_status} onChange={(e) => setP("nonprofit_status", e.target.checked)} /> Nonprofit status</label>
                    <label className="rd-chk"><input type="checkbox" checked={!!profile.willing_travel} onChange={(e) => setP("willing_travel", e.target.checked)} /> Willing to travel</label>
                    <label className="rd-chk"><input type="checkbox" checked={!!profile.willing_subcontract} onChange={(e) => setP("willing_subcontract", e.target.checked)} /> Willing to subcontract</label>
                  </div>
                  <label className="rd-span3">Capability statement (the ONLY facts drafts may claim about you)<textarea className="cw-textarea" rows={3} value={pf("bio") || ""} onChange={(e) => setP("bio", e.target.value)} /></label>
                </div>
              )}
              <div className="rd-row"><button data-testid="profile-save" className="rd-btn primary" onClick={saveProfile}><CheckCircle2 size={14} /> Save profile</button><small className="rd-dim">No field is required. More detail = better fit and eligibility scoring.</small></div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Filters */}
      <div className="rd-panel">
        <div className="rd-views">
          {VIEWS.map((v) => <button key={v.key} data-testid={`view-${v.key}`} className={view === v.key ? "rd-chip active" : "rd-chip"} onClick={() => setView(v.key)}>{v.label}</button>)}
        </div>
        <div className="rd-filters">
          <select data-testid="filter-type" className="cw-input" value={filters.type} onChange={(e) => setFilters({ ...filters, type: e.target.value })}><option value="">Any type</option>{TYPES.map((t) => <option key={t} value={t}>{t}</option>)}</select>
          <select data-testid="filter-source" className="cw-input" value={filters.source} onChange={(e) => setFilters({ ...filters, source: e.target.value })}><option value="">Any source</option>{sources.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select>
          <input data-testid="filter-min-score" type="number" className="cw-input rd-narrow" placeholder="Min score" value={filters.min_score} onChange={(e) => setFilters({ ...filters, min_score: e.target.value })} />
          <input type="number" className="cw-input rd-narrow" placeholder="Closing ≤ days" value={filters.closing_days} onChange={(e) => setFilters({ ...filters, closing_days: e.target.value })} />
          <input type="number" className="cw-input rd-narrow" placeholder="Max value $" value={filters.max_value} onChange={(e) => setFilters({ ...filters, max_value: e.target.value })} />
          <label className="rd-chk"><input type="checkbox" checked={filters.low_barrier} onChange={(e) => setFilters({ ...filters, low_barrier: e.target.checked })} /> lower barrier</label>
          <label className="rd-chk"><input type="checkbox" checked={filters.remote} onChange={(e) => setFilters({ ...filters, remote: e.target.checked })} /> remote/national</label>
          <div className="rd-search"><Search size={13} /><input data-testid="filter-q" value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} placeholder="keyword in title / issuer / eligibility" /></div>
        </div>
        <div className="rd-row rd-nl">
          <Sparkles size={14} />
          <input data-testid="nl-query" className="cw-input grow" value={nlq} onChange={(e) => setNlq(e.target.value)} placeholder='Natural-language search, e.g. "small technology grants under $250,000 closing in the next 60 days"' onKeyDown={(e) => e.key === "Enter" && runNl()} />
          <button data-testid="nl-run" className="rd-btn" onClick={runNl} disabled={nlBusy}>{nlBusy ? <Loader2 className="spin" size={14} /> : <Search size={14} />} Propose filters</button>
        </div>
        {nlProposal && (
          <div className="rd-proposal" data-testid="nl-proposal">
            <Info size={13} /> <span>AI proposes these filters (not applied yet): <code>{JSON.stringify(nlProposal.proposed_filters)}</code></span>
            <button className="rd-btn primary sm" data-testid="nl-apply" onClick={applyNl}>Apply</button>
            <button className="rd-btn sm" onClick={() => setNlProposal(null)}>Discard</button>
          </div>
        )}
      </div>

      {/* Feed */}
      {loading ? (
        <div className="rd-empty" data-testid="radar-loading"><Loader2 className="spin" size={18} /> Loading opportunities...</div>
      ) : items.length === 0 ? (
        <div className="rd-empty" data-testid="radar-empty"><RadarIcon size={26} /><p>No opportunities match this view yet. Set your profile, then press <b>Discover now</b> to pull live records from the configured sources.</p></div>
      ) : (
        <div className="rd-feed" data-testid="radar-feed">
          {items.map((o, i) => {
            const val = o.funding_amount ?? o.estimated_value;
            const saved = ["saved", "contacted", "submitted"].includes(o.user_status);
            return (
              <motion.article key={o.id} className={`rd-card ${o.status === "stale" ? "stale" : ""}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(i, 12) * 0.03 }} data-testid={`opp-${o.id}`}>
                <div className="rd-card-top">
                  <span className={`rd-type t-${o.opportunity_type}`}>{o.opportunity_type.replace("_", " ")}</span>
                  <SourceBadge o={o} />
                  {o.user_status !== "new" && <span className="rd-ustat">{o.user_status}</span>}
                </div>
                <h3 onClick={() => openDetail(o.id)} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && openDetail(o.id)} data-testid="opp-title">{o.title}</h3>
                <div className="rd-org"><Landmark size={12} /> {o.organization_name || NV}{o.issuing_department && o.source === "github_bounties" ? <span className="rd-dim"> · {o.issuing_department}</span> : null}</div>
                <div className="rd-facts">
                  <span><Coins size={12} /> {money(val) || NV}</span>
                  <span><Clock size={12} /> {o.deadline ? <>{dateS(o.deadline)} · <b className={o.days_remaining !== null && o.days_remaining <= 14 ? "rd-urgent" : ""}>{o.days_remaining}d</b></> : NV}</span>
                  <span><MapPin size={12} /> {o.remote_status || o.location || NV}</span>
                </div>
                <ScoreMeter score={o.score} />
                <div className="rd-barrier" title={`low: ${(o.barrier?.low || []).join(", ") || "-"} | high: ${(o.barrier?.high || []).join(", ") || "-"}`}>
                  <span className={`rd-bar-lbl ${o.barrier?.label?.startsWith("lower") ? "lo" : o.barrier?.label?.startsWith("higher") ? "hi" : ""}`}>{o.barrier?.label}</span>
                  {(o.required_entity_types || []).slice(0, 2).map((t) => <span key={t} className="rd-req">{t}</span>)}
                  {o.set_aside && <span className="rd-req">{o.set_aside}</span>}
                </div>
                <div className="rd-next">{o.ai?.fit?.recommended_next_action || (o.score?.label === "Poor fit" ? "Likely skip - open detail only if the source text reads differently to you." : "Open detail, run Fit + Skeptic analysis, then verify on the original source.")}</div>
                <div className="rd-actions">
                  <button className="rd-ic" data-testid="opp-save" title={saved ? "Unsave" : "Save"} onClick={() => patch(o.id, { user_status: saved ? "new" : "saved" })}>{saved ? <BookmarkCheck size={14} /> : <Bookmark size={14} />}</button>
                  <button className="rd-ic" data-testid="opp-dismiss" title={o.user_status === "dismissed" ? "Restore" : "Dismiss"} onClick={() => patch(o.id, { user_status: o.user_status === "dismissed" ? "new" : "dismissed" })}><EyeOff size={14} /></button>
                  <button className="rd-ic" data-testid="opp-pipeline" title={o.mission_id ? `On board: ${o.mission_title}` : "Add to pipeline (Sovereign Home mission)"} onClick={() => (o.mission_id ? (window.location.href = "/?tab=home") : toMission(o))}><Rocket size={14} /></button>
                  <a className="rd-ic" data-testid="opp-source" href={o.source_url} target="_blank" rel="noreferrer" title="Open original source"><ExternalLink size={14} /></a>
                  <button className="rd-btn sm" data-testid="opp-detail" onClick={() => openDetail(o.id)}><FileText size={13} /> Detail & drafts</button>
                </div>
              </motion.article>
            );
          })}
        </div>
      )}

      <AnimatePresence>{detail && <Detail o={detail} onClose={() => setDetail(null)} patch={patch} toMission={toMission} setDetail={setDetail} />}</AnimatePresence>
    </div>
  );
}

function Detail({ o, onClose, patch, toMission, setDetail }) {
  const [analyzing, setAnalyzing] = useState(false);
  const [draftKind, setDraftKind] = useState("email");
  const [formText, setFormText] = useState("");
  const [extra, setExtra] = useState("");
  const [drafting, setDrafting] = useState(false);
  const [notes, setNotes] = useState(o.notes || "");
  const val = o.funding_amount ?? o.estimated_value;
  const ai = o.ai || {};
  const draft = (o.drafts || {})[draftKind];

  const analyze = async () => {
    setAnalyzing(true);
    try { const r = await axios.post(`${API}/radar/opportunities/${o.id}/analyze`, { include_checklist: true }, { timeout: 180000 }); setDetail({ ...o, ...r.data }); toast.success("Fit Analyst, Skeptic and Compliance Sentinel have reported"); }
    catch (e) { toast.error(e?.response?.data?.detail || "Analysis failed"); }
    finally { setAnalyzing(false); }
  };
  const makeDraft = async () => {
    setDrafting(true);
    try {
      const r = await axios.post(`${API}/radar/opportunities/${o.id}/draft`, { kind: draftKind, form_text: draftKind === "form_answers" ? formText : null, extra_instructions: extra || null }, { timeout: 180000 });
      setDetail({ ...o, drafts: { ...(o.drafts || {}), [draftKind]: r.data }, stage: ["Discovered", "Reviewed", "Qualified"].includes(o.stage) ? "Preparing" : o.stage });
      toast.success(`Draft ready - ${r.data.placeholders} [FILL] placeholder(s) need your input`);
    } catch (e) { toast.error(e?.response?.data?.detail || "Draft failed"); }
    finally { setDrafting(false); }
  };
  const copy = async (t) => { try { await navigator.clipboard.writeText(t); toast.success("Copied"); } catch { toast.error("Copy failed"); } };
  const list = (a) => (Array.isArray(a) && a.length ? <ul>{a.map((x, i) => <li key={i}>{typeof x === "string" ? x : `${x.item || JSON.stringify(x)}${x.why ? ` - ${x.why}` : ""}${x.stated_by_source === false ? " (inferred, not stated by source)" : ""}`}</li>)}</ul> : <span className="rd-dim">none listed</span>);
  const stageIdx = STAGES.indexOf(o.stage || "Discovered");

  return (
    <motion.div className="rd-modal-bg" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose} data-testid="opp-detail-modal">
      <motion.div className="rd-modal" initial={{ y: 20 }} animate={{ y: 0 }} exit={{ y: 20 }} onClick={(e) => e.stopPropagation()}>
        <div className="rd-modal-h">
          <div>
            <div className="rd-card-top"><span className={`rd-type t-${o.opportunity_type}`}>{o.opportunity_type.replace("_", " ")}</span><SourceBadge o={o} /><span className="rd-ustat">{o.user_status}</span></div>
            <h2>{o.title}</h2>
            <div className="rd-org"><Landmark size={12} /> {o.organization_name || NV} {o.issuing_department ? <span className="rd-dim">· {o.issuing_department}</span> : null}</div>
          </div>
          <div className="rd-modal-actions">
            <a className="rd-btn" href={o.source_url} target="_blank" rel="noreferrer" data-testid="detail-source"><ExternalLink size={14} /> Original source</a>
            <a className="rd-btn" href={`${API}/radar/opportunities/${o.id}/export`} target="_blank" rel="noreferrer" data-testid="detail-export"><Download size={14} /> Export .md</a>
            <button className="rd-ic" onClick={onClose} data-testid="detail-close"><X size={16} /></button>
          </div>
        </div>

        <div className="rd-warn"><AlertTriangle size={14} /> <b>Verify before acting.</b> Retrieved {dateS(o.retrieved_at)} ({ago(o.retrieved_at)}) · HTTP {o.http_status} · parser {o.parser_version} · status <b>{o.status}</b>. Confirm deadline, amount and eligibility on the original page; this app never submits anything for you.</div>

        <div className="rd-stages" data-testid="detail-stages">
          {STAGES.map((s, i) => <button key={s} className={`rd-stage ${i <= stageIdx ? "done" : ""} ${s === o.stage ? "cur" : ""}`} onClick={() => patch(o.id, { stage: s })} title="Set stage">{s}</button>)}
        </div>

        <div className="rd-detail-grid">
          <section>
            <h4>Facts from source</h4>
            <dl className="rd-dl">
              <dt>Amount</dt><dd>{money(val) || NV}{o.funding_floor ? <span className="rd-dim"> (floor {money(o.funding_floor)})</span> : null}</dd>
              <dt>Deadline</dt><dd>{o.deadline ? `${dateS(o.deadline)} · ${o.days_remaining} days` : NV}</dd>
              <dt>Posted</dt><dd>{dateS(o.posted_date) || NV}</dd>
              <dt>Location</dt><dd>{o.location || NV} {o.remote_status ? `· ${o.remote_status}` : ""}</dd>
              <dt>Applicant types</dt><dd>{listToStr(o.required_entity_types) || <span className="rd-dim">Not stated by source</span>}</dd>
              <dt>Set-aside</dt><dd>{o.set_aside || <span className="rd-dim">none stated</span>}</dd>
              <dt>Registrations</dt><dd>{listToStr(o.required_registrations) || <span className="rd-dim">Not stated</span>}</dd>
              <dt>Cost sharing</dt><dd>{o.cost_sharing === true ? "Required" : o.cost_sharing === false ? "Not required" : NV}</dd>
              <dt>Codes</dt><dd>{listToStr(o.industry_codes) || <span className="rd-dim">none</span>}</dd>
              <dt>Contact</dt><dd>{o.contact_information ? (Array.isArray(o.contact_information) ? o.contact_information.map((c, i) => <div key={i}>{c.name} {c.email && <a href={`mailto:${c.email}`}>{c.email}</a>}</div>) : <>{o.contact_information.name} {o.contact_information.email && <a href={`mailto:${o.contact_information.email}`}>{o.contact_information.email}</a>}</>) : NV}</dd>
            </dl>
            <h4>Eligibility text (verbatim from source)</h4>
            <p className="rd-quote">{o.eligibility_text || <span className="rd-dim">Not stated by source</span>}</p>
            <h4>Description (from source)</h4>
            <p className="rd-desc">{o.description || <span className="rd-dim">Not provided by source - open the original page</span>}</p>
            {o.attachments?.length > 0 && <><h4>Original documents</h4><ul>{o.attachments.map((a) => <li key={a}><a href={a} target="_blank" rel="noreferrer">{a}</a></li>)}</ul></>}
            <h4>Evidence excerpts</h4>
            <ul className="rd-evidence" data-testid="detail-evidence">{(o.evidence || []).map((e, i) => <li key={i}><b>{e.field}</b> <q>{e.excerpt}</q> <code>{e.source_location}</code></li>)}</ul>
          </section>

          <section>
            <h4>Inferred score <small>heuristic, transparent</small></h4>
            <ScoreMeter score={o.score} size="lg" />
            <div className="rd-breakdown" data-testid="detail-breakdown">
              {Object.entries(o.score?.breakdown || {}).map(([k, b]) => (
                <div key={k} className="rd-bd-row"><span>{k.replace(/_/g, " ")}</span><div className="rd-bd-bar"><span style={{ width: `${(b.points / b.weight) * 100}%` }} /></div><small>{b.points}/{b.weight}</small></div>
              ))}
            </div>
            <ul className="rd-notes">{(o.score?.notes || []).map((n, i) => <li key={i}>{n}</li>)}</ul>
            <div className="rd-lbl-note">"Appears to match stated requirements" ≠ "legally eligible" ≠ "likely to win". Strong fit requires the Skeptic to have run.</div>

            <h4>Barrier signals <small>observed in source text</small></h4>
            <div className="rd-sig"><b className="lo">Lower:</b> {(o.barrier?.low || []).join(", ") || "none observed"}</div>
            <div className="rd-sig"><b className="hi">Higher:</b> {(o.barrier?.high || []).join(", ") || "none observed"}</div>

            <h4>AI personas <small>on demand · inferred</small></h4>
            <button className="rd-btn primary" onClick={analyze} disabled={analyzing} data-testid="detail-analyze">{analyzing ? <Loader2 className="spin" size={14} /> : <Sparkles size={14} />} {ai.fit ? "Re-run" : "Run"} Fit Analyst + Skeptic + Compliance Sentinel</button>
            {ai.fit && (
              <div className="rd-ai" data-testid="detail-fit">
                <div className="rd-ai-h"><ShieldCheck size={13} /> Fit Analyst <small>{ai.fit.model_label}</small></div>
                <p>{ai.fit.summary}</p>
                <div className="rd-two"><div><b>Why it may fit</b>{list(ai.fit.why_it_may_fit)}</div><div><b>Why it may not</b>{list(ai.fit.why_it_may_not_fit)}</div></div>
                <div><b>Matches stated requirements:</b> {String(ai.fit.appears_to_match_stated_requirements)} · <b>Effort:</b> {ai.fit.effort_estimate}</div>
                <div><b>Missing information</b>{list(ai.fit.missing_information)}</div>
                <div className="rd-next"><b>Next action:</b> {ai.fit.recommended_next_action}</div>
              </div>
            )}
            {ai.skeptic && (
              <div className={`rd-ai skeptic v-${ai.skeptic.verdict}`} data-testid="detail-skeptic">
                <div className="rd-ai-h"><ShieldAlert size={13} /> Skeptic <small>{ai.skeptic.model_label}</small> <span className="rd-verdict">{ai.skeptic.verdict}</span></div>
                <div><b>Concerns</b>{list(ai.skeptic.concerns)}</div>
                <div><b>Missing requirements</b>{list(ai.skeptic.missing_requirements)}</div>
                <div><b>Stale / suspicious</b>{list(ai.skeptic.stale_or_suspicious)}</div>
                <div><b>Verify at source</b>{list(ai.skeptic.verify_at_source)}</div>
              </div>
            )}
            {ai.checklist && (
              <div className="rd-ai" data-testid="detail-checklist">
                <div className="rd-ai-h"><ClipboardList size={13} /> Compliance Sentinel + Proposal Architect <small>{ai.checklist.model_label}</small></div>
                <div><b>Preparation checklist</b>{list(ai.checklist.preparation_checklist)}</div>
                <div><b>Questions for the contracting officer / funder</b>{list(ai.checklist.questions_for_contracting_officer_or_funder)}</div>
                <div><b>Proposal outline</b>{list(ai.checklist.proposal_outline)}</div>
              </div>
            )}

            <h4>Similar open opportunities</h4>
            <ul className="rd-similar">{(o.similar || []).map((s) => <li key={s.id}>{s.title} <small>{s.organization_name} · {s.score?.total}</small></li>)}{!o.similar?.length && <li className="rd-dim">none</li>}</ul>
          </section>
        </div>

        {/* Drafting desk */}
        <div className="rd-desk" data-testid="drafting-desk">
          <div className="rd-panel-h"><PenLine size={15} /> Drafting Desk <em>drafts use only your profile + the source text; unknowns become [FILL: ...] - you review and submit manually</em></div>
          <div className="rd-views">
            {DRAFTS.map((d) => { const I = d.icon; return <button key={d.key} data-testid={`draft-${d.key}`} className={draftKind === d.key ? "rd-chip active" : "rd-chip"} onClick={() => setDraftKind(d.key)}><I size={13} /> {d.label}{(o.drafts || {})[d.key] ? " ✓" : ""}</button>; })}
          </div>
          {draftKind === "form_answers" && <textarea data-testid="draft-form-text" className="cw-textarea" rows={5} value={formText} onChange={(e) => setFormText(e.target.value)} placeholder="Paste the application or form questions here, one per line..." />}
          <div className="rd-row">
            <input className="cw-input grow" value={extra} onChange={(e) => setExtra(e.target.value)} placeholder="Optional instructions (tone, emphasis, length)..." />
            <button className="rd-btn primary" data-testid="draft-generate" onClick={makeDraft} disabled={drafting || (draftKind === "form_answers" && !formText.trim())}>{drafting ? <Loader2 className="spin" size={14} /> : <Sparkles size={14} />} {draft ? "Regenerate" : "Generate"} {DRAFTS.find((d) => d.key === draftKind)?.label}</button>
          </div>
          {draft && (
            <div className="rd-draft" data-testid="draft-output">
              <div className="rd-draft-h"><span>{draft.model_label} · {ago(draft.generated_at)} · <b className={draft.placeholders ? "rd-urgent" : ""}>{draft.placeholders} [FILL] placeholder(s)</b></span><button className="rd-btn sm" onClick={() => copy(draft.content)}><Copy size={13} /> Copy</button></div>
              <Markdown text={draft.content} />
            </div>
          )}
        </div>

        <div className="rd-notes-box">
          <h4>Your notes</h4>
          <textarea data-testid="detail-notes" className="cw-textarea" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Calls made, documents gathered, questions asked..." />
          <div className="rd-row">
            <button className="rd-btn" data-testid="notes-save" onClick={() => patch(o.id, { notes })}><CheckCircle2 size={14} /> Save notes</button>
            <button className="rd-btn" data-testid="mark-contacted" onClick={() => patch(o.id, { user_status: "contacted" })}>Mark contacted</button>
            <button className="rd-btn" data-testid="mark-submitted" onClick={() => patch(o.id, { user_status: "submitted" })}>Mark submitted (by you)</button>
            <button className="rd-btn primary" data-testid="detail-pipeline" onClick={() => (o.mission_id ? (window.location.href = "/?tab=home") : toMission(o))}><Rocket size={14} /> {o.mission_id ? `On board: ${o.mission_title}` : "Add to pipeline"}</button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

```


### `backend/radar.py`
```python
"""
ACASO Opportunity Radar - real public-opportunity discovery with strict data integrity.

Rules enforced here:
  * AI never invents an opportunity, amount, deadline, agency or eligibility rule. Adapters only
    normalize what a source returned; every record carries source_url, retrieved_at, http_status,
    parser_version and evidence excerpts with a source_location for each important field.
  * Unknown fields stay None and are rendered "Not verified" by the UI.
  * Scores and classifications are explicitly labelled as inferred, with a full breakdown.
  * "Strong fit" requires the Skeptic persona to have run and not blocked.
  * Drafts (emails, grant narratives, packets, form answers) use only the owner's profile and the
    opportunity's source text; anything unknown becomes a [FILL: ...] placeholder. No auto-submission.
"""
import asyncio
import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Callable, Awaitable

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("radar")
router = APIRouter(prefix="/radar")

PARSER_VERSION = "radar-1.0"
UA = "ACASO-Opportunity-Radar/1.0 (+public data client; contact owner)"

# injected by server.py
db = None
llm_call_failover: Optional[Callable[..., Awaitable]] = None
compile_mission_from_text: Optional[Callable[..., Awaitable]] = None
extract_json: Optional[Callable] = None


def init(_db, _llm_failover, _compile_mission, _extract_json):
    global db, llm_call_failover, compile_mission_from_text, extract_json
    db, llm_call_failover, compile_mission_from_text, extract_json = _db, _llm_failover, _compile_mission, _extract_json


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ----------------------------------------------------------------------------------------------
# Profile
# ----------------------------------------------------------------------------------------------
ENTITY_TYPES = ["individual", "sole_proprietor", "llc", "corporation", "nonprofit", "startup", "creator",
                "contractor", "community_org", "government", "university"]
OPP_TYPES = ["grant", "contract", "subcontract", "procurement", "sponsorship", "rfp", "funding", "technical_bounty"]


class RadarProfile(BaseModel):
    id: str = "owner"
    entity_type: Optional[str] = None
    org_name: Optional[str] = None
    country: Optional[str] = "US"
    state: Optional[str] = None
    city: Optional[str] = None
    service_area: Optional[str] = None  # local | state | national | international
    industries: List[str] = []
    naics_codes: List[str] = []
    skills: List[str] = []
    keywords: List[str] = []
    years_experience: Optional[int] = None
    revenue_range: Optional[str] = None
    team_size: Optional[int] = None
    certifications: List[str] = []
    set_asides: List[str] = []  # minority, veteran, woman, disability, hubzone, 8a, sdvosb, disadvantaged
    nonprofit_status: Optional[bool] = None
    budget: Optional[float] = None
    hours_per_week: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    willing_travel: Optional[bool] = None
    willing_subcontract: Optional[bool] = None
    preferred_types: List[str] = []
    bio: Optional[str] = None  # owner-written capability statement; used verbatim as the only "claims" source
    updated_at: str = Field(default_factory=now_iso)


async def get_profile() -> dict:
    doc = await db.radar_profile.find_one({"id": "owner"}, {"_id": 0})
    return doc or RadarProfile().model_dump()


@router.get("/profile")
async def read_profile():
    return await get_profile()


@router.put("/profile")
async def write_profile(p: RadarProfile):
    p.id = "owner"
    p.updated_at = now_iso()
    await db.radar_profile.update_one({"id": "owner"}, {"$set": p.model_dump()}, upsert=True)
    return p


# ----------------------------------------------------------------------------------------------
# Helpers: text, money, dates, evidence
# ----------------------------------------------------------------------------------------------
MONEY_RE = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(k|m|million|thousand)?", re.I)


def parse_money(text: str):
    if not text:
        return None, None
    m = MONEY_RE.search(text)
    if not m:
        return None, None
    n = float(m.group(1).replace(",", ""))
    suf = (m.group(2) or "").lower()
    if suf in ("k", "thousand"):
        n *= 1_000
    elif suf in ("m", "million"):
        n *= 1_000_000
    start = max(0, m.start() - 60)
    return n, text[start:m.end() + 60].strip()


def parse_date(s):
    if not s:
        return None
    s = str(s).strip()
    fmts = ["%m/%d/%Y", "%b %d, %Y %I:%M:%S %p", "%b %d, %Y", "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"]
    s2 = re.sub(r"\s(EDT|EST|CDT|CST|MDT|MST|PDT|PST)$", "", s)
    for f in fmts:
        for cand in (s, s2):
            try:
                d = datetime.strptime(cand, f)
                if d.tzinfo is None:
                    d = d.replace(tzinfo=timezone.utc)
                return d.isoformat()
            except Exception:
                continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).isoformat()
    except Exception:
        return None


def days_until(iso):
    if not iso:
        return None
    try:
        d = datetime.fromisoformat(iso)
        return (d - datetime.now(timezone.utc)).days
    except Exception:
        return None


def ev(field, excerpt, location):
    if excerpt is None or excerpt == "":
        return None
    return {"field": field, "excerpt": str(excerpt)[:400], "source_location": location}


def strip_html(t):
    if not t:
        return ""
    t = re.sub(r"<[^>]+>", " ", str(t))
    return re.sub(r"\s+", " ", t).strip()


def dedupe_key(source, source_id, title, org, deadline):
    if source_id:
        return f"{source}:{source_id}"
    base = f"{re.sub(r'[^a-z0-9]', '', (title or '').lower())[:80]}|{(org or '').lower()[:40]}|{deadline or ''}"
    return "h:" + hashlib.sha1(base.encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
# Barrier signals (observable text only)
# ----------------------------------------------------------------------------------------------
LOW_SIGNALS = [
    ("micro-purchase", r"micro[- ]?purchase"),
    ("simplified acquisition", r"simplified acquisition"),
    ("request for quote", r"\brfq\b|request for quot"),
    ("small business set-aside", r"small business set[- ]aside|total small business"),
    ("no cost sharing", r"cost sharing[^.]{0,20}(no|not required)"),
    ("beginner-friendly label", r"good first issue|beginner|starter|easy"),
    ("subcontracting opportunity", r"subcontract"),
    ("remote/virtual delivery", r"\bremote\b|virtual"),
    ("open registration", r"open (vendor )?registration|register (as|to become) a vendor"),
]
HIGH_SIGNALS = [
    ("past performance required", r"past performance"),
    ("bonding requirement", r"\bbond(ing)?\b"),
    ("security clearance", r"security clearance|top secret|\bsecret\b clearance"),
    ("insurance requirement", r"insurance"),
    ("cost sharing / matching funds", r"cost[- ]sharing (is )?required|matching (funds|requirement)|\bmatch\b required"),
    ("restricted to governments/institutions", r"only (state|local|tribal) governments|institutions of higher education only|eligible applicants are (state|county|city)"),
    ("large staffing", r"minimum of \d{2,} (staff|employees|personnel)"),
    ("clinical trial", r"clinical trial"),
    ("in-person delivery", r"on[- ]site|in[- ]person"),
]


def barrier_signals(text: str, value, cost_sharing):
    t = (text or "").lower()
    low, high = [], []
    for name, rx in LOW_SIGNALS:
        if re.search(rx, t):
            low.append(name)
    for name, rx in HIGH_SIGNALS:
        if re.search(rx, t):
            high.append(name)
    if cost_sharing is True and "cost sharing / matching funds" not in high:
        high.append("cost sharing / matching funds")
    if cost_sharing is False and "no cost sharing" not in low:
        low.append("no cost sharing")
    if value is not None:
        if value <= 25_000:
            low.append("small dollar value")
        elif value >= 1_000_000:
            high.append("large dollar value")
    score = 0.5 + 0.12 * len(low) - 0.15 * len(high)
    score = max(0.0, min(1.0, score))
    label = "lower observed barrier" if score >= 0.6 else ("higher observed barrier" if score <= 0.35 else "mixed barrier signals")
    return {"low": low, "high": high, "score": round(score, 2), "label": label}


# ----------------------------------------------------------------------------------------------
# Scoring (transparent, 0-100, labelled inferred)
# ----------------------------------------------------------------------------------------------
WEIGHTS = {"profile_fit": 30, "eligibility_confidence": 20, "barrier": 15, "deadline_feasibility": 10,
           "effort_to_value": 10, "geographic_fit": 5, "competition": 5, "source_freshness": 5}

ENTITY_MAP = {  # profile entity -> words that indicate match in required entity types text
    "nonprofit": ["nonprofit", "non-profit", "501"],
    "llc": ["small business", "for-profit", "for profit", "business"],
    "corporation": ["small business", "for-profit", "for profit", "business"],
    "sole_proprietor": ["small business", "individual", "for-profit", "business"],
    "individual": ["individual", "unrestricted", "others"],
    "startup": ["small business", "for-profit", "business"],
    "creator": ["individual", "small business"],
    "contractor": ["small business", "for-profit", "business"],
    "community_org": ["nonprofit", "community", "others"],
    "university": ["institutions of higher education", "university"],
    "government": ["state governments", "county governments", "city or township", "government"],
}


def tokens(s):
    return {w for w in re.findall(r"[a-z0-9]{3,}", (s or "").lower())}


def score_opportunity(o: dict, profile: dict) -> dict:
    notes = []
    text = " ".join(filter(None, [o.get("title"), o.get("description"), o.get("eligibility_text"),
                                  " ".join(o.get("keywords") or []), " ".join(o.get("industry_codes") or [])]))
    tt = tokens(text)

    # profile fit
    prof_terms = set()
    for k in ("skills", "industries", "keywords", "naics_codes"):
        for v in profile.get(k) or []:
            prof_terms |= tokens(v)
    if not prof_terms:
        fit = 0.4
        notes.append("Profile has no skills/industries/keywords yet - fit defaulted to 0.4")
    else:
        hits = len(prof_terms & tt)
        fit = min(1.0, hits / 4.0)
        if hits:
            notes.append(f"{hits} profile term(s) appear in the source text")
    pref = profile.get("preferred_types") or []
    if pref and o.get("opportunity_type") in pref:
        fit = min(1.0, fit + 0.15)

    # eligibility confidence
    req = " ".join(o.get("required_entity_types") or []).lower()
    et = profile.get("entity_type")
    if not req:
        elig = 0.5
        notes.append("Eligibility not stated by source - Not verified")
    elif not et:
        elig = 0.5
        notes.append("Set your entity type to evaluate eligibility")
    else:
        words = ENTITY_MAP.get(et, [])
        if any(w in req for w in words) or "unrestricted" in req:
            elig = 0.9
            notes.append("Your entity type appears in the stated applicant types")
        else:
            elig = 0.2
            notes.append("Stated applicant types do not appear to include your entity type")
    sa = (o.get("set_aside") or "").lower()
    if sa and sa not in ("none", "n/a"):
        mine = [s.lower() for s in profile.get("set_asides") or []]
        if any(k in sa for k in ("women", "woman")) and "woman" not in mine:
            elig = min(elig, 0.25); notes.append("Set-aside requires woman-owned status not in your profile")
        if "veteran" in sa and not any("veteran" in m or "sdvosb" in m for m in mine):
            elig = min(elig, 0.25); notes.append("Set-aside requires veteran-owned status not in your profile")
        if "8(a)" in sa and "8a" not in mine:
            elig = min(elig, 0.25); notes.append("Set-aside requires 8(a) certification not in your profile")
        if "hubzone" in sa and "hubzone" not in mine:
            elig = min(elig, 0.25); notes.append("Set-aside requires HUBZone certification not in your profile")

    barrier = (o.get("barrier") or {}).get("score", 0.5)

    d = days_until(o.get("deadline"))
    if d is None:
        dl = 0.5; notes.append("No deadline stated - Not verified")
    elif d < 0:
        dl = 0.0; notes.append("Deadline has passed")
    elif d < 3:
        dl = 0.1
    elif d < 14:
        dl = 0.5
    elif d < 45:
        dl = 0.8
    else:
        dl = 1.0

    val = o.get("estimated_value") if o.get("estimated_value") is not None else o.get("funding_amount")
    mn, mx = profile.get("min_value"), profile.get("max_value")
    if val is None:
        e2v = 0.5; notes.append("Value/amount not stated - Not verified")
    elif mn is not None and val < mn:
        e2v = 0.3
    elif mx is not None and val > mx:
        e2v = 0.6
    else:
        e2v = 1.0

    rs = (o.get("remote_status") or "").lower()
    loc = (o.get("location") or "").lower()
    st = (profile.get("state") or "").lower()
    if rs in ("remote", "national", "international"):
        geo = 1.0
    elif st and st in loc:
        geo = 1.0
    elif not loc:
        geo = 0.5
    else:
        geo = 0.2 if not profile.get("willing_travel") else 0.6

    if sa and sa not in ("none", "n/a"):
        comp = 0.8
    elif o.get("opportunity_type") == "technical_bounty":
        comp = 0.5
    elif o.get("opportunity_type") == "grant":
        comp = 0.4
    else:
        comp = 0.5

    try:
        age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(o["retrieved_at"])).total_seconds() / 3600
    except Exception:
        age_h = 999
    fresh = 1.0 if (age_h < 24 and o.get("http_status") == 200) else (0.6 if age_h < 24 * 7 else 0.3)

    comps = {"profile_fit": fit, "eligibility_confidence": elig, "barrier": barrier, "deadline_feasibility": dl,
             "effort_to_value": e2v, "geographic_fit": geo, "competition": comp, "source_freshness": fresh}
    breakdown = {k: {"weight": WEIGHTS[k], "value": round(v, 2), "points": round(WEIGHTS[k] * v, 1)} for k, v in comps.items()}
    total = round(sum(b["points"] for b in breakdown.values()))

    skeptic = ((o.get("ai") or {}).get("skeptic") or {})
    if total >= 75:
        if skeptic.get("verdict") in ("clear", "caution"):
            label = "Strong fit"
        elif skeptic.get("verdict") == "block":
            label = "Needs verification"
        else:
            label = "Possible fit (Skeptic pending)"
    elif total >= 50:
        label = "Needs verification" if elig == 0.5 else "Possible fit"
    else:
        label = "Poor fit"
    return {"total": total, "label": label, "breakdown": breakdown, "notes": notes, "inferred": True,
            "eligibility_confidence": round(elig, 2), "scored_at": now_iso()}


# ----------------------------------------------------------------------------------------------
# Source adapters
# ----------------------------------------------------------------------------------------------
class SourceResult:
    def __init__(self, source, url, access_method):
        self.source, self.url, self.access_method = source, url, access_method
        self.http_status = None
        self.error = None
        self.records: List[dict] = []
        self.started = now_iso()
        self.usage_notes = ""


def profile_keywords(profile: dict, fallback: str) -> str:
    """One focused phrase per run: first keyword, else first skill, else first industry (broad ORs return noise)."""
    for k in ("keywords", "skills", "industries"):
        vals = profile.get(k) or []
        if vals:
            return str(vals[0])
    return fallback


async def adapter_grants_gov(profile: dict, keyword: Optional[str], limit: int) -> SourceResult:
    res = SourceResult("grants_gov", "https://api.grants.gov/v1/api/search2", "official public REST API (no key)")
    res.usage_notes = "Grants.gov public search API; detail via fetchOpportunity. Verify on grants.gov before applying."
    kw = keyword or profile_keywords(profile, "small business technology")
    payload = {"keyword": kw, "oppStatuses": "posted", "rows": min(limit, 50), "sortBy": "openDate|desc"}
    try:
        async with httpx.AsyncClient(timeout=25, headers={"User-Agent": UA}) as cx:
            r = await cx.post(res.url, json=payload)
            res.http_status = r.status_code
            r.raise_for_status()
            hits = (r.json().get("data") or {}).get("oppHits") or []
            sem = asyncio.Semaphore(4)

            async def detail(h):
                async with sem:
                    try:
                        d = await cx.post("https://api.grants.gov/v1/api/fetchOpportunity", json={"opportunityId": int(h["id"])})
                        return h, (d.json().get("data") or {}) if d.status_code == 200 else {}
                    except Exception as e:
                        logger.warning(f"grants detail {h.get('id')} failed: {e}")
                        return h, {}

            pairs = await asyncio.gather(*[detail(h) for h in hits[:limit]])
        retrieved = now_iso()
        for h, d in pairs:
            syn = d.get("synopsis") or {}
            oid = str(h.get("id"))
            src_url = f"https://www.grants.gov/search-results-detail/{oid}"
            desc = strip_html(syn.get("synopsisDesc"))
            elig_text = strip_html(syn.get("applicantEligibilityDesc"))
            app_types = [a.get("description") for a in (syn.get("applicantTypes") or []) if a.get("description")]
            ceiling = syn.get("awardCeiling")
            floor = syn.get("awardFloor")
            amt = None
            if ceiling not in (None, "", "none"):
                try:
                    amt = float(str(ceiling).replace(",", "").replace("$", ""))
                except Exception:
                    amt = None
            deadline = parse_date(syn.get("responseDate") or h.get("closeDate"))
            evidence = [x for x in [
                ev("title", h.get("title"), "search2.oppHits[].title"),
                ev("organization_name", h.get("agency"), "search2.oppHits[].agency"),
                ev("deadline", syn.get("responseDate") or h.get("closeDate"), "synopsis.responseDate | oppHits[].closeDate"),
                ev("funding_amount", f"awardCeiling={ceiling} awardFloor={floor}" if (ceiling or floor) else None, "synopsis.awardCeiling/awardFloor"),
                ev("required_entity_types", "; ".join(app_types) if app_types else None, "synopsis.applicantTypes[].description"),
                ev("eligibility_text", elig_text[:400] if elig_text else None, "synopsis.applicantEligibilityDesc"),
                ev("description", desc[:400] if desc else None, "synopsis.synopsisDesc"),
                ev("cost_sharing", syn.get("costSharing"), "synopsis.costSharing"),
            ] if x]
            contact = {k: v for k, v in {"name": syn.get("agencyContactName"), "email": syn.get("agencyContactEmail"),
                                        "phone": syn.get("agencyContactPhone")}.items() if v}
            res.records.append({
                "source": "grants_gov", "source_id": oid, "source_url": src_url, "submission_url": src_url,
                "title": h.get("title"), "description": desc or None, "opportunity_type": "grant",
                "organization_name": h.get("agency") or syn.get("agencyName"), "organization_type": "federal agency",
                "issuing_department": h.get("agencyCode"), "location": "United States", "remote_status": "national",
                "estimated_value": None, "funding_amount": amt, "funding_floor": floor if floor not in ("", "none") else None,
                "currency": "USD", "posted_date": parse_date(h.get("openDate") or syn.get("postingDate")), "deadline": deadline,
                "eligibility_text": elig_text or None, "required_entity_types": app_types, "required_certifications": [],
                "required_registrations": ["SAM.gov UEI registration (standard for federal grants - verify)", "Grants.gov applicant account (verify)"],
                "required_experience": None, "industry_codes": h.get("cfdaList") or [],
                "keywords": [c.get("description") for c in (syn.get("fundingActivityCategories") or []) if c.get("description")],
                "set_aside": None, "cost_sharing": syn.get("costSharing"), "contact_information": contact or None,
                "attachments": [u for u in (d.get("synopsisDocumentURLs") or []) if isinstance(u, str)][:5],
                "evidence": evidence, "source_reliability": "official government API", "http_status": res.http_status,
                "retrieved_at": retrieved, "raw_status": h.get("oppStatus"),
            })
    except Exception as e:
        res.error = str(e)[:400]
        logger.error(f"grants_gov adapter failed: {e}")
    return res


async def adapter_sam_gov(profile: dict, keyword: Optional[str], limit: int) -> SourceResult:
    res = SourceResult("sam_gov", "https://api.sam.gov/opportunities/v2/search", "official REST API (api.data.gov key)")
    res.usage_notes = "Requires SAM_GOV_API_KEY (free at api.data.gov / sam.gov account). Rate-limited by SAM.gov."
    key = os.environ.get("SAM_GOV_API_KEY")
    if not key:
        res.error = "not_configured: set SAM_GOV_API_KEY in backend/.env (free key from your SAM.gov account -> Account Details -> API key)"
        return res
    today = datetime.now(timezone.utc)
    params = {"api_key": key, "limit": min(limit, 50), "postedFrom": (today - timedelta(days=30)).strftime("%m/%d/%Y"),
              "postedTo": today.strftime("%m/%d/%Y"), "ptype": "o,k,p", "active": "true"}
    kw = keyword or profile_keywords(profile, "")
    if kw:
        params["title"] = kw
    if profile.get("naics_codes"):
        params["ncode"] = profile["naics_codes"][0]
    if profile.get("state") and (profile.get("service_area") in ("local", "state")):
        params["state"] = profile["state"]
    try:
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": UA}) as cx:
            r = await cx.get(res.url, params=params)
            res.http_status = r.status_code
            r.raise_for_status()
            data = r.json().get("opportunitiesData") or []
            retrieved = now_iso()
            for o in data[:limit]:
                nid = o.get("noticeId")
                ui = o.get("uiLink") or f"https://sam.gov/opp/{nid}/view"
                pop = o.get("placeOfPerformance") or {}
                loc = ", ".join(filter(None, [(pop.get("city") or {}).get("name"), (pop.get("state") or {}).get("code")])) or None
                contacts = [{"name": c.get("fullName"), "email": c.get("email"), "phone": c.get("phone"), "type": c.get("type")}
                            for c in (o.get("pointOfContact") or []) if c.get("email") or c.get("fullName")]
                sa = o.get("typeOfSetAsideDescription")
                evidence = [x for x in [
                    ev("title", o.get("title"), "opportunitiesData[].title"),
                    ev("organization_name", o.get("fullParentPathName"), "opportunitiesData[].fullParentPathName"),
                    ev("deadline", o.get("responseDeadLine"), "opportunitiesData[].responseDeadLine"),
                    ev("set_aside", sa, "opportunitiesData[].typeOfSetAsideDescription"),
                    ev("industry_codes", o.get("naicsCode"), "opportunitiesData[].naicsCode"),
                    ev("notice_type", o.get("type"), "opportunitiesData[].type"),
                    ev("location", loc, "opportunitiesData[].placeOfPerformance"),
                ] if x]
                res.records.append({
                    "source": "sam_gov", "source_id": nid, "source_url": ui, "submission_url": ui,
                    "title": o.get("title"), "description": None, "opportunity_type": "contract",
                    "organization_name": o.get("fullParentPathName"), "organization_type": "federal agency",
                    "issuing_department": (o.get("fullParentPathName") or "").split(".")[-1] or None,
                    "location": loc, "remote_status": None, "estimated_value": None, "funding_amount": None, "currency": "USD",
                    "posted_date": parse_date(o.get("postedDate")), "deadline": parse_date(o.get("responseDeadLine")),
                    "eligibility_text": (f"Set-aside: {sa}" if sa else None), "required_entity_types": (["small business"] if sa and "small business" in sa.lower() else []),
                    "required_certifications": [], "required_registrations": ["Active SAM.gov entity registration (UEI) - verify"],
                    "required_experience": None, "industry_codes": [c for c in [o.get("naicsCode"), o.get("classificationCode")] if c],
                    "keywords": [o.get("type")] if o.get("type") else [], "set_aside": sa, "cost_sharing": None,
                    "contact_information": contacts or None, "attachments": [], "notice_type": o.get("type"),
                    "solicitation_number": o.get("solicitationNumber"),
                    "evidence": evidence, "source_reliability": "official government API", "http_status": res.http_status,
                    "retrieved_at": retrieved, "raw_status": "active" if str(o.get("active")).lower() == "yes" else o.get("active"),
                })
    except Exception as e:
        res.error = str(e)[:400]
        logger.error(f"sam_gov adapter failed: {e}")
    return res


async def adapter_github_bounties(profile: dict, keyword: Optional[str], limit: int) -> SourceResult:
    res = SourceResult("github_bounties", "https://api.github.com/search/issues", "official public REST API (optional GITHUB_TOKEN)")
    res.usage_notes = "GitHub issue search for open issues labelled bounty. 10 req/min unauthenticated. Amounts are extracted from issue text and marked as such."
    q = "label:bounty state:open is:issue"
    kw = keyword or " ".join((profile.get("skills") or [])[:2])
    if kw:
        q += f" {kw}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": UA}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    try:
        async with httpx.AsyncClient(timeout=25, headers=headers) as cx:
            r = await cx.get(res.url, params={"q": q, "sort": "created", "order": "desc", "per_page": min(limit, 30)})
            res.http_status = r.status_code
            r.raise_for_status()
            items = r.json().get("items") or []
        retrieved = now_iso()
        for it in items[:limit]:
            body = (it.get("body") or "")[:3000]
            amt, amt_ev = parse_money(it.get("title") or "")
            if amt is None:
                amt, amt_ev = parse_money(body)
            repo = (it.get("repository_url") or "").replace("https://api.github.com/repos/", "")
            labels = [l.get("name") for l in (it.get("labels") or []) if l.get("name")]
            evidence = [x for x in [
                ev("title", it.get("title"), "issue.title"),
                ev("estimated_value", amt_ev, "issue.title/body (regex-extracted $ amount)"),
                ev("labels", ", ".join(labels), "issue.labels[].name"),
                ev("description", strip_html(body)[:400], "issue.body"),
            ] if x]
            res.records.append({
                "source": "github_bounties", "source_id": str(it.get("id")), "source_url": it.get("html_url"), "submission_url": it.get("html_url"),
                "title": it.get("title"), "description": strip_html(body)[:2000] or None, "opportunity_type": "technical_bounty",
                "organization_name": repo.split("/")[0] if repo else None, "organization_type": "open-source project",
                "issuing_department": repo or None, "location": None, "remote_status": "remote",
                "estimated_value": amt, "funding_amount": None, "currency": "USD" if amt else None,
                "posted_date": parse_date(it.get("created_at")), "deadline": None, "eligibility_text": None,
                "required_entity_types": ["individual", "unrestricted"], "required_certifications": [], "required_registrations": ["GitHub account"],
                "required_experience": None, "industry_codes": [], "keywords": labels, "set_aside": None, "cost_sharing": None,
                "contact_information": None, "attachments": [], "evidence": evidence,
                "source_reliability": "official platform API (community-posted bounty; payout terms unverified)",
                "http_status": res.http_status, "retrieved_at": retrieved, "raw_status": it.get("state"),
            })
    except Exception as e:
        res.error = str(e)[:400]
        logger.error(f"github adapter failed: {e}")
    return res


ADAPTERS = {"grants_gov": adapter_grants_gov, "sam_gov": adapter_sam_gov, "github_bounties": adapter_github_bounties}
SOURCE_META = {
    "grants_gov": {"name": "Grants.gov", "type": "federal grants", "needs_key": False},
    "sam_gov": {"name": "SAM.gov Contract Opportunities", "type": "federal contracts", "needs_key": True, "env": "SAM_GOV_API_KEY"},
    "github_bounties": {"name": "GitHub bounty issues", "type": "technical bounties", "needs_key": False, "env": "GITHUB_TOKEN (optional)"},
}


@router.get("/sources")
async def list_sources():
    out = []
    for k, meta in SOURCE_META.items():
        last = await db.radar_source_runs.find_one({"source": k}, {"_id": 0}, sort=[("retrieved_at", -1)])
        configured = True
        if meta.get("needs_key"):
            configured = bool(os.environ.get(meta["env"]))
        count = await db.radar_opportunities.count_documents({"source": k, "status": {"$ne": "closed"}})
        out.append({"id": k, **meta, "configured": configured, "last_run": last, "active_count": count})
    return out


# ----------------------------------------------------------------------------------------------
# Pipeline: validate -> dedupe -> barrier -> score -> persist -> stale marking
# ----------------------------------------------------------------------------------------------
def validate(rec: dict) -> Optional[str]:
    if not rec.get("title"):
        return "missing title"
    if not rec.get("source_url") or not str(rec["source_url"]).startswith("http"):
        return "missing source_url"
    if not rec.get("retrieved_at"):
        return "missing retrieved_at"
    return None


class DiscoverRequest(BaseModel):
    sources: Optional[List[str]] = None
    keyword: Optional[str] = None
    limit: int = 20


@router.post("/discover")
async def discover(req: DiscoverRequest):
    profile = await get_profile()
    names = [s for s in (req.sources or list(ADAPTERS)) if s in ADAPTERS]
    if not names:
        raise HTTPException(400, "no valid sources")
    limit = max(1, min(req.limit, 50))
    results: List[SourceResult] = await asyncio.gather(*[ADAPTERS[n](profile, req.keyword, limit) for n in names])
    summary = []
    for res in results:
        fetched = len(res.records)
        new = updated = invalid = dup = 0
        for rec in res.records:
            err = validate(rec)
            if err:
                invalid += 1
                continue
            key = dedupe_key(rec["source"], rec.get("source_id"), rec.get("title"), rec.get("organization_name"), rec.get("deadline"))
            rec["dedupe_key"] = key
            rec["parser_version"] = PARSER_VERSION
            rec["last_verified_at"] = rec["retrieved_at"]
            text_blob = " ".join(filter(None, [rec.get("title"), rec.get("description"), rec.get("eligibility_text"), rec.get("set_aside")]))
            rec["barrier"] = barrier_signals(text_blob, rec.get("estimated_value") or rec.get("funding_amount"), rec.get("cost_sharing"))
            d = days_until(rec.get("deadline"))
            rec["status"] = "closed" if (d is not None and d < 0) else "open"
            existing = await db.radar_opportunities.find_one({"$or": [{"dedupe_key": key}, {"source_url": rec["source_url"]}]}, {"_id": 0})
            if existing:
                # cross-source near-duplicate check by title+org
                merged = {**existing, **{k: v for k, v in rec.items() if v not in (None, [], "")}}
                merged["score"] = score_opportunity(merged, profile)
                merged["updated_at"] = now_iso()
                await db.radar_opportunities.update_one({"id": existing["id"]}, {"$set": merged})
                updated += 1
            else:
                near = await db.radar_opportunities.find_one({"title": rec["title"], "organization_name": rec.get("organization_name"),
                                                             "deadline": rec.get("deadline")}, {"_id": 0, "id": 1})
                if near:
                    dup += 1
                    await db.radar_opportunities.update_one({"id": near["id"]}, {"$addToSet": {"also_seen_at": rec["source_url"]}})
                    continue
                rec["id"] = str(uuid.uuid4())
                rec["user_status"] = "new"
                rec["stage"] = "Discovered"
                rec["notes"] = ""
                rec["ai"] = {}
                rec["drafts"] = {}
                rec["created_at"] = now_iso()
                rec["updated_at"] = rec["created_at"]
                rec["is_demo"] = False
                rec["score"] = score_opportunity(rec, profile)
                await db.radar_opportunities.insert_one(dict(rec))
                new += 1
        run = {"id": str(uuid.uuid4()), "source": res.source, "source_url": res.url, "access_method": res.access_method,
               "retrieved_at": res.started, "finished_at": now_iso(), "http_status": res.http_status, "parser_version": PARSER_VERSION,
               "error": res.error, "usage_notes": res.usage_notes, "fetched": fetched, "new": new, "updated": updated,
               "invalid": invalid, "near_duplicates": dup, "keyword": req.keyword}
        await db.radar_source_runs.insert_one(dict(run))
        run.pop("_id", None)
        summary.append(run)
    # stale marking: not re-seen for 7 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    await db.radar_opportunities.update_many({"last_verified_at": {"$lt": cutoff}, "status": "open"}, {"$set": {"status": "stale"}})
    return {"runs": summary, "total_active": await db.radar_opportunities.count_documents({"status": {"$ne": "closed"}})}


@router.get("/runs")
async def runs(limit: int = Query(30, ge=1, le=200)):
    return await db.radar_source_runs.find({}, {"_id": 0}).sort("retrieved_at", -1).to_list(limit)


# ----------------------------------------------------------------------------------------------
# Feed, detail, actions
# ----------------------------------------------------------------------------------------------
@router.get("/opportunities")
async def list_opportunities(
    type: Optional[str] = None, source: Optional[str] = None, status: Optional[str] = None,
    user_status: Optional[str] = None, min_score: Optional[int] = None, closing_days: Optional[int] = None,
    low_barrier: Optional[bool] = None, remote: Optional[bool] = None, max_value: Optional[float] = None,
    q: Optional[str] = None, saved: Optional[bool] = None, include_dismissed: bool = False,
    sort: str = "score", limit: int = Query(100, ge=1, le=300),
):
    f = {"is_demo": {"$ne": True}}
    if type:
        f["opportunity_type"] = type
    if source:
        f["source"] = source
    if status:
        f["status"] = status
    else:
        f["status"] = {"$ne": "closed"}
    if user_status:
        f["user_status"] = user_status
    elif saved:
        f["user_status"] = {"$in": ["saved", "contacted", "submitted"]}
    elif not include_dismissed:
        f["user_status"] = {"$ne": "dismissed"}
    if min_score is not None:
        f["score.total"] = {"$gte": min_score}
    if low_barrier:
        f["barrier.label"] = "lower observed barrier"
    if remote:
        f["remote_status"] = {"$in": ["remote", "national", "international"]}
    if max_value is not None:
        f["$or"] = [{"estimated_value": {"$lte": max_value}}, {"funding_amount": {"$lte": max_value}},
                    {"estimated_value": None, "funding_amount": None}]
    if closing_days is not None:
        f["deadline"] = {"$lte": (datetime.now(timezone.utc) + timedelta(days=closing_days)).isoformat(), "$ne": None}
    if q:
        rx = {"$regex": re.escape(q), "$options": "i"}
        f["$and"] = [{"$or": [{"title": rx}, {"description": rx}, {"organization_name": rx}, {"eligibility_text": rx}]}]
    docs = await db.radar_opportunities.find(f, {"_id": 0, "description": 0, "drafts": 0}).to_list(2000)
    if sort == "deadline":
        docs.sort(key=lambda d: d.get("deadline") or "9999")
    elif sort == "new":
        docs.sort(key=lambda d: d.get("created_at") or "", reverse=True)
    else:
        docs.sort(key=lambda d: (d.get("score") or {}).get("total", 0), reverse=True)
    docs = docs[:limit]
    for d in docs:
        d["days_remaining"] = days_until(d.get("deadline"))
    return docs


@router.get("/opportunities/{oid}")
async def get_opportunity(oid: str):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    d["days_remaining"] = days_until(d.get("deadline"))
    sim = await db.radar_opportunities.find(
        {"id": {"$ne": oid}, "opportunity_type": d.get("opportunity_type"), "status": {"$ne": "closed"}},
        {"_id": 0, "id": 1, "title": 1, "organization_name": 1, "score": 1, "deadline": 1}).sort("score.total", -1).to_list(5)
    d["similar"] = sim
    return d


STAGES = ["Discovered", "Reviewed", "Qualified", "Preparing", "Submitted", "Awarded", "Not Awarded"]


class PatchOpportunity(BaseModel):
    user_status: Optional[str] = None  # new | saved | dismissed | contacted | submitted
    stage: Optional[str] = None
    notes: Optional[str] = None


@router.patch("/opportunities/{oid}")
async def patch_opportunity(oid: str, p: PatchOpportunity):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0, "id": 1, "user_status": 1, "stage": 1})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    upd = {"updated_at": now_iso()}
    if p.user_status is not None:
        if p.user_status not in ("new", "saved", "dismissed", "contacted", "submitted"):
            raise HTTPException(400, "invalid user_status")
        upd["user_status"] = p.user_status
        if p.user_status == "submitted":
            upd["stage"] = "Submitted"
        elif p.user_status == "contacted" and d.get("stage") in ("Discovered", "Reviewed"):
            upd["stage"] = "Qualified"
        elif p.user_status == "saved" and d.get("stage") == "Discovered":
            upd["stage"] = "Reviewed"
    if p.stage is not None:
        if p.stage not in STAGES:
            raise HTTPException(400, "invalid stage")
        upd["stage"] = p.stage
    if p.notes is not None:
        upd["notes"] = p.notes[:5000]
    await db.radar_opportunities.update_one({"id": oid}, {"$set": upd, "$push": {"audit": {"at": upd["updated_at"], "change": {k: v for k, v in upd.items() if k != "updated_at"}}}})
    return await get_opportunity(oid)


@router.post("/opportunities/{oid}/to-mission")
async def opportunity_to_mission(oid: str):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    if d.get("mission_id"):
        m = await db.missions.find_one({"id": d["mission_id"]}, {"_id": 0})
        if m:
            return m
    val = d.get("funding_amount") or d.get("estimated_value")
    text = (f"Pursue this verified public opportunity (do NOT auto-submit; owner reviews and submits manually):\n"
            f"Title: {d.get('title')}\nType: {d.get('opportunity_type')}\nIssuer: {d.get('organization_name') or 'Not verified'}\n"
            f"Deadline: {d.get('deadline') or 'Not verified'}\nStated amount: {val if val is not None else 'Not verified'}\n"
            f"Eligibility (source text): {(d.get('eligibility_text') or 'Not stated')[:600]}\n"
            f"Required registrations: {', '.join(d.get('required_registrations') or []) or 'Not stated'}\n"
            f"Source: {d.get('source_url')}\n"
            f"Steps must include: verify on original source, confirm eligibility, gather required registrations/documents, "
            f"prepare submission, submit manually before deadline, log outcome.")
    mission = await compile_mission_from_text(text, "Collect" if d.get("opportunity_type") in ("grant", "funding") else "Move",
                                              source_opportunity_id=oid)
    await db.radar_opportunities.update_one({"id": oid}, {"$set": {"mission_id": mission.id, "mission_title": mission.title,
                                                                    "stage": "Preparing", "updated_at": now_iso()}})
    return mission


# ----------------------------------------------------------------------------------------------
# Natural-language search -> proposed structured filters (never applied silently)
# ----------------------------------------------------------------------------------------------
class NLSearch(BaseModel):
    query: str


@router.post("/search/nl")
async def nl_search(req: NLSearch):
    if not req.query.strip():
        raise HTTPException(400, "query required")
    system = ("You translate a natural-language opportunity search into a JSON filter object. Allowed keys ONLY: "
              "type (one of grant, contract, subcontract, procurement, sponsorship, rfp, funding, technical_bounty), "
              "source (grants_gov|sam_gov|github_bounties), min_score (int), closing_days (int), low_barrier (bool), "
              "remote (bool), max_value (number), q (short keyword string), exclusions (list of short strings the user "
              "wants to avoid, e.g. 'five years past performance'). Omit keys you cannot infer. Never add criteria the "
              "user did not state. Respond ONLY with minified JSON.")
    try:
        raw, _, label = await llm_call_failover(system, req.query, ["openai", "gemini", "anthropic"])
        filters = extract_json(raw)
    except Exception as e:
        raise HTTPException(502, f"could not parse query: {e}")
    allowed = {"type", "source", "min_score", "closing_days", "low_barrier", "remote", "max_value", "q", "exclusions"}
    filters = {k: v for k, v in (filters or {}).items() if k in allowed}
    return {"query": req.query, "proposed_filters": filters, "model": label,
            "note": "Review these filters before applying - the AI proposal is not applied automatically."}


# ----------------------------------------------------------------------------------------------
# AI personas on demand: Fit Analyst + Skeptic (+ checklist & questions)
# ----------------------------------------------------------------------------------------------
def source_pack(d: dict) -> str:
    fields = ["title", "opportunity_type", "organization_name", "location", "remote_status", "estimated_value", "funding_amount",
              "deadline", "eligibility_text", "required_entity_types", "required_certifications", "required_registrations",
              "set_aside", "cost_sharing", "industry_codes", "keywords", "notice_type", "source_url", "retrieved_at"]
    lines = [f"{k}: {d.get(k) if d.get(k) not in (None, [], '') else 'NOT STATED BY SOURCE'}" for k in fields]
    desc = (d.get("description") or "NOT STATED BY SOURCE")[:2500]
    evs = "\n".join([f"- [{e['field']}] \"{e['excerpt'][:200]}\" ({e['source_location']})" for e in d.get("evidence") or []])
    return "SOURCE FIELDS:\n" + "\n".join(lines) + f"\n\nSOURCE DESCRIPTION:\n{desc}\n\nEVIDENCE EXCERPTS:\n{evs}"


def profile_pack(p: dict) -> str:
    keys = ["entity_type", "org_name", "country", "state", "city", "service_area", "industries", "naics_codes", "skills", "keywords",
            "years_experience", "revenue_range", "team_size", "certifications", "set_asides", "nonprofit_status", "budget",
            "hours_per_week", "min_value", "max_value", "willing_travel", "willing_subcontract", "preferred_types", "bio"]
    return "OWNER PROFILE (the ONLY permitted source of claims about the owner):\n" + "\n".join(
        [f"{k}: {p.get(k) if p.get(k) not in (None, [], '') else 'NOT PROVIDED'}" for k in keys])


INTEGRITY = ("INTEGRITY RULES: Use only the SOURCE FIELDS/DESCRIPTION/EVIDENCE and the OWNER PROFILE. Never invent amounts, "
             "deadlines, agencies, eligibility rules, or facts about the owner. If something is not stated, say 'Not stated by source' "
             "or 'Not in profile'. Never claim the owner is legally eligible or will win; distinguish 'appears to match stated "
             "requirements' from 'legally eligible' from 'likely to win'. Respond ONLY with minified JSON.")


class AnalyzeRequest(BaseModel):
    include_checklist: bool = True


@router.post("/opportunities/{oid}/analyze")
async def analyze(oid: str, req: AnalyzeRequest = None):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    profile = await get_profile()
    sp, pp = source_pack(d), profile_pack(profile)
    include_ck = req.include_checklist if req else True

    fit_sys = ("You are the FIT ANALYST persona of ACASO Opportunity Radar. Compare the owner profile to the opportunity. " + INTEGRITY +
               " JSON keys: summary (2 sentences), why_it_may_fit (list), why_it_may_not_fit (list), appears_to_match_stated_requirements "
               "(true|false|unknown), missing_information (list), effort_estimate (string labelled 'uncertain estimate'), "
               "recommended_next_action (one sentence).")
    skeptic_sys = ("You are the SKEPTIC persona of ACASO Opportunity Radar. Your job is to find what is missing, stale, suspicious or "
                   "unrealistic before the owner relies on this opportunity. " + INTEGRITY +
                   " JSON keys: verdict (clear|caution|block), concerns (list), missing_requirements (list), stale_or_suspicious (list), "
                   "unrealistic_assumptions (list), verify_at_source (list of exact things to verify on the original page).")
    ck_sys = ("You are the COMPLIANCE SENTINEL + PROPOSAL ARCHITECT personas of ACASO Opportunity Radar. " + INTEGRITY +
              " JSON keys: preparation_checklist (list of {item, why, stated_by_source: true|false}), "
              "questions_for_contracting_officer_or_funder (list of strings), proposal_outline (list of section titles with one-line guidance; no fabricated claims).")

    body = f"{sp}\n\n{pp}"
    tasks = [llm_call_failover(fit_sys, body, ["openai", "gemini", "anthropic"]),
             llm_call_failover(skeptic_sys, body, ["anthropic", "openai", "gemini"])]
    if include_ck:
        tasks.append(llm_call_failover(ck_sys, body, ["gemini", "openai", "anthropic"]))
    outs = await asyncio.gather(*tasks, return_exceptions=True)

    def parse(o, name):
        if isinstance(o, Exception):
            return {"error": str(o)[:200], "persona": name}
        raw, _, label = o
        try:
            j = extract_json(raw)
        except Exception:
            j = {"raw": raw[:1500]}
        j["model_label"] = label
        j["generated_at"] = now_iso()
        j["inferred"] = True
        return j

    ai = dict(d.get("ai") or {})
    ai["fit"] = parse(outs[0], "fit_analyst")
    ai["skeptic"] = parse(outs[1], "skeptic")
    if include_ck:
        ai["checklist"] = parse(outs[2], "compliance_sentinel")
    d["ai"] = ai
    d["score"] = score_opportunity(d, profile)
    if d.get("stage") == "Discovered":
        d["stage"] = "Reviewed"
    await db.radar_opportunities.update_one({"id": oid}, {"$set": {"ai": ai, "score": d["score"], "stage": d["stage"], "updated_at": now_iso()}})
    return {"ai": ai, "score": d["score"], "stage": d["stage"]}


# ----------------------------------------------------------------------------------------------
# Drafting desk: email / grant narrative / outreach packet / fill-a-form
# ----------------------------------------------------------------------------------------------
DRAFT_KINDS = {
    "email": ("Write a concise, specific introductory email (subject line + body under 180 words) from the owner to the issuing "
              "organization's contact about this opportunity. Ask 1-2 clarifying questions that the source leaves unanswered."),
    "grant_narrative": ("Write a grant proposal narrative draft with these sections: Statement of Need, Project Description, "
                        "Goals & Measurable Objectives, Organizational Capacity, Timeline, Budget Narrative, Evaluation, Sustainability. "
                        "Ground every capacity/experience statement in the owner profile verbatim; anywhere a fact is missing, insert a "
                        "bracketed placeholder like [FILL: past project example] rather than inventing it."),
    "outreach_packet": ("Produce a full outreach packet: (1) one-paragraph capability statement, (2) cold email, (3) LinkedIn/DM version "
                        "under 80 words, (4) follow-up message for day 3, (5) call script opening 60 seconds, (6) list of documents to attach "
                        "based on stated requirements. Use only profile facts; use [FILL: ...] placeholders for anything missing."),
    "form_answers": ("The owner pasted application/form questions. Answer each question using ONLY the owner profile and the opportunity's "
                     "source text. For any answer requiring information not in the profile, write [FILL: what is needed] instead of guessing. "
                     "Output as numbered Q/A pairs."),
}


class DraftRequest(BaseModel):
    kind: str
    form_text: Optional[str] = None
    tone: Optional[str] = "professional, direct, human"
    extra_instructions: Optional[str] = None


@router.post("/opportunities/{oid}/draft")
async def draft(oid: str, req: DraftRequest):
    if req.kind not in DRAFT_KINDS:
        raise HTTPException(400, f"kind must be one of {list(DRAFT_KINDS)}")
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    if req.kind == "form_answers" and not (req.form_text or "").strip():
        raise HTTPException(400, "form_text is required for form_answers")
    profile = await get_profile()
    system = ("You are the PROPOSAL ARCHITECT persona of ACASO Opportunity Radar, drafting on behalf of the owner. "
              "HARD RULES: Never fabricate experience, revenue, credentials, certifications, past performance, partners, or metrics. "
              "The ONLY permitted facts about the owner are in the OWNER PROFILE; the ONLY permitted facts about the opportunity are in "
              "the SOURCE FIELDS/DESCRIPTION/EVIDENCE. Anything else must be a bracketed placeholder [FILL: ...]. Do not claim eligibility "
              "or that funding is likely. The owner will review and submit manually; never state that anything has been submitted. "
              f"Tone: {req.tone}. Output Markdown. End with a short 'Before sending' checklist of every [FILL] placeholder and every "
              "claim the owner must verify.")
    prompt = f"{source_pack(d)}\n\n{profile_pack(profile)}\n\nTASK: {DRAFT_KINDS[req.kind]}"
    if req.form_text:
        prompt += f"\n\nFORM QUESTIONS:\n{req.form_text[:6000]}"
    if req.extra_instructions:
        prompt += f"\n\nOWNER INSTRUCTIONS: {req.extra_instructions[:1000]}"
    try:
        text, _, label = await llm_call_failover(system, prompt, ["openai", "anthropic", "gemini"])
    except Exception as e:
        raise HTTPException(502, f"draft failed: {e}")
    fills = re.findall(r"\[FILL:[^\]]*\]", text)
    item = {"kind": req.kind, "content": text.strip(), "model_label": label, "generated_at": now_iso(),
            "placeholders": len(fills), "form_text": (req.form_text or None)}
    drafts = dict(d.get("drafts") or {})
    drafts[req.kind] = item
    upd = {"drafts": drafts, "updated_at": now_iso()}
    if d.get("stage") in ("Discovered", "Reviewed", "Qualified"):
        upd["stage"] = "Preparing"
    await db.radar_opportunities.update_one({"id": oid}, {"$set": upd})
    return item


@router.get("/opportunities/{oid}/drafts")
async def get_drafts(oid: str):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0, "drafts": 1})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    return d.get("drafts") or {}


@router.get("/opportunities/{oid}/export")
async def export_opportunity(oid: str):
    from fastapi.responses import Response
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    sc = d.get("score") or {}
    lines = [f"# {d.get('title')}", "",
             f"> VERIFY BEFORE ACTING: confirm every field on the original source: {d.get('source_url')}",
             f"> Retrieved {d.get('retrieved_at')} | parser {d.get('parser_version')} | HTTP {d.get('http_status')} | status {d.get('status')}", "",
             "## Facts from source",
             f"- Type: {d.get('opportunity_type')}", f"- Issuer: {d.get('organization_name') or 'Not verified'}",
             f"- Deadline: {d.get('deadline') or 'Not verified'}",
             f"- Amount: {d.get('funding_amount') if d.get('funding_amount') is not None else (d.get('estimated_value') if d.get('estimated_value') is not None else 'Not verified')}",
             f"- Eligibility text: {d.get('eligibility_text') or 'Not stated by source'}",
             f"- Required registrations: {', '.join(d.get('required_registrations') or []) or 'Not stated'}", "",
             f"## Inferred score: {sc.get('total')} / 100 - {sc.get('label')}"]
    for k, b in (sc.get("breakdown") or {}).items():
        lines.append(f"- {k}: {b['points']} / {b['weight']}")
    lines += ["", "## Evidence excerpts"] + [f"- [{e['field']}] \"{e['excerpt']}\" - {e['source_location']}" for e in d.get("evidence") or []]
    ai = d.get("ai") or {}
    for k in ("fit", "skeptic", "checklist"):
        if ai.get(k):
            lines += ["", f"## AI {k} (inferred, {ai[k].get('model_label','')})", "```json", json.dumps({x: y for x, y in ai[k].items() if x not in ('model_label',)}, indent=1)[:6000], "```"]
    for k, v in (d.get("drafts") or {}).items():
        lines += ["", f"## Draft: {k} ({v.get('placeholders')} placeholders to fill)", v.get("content", "")]
    if d.get("notes"):
        lines += ["", "## Notes", d["notes"]]
    md = "\n".join(lines)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", (d.get("title") or "opportunity"))[:50]
    return Response(content=md, media_type="text/markdown", headers={"Content-Disposition": f'attachment; filename="radar-{safe}.md"'})

```


### `backend/node.py`
```python
"""
ACASO Local Node orchestration + server-side research browser.

Reality: the hosted app cannot touch the owner's PC. A small Python client (handoff/local_node/acaso_node.py)
runs on the owner's machine, pairs with this API using the Agent Bridge key, and polls for tasks.

Safety model (owner decisions):
  * Every WRITE / shell / browser action is created as `proposed` and must be approved in the UI before the
    node is allowed to fetch it. Read-only actions (list/read/stat) are auto-approved.
  * The node itself enforces allowed roots; the server records them and rejects paths outside them too.
  * Browser tasks fill forms and STOP before submit; a separate `browser_submit` task (owner-approved) clicks submit.
    Passwords / 2FA are typed by the owner in the real Chrome window on their PC; never sent to this server.
  * Server research browser (headless Chromium here) is for public pages only: text + links + screenshot.
"""
import base64
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Callable, Awaitable

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

logger = logging.getLogger("node")
router = APIRouter(prefix="/node")
browse_router = APIRouter(prefix="/browse")

db = None
require_key = None
llm_call_failover: Optional[Callable[..., Awaitable]] = None
extract_json: Optional[Callable] = None
PROTOCOL_VERSION = "node-1.0"

READ_ONLY_KINDS = {"file_list", "file_read", "file_stat", "sys_info", "browser_screenshot"}
WRITE_KINDS = {"file_write", "file_append", "mkdir", "file_move", "file_delete", "shell", "browser_open", "browser_fill", "browser_submit", "browser_close"}
ALL_KINDS = READ_ONLY_KINDS | WRITE_KINDS


def init(_db, _require_key, _llm_failover, _extract_json):
    global db, require_key, llm_call_failover, extract_json
    db, require_key, llm_call_failover, extract_json = _db, _require_key, _llm_failover, _extract_json
    # dependency must be resolved at import time for FastAPI; register node-auth routes now
    _register_node_routes()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ----------------------------------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------------------------------
class NodeRegister(BaseModel):
    name: str
    os: str
    hostname: Optional[str] = None
    allowed_roots: List[str] = []
    capabilities: List[str] = ["files"]  # files | shell | browser
    node_version: Optional[str] = None
    node_id: Optional[str] = None  # re-register existing


class TaskCreate(BaseModel):
    node_id: str
    kind: str
    params: dict = {}
    title: Optional[str] = None
    plan_id: Optional[str] = None


class TaskResult(BaseModel):
    status: str  # done | failed | awaiting_submit
    result: Optional[dict] = None
    error: Optional[str] = None
    screenshot_b64: Optional[str] = None


class PlanRequest(BaseModel):
    node_id: str
    goal: str
    context: Optional[str] = None


class Decision(BaseModel):
    approved: bool
    note: Optional[str] = None


# ----------------------------------------------------------------------------------------------
# Owner-side routes (UI; single-owner app, same trust level as the rest of the app)
# ----------------------------------------------------------------------------------------------
@router.get("/nodes")
async def list_nodes():
    nodes = await db.nodes.find({}, {"_id": 0}).sort("last_seen", -1).to_list(50)
    for n in nodes:
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(n["last_seen"])).total_seconds()
        except Exception:
            age = 1e9
        n["online"] = age < 45
        n["pending_approvals"] = await db.node_tasks.count_documents({"node_id": n["id"], "status": "proposed"})
    return nodes


@router.delete("/nodes/{node_id}")
async def forget_node(node_id: str):
    r = await db.nodes.delete_one({"id": node_id})
    if not r.deleted_count:
        raise HTTPException(404, "Node not found")
    await db.node_tasks.update_many({"node_id": node_id, "status": {"$in": ["proposed", "queued"]}}, {"$set": {"status": "cancelled"}})
    return {"ok": True}


def _validate_path_in_roots(path: str, roots: List[str]) -> bool:
    if not roots:
        return False
    p = os.path.normpath(path).replace("\\", "/").lower().rstrip("/")
    for r in roots:
        rr = os.path.normpath(r).replace("\\", "/").lower().rstrip("/")
        if p == rr or p.startswith(rr + "/"):
            return True
    return False


@router.post("/tasks")
async def create_task(t: TaskCreate):
    if t.kind not in ALL_KINDS:
        raise HTTPException(400, f"kind must be one of {sorted(ALL_KINDS)}")
    node = await db.nodes.find_one({"id": t.node_id}, {"_id": 0})
    if not node:
        raise HTTPException(404, "Node not found - pair the Local Node first")
    # path checks against the node's declared roots (node re-checks locally too)
    for key in ("path", "src", "dst", "cwd"):
        v = t.params.get(key)
        if v and not _validate_path_in_roots(v, node.get("allowed_roots") or []):
            raise HTTPException(400, f"{key} '{v}' is outside this node's allowed roots {node.get('allowed_roots')}")
    if t.kind == "shell" and "shell" not in (node.get("capabilities") or []):
        raise HTTPException(400, "This node was started without shell capability")
    if t.kind.startswith("browser") and "browser" not in (node.get("capabilities") or []):
        raise HTTPException(400, "This node was started without browser capability (pip install playwright; playwright install chrome)")
    if t.kind == "browser_fill" and t.params.get("submit"):
        raise HTTPException(400, "browser_fill never submits. Approve a separate browser_submit task after reviewing the filled form.")
    auto = t.kind in READ_ONLY_KINDS
    doc = {
        "id": str(uuid.uuid4()), "node_id": t.node_id, "kind": t.kind, "params": t.params,
        "title": t.title or _default_title(t.kind, t.params), "plan_id": t.plan_id,
        "requires_approval": not auto, "status": "queued" if auto else "proposed",
        "created_at": now_iso(), "approved_at": now_iso() if auto else None, "started_at": None, "finished_at": None,
        "result": None, "error": None, "screenshot_b64": None,
        "audit": [{"at": now_iso(), "event": "created", "auto_approved": auto}],
    }
    await db.node_tasks.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


def _default_title(kind, p):
    if kind in ("file_read", "file_write", "file_append", "file_delete", "file_stat", "mkdir"):
        return f"{kind.replace('_', ' ')}: {p.get('path', '')}"
    if kind == "file_list":
        return f"list: {p.get('path', '')}"
    if kind == "file_move":
        return f"move: {p.get('src', '')} -> {p.get('dst', '')}"
    if kind == "shell":
        return f"shell: {str(p.get('command', ''))[:60]}"
    if kind.startswith("browser"):
        return f"{kind.replace('_', ' ')}: {p.get('url', p.get('session_id', ''))}"
    return kind


@router.get("/tasks")
async def list_tasks(node_id: Optional[str] = None, status: Optional[str] = None, limit: int = Query(60, ge=1, le=300)):
    f = {}
    if node_id:
        f["node_id"] = node_id
    if status:
        f["status"] = status
    docs = await db.node_tasks.find(f, {"_id": 0, "screenshot_b64": 0}).sort("created_at", -1).to_list(limit)
    return docs


@router.get("/tasks/{tid}")
async def get_task(tid: str):
    d = await db.node_tasks.find_one({"id": tid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Task not found")
    return d


@router.post("/tasks/{tid}/decision")
async def decide_task(tid: str, d: Decision):
    t = await db.node_tasks.find_one({"id": tid}, {"_id": 0})
    if not t:
        raise HTTPException(404, "Task not found")
    if t["status"] != "proposed":
        raise HTTPException(400, f"Task is '{t['status']}', nothing to decide")
    new = "queued" if d.approved else "rejected"
    await db.node_tasks.update_one({"id": tid}, {"$set": {"status": new, "approved_at": now_iso() if d.approved else None},
                                                 "$push": {"audit": {"at": now_iso(), "event": new, "note": d.note}}})
    return await get_task(tid)


@router.post("/tasks/{tid}/cancel")
async def cancel_task(tid: str):
    t = await db.node_tasks.find_one({"id": tid}, {"_id": 0, "status": 1})
    if not t:
        raise HTTPException(404, "Task not found")
    if t["status"] not in ("proposed", "queued"):
        raise HTTPException(400, f"Cannot cancel a task that is '{t['status']}'")
    await db.node_tasks.update_one({"id": tid}, {"$set": {"status": "cancelled"}, "$push": {"audit": {"at": now_iso(), "event": "cancelled"}}})
    return {"ok": True}


# ---- LLM planner: goal -> proposed tasks (all land in the approval queue; nothing runs) ----
PLANNER_SYSTEM = (
    "You are ACASO's Local Node planner. Turn the owner's goal into a SHORT ordered list of concrete tasks that a "
    "trusted agent on the owner's own PC will execute after the owner approves each one. Allowed task kinds and params:\n"
    "file_list {path}; file_read {path}; file_stat {path}; mkdir {path}; file_write {path, content}; file_append {path, content}; "
    "file_move {src, dst}; file_delete {path}; shell {command, cwd}; browser_open {url, session_id}; "
    "browser_fill {session_id, url?, fields:[{label_or_selector, value}]}; browser_screenshot {session_id}; browser_close {session_id}.\n"
    "Rules: every path MUST be inside one of the allowed roots given. Prefer reads before writes. Never include a browser_submit - the owner "
    "approves submission separately after seeing the filled form. Never put passwords or secrets in values; write [OWNER TYPES THIS] instead. "
    "Keep to at most 8 tasks. Respond ONLY with minified JSON: {\"summary\": string, \"tasks\": [{\"kind\":..., \"params\":{...}, \"title\": string, \"why\": string}]}"
)


@router.post("/plan")
async def plan_tasks(req: PlanRequest):
    node = await db.nodes.find_one({"id": req.node_id}, {"_id": 0})
    if not node:
        raise HTTPException(404, "Node not found")
    prompt = (f"NODE: os={node.get('os')} hostname={node.get('hostname')} capabilities={node.get('capabilities')}\n"
              f"ALLOWED ROOTS: {node.get('allowed_roots')}\n\nGOAL: {req.goal}\n" + (f"CONTEXT: {req.context}\n" if req.context else ""))
    try:
        raw, _, label = await llm_call_failover(PLANNER_SYSTEM, prompt, ["openai", "anthropic", "gemini"])
        parsed = extract_json(raw)
    except Exception as e:
        raise HTTPException(502, f"planner failed: {e}")
    tasks = [t for t in (parsed.get("tasks") or []) if t.get("kind") in ALL_KINDS and t.get("kind") != "browser_submit"][:8]
    pid = str(uuid.uuid4())
    created = []
    for t in tasks:
        try:
            doc = await create_task(TaskCreate(node_id=req.node_id, kind=t["kind"], params=t.get("params") or {}, title=t.get("title"), plan_id=pid))
            doc["why"] = t.get("why")
            created.append(doc)
        except HTTPException as he:
            created.append({"kind": t.get("kind"), "params": t.get("params"), "title": t.get("title"), "status": "rejected_by_policy", "error": str(he.detail)})
    plan = {"id": pid, "node_id": req.node_id, "goal": req.goal, "summary": parsed.get("summary", ""), "model_label": label,
            "tasks": [{k: v for k, v in c.items() if k in ("id", "kind", "title", "status", "why", "error")} for c in created], "created_at": now_iso()}
    await db.node_plans.insert_one(dict(plan))
    plan.pop("_id", None)
    return plan


@router.get("/plans")
async def list_plans(limit: int = Query(20, ge=1, le=100)):
    return await db.node_plans.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)


@router.get("/setup")
async def setup_info():
    """Everything the owner needs to run the node - the key is fetched separately from the Agent Bridge tab."""
    return {
        "protocol": PROTOCOL_VERSION,
        "download": ["/local-node/acaso_node.py", "/local-node/README.md", "/local-node/run_node.bat", "/local-node/run_node.sh"],
        "install": ["python -m pip install httpx", "optional browser: python -m pip install playwright && python -m playwright install chrome"],
        "run_windows": 'set ACASO_URL=<this site>&& set ACASO_KEY=<your Agent Bridge key>&& python acaso_node.py --root "C:\\Users\\you\\ACASO" --shell --browser',
        "run_linux": 'ACASO_URL=<this site> ACASO_KEY=<your Agent Bridge key> python3 acaso_node.py --root ~/ACASO --shell --browser',
        "safety": ["Only paths inside --root folders are touched", "Every write/shell/browser action waits for your approval in this tab",
                   "Forms are filled but never submitted until you approve a separate submit step", "Passwords and 2FA are typed by you in your own Chrome; never stored here"],
    }


# ----------------------------------------------------------------------------------------------
# Node-side routes (authenticated with X-ACASO-Key, registered after init so Depends resolves)
# ----------------------------------------------------------------------------------------------
def _register_node_routes():
    dep = [Depends(require_key)]

    @router.post("/register", dependencies=dep)
    async def register(n: NodeRegister):
        nid = n.node_id or str(uuid.uuid4())
        doc = {"id": nid, "name": n.name[:60], "os": n.os[:40], "hostname": (n.hostname or "")[:80],
               "allowed_roots": [r for r in n.allowed_roots if r][:10], "capabilities": [c for c in n.capabilities if c in ("files", "shell", "browser")],
               "node_version": n.node_version, "protocol": PROTOCOL_VERSION, "last_seen": now_iso()}
        existing = await db.nodes.find_one({"id": nid}, {"_id": 0, "created_at": 1})
        doc["created_at"] = (existing or {}).get("created_at") or now_iso()
        await db.nodes.update_one({"id": nid}, {"$set": doc}, upsert=True)
        return doc

    @router.post("/{node_id}/heartbeat", dependencies=dep)
    async def heartbeat(node_id: str):
        r = await db.nodes.update_one({"id": node_id}, {"$set": {"last_seen": now_iso()}})
        if not r.matched_count:
            raise HTTPException(404, "Unknown node - register first")
        pending = await db.node_tasks.count_documents({"node_id": node_id, "status": "queued"})
        return {"ok": True, "queued": pending, "server_time": now_iso()}

    @router.post("/{node_id}/claim", dependencies=dep)
    async def claim(node_id: str):
        """Atomically hand ONE approved task to the node."""
        doc = await db.node_tasks.find_one_and_update(
            {"node_id": node_id, "status": "queued"}, {"$set": {"status": "running", "started_at": now_iso()}, "$push": {"audit": {"at": now_iso(), "event": "claimed"}}},
            sort=[("created_at", 1)], projection={"_id": 0, "screenshot_b64": 0})
        await db.nodes.update_one({"id": node_id}, {"$set": {"last_seen": now_iso()}})
        return doc or {}

    @router.post("/tasks/{tid}/result", dependencies=dep)
    async def post_result(tid: str, r: TaskResult):
        t = await db.node_tasks.find_one({"id": tid}, {"_id": 0, "status": 1})
        if not t:
            raise HTTPException(404, "Task not found")
        if t["status"] != "running":
            raise HTTPException(400, f"Task is '{t['status']}', not running")
        status = r.status if r.status in ("done", "failed", "awaiting_submit") else "failed"
        shot = r.screenshot_b64
        if shot and len(shot) > 2_500_000:
            shot = None
        await db.node_tasks.update_one({"id": tid}, {"$set": {"status": status, "result": r.result, "error": r.error, "screenshot_b64": shot,
                                                              "finished_at": now_iso()}, "$push": {"audit": {"at": now_iso(), "event": status}}})
        return {"ok": True, "status": status}


# ----------------------------------------------------------------------------------------------
# Server research browser (headless Chromium in this container) - public pages only
# ----------------------------------------------------------------------------------------------
class ResearchRequest(BaseModel):
    url: str
    question: Optional[str] = None
    screenshot: bool = True


@browse_router.post("/research")
async def research(req: ResearchRequest):
    url = req.url.strip()
    if not re.match(r"^https?://", url):
        url = "https://" + url
    try:
        if "PLAYWRIGHT_BROWSERS_PATH" not in os.environ and os.path.isdir("/pw-browsers"):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/pw-browsers"
        from playwright.async_api import async_playwright
    except Exception as e:
        raise HTTPException(500, f"Playwright not available on server: {e}")
    started = now_iso()
    text, links, title, shot, status = "", [], "", None, None
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(headless=True)
            ctx = await b.new_context(user_agent="ACASO-Research/1.0 (+public page reader)", viewport={"width": 1280, "height": 900})
            pg = await ctx.new_page()
            resp = await pg.goto(url, timeout=45000, wait_until="domcontentloaded")
            status = resp.status if resp else None
            await pg.wait_for_timeout(1200)
            title = await pg.title()
            text = await pg.evaluate("() => document.body ? document.body.innerText : ''")
            links = await pg.evaluate("() => Array.from(document.querySelectorAll('a[href]')).slice(0,120).map(a => ({text: (a.innerText||'').trim().slice(0,80), href: a.href}))")
            forms = await pg.evaluate("() => Array.from(document.querySelectorAll('form')).slice(0,5).map(f => ({action: f.action, fields: Array.from(f.querySelectorAll('input,select,textarea')).slice(0,30).map(i => ({name: i.name, type: i.type, placeholder: i.placeholder, required: i.required}))}))")
            if req.screenshot:
                shot = base64.b64encode(await pg.screenshot(type="jpeg", quality=45, full_page=False)).decode()
            await b.close()
    except Exception as e:
        raise HTTPException(502, f"Could not load page: {str(e)[:300]}")
    text = re.sub(r"\n{3,}", "\n\n", text or "").strip()
    answer = None
    if req.question and text:
        try:
            ans, _, label = await llm_call_failover(
                "You answer questions strictly from the provided page text. If the page does not contain the answer, say so. Quote the exact passage you rely on. Never invent.",
                f"PAGE: {title} ({url})\n\nTEXT:\n{text[:14000]}\n\nQUESTION: {req.question}", ["openai", "gemini", "anthropic"])
            answer = {"text": ans.strip(), "model_label": label}
        except Exception as e:
            answer = {"error": str(e)[:200]}
    doc = {"id": str(uuid.uuid4()), "url": url, "title": title, "http_status": status, "retrieved_at": started, "chars": len(text),
           "text_excerpt": text[:6000], "links": links, "forms": forms, "answer": answer, "screenshot_b64": shot,
           "note": "Server headless browser: datacenter IP, no logins. Use your Local Node browser for anything with an account."}
    await db.research_pages.insert_one({**doc, "screenshot_b64": None})
    return doc


@browse_router.get("/history")
async def research_history(limit: int = Query(20, ge=1, le=100)):
    return await db.research_pages.find({}, {"_id": 0, "text_excerpt": 0, "links": 0, "forms": 0, "screenshot_b64": 0}).sort("retrieved_at", -1).to_list(limit)

```


### `backend/apex.py`
```python
"""
ACASO Apex Nexus - zero-capital digital products with an order -> pay -> unlock flow.

Products (Oracle Cortex vectors chosen by the owner):
  #6  rfp_kit         - proposal response kit for a real RFP/grant (from Radar or pasted text)
  #2  prompt_library  - packaged domain prompt library (Markdown + JSON, gated API endpoint)
  #10 seo_pack        - programmatic local landing-page copy pack for high-intent B2B terms

Integrity:
  * Generators use only the owner's Radar profile (capability facts) + the inputs the owner typed + the opportunity's
    stored source text. Unknown facts become [FILL: ...] placeholders. Nothing is auto-submitted anywhere.
  * Payment: Stripe Checkout when STRIPE_API_KEY is configured (wired separately with the owner's keys via the
    integration playbook). Until then, orders are unlocked manually by the owner ("Mark paid"). The UI shows which.
"""
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Callable, Awaitable

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

logger = logging.getLogger("apex")
router = APIRouter(prefix="/apex")

db = None
llm_call_failover: Optional[Callable[..., Awaitable]] = None
extract_json: Optional[Callable] = None


def init(_db, _llm_failover, _extract_json):
    global db, llm_call_failover, extract_json
    db, llm_call_failover, extract_json = _db, _llm_failover, _extract_json


def now_iso():
    return datetime.now(timezone.utc).isoformat()


PRODUCTS = {
    "rfp_kit": {
        "id": "rfp_kit", "vector": 6, "name": "RFP Response Kit", "price_usd": 149,
        "tagline": "A complete first-draft proposal package for a specific public RFP or grant - cover letter, executive summary, approach, compliance matrix, pricing skeleton, submission checklist.",
        "buyer": "Small contractors and nonprofits chasing a specific solicitation",
        "inputs": ["opportunity_id (from Radar) OR rfp_text", "bidder_name", "bidder_capabilities", "differentiators", "price_basis"],
        "deliverable": "Markdown kit + compliance matrix JSON",
    },
    "prompt_library": {
        "id": "prompt_library", "vector": 2, "name": "Prompt Library", "price_usd": 49,
        "tagline": "A curated, tested-format library of domain prompts with variables and examples, delivered as Markdown + JSON and a gated API endpoint.",
        "buyer": "Teams standardising AI use in one domain (legal intake, logistics ops, real-estate marketing...)",
        "inputs": ["domain", "audience", "use_cases", "count (10-30)", "tone"],
        "deliverable": "Markdown + JSON + API access key",
    },
    "seo_pack": {
        "id": "seo_pack", "vector": 10, "name": "Local SEO Content Pack", "price_usd": 199,
        "tagline": "Landing-page copy for zero-volume, high-intent local B2B terms: title, meta, H1, sections, FAQ, CTA and LocalBusiness schema per page.",
        "buyer": "Local B2B service businesses and agencies",
        "inputs": ["business", "service", "city_region", "terms (or let ACASO propose)", "count (5-15)", "proof_points"],
        "deliverable": "Markdown pages + JSON + JSON-LD",
    },
}

INTEGRITY = ("INTEGRITY: Use only the facts provided (owner profile, inputs, source text). Never invent past performance, "
             "clients, revenue, certifications, metrics, addresses or phone numbers - write [FILL: what is needed] instead. "
             "No guarantees of award, ranking or results.")


class GenerateRequest(BaseModel):
    product: str
    inputs: dict = {}


class OrderCreate(BaseModel):
    product: str
    buyer_email: str
    buyer_name: Optional[str] = None
    deliverable_id: Optional[str] = None
    price_usd: Optional[float] = None
    note: Optional[str] = None


class OrderPatch(BaseModel):
    status: Optional[str] = None  # pending_payment | paid | refunded | cancelled
    deliverable_id: Optional[str] = None
    note: Optional[str] = None


async def _profile_text() -> str:
    p = await db.radar_profile.find_one({"id": "owner"}, {"_id": 0}) or {}
    keys = ["org_name", "entity_type", "city", "state", "industries", "skills", "certifications", "years_experience", "team_size", "bio"]
    return "OWNER PROFILE (only permitted source of claims about the seller/bidder):\n" + "\n".join(
        [f"{k}: {p.get(k) if p.get(k) not in (None, [], '') else 'NOT PROVIDED'}" for k in keys])


# ----------------------------------------------------------------------------------------------
@router.get("/products")
async def products():
    stripe = bool(os.environ.get("STRIPE_API_KEY"))
    out = []
    for p in PRODUCTS.values():
        n_del = await db.apex_deliverables.count_documents({"product": p["id"]})
        n_ord = await db.apex_orders.count_documents({"product": p["id"]})
        paid = await db.apex_orders.count_documents({"product": p["id"], "status": "paid"})
        out.append({**p, "deliverables": n_del, "orders": n_ord, "paid_orders": paid})
    return {"products": out, "payments": {"provider": "stripe" if stripe else "manual",
                                          "stripe_configured": stripe,
                                          "note": ("Stripe Checkout active." if stripe else
                                                   "Stripe not connected: set STRIPE_API_KEY (and the webhook secret) in backend/.env to enable "
                                                   "checkout links. Until then, mark orders paid manually after you receive payment.")}}


# ---- generators ----
async def gen_rfp_kit(inp: dict) -> dict:
    opp_text = ""
    opp = None
    if inp.get("opportunity_id"):
        opp = await db.radar_opportunities.find_one({"id": inp["opportunity_id"]}, {"_id": 0})
        if not opp:
            raise HTTPException(404, "Radar opportunity not found")
        opp_text = (f"TITLE: {opp.get('title')}\nISSUER: {opp.get('organization_name')}\nTYPE: {opp.get('opportunity_type')}\n"
                    f"DEADLINE: {opp.get('deadline') or 'Not stated'}\nAMOUNT: {opp.get('funding_amount') or opp.get('estimated_value') or 'Not stated'}\n"
                    f"SET-ASIDE: {opp.get('set_aside') or 'none stated'}\nELIGIBILITY: {opp.get('eligibility_text') or 'Not stated'}\n"
                    f"REQUIRED REGISTRATIONS: {opp.get('required_registrations')}\nSOURCE: {opp.get('source_url')}\n"
                    f"DESCRIPTION:\n{(opp.get('description') or 'Not provided - see source')[:5000]}")
    elif inp.get("rfp_text"):
        opp_text = inp["rfp_text"][:12000]
    else:
        raise HTTPException(400, "Provide opportunity_id (from Radar) or rfp_text")
    system = ("You are ACASO's Proposal Architect producing a sellable RFP RESPONSE KIT in Markdown. " + INTEGRITY +
              " Sections, in order: # Cover Letter; # Executive Summary; # Understanding of the Requirement; # Technical / Service Approach; "
              "# Management & Staffing Plan; # Past Performance (profile facts only, else [FILL]); # Compliance Matrix (a Markdown table: "
              "Requirement | Where addressed | Status); # Pricing Skeleton (table with line items and [FILL: price] cells, plus assumptions); "
              "# Questions to Ask the Contracting Officer / Funder; # Submission Checklist (registrations, forms, formats, deadline); "
              "# Before Sending (every [FILL] and every claim to verify). After the Markdown, on its own line write ===JSON=== then a minified "
              "JSON object {\"compliance_matrix\": [{\"requirement\":..., \"addressed_in\":..., \"status\": \"draft|fill|n/a\"}], \"placeholders\": int, "
              "\"deadline\": string|null, \"issuer\": string|null}.")
    prompt = (f"SOLICITATION / OPPORTUNITY (source text):\n{opp_text}\n\n{await _profile_text()}\n\n"
              f"BIDDER NAME: {inp.get('bidder_name') or 'from profile'}\nBIDDER CAPABILITIES (owner-stated): {inp.get('bidder_capabilities') or 'from profile'}\n"
              f"DIFFERENTIATORS (owner-stated): {inp.get('differentiators') or 'NOT PROVIDED'}\nPRICE BASIS: {inp.get('price_basis') or 'NOT PROVIDED - use [FILL]'}\n\n"
              "Produce the kit.")
    text, _, label = await llm_call_failover(system, prompt, ["openai", "anthropic", "gemini"])
    md, data = _split_json(text)
    title = f"RFP Kit - {(opp or {}).get('title') or (inp.get('rfp_text') or '')[:60].strip()}"
    return {"title": title, "markdown": md, "data": data, "model_label": label, "source_url": (opp or {}).get("source_url")}


async def gen_prompt_library(inp: dict) -> dict:
    domain = (inp.get("domain") or "").strip()
    if not domain:
        raise HTTPException(400, "domain is required")
    count = max(10, min(int(inp.get("count") or 15), 30))
    system = ("You are ACASO's Prompt Engineer producing a sellable PROMPT LIBRARY. Every prompt must be concrete, reusable, and use "
              "{{double_curly_variables}} for every part the buyer changes (names, dates, amounts, addresses) - these are TEMPLATE VARIABLES, "
              "not missing facts, so do NOT write [FILL] inside prompts. Reserve [FILL: ...] only for claims about the seller. " + INTEGRITY +
              " Output Markdown: # <Library name>; ## How to use; then one ### section per prompt with: **Use case**, **Prompt** (code block), "
              "**Variables**, **Example input**, **Tips**. After the Markdown write ===JSON=== then minified JSON "
              "{\"name\":..., \"domain\":..., \"prompts\":[{\"id\":\"p01\",\"title\":...,\"use_case\":...,\"prompt\":...,\"variables\":[...],\"example_input\":...,\"tips\":...}]}.")
    prompt = (f"DOMAIN: {domain}\nAUDIENCE: {inp.get('audience') or 'practitioners in this domain'}\nUSE CASES TO COVER: {inp.get('use_cases') or 'the most valuable everyday tasks'}\n"
              f"TONE: {inp.get('tone') or 'professional'}\nCOUNT: exactly {count} prompts, no filler.")
    text, _, label = await llm_call_failover(system, prompt, ["openai", "gemini", "anthropic"])
    md, data = _split_json(text)
    return {"title": f"Prompt Library - {domain}", "markdown": md, "data": data, "model_label": label, "count": len((data or {}).get("prompts") or [])}


async def gen_seo_pack(inp: dict) -> dict:
    business = (inp.get("business") or "").strip()
    service = (inp.get("service") or "").strip()
    region = (inp.get("city_region") or "").strip()
    if not (business and service and region):
        raise HTTPException(400, "business, service and city_region are required")
    count = max(5, min(int(inp.get("count") or 8), 15))
    terms = inp.get("terms")
    system = ("You are ACASO's Programmatic SEO writer producing a sellable LOCAL SEO CONTENT PACK: one landing page per zero-volume, "
              "high-intent B2B search term. " + INTEGRITY + " Never invent reviews, ratings, addresses, phone numbers or client names; "
              "use [FILL: ...]. Output Markdown: # Pack overview (terms + intent); then per page: ## <Term> with **Slug**, **Title tag** (<=60 chars), "
              "**Meta description** (<=155 chars), **H1**, 3-4 H2 sections with 60-120 words each, **FAQ** (3 Q/A), **CTA**. "
              "After the Markdown write ===JSON=== then minified JSON {\"pages\":[{\"term\":...,\"slug\":...,\"title\":...,\"meta\":...,\"h1\":...,"
              "\"sections\":[{\"h2\":...,\"copy\":...}],\"faq\":[{\"q\":...,\"a\":...}],\"cta\":...,\"jsonld\":{\"@context\":\"https://schema.org\",\"@type\":\"LocalBusiness\",\"name\":...,\"areaServed\":...,\"description\":...}}]}.")
    prompt = (f"BUSINESS: {business}\nSERVICE: {service}\nCITY/REGION: {region}\nPROOF POINTS (owner-stated, use verbatim or [FILL]): {inp.get('proof_points') or 'NOT PROVIDED'}\n"
              + (f"TERMS (use these): {terms}\n" if terms else f"TERMS: propose {count} zero-volume, high-intent local B2B terms (e.g. '<service> for <niche> in <city>', 'emergency <service> <city> commercial').\n")
              + f"COUNT: {count} pages.\n{await _profile_text()}")
    text, _, label = await llm_call_failover(system, prompt, ["openai", "gemini", "anthropic"])
    md, data = _split_json(text)
    return {"title": f"SEO Pack - {service} in {region}", "markdown": md, "data": data, "model_label": label, "count": len((data or {}).get("pages") or [])}


def _split_json(text: str):
    if "===JSON===" in text:
        md, js = text.split("===JSON===", 1)
        try:
            return md.strip(), extract_json(js)
        except Exception:
            return md.strip(), None
    return text.strip(), None


GENERATORS = {"rfp_kit": gen_rfp_kit, "prompt_library": gen_prompt_library, "seo_pack": gen_seo_pack}


@router.post("/generate")
async def generate(req: GenerateRequest):
    if req.product not in GENERATORS:
        raise HTTPException(400, f"product must be one of {list(GENERATORS)}")
    started = datetime.now(timezone.utc)
    try:
        out = await GENERATORS[req.product](req.inputs or {})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"generation failed: {str(e)[:200]}")
    fills = len(re.findall(r"\[FILL:[^\]]*\]", out["markdown"]))
    doc = {"id": str(uuid.uuid4()), "product": req.product, "title": out["title"], "inputs": req.inputs, "markdown": out["markdown"],
           "data": out.get("data"), "placeholders": fills, "model_label": out.get("model_label"), "source_url": out.get("source_url"),
           "count": out.get("count"), "chars": len(out["markdown"]), "duration_s": round((datetime.now(timezone.utc) - started).total_seconds(), 1),
           "created_at": now_iso(), "api_key": uuid.uuid4().hex if req.product == "prompt_library" else None}
    await db.apex_deliverables.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


@router.get("/deliverables")
async def deliverables(product: Optional[str] = None, limit: int = Query(50, ge=1, le=200)):
    f = {"product": product} if product else {}
    return await db.apex_deliverables.find(f, {"_id": 0, "markdown": 0, "data": 0}).sort("created_at", -1).to_list(limit)


@router.get("/deliverables/{did}")
async def deliverable(did: str):
    d = await db.apex_deliverables.find_one({"id": did}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Deliverable not found")
    return d


@router.delete("/deliverables/{did}")
async def delete_deliverable(did: str):
    r = await db.apex_deliverables.delete_one({"id": did})
    if not r.deleted_count:
        raise HTTPException(404, "Deliverable not found")
    return {"ok": True}


@router.get("/deliverables/{did}/export")
async def export_deliverable(did: str, fmt: str = "md"):
    d = await db.apex_deliverables.find_one({"id": did}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Deliverable not found")
    return _export(d, fmt)


def _export(d: dict, fmt: str):
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", d.get("title") or d["product"])[:60]
    if fmt == "json":
        return Response(content=json.dumps({"title": d["title"], "product": d["product"], "generated_at": d["created_at"], "data": d.get("data")}, indent=1),
                        media_type="application/json", headers={"Content-Disposition": f'attachment; filename="{safe}.json"'})
    md = (f"{d['markdown']}\n\n---\n*Generated by ACASO Apex Nexus - {d['created_at'][:10]} - {d.get('placeholders', 0)} [FILL] placeholder(s) to complete before use. "
          "Drafts only; verify every claim; nothing has been submitted on your behalf.*\n")
    return Response(content=md, media_type="text/markdown", headers={"Content-Disposition": f'attachment; filename="{safe}.md"'})


# ---- orders: pending_payment -> paid -> unlocked via token ----
@router.post("/orders")
async def create_order(o: OrderCreate):
    if o.product not in PRODUCTS:
        raise HTTPException(400, "unknown product")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", o.buyer_email or ""):
        raise HTTPException(400, "valid buyer_email required")
    if o.deliverable_id:
        d = await db.apex_deliverables.find_one({"id": o.deliverable_id}, {"_id": 0, "product": 1})
        if not d:
            raise HTTPException(404, "Deliverable not found")
        if d["product"] != o.product:
            raise HTTPException(400, "Deliverable belongs to a different product")
    stripe = bool(os.environ.get("STRIPE_API_KEY"))
    doc = {"id": str(uuid.uuid4()), "product": o.product, "buyer_email": o.buyer_email.lower(), "buyer_name": o.buyer_name,
           "deliverable_id": o.deliverable_id, "price_usd": o.price_usd if o.price_usd is not None else PRODUCTS[o.product]["price_usd"],
           "status": "pending_payment", "payment_provider": "stripe" if stripe else "manual", "checkout_url": None,
           "unlock_token": uuid.uuid4().hex, "note": o.note, "created_at": now_iso(), "paid_at": None,
           "audit": [{"at": now_iso(), "event": "created"}]}
    await db.apex_orders.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


@router.get("/orders")
async def orders(status: Optional[str] = None, limit: int = Query(100, ge=1, le=500)):
    f = {"status": status} if status else {}
    return await db.apex_orders.find(f, {"_id": 0}).sort("created_at", -1).to_list(limit)


@router.patch("/orders/{oid}")
async def patch_order(oid: str, p: OrderPatch):
    o = await db.apex_orders.find_one({"id": oid}, {"_id": 0})
    if not o:
        raise HTTPException(404, "Order not found")
    upd = {}
    if p.status:
        if p.status not in ("pending_payment", "paid", "refunded", "cancelled"):
            raise HTTPException(400, "invalid status")
        upd["status"] = p.status
        if p.status == "paid":
            upd["paid_at"] = now_iso()
    if p.deliverable_id is not None:
        d = await db.apex_deliverables.find_one({"id": p.deliverable_id}, {"_id": 0, "product": 1})
        if not d or d["product"] != o["product"]:
            raise HTTPException(400, "Deliverable missing or wrong product")
        upd["deliverable_id"] = p.deliverable_id
    if p.note is not None:
        upd["note"] = p.note[:2000]
    if not upd:
        raise HTTPException(400, "nothing to update")
    await db.apex_orders.update_one({"id": oid}, {"$set": upd, "$push": {"audit": {"at": now_iso(), "event": "updated", "fields": list(upd)}}})
    return await db.apex_orders.find_one({"id": oid}, {"_id": 0})


# ---- public unlock (buyer link) ----
@router.get("/unlock/{token}")
async def unlock(token: str, fmt: str = "md"):
    o = await db.apex_orders.find_one({"unlock_token": token}, {"_id": 0})
    if not o:
        raise HTTPException(404, "Unknown link")
    if o["status"] != "paid":
        raise HTTPException(402, "This deliverable unlocks after payment is confirmed")
    if not o.get("deliverable_id"):
        raise HTTPException(409, "Payment received - the seller has not attached the deliverable yet")
    d = await db.apex_deliverables.find_one({"id": o["deliverable_id"]}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Deliverable missing")
    await db.apex_orders.update_one({"id": o["id"]}, {"$inc": {"downloads": 1}, "$set": {"last_download_at": now_iso()}})
    if fmt == "status":
        return {"product": o["product"], "title": d["title"], "status": o["status"], "api_key": d.get("api_key")}
    return _export(d, fmt)


# ---- gated prompt-library API (vector #2 payment path: API key unlocked by a paid order) ----
@router.get("/library/{did}")
async def library_api(did: str, key: str = Query(...)):
    d = await db.apex_deliverables.find_one({"id": did, "product": "prompt_library"}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Library not found")
    if not d.get("api_key") or key != d["api_key"]:
        raise HTTPException(401, "invalid key")
    paid = await db.apex_orders.count_documents({"deliverable_id": did, "status": "paid"})
    if not paid:
        raise HTTPException(402, "No paid order for this library")
    return {"title": d["title"], "domain": (d.get("data") or {}).get("domain"), "prompts": (d.get("data") or {}).get("prompts") or []}

```


### `backend/auth.py`
```python
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

```


### `frontend/src/components/AuthScreen.js`
```javascript
import React, { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Castle, Mail, Lock, LogIn, UserPlus, Loader2, Eye, EyeOff, ShieldCheck } from "lucide-react";
import { API } from "../App";

export default function AuthScreen({ onAuthed }) {
  const [status, setStatus] = useState(null);
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", name: "", remember_me: true });
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    axios.get(`${API}/auth/status`).then((r) => { setStatus(r.data); setMode(r.data.registration_open ? "register" : "login"); }).catch(() => setStatus({ has_owner: true, registration_open: false }));
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const r = await axios.post(`${API}/auth/${mode}`, form);
      toast.success(mode === "register" ? "Owner account created - welcome, Sovereign" : `Welcome back${r.data.user.name ? `, ${r.data.user.name}` : ""}`);
      onAuthed(r.data.user);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Could not sign in");
    } finally { setBusy(false); }
  };

  return (
    <div className="auth-root" data-testid="auth-screen">
      <motion.div className="auth-card" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}>
        <div className="auth-brand"><Castle size={22} /> ACASO <span>Omniverse</span></div>
        <h1>{mode === "register" ? "Claim the throne" : "Owner sign-in"}</h1>
        <p className="auth-sub">
          {status === null ? "Checking..." : mode === "register"
            ? "No owner exists yet. The first account created here becomes the single owner; registration then closes."
            : "This workspace belongs to its owner. Sign in with your email and password."}
        </p>
        <form onSubmit={submit} className="auth-form">
          {mode === "register" && (
            <label>Name (optional)<input data-testid="auth-name" className="cw-input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} autoComplete="name" /></label>
          )}
          <label><span><Mail size={12} /> Email</span><input data-testid="auth-email" className="cw-input" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} autoComplete="email" /></label>
          <label><span><Lock size={12} /> Password</span>
            <div className="auth-pw">
              <input data-testid="auth-password" className="cw-input" type={show ? "text" : "password"} required minLength={mode === "register" ? 10 : 1} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} autoComplete={mode === "register" ? "new-password" : "current-password"} />
              <button type="button" className="auth-eye" onClick={() => setShow((s) => !s)} aria-label="toggle password">{show ? <EyeOff size={14} /> : <Eye size={14} />}</button>
            </div>
            {mode === "register" && <small className="auth-hint">10+ characters, upper & lower case, and a digit.</small>}
          </label>
          <label className="auth-remember"><input data-testid="auth-remember" type="checkbox" checked={form.remember_me} onChange={(e) => setForm({ ...form, remember_me: e.target.checked })} /> Remember me for 30 days (otherwise 7)</label>
          <button data-testid="auth-submit" className="auth-submit" type="submit" disabled={busy || status === null}>
            {busy ? <Loader2 className="spin" size={15} /> : mode === "register" ? <UserPlus size={15} /> : <LogIn size={15} />} {mode === "register" ? "Create owner account" : "Sign in"}
          </button>
        </form>
        {status?.registration_open && mode === "register" && <button className="auth-link" onClick={() => setMode("login")}>Already have an account? Sign in</button>}
        {status && !status.registration_open && <div className="auth-foot"><ShieldCheck size={12} /> Registration closed - single-owner workspace. Sessions use an httpOnly cookie; passwords are bcrypt-hashed.</div>}
      </motion.div>
    </div>
  );
}

```


### `frontend/src/components/AccountMenu.js`
```javascript
import React, { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { AnimatePresence, motion } from "framer-motion";
import { User, LogOut, KeyRound, X, Loader2, ShieldCheck } from "lucide-react";
import { API } from "../App";

export const AccountMenu = ({ user, onLogout, onUserChange }) => {
  const [open, setOpen] = useState(false);
  const [pw, setPw] = useState({ current_password: "", new_password: "" });
  const [changing, setChanging] = useState(false);
  const [showPw, setShowPw] = useState(false);

  const change = async (e) => {
    e.preventDefault();
    setChanging(true);
    try {
      const r = await axios.post(`${API}/auth/change-password`, pw);
      toast.success(r.data.note || "Password updated");
      setPw({ current_password: "", new_password: "" }); setShowPw(false);
    } catch (err) { toast.error(err?.response?.data?.detail || "Could not change password"); }
    finally { setChanging(false); }
  };

  return (
    <div className="acct" data-testid="account-menu">
      <button className="owner-badge acct-btn" onClick={() => setOpen((o) => !o)} data-testid="account-toggle" title={user.email}>
        <span className="dot" /> {user.name || "Owner"} · Sovereign
      </button>
      <AnimatePresence>
        {open && (
          <motion.div className="acct-pop" initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} data-testid="account-popover">
            <div className="acct-row"><User size={13} /> <div><b>{user.name || "Owner"}</b><small>{user.email}</small></div><button className="rd-ic" onClick={() => setOpen(false)}><X size={13} /></button></div>
            <div className="acct-meta"><ShieldCheck size={11} /> single-owner workspace · httpOnly session cookie</div>
            {!showPw ? (
              <button className="acct-item" onClick={() => setShowPw(true)} data-testid="account-change-pw"><KeyRound size={13} /> Change password</button>
            ) : (
              <form className="acct-form" onSubmit={change}>
                <input className="cw-input" type="password" placeholder="current password" required value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} data-testid="pw-current" autoComplete="current-password" />
                <input className="cw-input" type="password" placeholder="new password (10+, mixed case, digit)" required minLength={10} value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} data-testid="pw-new" autoComplete="new-password" />
                <div className="cw-row" style={{ marginTop: 6 }}>
                  <button className="rd-btn primary sm" type="submit" disabled={changing} data-testid="pw-submit">{changing ? <Loader2 className="spin" size={13} /> : <KeyRound size={13} />} Update</button>
                  <button className="rd-btn sm" type="button" onClick={() => setShowPw(false)}>Cancel</button>
                </div>
              </form>
            )}
            <button className="acct-item danger" onClick={onLogout} data-testid="account-logout"><LogOut size={13} /> Sign out</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AccountMenu;

```


### `frontend/src/components/Apex.js`
```javascript
import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Store, FileText, BookOpen, Globe2, Sparkles, Loader2, Download, Copy, Link2, CreditCard, CheckCircle2, X, Trash2,
  ShoppingCart, KeyRound, AlertTriangle, Package, ExternalLink
} from "lucide-react";
import { API } from "../App";
import { Markdown } from "./FileAnalyzer";

const ICON = { rfp_kit: FileText, prompt_library: BookOpen, seo_pack: Globe2 };
const fmt = (iso) => { try { return iso ? new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : ""; } catch { return ""; } };
const money = (v) => `$${Number(v || 0).toLocaleString()}`;

export default function Apex() {
  const [catalog, setCatalog] = useState(null);
  const [product, setProduct] = useState("rfp_kit");
  const [inputs, setInputs] = useState({});
  const [opps, setOpps] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [deliverables, setDeliverables] = useState([]);
  const [current, setCurrent] = useState(null);
  const [orders, setOrders] = useState([]);
  const [orderForm, setOrderForm] = useState({ buyer_email: "", buyer_name: "", price_usd: "" });

  const load = useCallback(async () => {
    try {
      const [c, d, o] = await Promise.all([axios.get(`${API}/apex/products`), axios.get(`${API}/apex/deliverables`), axios.get(`${API}/apex/orders`)]);
      setCatalog(c.data); setDeliverables(d.data); setOrders(o.data);
    } catch { toast.error("Could not load Apex Nexus"); }
  }, []);
  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (product === "rfp_kit") axios.get(`${API}/radar/opportunities`, { params: { limit: 40 } }).then((r) => setOpps(r.data)).catch(() => {});
  }, [product]);

  const p = catalog?.products.find((x) => x.id === product);
  const set = (k, v) => setInputs((i) => ({ ...i, [k]: v }));

  const generate = async () => {
    setGenerating(true); setCurrent(null);
    try {
      const r = await axios.post(`${API}/apex/generate`, { product, inputs }, { timeout: 300000 });
      setCurrent(r.data); toast.success(`${r.data.title} ready - ${r.data.placeholders} [FILL] placeholder(s) to complete`); load();
    } catch (e) { toast.error(e?.response?.data?.detail || "Generation failed"); }
    finally { setGenerating(false); }
  };
  const openDeliverable = async (id) => { try { setCurrent((await axios.get(`${API}/apex/deliverables/${id}`)).data); window.scrollTo({ top: 0, behavior: "smooth" }); } catch { /* ignore */ } };
  const removeDeliverable = async (id) => { try { await axios.delete(`${API}/apex/deliverables/${id}`); if (current?.id === id) setCurrent(null); load(); } catch { toast.error("Delete failed"); } };
  const copy = async (t) => { try { await navigator.clipboard.writeText(t); toast.success("Copied"); } catch { toast.error("Copy failed"); } };

  const createOrder = async () => {
    if (!current) { toast.error("Generate or open a deliverable first"); return; }
    try {
      const r = await axios.post(`${API}/apex/orders`, { product: current.product, deliverable_id: current.id, buyer_email: orderForm.buyer_email, buyer_name: orderForm.buyer_name || null, price_usd: orderForm.price_usd ? Number(orderForm.price_usd) : null });
      toast.success(`Order created for ${r.data.buyer_email} - ${r.data.payment_provider === "stripe" ? "checkout link ready" : "mark paid when payment arrives"}`);
      setOrderForm({ buyer_email: "", buyer_name: "", price_usd: "" }); load();
    } catch (e) { toast.error(e?.response?.data?.detail || "Order failed"); }
  };
  const patchOrder = async (id, body) => { try { await axios.patch(`${API}/apex/orders/${id}`, body); load(); } catch (e) { toast.error(e?.response?.data?.detail || "Update failed"); } };
  const unlockLink = (o) => `${API}/apex/unlock/${o.unlock_token}`;

  return (
    <div className="ax-wrap" data-testid="apex-page">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><Store size={18} /> Apex Nexus</div>
          <p>Zero-capital digital products generated on demand and sold with an <b>order → pay → unlock</b> flow. Three vectors are live: the <b>RFP Response Kit</b> (built on real Radar solicitations), the <b>Prompt Library</b> (Markdown + JSON + a gated API key), and the <b>Local SEO Content Pack</b>. Everything is a first draft with <code>[FILL]</code> placeholders where facts are missing - you review, complete and deliver; nothing is submitted or sent automatically.</p>
        </div>
        <div className="chr-hero-stats">
          <div className="chr-stat"><span className="v">{deliverables.length}</span><span className="l">deliverables</span></div>
          <div className="chr-stat gold"><span className="v">{money(orders.filter((o) => o.status === "paid").reduce((a, o) => a + (o.price_usd || 0), 0))}</span><span className="l">paid orders</span></div>
        </div>
      </div>

      {catalog && (
        <div className={`ax-pay ${catalog.payments.stripe_configured ? "on" : ""}`} data-testid="apex-payments">
          <CreditCard size={14} /> <b>Payments: {catalog.payments.stripe_configured ? "Stripe Checkout" : "manual unlock"}</b> - {catalog.payments.note}
        </div>
      )}

      {/* Product picker */}
      <div className="ax-products" data-testid="apex-products">
        {(catalog?.products || []).map((x) => { const I = ICON[x.id] || Package; return (
          <button key={x.id} className={`ax-product ${product === x.id ? "active" : ""}`} onClick={() => { setProduct(x.id); setInputs({}); }} data-testid={`apex-product-${x.id}`}>
            <div className="ax-product-top"><I size={16} /> <b>{x.name}</b> <span className="ax-price">{money(x.price_usd)}</span></div>
            <small>{x.tagline}</small>
            <small className="ax-buyer">Buyer: {x.buyer} · vector #{x.vector} · {x.deliverables} made · {x.paid_orders} paid</small>
          </button>); })}
      </div>

      {/* Workbench */}
      {p && (
        <div className="fa-console" data-testid="apex-workbench">
          <div className="fa-head"><Sparkles size={16} /> {p.name} workbench <em>{p.deliverable}</em></div>
          <div className="rd-grid3 ax-form">
            {product === "rfp_kit" && <>
              <label className="rd-span3">Radar opportunity (real RFP/grant) — or paste text below
                <select className="cw-input" data-testid="ax-opp" value={inputs.opportunity_id || ""} onChange={(e) => set("opportunity_id", e.target.value || undefined)}>
                  <option value="">— pick from Radar ({opps.length} loaded) —</option>
                  {opps.map((o) => <option key={o.id} value={o.id}>{o.title.slice(0, 90)} · {o.organization_name || "?"} · {o.score?.total}</option>)}
                </select>
              </label>
              <label className="rd-span3">Or paste the RFP / solicitation text<textarea className="cw-textarea" rows={4} data-testid="ax-rfp-text" value={inputs.rfp_text || ""} onChange={(e) => set("rfp_text", e.target.value)} placeholder="Scope of work, requirements, evaluation criteria, deadline..." /></label>
              <label>Bidder name<input className="cw-input" value={inputs.bidder_name || ""} onChange={(e) => set("bidder_name", e.target.value)} placeholder="from Radar profile if blank" /></label>
              <label>Capabilities (facts only)<input className="cw-input" value={inputs.bidder_capabilities || ""} onChange={(e) => set("bidder_capabilities", e.target.value)} /></label>
              <label>Differentiators<input className="cw-input" value={inputs.differentiators || ""} onChange={(e) => set("differentiators", e.target.value)} /></label>
              <label>Price basis<input className="cw-input" value={inputs.price_basis || ""} onChange={(e) => set("price_basis", e.target.value)} placeholder="e.g. $95/hr, fixed $12k, monthly $349" /></label>
            </>}
            {product === "prompt_library" && <>
              <label>Domain *<input className="cw-input" data-testid="ax-domain" value={inputs.domain || ""} onChange={(e) => set("domain", e.target.value)} placeholder="e.g. moving company operations" /></label>
              <label>Audience<input className="cw-input" value={inputs.audience || ""} onChange={(e) => set("audience", e.target.value)} /></label>
              <label>Count (10-30)<input type="number" className="cw-input" value={inputs.count || 15} onChange={(e) => set("count", Number(e.target.value))} /></label>
              <label className="rd-span3">Use cases to cover<input className="cw-input" value={inputs.use_cases || ""} onChange={(e) => set("use_cases", e.target.value)} placeholder="comma-separated" /></label>
              <label>Tone<input className="cw-input" value={inputs.tone || ""} onChange={(e) => set("tone", e.target.value)} placeholder="professional" /></label>
            </>}
            {product === "seo_pack" && <>
              <label>Business *<input className="cw-input" data-testid="ax-business" value={inputs.business || ""} onChange={(e) => set("business", e.target.value)} /></label>
              <label>Service *<input className="cw-input" data-testid="ax-service" value={inputs.service || ""} onChange={(e) => set("service", e.target.value)} placeholder="e.g. office relocation" /></label>
              <label>City / region *<input className="cw-input" data-testid="ax-region" value={inputs.city_region || ""} onChange={(e) => set("city_region", e.target.value)} placeholder="Boston, MA" /></label>
              <label>Pages (5-15)<input type="number" className="cw-input" value={inputs.count || 8} onChange={(e) => set("count", Number(e.target.value))} /></label>
              <label className="rd-span3">Terms (optional - blank lets ACASO propose high-intent terms)<input className="cw-input" value={inputs.terms || ""} onChange={(e) => set("terms", e.target.value)} placeholder="comma-separated" /></label>
              <label className="rd-span3">Proof points (facts only)<input className="cw-input" value={inputs.proof_points || ""} onChange={(e) => set("proof_points", e.target.value)} placeholder="e.g. 'insured, 2 trucks, same-day quotes' - missing facts become [FILL]" /></label>
            </>}
          </div>
          <div className="cw-row">
            <button className="rd-btn primary" data-testid="ax-generate" onClick={generate} disabled={generating}>{generating ? <Loader2 className="spin" size={14} /> : <Sparkles size={14} />} {generating ? "Generating (30-90s)..." : `Generate ${p.name}`}</button>
            <span className="rd-dim">One model call. Output is a draft with [FILL] placeholders - never sold or sent without your review.</span>
          </div>
        </div>
      )}

      {/* Current deliverable */}
      <AnimatePresence>
        {current && (
          <motion.div className="ax-deliverable" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} data-testid="ax-deliverable">
            <div className="ax-del-head">
              <div>
                <div className="fa-head"><Package size={16} /> {current.title}</div>
                <div className="cw-meta">{fmt(current.created_at)} · {current.model_label} · {current.chars} chars · <b className={current.placeholders ? "rd-urgent" : ""}>{current.placeholders} [FILL]</b>{current.count ? ` · ${current.count} items` : ""}{current.source_url ? <> · <a href={current.source_url} target="_blank" rel="noreferrer">source <ExternalLink size={10} /></a></> : null}</div>
              </div>
              <div className="cw-actions">
                <a className="rd-btn" href={`${API}/apex/deliverables/${current.id}/export?fmt=md`} target="_blank" rel="noreferrer" data-testid="ax-export-md"><Download size={13} /> .md</a>
                {current.data && <a className="rd-btn" href={`${API}/apex/deliverables/${current.id}/export?fmt=json`} target="_blank" rel="noreferrer" data-testid="ax-export-json"><Download size={13} /> .json</a>}
                <button className="rd-btn" onClick={() => copy(current.markdown)}><Copy size={13} /> Copy</button>
                {current.api_key && <button className="rd-btn" onClick={() => copy(`${API}/apex/library/${current.id}?key=${current.api_key}`)} title="Gated API endpoint - works after a paid order" data-testid="ax-api-key"><KeyRound size={13} /> API link</button>}
                <button className="rd-ic" onClick={() => setCurrent(null)}><X size={14} /></button>
              </div>
            </div>
            <div className="ax-del-grid">
              <div className="ax-md"><Markdown text={current.markdown} /></div>
              <aside className="ax-sell">
                <div className="cw-side-title"><ShoppingCart size={14} /> Sell this deliverable</div>
                <input className="cw-input" placeholder="buyer email *" data-testid="ax-buyer-email" value={orderForm.buyer_email} onChange={(e) => setOrderForm({ ...orderForm, buyer_email: e.target.value })} />
                <input className="cw-input" placeholder="buyer name" value={orderForm.buyer_name} onChange={(e) => setOrderForm({ ...orderForm, buyer_name: e.target.value })} />
                <input className="cw-input" type="number" placeholder={`price (default ${money(p?.price_usd)})`} value={orderForm.price_usd} onChange={(e) => setOrderForm({ ...orderForm, price_usd: e.target.value })} />
                <button className="rd-btn primary" onClick={createOrder} data-testid="ax-create-order"><ShoppingCart size={14} /> Create order</button>
                <div className="rd-lbl-note">{catalog?.payments.stripe_configured ? "A Stripe Checkout link is attached to the order." : "Manual mode: send the buyer your payment link, then press Mark paid - the unlock link starts working immediately."}</div>
                <div className="ax-warn"><AlertTriangle size={12} /> Complete every [FILL] before delivering. Drafts carry no guarantee of award, ranking or results.</div>
              </aside>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Orders */}
      <div className="fa-console">
        <div className="fa-head"><CreditCard size={16} /> Orders <em>{orders.length} total · {orders.filter((o) => o.status === "paid").length} paid</em></div>
        {orders.length === 0 ? <div className="attach-empty" data-testid="ax-orders-empty">No orders yet. Generate a deliverable, then create an order for a buyer.</div> : (
          <div className="ax-orders" data-testid="ax-orders">
            {orders.map((o) => (
              <div key={o.id} className={`ax-order s-${o.status}`} data-testid={`ax-order-${o.id}`}>
                <span className={`bb-tag`}>{o.product}</span>
                <span className="ax-order-buyer">{o.buyer_email}{o.buyer_name ? ` · ${o.buyer_name}` : ""}</span>
                <span className="ax-order-price">{money(o.price_usd)}</span>
                <span className={`ln-status s-${o.status === "paid" ? "done" : o.status === "pending_payment" ? "proposed" : "failed"}`}>{o.status.replace("_", " ")}</span>
                <span className="ln-when">{fmt(o.created_at)}{o.downloads ? ` · ${o.downloads} download(s)` : ""}</span>
                <button className="rd-ic" title="Copy buyer unlock link" onClick={() => copy(unlockLink(o))} data-testid="ax-copy-unlock"><Link2 size={13} /></button>
                {o.status === "pending_payment" && <button className="rd-btn sm primary" onClick={() => patchOrder(o.id, { status: "paid" })} data-testid="ax-mark-paid"><CheckCircle2 size={13} /> Mark paid</button>}
                {o.status === "pending_payment" && <button className="rd-ic" title="Cancel" onClick={() => patchOrder(o.id, { status: "cancelled" })}><X size={13} /></button>}
                {o.status === "paid" && <button className="rd-btn sm" onClick={() => patchOrder(o.id, { status: "refunded" })}>Refund</button>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Deliverable library */}
      <div className="fa-console">
        <div className="fa-head"><Package size={16} /> Deliverables <em>{deliverables.length}</em></div>
        {deliverables.length === 0 ? <div className="attach-empty" data-testid="ax-deliverables-empty">Nothing generated yet.</div> : (
          <div className="cw-history" data-testid="ax-deliverables">
            {deliverables.map((d) => (
              <div key={d.id} className="cw-hrow">
                <button className="cw-hmain" onClick={() => openDeliverable(d.id)} data-testid={`ax-del-${d.id}`}>
                  <span className="bb-tag">{d.product}</span>
                  <span className="cw-htitle">{d.title}</span>
                  <span className="cw-hmeta">{fmt(d.created_at)} · {d.placeholders} [FILL]{d.count ? ` · ${d.count} items` : ""}</span>
                </button>
                <a className="attach-btn" href={`${API}/apex/deliverables/${d.id}/export?fmt=md`} target="_blank" rel="noreferrer" title="Download"><Download size={13} /></a>
                <button className="attach-btn danger" onClick={() => removeDeliverable(d.id)} title="Delete"><Trash2 size={13} /></button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

```


### `frontend/src/components/Companion.js`
```javascript
import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  Castle, Mic, Square, MonitorUp, MonitorOff, Send, Volume2, VolumeX, Loader2, Trash2, Camera, Radio, ExternalLink, Pin, Eye, EyeOff, Download
} from "lucide-react";
import { API } from "../App";

const SR = typeof window !== "undefined" ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null;
const TTS = typeof window !== "undefined" ? window.speechSynthesis : null;
const getSession = () => { try { let s = localStorage.getItem("acaso_companion_session"); if (!s) { s = crypto.randomUUID(); localStorage.setItem("acaso_companion_session", s); } return s; } catch { return "companion"; } };

/** Open the Companion as its own small desktop window (popup). Used by the launcher button in the main app. */
export function openCompanionWindow() {
  const url = `${window.location.origin}/?mode=companion`;
  const w = window.open(url, "acaso-companion", "popup=yes,width=440,height=760,left=" + Math.max(0, window.screen.availWidth - 470) + ",top=60,resizable=yes");
  if (!w) toast.error("Popup blocked - allow popups for this site, or open /?mode=companion in a new window");
  return w;
}

export default function Companion({ standalone = true }) {
  const [sessionId, setSessionId] = useState(getSession);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [streaming, setStreaming] = useState("");
  const [busy, setBusy] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [shareLabel, setShareLabel] = useState("");
  const [includeFrame, setIncludeFrame] = useState(true);
  const [listening, setListening] = useState(false);
  const [handsFree, setHandsFree] = useState(false);
  const [speak, setSpeak] = useState(true);
  const [speaking, setSpeaking] = useState(false);
  const [watch, setWatch] = useState(false);
  const [watchState, setWatchState] = useState({ glances: 0, skipped: 0, last: null, checking: false });
  const watchRef = useRef({ prevHash: null, prevSummary: null, lastSpoken: null, busy: false });
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const recRef = useRef(null);
  const endRef = useRef(null);
  const handsFreeRef = useRef(false);
  useEffect(() => { handsFreeRef.current = handsFree; }, [handsFree]);

  useEffect(() => {
    (async () => { try { setMessages((await axios.get(`${API}/companion/history`, { params: { session_id: sessionId } })).data); } catch { /* silent */ } })();
  }, [sessionId]);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streaming]);
  const [installEvt, setInstallEvt] = useState(null);
  const [installed, setInstalled] = useState(() => typeof window !== "undefined" && window.matchMedia?.("(display-mode: standalone)").matches);
  useEffect(() => {
    if (!standalone) return undefined;
    document.title = "ACASO Companion";
    // swap the page manifest so Chrome offers to install *the Companion* as its own desktop app
    document.querySelectorAll('link[rel="manifest"]').forEach((l) => l.remove());
    const link = document.createElement("link"); link.rel = "manifest"; link.href = "/companion.webmanifest"; document.head.appendChild(link);
    const onPrompt = (e) => { e.preventDefault(); setInstallEvt(e); };
    const onInstalled = () => { setInstalled(true); setInstallEvt(null); toast.success("ACASO Companion installed - find it in your Start menu / dock"); };
    window.addEventListener("beforeinstallprompt", onPrompt);
    window.addEventListener("appinstalled", onInstalled);
    return () => { window.removeEventListener("beforeinstallprompt", onPrompt); window.removeEventListener("appinstalled", onInstalled); };
  }, [standalone]);
  const install = async () => {
    if (installEvt) { installEvt.prompt(); const r = await installEvt.userChoice.catch(() => null); if (r?.outcome === "accepted") setInstallEvt(null); return; }
    toast("Chrome: menu (⋮) → Cast, save and share → Install page as app. Or run the Local Node with --companion for an always-on-top window.", { duration: 9000 });
  };

  // ---- screen / window share ----
  const startShare = async () => {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: { frameRate: 5 }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) { videoRef.current.srcObject = stream; await videoRef.current.play(); }
      const track = stream.getVideoTracks()[0];
      const s = track.getSettings();
      setShareLabel(track.label || (s.displaySurface ? `${s.displaySurface}` : "shared screen"));
      setSharing(true);
      track.onended = () => stopShare();
      toast.success("Sharing started - ask anything about what you see");
    } catch (e) { if (e?.name !== "NotAllowedError") toast.error("Could not start sharing"); }
  };
  const stopShare = useCallback(() => {
    try { streamRef.current?.getTracks().forEach((t) => t.stop()); } catch { /* ignore */ }
    streamRef.current = null; setSharing(false); setShareLabel(""); setWatch(false);
    if (videoRef.current) videoRef.current.srcObject = null;
  }, []);
  const captureFrame = () => {
    const v = videoRef.current;
    if (!v || !streamRef.current || !v.videoWidth) return null;
    const maxW = 1280;
    const scale = Math.min(1, maxW / v.videoWidth);
    const c = document.createElement("canvas");
    c.width = Math.round(v.videoWidth * scale); c.height = Math.round(v.videoHeight * scale);
    c.getContext("2d").drawImage(v, 0, 0, c.width, c.height);
    return c.toDataURL("image/jpeg", 0.72).split(",")[1];
  };
  /** 16x16 grayscale fingerprint - lets watch mode skip frames that barely changed (no model call). */
  const frameHash = () => {
    const v = videoRef.current;
    if (!v || !v.videoWidth) return null;
    const c = document.createElement("canvas"); c.width = 16; c.height = 16;
    const ctx = c.getContext("2d"); ctx.drawImage(v, 0, 0, 16, 16);
    const d = ctx.getImageData(0, 0, 16, 16).data; const out = [];
    for (let i = 0; i < d.length; i += 4) out.push((d[i] + d[i + 1] + d[i + 2]) / 3);
    return out;
  };
  const hashDiff = (a, b) => { if (!a || !b) return 1; let s = 0; for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s / (a.length * 255); };


  // ---- TTS ----
  const say = useCallback((t, onDone) => {
    if (!TTS || !t) { onDone?.(); return; }
    TTS.cancel();
    const u = new SpeechSynthesisUtterance(t.replace(/\*\*/g, ""));
    const pref = localStorage.getItem("acaso_voice_name");
    const v = TTS.getVoices().find((x) => x.name === pref);
    if (v) u.voice = v;
    u.onstart = () => setSpeaking(true);
    u.onend = () => { setSpeaking(false); onDone?.(); };
    u.onerror = () => { setSpeaking(false); onDone?.(); };
    TTS.speak(u);
  }, []);

  // ---- watch mode loop: glance every 30s, only call the model when the screen changed, speak only if notable ----
  useEffect(() => {
    if (!watch || !sharing) return undefined;
    let cancelled = false;
    const glance = async () => {
      if (cancelled || watchRef.current.busy || busy) return;
      const h = frameHash();
      if (!h) return;
      const changed = hashDiff(watchRef.current.prevHash, h) > 0.04; // ~4% average pixel change
      if (!changed) { setWatchState((w) => ({ ...w, skipped: w.skipped + 1, last: new Date() })); return; }
      const frame = captureFrame();
      if (!frame) return;
      watchRef.current.busy = true; setWatchState((w) => ({ ...w, checking: true }));
      try {
        const r = await axios.post(`${API}/companion/watch`, { image_b64: frame, session_id: sessionId, share_label: shareLabel,
          previous_summary: watchRef.current.prevSummary, last_spoken: watchRef.current.lastSpoken }, { timeout: 60000 });
        watchRef.current.prevHash = h; watchRef.current.prevSummary = r.data.summary;
        setWatchState((w) => ({ ...w, glances: w.glances + 1, last: new Date(), checking: false }));
        if (r.data.notable && r.data.message) {
          watchRef.current.lastSpoken = r.data.message;
          setMessages((m) => [...m, { id: `w-${Date.now()}`, role: "assistant", content: r.data.message, model_label: r.data.model_label, watch: true, kind: r.data.kind, created_at: r.data.at }]);
          if (speak) say(r.data.message);
        }
      } catch { setWatchState((w) => ({ ...w, checking: false })); }
      finally { watchRef.current.busy = false; }
    };
    const t0 = setTimeout(glance, 1500);
    const iv = setInterval(glance, 30000);
    return () => { cancelled = true; clearTimeout(t0); clearInterval(iv); };
  }, [watch, sharing, sessionId, shareLabel, speak, say, busy]);

  // ---- send (SSE stream) ----
  const send = useCallback(async (msg, withFrame = includeFrame) => {
    const content = (msg || "").trim();
    const frame = withFrame && sharing ? captureFrame() : null;
    if (!content && !frame) return;
    setBusy(true); setStreaming("");
    setMessages((m) => [...m, { id: `u-${Date.now()}`, role: "user", content: content || "(shared screen)", had_image: !!frame, created_at: new Date().toISOString() }]);
    try {
      const res = await fetch(`${API}/companion/chat`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content, session_id: sessionId, image_b64: frame, share_label: frame ? shareLabel : null }) });
      if (!res.ok) throw new Error((await res.json().catch(() => ({})))?.detail || `HTTP ${res.status}`);
      const reader = res.body.getReader(); const dec = new TextDecoder(); let buf = ""; let full = ""; let label = null;
      for (;;) {
        const { value, done } = await reader.read(); if (done) break;
        buf += dec.decode(value, { stream: true });
        const parts = buf.split("\n\n"); buf = parts.pop();
        for (const p of parts) {
          if (!p.startsWith("data: ")) continue;
          const ev = JSON.parse(p.slice(6));
          if (ev.type === "delta") { full += ev.content; setStreaming(full); }
          else if (ev.type === "done") { full = ev.content || full; label = ev.model_label; }
        }
      }
      setStreaming("");
      setMessages((m) => [...m, { id: `a-${Date.now()}`, role: "assistant", content: full, model_label: label, created_at: new Date().toISOString() }]);
      const after = () => { if (handsFreeRef.current) startListening(); }; // eslint-disable-line no-use-before-define
      if (speak) say(full, after); else after();
    } catch (e) {
      toast.error(e.message || "Companion failed");
      setStreaming("");
    } finally { setBusy(false); }
  }, [includeFrame, sharing, sessionId, shareLabel, speak, say]);

  // ---- STT ----
  const stopListening = useCallback(() => { try { recRef.current?.stop(); } catch { /* ignore */ } setListening(false); }, []);
  const startListening = useCallback(() => {
    if (!SR) { toast.error("Speech recognition needs Chrome, Edge or Safari"); return; }
    try { TTS?.cancel(); } catch { /* ignore */ }
    const rec = new SR(); rec.lang = "en-US"; rec.interimResults = true; rec.continuous = false;
    let fin = "";
    rec.onstart = () => setListening(true);
    rec.onresult = (ev) => { fin = ""; let inter = ""; for (let i = 0; i < ev.results.length; i++) { const t = ev.results[i][0].transcript; if (ev.results[i].isFinal) fin += t + " "; else inter += t; } setText((fin + inter).trim()); };
    rec.onerror = (ev) => { setListening(false); if (ev.error === "not-allowed") { toast.error("Microphone permission denied"); setHandsFree(false); } else if (ev.error === "no-speech" && handsFreeRef.current) setTimeout(() => startListening(), 400); };
    rec.onend = () => { setListening(false); const heard = fin.trim(); if (heard) { setText(""); send(heard); } else if (handsFreeRef.current && !busy) setTimeout(() => startListening(), 300); };
    recRef.current = rec;
    try { rec.start(); } catch { /* ignore */ }
  }, [send, busy]);

  const toggleHandsFree = () => {
    if (handsFree) { setHandsFree(false); handsFreeRef.current = false; stopListening(); TTS?.cancel(); }
    else { setHandsFree(true); handsFreeRef.current = true; startListening(); }
  };
  const clear = async () => { try { await axios.delete(`${API}/companion/history`, { params: { session_id: sessionId } }); } catch { /* ignore */ } const s = crypto.randomUUID(); localStorage.setItem("acaso_companion_session", s); setSessionId(s); setMessages([]); };
  useEffect(() => () => { stopShare(); try { recRef.current?.abort(); TTS?.cancel(); } catch { /* ignore */ } }, [stopShare]);

  return (
    <div className={`cp ${standalone ? "standalone" : ""}`} data-testid="companion">
      <header className="cp-head">
        <div className="cp-brand"><Castle size={16} /> ACASO Companion <span className={`cp-dot ${busy ? "busy" : sharing ? "on" : ""}`} /></div>
        <div className="cp-head-actions">
          <button className="cp-ic" title={speak ? "Mute replies" : "Speak replies"} onClick={() => { setSpeak((s) => !s); TTS?.cancel(); }} data-testid="cp-mute">{speak ? <Volume2 size={14} /> : <VolumeX size={14} />}</button>
          <button className="cp-ic" title="Clear conversation" onClick={clear} data-testid="cp-clear"><Trash2 size={14} /></button>
          {!standalone && <button className="cp-ic" title="Open as its own window" onClick={openCompanionWindow} data-testid="cp-popout"><ExternalLink size={14} /></button>}
          {standalone && !installed && <button className="cp-install" onClick={install} title="Install as a desktop app" data-testid="cp-install"><Download size={12} /> Install app</button>}
          {standalone && installed && <span className="cp-pin" title="Running as an installed desktop app"><Pin size={12} /> desktop app</span>}
        </div>
      </header>

      <div className={`cp-share ${sharing ? "on" : ""}`} data-testid="cp-share">
        <video ref={videoRef} muted playsInline className="cp-video" style={{ display: sharing ? "block" : "none" }} />
        {!sharing ? (
          <button className="cp-share-btn" onClick={startShare} data-testid="cp-share-start"><MonitorUp size={16} /> Share a window, tab or screen</button>
        ) : (
          <div className="cp-share-bar">
            <span title={shareLabel}><Radio size={11} /> {shareLabel.slice(0, 38) || "sharing"}</span>
            <label className="cp-chk" title="Attach a frame of the shared window to each message"><input type="checkbox" checked={includeFrame} onChange={(e) => setIncludeFrame(e.target.checked)} data-testid="cp-include-frame" /> see it</label>
            <button className={`cp-ic ${watch ? "on" : ""}`} title={watch ? "Watch mode on - glances every 30s, speaks only for errors, forms or action prompts" : "Watch mode: glance every 30s and speak up only when something notable appears"} onClick={() => setWatch((w) => !w)} data-testid="cp-watch">{watch ? <Eye size={14} /> : <EyeOff size={14} />}</button>
            <button className="cp-ic" title="Describe what's on screen now" onClick={() => send("", true)} disabled={busy} data-testid="cp-look"><Camera size={14} /></button>
            <button className="cp-ic" title="Stop sharing" onClick={stopShare} data-testid="cp-share-stop"><MonitorOff size={14} /></button>
          </div>
        )}
      </div>

      {watch && sharing && (
        <div className="cp-watchbar" data-testid="cp-watch-status">
          <Eye size={11} /> watching · {watchState.glances} glance{watchState.glances === 1 ? "" : "s"} · {watchState.skipped} unchanged skipped{watchState.checking ? " · checking..." : ""}
        </div>
      )}
      <div className="cp-log" data-testid="cp-log">
        {messages.length === 0 && !streaming && (
          <div className="cp-empty">Talk or type. Share a window and I can read what's on it - errors, forms, documents, dashboards - and tell you what to do next.</div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`cp-msg ${m.role}`} data-testid={`cp-msg-${m.role}`}>
            {m.had_image && <span className="cp-tag"><Camera size={10} /> frame</span>}
            {m.watch && <span className={`cp-tag k-${m.kind}`}><Eye size={10} /> watch · {m.kind}</span>}
            <div>{m.content}</div>
            {m.role === "assistant" && <button className="cp-replay" onClick={() => say(m.content)} title="Speak"><Volume2 size={11} /></button>}
          </div>
        ))}
        {streaming && <div className="cp-msg assistant streaming" data-testid="cp-streaming">{streaming}</div>}
        {busy && !streaming && <div className="cp-thinking"><Loader2 className="spin" size={12} /> looking...</div>}
        <div ref={endRef} />
      </div>

      <form className="cp-input" onSubmit={(e) => { e.preventDefault(); const t = text; setText(""); send(t); }}>
        <button type="button" className={`cp-mic ${handsFree ? "on" : ""} ${listening ? "live" : ""}`} onClick={toggleHandsFree} title={handsFree ? "Stop hands-free" : "Hands-free conversation"} data-testid="cp-handsfree">
          {handsFree ? <Square size={15} /> : <Mic size={15} />}
        </button>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder={listening ? "listening..." : sharing ? "Ask about what you see..." : "Ask ACASO..."} data-testid="cp-text" />
        <button type="submit" className="cp-send" disabled={busy || (!text.trim() && !sharing)} data-testid="cp-send">{busy ? <Loader2 className="spin" size={15} /> : <Send size={15} />}</button>
      </form>
      {speaking && <button className="cp-stopvoice" onClick={() => TTS?.cancel()}>stop voice</button>}
    </div>
  );
}

```


### `frontend/src/components/LocalNode.js`
```javascript
import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  MonitorSmartphone, Wifi, WifiOff, Download, KeyRound, ShieldCheck, Check, X, Loader2, Play, Sparkles,
  FolderOpen, FileText, TerminalSquare, Globe, Camera, Trash2, RefreshCw, AlertTriangle, ChevronDown, ChevronUp, ExternalLink, Search
} from "lucide-react";
import { API } from "../App";

const KIND_ICON = { file_list: FolderOpen, file_read: FileText, file_stat: FileText, file_write: FileText, file_append: FileText, mkdir: FolderOpen,
  file_move: FolderOpen, file_delete: Trash2, shell: TerminalSquare, browser_open: Globe, browser_fill: Globe, browser_submit: Globe, browser_screenshot: Camera, browser_close: Globe, sys_info: MonitorSmartphone };
const KINDS = ["file_list", "file_read", "file_stat", "mkdir", "file_write", "file_append", "file_move", "file_delete", "shell", "browser_open", "browser_fill", "browser_screenshot", "browser_close"];
const fmt = (iso) => { try { return iso ? new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : ""; } catch { return ""; } };

export default function LocalNode() {
  const [nodes, setNodes] = useState([]);
  const [nodeId, setNodeId] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [setup, setSetup] = useState(null);
  const [bridgeKey, setBridgeKey] = useState(null);
  const [showKey, setShowKey] = useState(false);
  const [goal, setGoal] = useState("");
  const [planning, setPlanning] = useState(false);
  const [plan, setPlan] = useState(null);
  const [manual, setManual] = useState({ kind: "file_list", params: '{"path": ""}' });
  const [open, setOpen] = useState(null);
  const [detail, setDetail] = useState(null);
  const [research, setResearch] = useState({ url: "", question: "" });
  const [researching, setResearching] = useState(false);
  const [page, setPage] = useState(null);
  const [showSetup, setShowSetup] = useState(true);

  const load = useCallback(async () => {
    try {
      const [n, s] = await Promise.all([axios.get(`${API}/node/nodes`), setup ? Promise.resolve({ data: setup }) : axios.get(`${API}/node/setup`)]);
      setNodes(n.data); setSetup(s.data);
      if (!nodeId && n.data[0]) setNodeId(n.data[0].id);
      if (n.data.length) setShowSetup(false);
    } catch { /* silent */ }
  }, [nodeId, setup]);
  const loadTasks = useCallback(async () => {
    if (!nodeId) { setTasks([]); return; }
    try { setTasks((await axios.get(`${API}/node/tasks`, { params: { node_id: nodeId, limit: 80 } })).data); } catch { /* silent */ }
  }, [nodeId]);

  useEffect(() => { load(); const t = setInterval(load, 10000); return () => clearInterval(t); }, [load]);
  useEffect(() => { loadTasks(); const t = setInterval(loadTasks, 4000); return () => clearInterval(t); }, [loadTasks]);

  const revealKey = async () => {
    try { const r = await axios.get(`${API}/bridge/info`); setBridgeKey(r.data.api_key); setShowKey(true); } catch { toast.error("Could not fetch key"); }
  };
  const decide = async (id, approved) => {
    try { await axios.post(`${API}/node/tasks/${id}/decision`, { approved }); toast[approved ? "success" : "info"](approved ? "Approved - the node will run it" : "Rejected"); loadTasks(); }
    catch (e) { toast.error(e?.response?.data?.detail || "Failed"); }
  };
  const cancel = async (id) => { try { await axios.post(`${API}/node/tasks/${id}/cancel`); loadTasks(); } catch { /* ignore */ } };
  const approveAll = async () => { for (const t of tasks.filter((x) => x.status === "proposed")) await axios.post(`${API}/node/tasks/${t.id}/decision`, { approved: true }); toast.success("All pending tasks approved"); loadTasks(); };

  const doPlan = async () => {
    if (!goal.trim() || !nodeId) return;
    setPlanning(true);
    try { const r = await axios.post(`${API}/node/plan`, { node_id: nodeId, goal }, { timeout: 120000 }); setPlan(r.data); toast.success(`${r.data.tasks.length} task(s) proposed - review and approve below`); loadTasks(); }
    catch (e) { toast.error(e?.response?.data?.detail || "Planner failed"); }
    finally { setPlanning(false); }
  };
  const addManual = async () => {
    let params;
    try { params = JSON.parse(manual.params || "{}"); } catch { toast.error("Params must be valid JSON"); return; }
    try { await axios.post(`${API}/node/tasks`, { node_id: nodeId, kind: manual.kind, params }); toast.success("Task created"); loadTasks(); }
    catch (e) { toast.error(e?.response?.data?.detail || "Rejected"); }
  };
  const openDetail = async (id) => { try { setDetail((await axios.get(`${API}/node/tasks/${id}`)).data); } catch { /* ignore */ } };
  const submitFor = async (t) => {
    const sid = t.result?.session_id;
    if (!sid) return;
    try { await axios.post(`${API}/node/tasks`, { node_id: t.node_id, kind: "browser_submit", params: { session_id: sid }, title: `submit form in session ${sid}` }); toast.success("Submit step proposed - approve it in the queue to actually submit"); loadTasks(); }
    catch (e) { toast.error(e?.response?.data?.detail || "Failed"); }
  };
  const doResearch = async () => {
    if (!research.url.trim()) return;
    setResearching(true); setPage(null);
    try { setPage((await axios.post(`${API}/browse/research`, { url: research.url, question: research.question || null, screenshot: true }, { timeout: 120000 })).data); }
    catch (e) { toast.error(e?.response?.data?.detail || "Could not load page"); }
    finally { setResearching(false); }
  };

  const node = nodes.find((n) => n.id === nodeId);
  const pending = tasks.filter((t) => t.status === "proposed");
  const awaiting = tasks.filter((t) => t.status === "awaiting_submit");

  return (
    <div className="ln-wrap" data-testid="localnode-page">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><MonitorSmartphone size={18} /> Local Node</div>
          <p>ACASO cannot reach your PC from this server - so a small program you run <b>on your machine</b> pairs with your Agent Bridge key and executes tasks there: create and fix files inside folders you allow, run scripts, and drive a real Chrome window for sign-ups and forms. <b>Every write, command and browser action waits for your approval here.</b> Forms are filled but never submitted until you approve the submit step; you type passwords and 2FA yourself.</p>
        </div>
        <div className="chr-hero-stats">
          <div className={`chr-stat ${node?.online ? "gold" : ""}`}><span className="v">{node ? (node.online ? "ONLINE" : "OFFLINE") : "—"}</span><span className="l">{node?.name || "no node paired"}</span></div>
          <div className="chr-stat"><span className="v">{pending.length}</span><span className="l">awaiting approval</span></div>
        </div>
      </div>

      {/* Setup */}
      <div className="fa-console">
        <div className="fa-head" role="button" tabIndex={0} onClick={() => setShowSetup((s) => !s)} onKeyDown={(e) => e.key === "Enter" && setShowSetup((s) => !s)}><Download size={16} /> Install & pair {showSetup ? <ChevronUp size={14} /> : <ChevronDown size={14} />} <em>{nodes.length ? `${nodes.length} node(s) paired` : "no node yet"}</em></div>
        {showSetup && setup && (
          <div className="ln-setup" data-testid="localnode-setup">
            <ol>
              <li>Download <a href="/local-node/acaso_node.py" download data-testid="ln-download-py">acaso_node.py</a>, the <a href="/local-node/README.md" download>README</a>, and a launcher: <a href="/local-node/run_node.bat" download>run_node.bat</a> (Windows) / <a href="/local-node/run_node.sh" download>run_node.sh</a> (Linux).</li>
              <li>Install: <code>python -m pip install httpx</code> — for browser tasks also <code>python -m pip install playwright && python -m playwright install chrome</code>.</li>
              <li>Your key: {showKey && bridgeKey ? <code className="ln-key" data-testid="ln-key">{bridgeKey}</code> : <button className="fa-btn" onClick={revealKey} data-testid="ln-reveal-key"><KeyRound size={13} /> Reveal Agent Bridge key</button>} — paste it into the launcher or <code>ACASO_KEY</code>.</li>
              <li>Run it. Windows: <code>{setup.run_windows}</code></li>
              <li className="ln-dim">Linux: <code>{setup.run_linux}</code></li>
            </ol>
            <div className="ln-safety">{setup.safety.map((s) => <span key={s}><ShieldCheck size={12} /> {s}</span>)}</div>
          </div>
        )}
      </div>

      {/* Nodes */}
      {nodes.length > 0 && (
        <div className="ln-nodes" data-testid="ln-nodes">
          {nodes.map((n) => (
            <button key={n.id} className={`ln-node ${n.id === nodeId ? "active" : ""} ${n.online ? "on" : ""}`} onClick={() => setNodeId(n.id)} data-testid={`ln-node-${n.id}`}>
              {n.online ? <Wifi size={14} /> : <WifiOff size={14} />}
              <span><b>{n.name}</b><small>{n.os} · {n.hostname} · {(n.capabilities || []).join(", ")}</small><small>roots: {(n.allowed_roots || []).join(" | ")}</small><small>last seen {fmt(n.last_seen)}</small></span>
              {n.pending_approvals > 0 && <em>{n.pending_approvals}</em>}
            </button>
          ))}
        </div>
      )}

      {node && (
        <>
          {/* Planner + manual */}
          <div className="fa-console">
            <div className="fa-head"><Sparkles size={16} /> Give the node a goal <em>ACASO plans the steps; nothing runs until you approve each one</em></div>
            <div className="cw-row">
              <input data-testid="ln-goal" className="cw-input grow" value={goal} onChange={(e) => setGoal(e.target.value)} placeholder='e.g. "Organize my ACASO folder: move all PDFs into /invoices and write an index.md listing them"' onKeyDown={(e) => e.key === "Enter" && doPlan()} />
              <button data-testid="ln-plan" className="fa-btn primary" onClick={doPlan} disabled={planning || !goal.trim()}>{planning ? <Loader2 className="spin" size={14} /> : <Sparkles size={14} />} Plan tasks</button>
            </div>
            {plan && <div className="ln-plan" data-testid="ln-plan-summary"><b>Plan:</b> {plan.summary} <small>({plan.model_label})</small></div>}
            <details className="ln-manual">
              <summary>Add a single task manually</summary>
              <div className="cw-row">
                <select className="cw-input" value={manual.kind} onChange={(e) => setManual({ ...manual, kind: e.target.value })} data-testid="ln-manual-kind">{KINDS.map((k) => <option key={k}>{k}</option>)}</select>
                <input className="cw-input grow" value={manual.params} onChange={(e) => setManual({ ...manual, params: e.target.value })} placeholder='{"path": "C:\\Users\\you\\ACASO\\notes.txt", "content": "..."}' data-testid="ln-manual-params" />
                <button className="fa-btn" onClick={addManual} data-testid="ln-manual-add"><Play size={14} /> Queue</button>
              </div>
            </details>
          </div>

          {/* Awaiting submit */}
          {awaiting.length > 0 && (
            <div className="ln-await" data-testid="ln-awaiting">
              <div className="fa-head"><Globe size={16} /> Forms filled - waiting for your submit decision</div>
              {awaiting.map((t) => (
                <div key={t.id} className="ln-await-row">
                  <span>{t.title} · session <code>{t.result?.session_id}</code> · filled {t.result?.filled?.length || 0} field(s){t.result?.skipped?.length ? ` · ${t.result.skipped.length} for you to type` : ""}</span>
                  <button className="fa-btn" onClick={() => openDetail(t.id)}><Camera size={13} /> View screenshot</button>
                  <button className="fa-btn primary" onClick={() => submitFor(t)} data-testid="ln-propose-submit"><Check size={13} /> Propose submit</button>
                </div>
              ))}
            </div>
          )}

          {/* Queue */}
          <div className="fa-console">
            <div className="fa-head"><ShieldCheck size={16} /> Task queue {pending.length > 0 && <button className="fa-btn" style={{ marginLeft: 10 }} onClick={approveAll} data-testid="ln-approve-all"><Check size={13} /> Approve all {pending.length}</button>} <em><button className="attach-btn" onClick={loadTasks} title="Refresh"><RefreshCw size={13} /></button></em></div>
            {tasks.length === 0 ? <div className="attach-empty" data-testid="ln-empty">No tasks yet. Give the node a goal above.</div> : (
              <div className="ln-tasks" data-testid="ln-tasks">
                <AnimatePresence initial={false}>
                  {tasks.map((t) => { const I = KIND_ICON[t.kind] || FileText; const isOpen = open === t.id; return (
                    <motion.div key={t.id} className={`ln-task s-${t.status}`} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} data-testid={`ln-task-${t.id}`}>
                      <div className="ln-task-h">
                        <I size={14} />
                        <span className="ln-task-title" onClick={() => setOpen(isOpen ? null : t.id)} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && setOpen(isOpen ? null : t.id)}>{t.title}</span>
                        <span className={`ln-status s-${t.status}`} data-testid="ln-task-status">{t.status.replace("_", " ")}</span>
                        <span className="ln-when">{fmt(t.created_at)}</span>
                        {t.status === "proposed" && <>
                          <button className="ln-ok" onClick={() => decide(t.id, true)} data-testid="ln-approve" title="Approve"><Check size={14} /></button>
                          <button className="ln-no" onClick={() => decide(t.id, false)} data-testid="ln-reject" title="Reject"><X size={14} /></button>
                        </>}
                        {t.status === "queued" && <button className="ln-no" onClick={() => cancel(t.id)} title="Cancel"><X size={14} /></button>}
                        {(t.status === "done" || t.status === "failed" || t.status === "awaiting_submit") && <button className="attach-btn" onClick={() => openDetail(t.id)} title="Result"><Search size={13} /></button>}
                      </div>
                      {isOpen && <pre className="ln-params">{JSON.stringify(t.params, null, 1)}</pre>}
                      {t.error && <div className="ln-err"><AlertTriangle size={12} /> {t.error}</div>}
                    </motion.div>); })}
                </AnimatePresence>
              </div>
            )}
          </div>
        </>
      )}

      {/* Server research browser */}
      <div className="fa-console">
        <div className="fa-head"><Globe size={16} /> Research browser (server) <em>headless Chromium here - public pages only; datacenter IP; no logins</em></div>
        <div className="cw-row">
          <input className="cw-input grow" data-testid="ln-research-url" value={research.url} onChange={(e) => setResearch({ ...research, url: e.target.value })} placeholder="https://..." />
          <input className="cw-input grow" data-testid="ln-research-q" value={research.question} onChange={(e) => setResearch({ ...research, question: e.target.value })} placeholder="Question about the page (optional)" />
          <button className="fa-btn primary" data-testid="ln-research-run" onClick={doResearch} disabled={researching || !research.url.trim()}>{researching ? <Loader2 className="spin" size={14} /> : <Globe size={14} />} Read page</button>
        </div>
        {page && (
          <div className="ln-page" data-testid="ln-research-result">
            <div className="ln-page-h"><b>{page.title}</b> · HTTP {page.http_status} · {page.chars} chars · {page.links.length} links · {page.forms.length} form(s) <a href={page.url} target="_blank" rel="noreferrer"><ExternalLink size={12} /></a></div>
            {page.answer && <div className="ln-answer"><Sparkles size={12} /> {page.answer.text || page.answer.error} <small>{page.answer.model_label}</small></div>}
            <div className="ln-page-grid">
              {page.screenshot_b64 && <img alt="page screenshot" src={`data:image/jpeg;base64,${page.screenshot_b64}`} className="ln-shot" />}
              <pre className="ln-text">{page.text_excerpt.slice(0, 3000)}</pre>
            </div>
            {page.forms.length > 0 && <div className="ln-forms">Forms detected: {page.forms.map((f, i) => <code key={i}>{f.fields.map((x) => x.name || x.placeholder || x.type).filter(Boolean).slice(0, 8).join(", ")}</code>)} — to fill one with your account, use the Local Node browser (browser_fill).</div>}
          </div>
        )}
      </div>

      <AnimatePresence>
        {detail && (
          <motion.div className="rd-modal-bg" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setDetail(null)} data-testid="ln-detail-modal">
            <motion.div className="rd-modal ln-detail" initial={{ y: 16 }} animate={{ y: 0 }} exit={{ y: 16 }} onClick={(e) => e.stopPropagation()}>
              <div className="rd-modal-h"><div><h2>{detail.title}</h2><div className="ln-when">{detail.kind} · {detail.status} · {fmt(detail.finished_at || detail.created_at)}</div></div><button className="rd-ic" onClick={() => setDetail(null)}><X size={16} /></button></div>
              {detail.screenshot_b64 && <img alt="node screenshot" className="ln-shot big" src={`data:image/jpeg;base64,${detail.screenshot_b64}`} />}
              {detail.result?.content !== undefined && <pre className="ln-text">{detail.result.content}</pre>}
              {detail.result?.stdout !== undefined && <pre className="ln-text">$ {detail.result.command}{"\n"}{detail.result.stdout}{detail.result.stderr ? `\n[stderr]\n${detail.result.stderr}` : ""}</pre>}
              {detail.result?.items && <pre className="ln-text">{detail.result.items.map((i) => `${i.type === "dir" ? "📁" : "  "} ${i.name}  ${i.size}`).join("\n")}</pre>}
              {detail.result && !detail.result.content && !detail.result.stdout && !detail.result.items && <pre className="ln-text">{JSON.stringify(detail.result, null, 1)}</pre>}
              {detail.error && <div className="ln-err"><AlertTriangle size={12} /> {detail.error}</div>}
              <details><summary className="ln-dim">Audit trail</summary><pre className="ln-text">{JSON.stringify(detail.audit, null, 1)}</pre></details>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

```


### `handoff/local_node/acaso_node.py`
```python
#!/usr/bin/env python3
"""
ACASO Local Node - runs ON YOUR PC and lets the hosted ACASO app work with your files and your browser.

    Windows:  set ACASO_URL=https://<your-acaso> && set ACASO_KEY=<Agent Bridge key> && python acaso_node.py --root "C:\\Users\\you\\ACASO" --shell --browser
    Linux:    ACASO_URL=https://<your-acaso> ACASO_KEY=<Agent Bridge key> python3 acaso_node.py --root ~/ACASO --shell --browser

Requirements:  python -m pip install httpx
Browser (opt): python -m pip install playwright && python -m playwright install chrome

Safety, enforced HERE on your machine (the server enforces the same rules again):
  * Only paths inside the --root folder(s) you pass are ever read or written.
  * The node only executes tasks you APPROVED in the ACASO "Local Node" tab. Read-only tasks are auto-approved.
  * Browser tasks fill forms and STOP. Nothing is submitted until you approve a separate submit step.
  * Passwords / 2FA: type them yourself in the Chrome window that opens. This program never sees or stores them.
  * --shell is off unless you pass it. Shell commands run inside the allowed root with a timeout.
  * --companion opens the ACASO Companion as its own small always-on-top desktop window (real Chrome in app mode,
    separate profile, so it survives closing your normal browser). Works with or without pairing.
"""
import argparse
import base64
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Missing dependency: python -m pip install httpx")
    sys.exit(1)

NODE_VERSION = "1.0.0"
STATE_FILE = Path.home() / ".acaso_node.json"


# ----------------------------------------------------------------------------------------------
class Node:
    def __init__(self, url, key, roots, shell, browser, name):
        self.api = url.rstrip("/") + "/api"
        self.h = {"X-ACASO-Key": key, "Content-Type": "application/json"}
        self.roots = [Path(r).expanduser().resolve() for r in roots]
        for r in self.roots:
            r.mkdir(parents=True, exist_ok=True)
        self.shell = shell
        self.browser = browser
        self.name = name or f"{platform.node()}-node"
        self.node_id = None
        self.pw = None
        self.browser_ctx = None
        self.pages = {}  # session_id -> page
        self.cx = httpx.Client(timeout=60)

    # ---- path safety ----
    def safe(self, p: str) -> Path:
        rp = Path(p).expanduser().resolve()
        for r in self.roots:
            try:
                rp.relative_to(r)
                return rp
            except ValueError:
                continue
        raise PermissionError(f"Path outside allowed roots: {p}")

    # ---- pairing ----
    def register(self):
        saved = {}
        if STATE_FILE.exists():
            try:
                saved = json.loads(STATE_FILE.read_text())
            except Exception:
                saved = {}
        caps = ["files"] + (["shell"] if self.shell else []) + (["browser"] if self.browser else [])
        body = {"name": self.name, "os": f"{platform.system()} {platform.release()}", "hostname": socket.gethostname(),
                "allowed_roots": [str(r) for r in self.roots], "capabilities": caps, "node_version": NODE_VERSION,
                "node_id": saved.get("node_id")}
        r = self.cx.post(f"{self.api}/node/register", headers=self.h, json=body)
        if r.status_code == 401:
            print("Rejected: bad ACASO_KEY. Copy it from the Agent Bridge tab.")
            sys.exit(1)
        r.raise_for_status()
        self.node_id = r.json()["id"]
        STATE_FILE.write_text(json.dumps({"node_id": self.node_id}))
        print(f"Paired as '{self.name}' ({self.node_id[:8]}) | roots={[str(x) for x in self.roots]} | caps={caps}")

    # ---- main loop ----
    def run(self):
        self.register()
        print("Waiting for approved tasks... (Ctrl+C to stop)")
        beat = 0
        while True:
            try:
                r = self.cx.post(f"{self.api}/node/{self.node_id}/claim", headers=self.h)
                if r.status_code == 404:
                    self.register()
                    continue
                task = r.json() if r.status_code == 200 else {}
                if task and task.get("id"):
                    self.execute(task)
                    continue
                beat += 1
                if beat % 8 == 0:
                    self.cx.post(f"{self.api}/node/{self.node_id}/heartbeat", headers=self.h)
            except KeyboardInterrupt:
                print("\nStopping node.")
                self.close_browser()
                return
            except Exception as e:
                print(f"[net] {e}")
                time.sleep(5)
            time.sleep(3)

    def report(self, tid, status, result=None, error=None, shot=None):
        body = {"status": status, "result": result, "error": error, "screenshot_b64": shot}
        self.cx.post(f"{self.api}/node/tasks/{tid}/result", headers=self.h, json=body)

    # ---- execution ----
    def execute(self, t):
        kind, p, tid = t["kind"], t.get("params") or {}, t["id"]
        print(f"-> {kind} {json.dumps(p)[:120]}")
        try:
            fn = getattr(self, "do_" + kind, None)
            if not fn:
                raise ValueError(f"unsupported task kind {kind}")
            out = fn(p)
            if isinstance(out, tuple):  # (status, result, screenshot)
                self.report(tid, out[0], out[1], None, out[2] if len(out) > 2 else None)
            else:
                self.report(tid, "done", out)
            print("   done")
        except Exception as e:
            print(f"   FAILED: {e}")
            self.report(tid, "failed", None, str(e)[:800])

    def do_sys_info(self, p):
        return {"os": platform.platform(), "python": sys.version.split()[0], "cwd": os.getcwd(), "roots": [str(r) for r in self.roots],
                "disk_free_gb": round(shutil.disk_usage(str(self.roots[0])).free / 1e9, 1) if self.roots else None}

    def do_file_list(self, p):
        d = self.safe(p.get("path") or str(self.roots[0]))
        if not d.is_dir():
            raise FileNotFoundError(f"not a directory: {d}")
        items = []
        for c in sorted(d.iterdir())[:500]:
            st = c.stat()
            items.append({"name": c.name, "type": "dir" if c.is_dir() else "file", "size": st.st_size, "modified": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(st.st_mtime))})
        return {"path": str(d), "count": len(items), "items": items}

    def do_file_stat(self, p):
        f = self.safe(p["path"])
        if not f.exists():
            return {"path": str(f), "exists": False}
        st = f.stat()
        return {"path": str(f), "exists": True, "type": "dir" if f.is_dir() else "file", "size": st.st_size}

    def do_file_read(self, p):
        f = self.safe(p["path"])
        data = f.read_bytes()
        limit = int(p.get("max_bytes") or 200_000)
        try:
            text = data[:limit].decode("utf-8")
            return {"path": str(f), "size": len(data), "truncated": len(data) > limit, "content": text}
        except UnicodeDecodeError:
            return {"path": str(f), "size": len(data), "binary": True, "b64_head": base64.b64encode(data[:4096]).decode()}

    def do_mkdir(self, p):
        d = self.safe(p["path"]); d.mkdir(parents=True, exist_ok=True)
        return {"path": str(d), "created": True}

    def do_file_write(self, p):
        f = self.safe(p["path"]); f.parent.mkdir(parents=True, exist_ok=True)
        existed = f.exists()
        if existed and p.get("backup", True):
            shutil.copy2(f, f.with_suffix(f.suffix + ".acaso.bak"))
        f.write_text(p.get("content") or "", encoding="utf-8")
        return {"path": str(f), "bytes": f.stat().st_size, "overwrote": existed, "backup": str(f.with_suffix(f.suffix + '.acaso.bak')) if existed else None}

    def do_file_append(self, p):
        f = self.safe(p["path"]); f.parent.mkdir(parents=True, exist_ok=True)
        with f.open("a", encoding="utf-8") as fh:
            fh.write(p.get("content") or "")
        return {"path": str(f), "bytes": f.stat().st_size}

    def do_file_move(self, p):
        s, d = self.safe(p["src"]), self.safe(p["dst"])
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
        return {"src": str(s), "dst": str(d)}

    def do_file_delete(self, p):
        f = self.safe(p["path"])
        trash = self.roots[0] / ".acaso_trash"; trash.mkdir(exist_ok=True)
        dest = trash / f"{int(time.time())}_{f.name}"
        shutil.move(str(f), str(dest))
        return {"path": str(f), "moved_to_trash": str(dest), "note": "soft-deleted; restore from .acaso_trash"}

    def do_shell(self, p):
        if not self.shell:
            raise PermissionError("node started without --shell")
        cwd = self.safe(p.get("cwd") or str(self.roots[0]))
        cmd = p["command"]
        r = subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True, text=True, timeout=int(p.get("timeout") or 120))
        return {"command": cmd, "cwd": str(cwd), "returncode": r.returncode, "stdout": r.stdout[-8000:], "stderr": r.stderr[-4000:]}

    # ---- browser (real Chrome on this PC, headed) ----
    def ensure_browser(self):
        if not self.browser:
            raise PermissionError("node started without --browser")
        if self.browser_ctx:
            return
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        profile = Path.home() / ".acaso_chrome_profile"
        try:
            self.browser_ctx = self.pw.chromium.launch_persistent_context(str(profile), channel="chrome", headless=False, viewport={"width": 1280, "height": 900})
        except Exception:
            self.browser_ctx = self.pw.chromium.launch_persistent_context(str(profile), headless=False, viewport={"width": 1280, "height": 900})
        print("   Chrome opened (persistent profile: logins you do here are kept between runs)")

    def close_browser(self):
        try:
            if self.browser_ctx:
                self.browser_ctx.close()
            if self.pw:
                self.pw.stop()
        except Exception:
            pass
        self.browser_ctx = None; self.pw = None; self.pages = {}

    def page(self, sid):
        self.ensure_browser()
        if sid not in self.pages or self.pages[sid].is_closed():
            self.pages[sid] = self.browser_ctx.new_page()
        return self.pages[sid]

    def shot(self, pg):
        return base64.b64encode(pg.screenshot(type="jpeg", quality=45)).decode()

    def do_browser_open(self, p):
        sid = p.get("session_id") or str(uuid.uuid4())[:8]
        pg = self.page(sid)
        pg.goto(p["url"], timeout=60000, wait_until="domcontentloaded")
        pg.wait_for_timeout(1000)
        return ("done", {"session_id": sid, "url": pg.url, "title": pg.title()}, self.shot(pg))

    def do_browser_screenshot(self, p):
        pg = self.page(p["session_id"])
        return ("done", {"session_id": p["session_id"], "url": pg.url, "title": pg.title()}, self.shot(pg))

    def _locate(self, pg, ref):
        ref = str(ref)
        for cand in (lambda: pg.get_by_label(ref, exact=False), lambda: pg.get_by_placeholder(ref, exact=False),
                     lambda: pg.locator(f"[name='{ref}']"), lambda: pg.locator(ref)):
            try:
                loc = cand()
                if loc.count() > 0:
                    return loc.first
            except Exception:
                continue
        raise LookupError(f"field not found: {ref}")

    def do_browser_fill(self, p):
        sid = p.get("session_id") or str(uuid.uuid4())[:8]
        pg = self.page(sid)
        if p.get("url"):
            pg.goto(p["url"], timeout=60000, wait_until="domcontentloaded"); pg.wait_for_timeout(800)
        filled, skipped = [], []
        for f in p.get("fields") or []:
            ref, val = f.get("label_or_selector"), f.get("value")
            if val is None or "[OWNER TYPES THIS]" in str(val):
                skipped.append({"field": ref, "reason": "owner types this manually (password/2FA/secret)"}); continue
            try:
                loc = self._locate(pg, ref)
                tag = loc.evaluate("e => e.tagName.toLowerCase()")
                typ = loc.evaluate("e => e.type || ''")
                if tag == "select":
                    loc.select_option(label=str(val))
                elif typ in ("checkbox", "radio"):
                    loc.check() if str(val).lower() in ("true", "yes", "1", "on") else loc.uncheck()
                else:
                    loc.fill(str(val))
                filled.append(ref)
            except Exception as e:
                skipped.append({"field": ref, "reason": str(e)[:120]})
        return ("awaiting_submit", {"session_id": sid, "url": pg.url, "title": pg.title(), "filled": filled, "skipped": skipped,
                                    "note": "Form filled, NOT submitted. Review the screenshot, finish any manual fields in the Chrome window, then approve a browser_submit task."}, self.shot(pg))

    def do_browser_submit(self, p):
        pg = self.page(p["session_id"])
        ref = p.get("label_or_selector")
        btn = self._locate(pg, ref) if ref else pg.locator("button[type=submit], input[type=submit], button:has-text('Submit'), button:has-text('Sign up'), button:has-text('Create account'), button:has-text('Continue')").first
        btn.click(timeout=15000)
        pg.wait_for_timeout(2500)
        return ("done", {"session_id": p["session_id"], "url": pg.url, "title": pg.title()}, self.shot(pg))

    def do_browser_close(self, p):
        sid = p.get("session_id")
        if sid and sid in self.pages:
            try: self.pages[sid].close()
            except Exception: pass
            self.pages.pop(sid, None)
        else:
            self.close_browser()
        return {"closed": sid or "all"}


# ----------------------------------------------------------------------------------------------
# Companion desktop window: Chrome --app mode + best-effort always-on-top
# ----------------------------------------------------------------------------------------------
def _find_chrome():
    cands = []
    if platform.system() == "Windows":
        pf = [os.environ.get("PROGRAMFILES", r"C:\Program Files"), os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"), os.environ.get("LOCALAPPDATA", "")]
        for base in pf:
            cands += [os.path.join(base, r"Google\Chrome\Application\chrome.exe"), os.path.join(base, r"Microsoft\Edge\Application\msedge.exe"),
                      os.path.join(base, r"BraveSoftware\Brave-Browser\Application\brave.exe")]
    elif platform.system() == "Darwin":
        cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    else:
        for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
            path = shutil.which(n)
            if path:
                cands.append(path)
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def _keep_on_top_windows(title_part: str, stop):
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE, SWP_NOACTIVATE = -1, 0x0002, 0x0001, 0x0010
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def find():
        found = []
        def cb(hwnd, _):
            n = user32.GetWindowTextLengthW(hwnd)
            if n:
                buf = ctypes.create_unicode_buffer(n + 1); user32.GetWindowTextW(hwnd, buf, n + 1)
                if title_part.lower() in buf.value.lower() and user32.IsWindowVisible(hwnd):
                    found.append(hwnd)
            return True
        user32.EnumWindows(EnumWindowsProc(cb), 0)
        return found
    while not stop.is_set():
        for hwnd in find():
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
        time.sleep(3)


def _keep_on_top_linux(title_part: str, stop):
    if not shutil.which("wmctrl"):
        print("   (install 'wmctrl' for always-on-top on Linux: sudo apt install wmctrl)")
        return
    while not stop.is_set():
        subprocess.run(["wmctrl", "-r", title_part, "-b", "add,above"], capture_output=True)
        time.sleep(3)


def launch_companion(url: str, on_top: bool = True):
    """Open the Companion as its own app window; returns the Popen (or None)."""
    import threading
    chrome = _find_chrome()
    target = url.rstrip("/") + "/?mode=companion"
    if not chrome:
        print("No Chrome/Edge found - opening the Companion in your default browser instead.")
        import webbrowser; webbrowser.open(target)
        return None
    profile = Path.home() / ".acaso_companion_profile"
    args = [chrome, f"--app={target}", f"--user-data-dir={profile}", "--window-size=440,760", "--window-position=40,40",
            "--no-first-run", "--no-default-browser-check", "--disable-features=TranslateUI"]
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Companion window opened ({os.path.basename(chrome)} app mode, profile {profile})")
    if on_top:
        stop = threading.Event()
        fn = _keep_on_top_windows if platform.system() == "Windows" else (_keep_on_top_linux if platform.system() == "Linux" else None)
        if fn:
            threading.Thread(target=fn, args=("ACASO Companion", stop), daemon=True).start()
            print("   always-on-top: enabled")
        else:
            print("   always-on-top: not available on this OS (window still opens as an app)")
    return proc


def main():
    ap = argparse.ArgumentParser(description="ACASO Local Node")
    ap.add_argument("--url", default=os.environ.get("ACASO_URL"), help="ACASO site URL (or env ACASO_URL)")
    ap.add_argument("--key", default=os.environ.get("ACASO_KEY"), help="Agent Bridge key (or env ACASO_KEY)")
    ap.add_argument("--root", action="append", default=[], help="Allowed folder (repeatable). Default: ~/ACASO")
    ap.add_argument("--shell", action="store_true", help="Allow approved shell commands inside the root")
    ap.add_argument("--browser", action="store_true", help="Allow approved browser tasks in a real Chrome window")
    ap.add_argument("--name", default=None)
    ap.add_argument("--companion", action="store_true", help="Open the ACASO Companion as its own always-on-top desktop window")
    ap.add_argument("--no-top", action="store_true", help="With --companion: do not force always-on-top")
    a = ap.parse_args()
    if not a.url:
        print("Need --url or ACASO_URL."); sys.exit(1)
    proc = launch_companion(a.url, on_top=not a.no_top) if a.companion else None
    if not a.key:
        if a.companion:
            print("No ACASO_KEY given - running Companion window only (no file/browser tasks). Ctrl+C to close.")
            try:
                while proc is None or proc.poll() is None:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            return
        print("Need --key/ACASO_KEY (key is on the Agent Bridge tab)."); sys.exit(1)
    roots = a.root or [str(Path.home() / "ACASO")]
    Node(a.url, a.key, roots, a.shell, a.browser, a.name).run()


if __name__ == "__main__":
    main()

```


### `handoff/scripts/acaso_client.py`
```python
"""
ACASO Omniverse - shared client for the runner scripts.

Set ACASO_URL to your deployment, e.g.
    export ACASO_URL=https://contest-ready-app.preview.emergentagent.com
Defaults to the hosted preview. All routes live under /api.
"""
import os, sys
from datetime import datetime
import httpx

ACASO_URL = os.environ.get("ACASO_URL", "https://contest-ready-app.preview.emergentagent.com").rstrip("/")
API = f"{ACASO_URL}/api"
# The app requires owner login; scripts authenticate with the Agent Bridge key instead (Agent Bridge tab).
HEADERS = {"X-ACASO-Key": os.environ.get("ACASO_KEY", "")}


def check_online() -> bool:
    try:
        return httpx.get(f"{API}/acaso/presets", headers=HEADERS, timeout=10.0).status_code == 200
    except Exception:
        return False


def deliberate(challenge: str, challenge_type: str, additional_context: str = "", preset_id: str | None = None) -> dict:
    with httpx.Client(timeout=320.0) as client:
        r = client.post(f"{API}/acaso/deliberate", headers=HEADERS, json={
            "challenge": challenge,
            "challenge_type": challenge_type,
            "preset_id": preset_id,
            "context": {"additional_context": additional_context} if additional_context else None,
        })
        r.raise_for_status()
        return r.json()


def fetch_preset(preset_id: str) -> dict:
    r = httpx.get(f"{API}/acaso/presets", headers=HEADERS, timeout=10.0)
    r.raise_for_status()
    for p in r.json():
        if p["id"] == preset_id:
            return p
    raise SystemExit(f"preset {preset_id!r} not found on server")


def write_report(result: dict, title: str, out_file: str, extra_sections: str = "") -> str:
    council = result.get("council_consulted", [])
    md = f"""# {title}
Generated: {result.get('timestamp', datetime.now().isoformat())[:19]} | Deliberation: {result.get('deliberation_id')}
Council: {', '.join(council) if council else 'n/a'} | Shadow veto: {'YES' if result.get('shadow_veto') else 'no'}

> {result.get('data_provenance', '')}

---
## WEAK SIGNALS (inferred)
{result.get('weak_signals') or '_none_'}

---
{result.get('sovereign_directive', '')}

---
## INTERNAL WEAVERS ANALYSIS
{result.get('weavers_synthesis', '')}
{extra_sections}
---
*ACASO Omniverse - Council of Weavers - (c) 2026 Alexander Mojica / MediaLinxS*
"""
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md)
    return out_file


def require_online():
    print(f"Checking ACASO at {ACASO_URL} ...")
    if not check_online():
        print("ACASO is not reachable or the key is missing. Set ACASO_URL and ACASO_KEY (Agent Bridge tab).")
        sys.exit(1)
    print("ACASO Omniverse online.\n")

```


### `handoff/scripts/script_01_genesis_engine.py`
```python
"""
ACASO KING - SCRIPT 01: THE GENESIS ENGINE  (ACASO Omniverse edition)
One-Of-A-Kind Product / Service / Invention Generator.

Calls the live Council of Weavers at POST /api/acaso/deliberate using the server-side
'genesis' preset (edit FOUNDER_OVERRIDE below to customise the founder profile).

HOW TO RUN:
    pip install httpx
    export ACASO_URL=https://<your-acaso-host>
    python script_01_genesis_engine.py
"""
import sys
from datetime import datetime
from acaso_client import require_online, fetch_preset, deliberate, write_report

FOUNDER_OVERRIDE = ""  # optional: paste a new 'Founder Profile' block to replace the preset's


def main():
    print("ACASO GENESIS ENGINE - INVENTION DISCOVERY")
    require_online()
    preset = fetch_preset("genesis")
    challenge = preset["challenge"]
    if FOUNDER_OVERRIDE.strip():
        head, _, tail = challenge.partition("MISSION:")
        challenge = f"GENESIS DIRECTIVE - INVENTION MANDATE\n\nFounder Profile:\n{FOUNDER_OVERRIDE.strip()}\n\nMISSION:{tail}"
    print("Convening Architect / Shadow / Muse / Finance -> Meta-Weaver (60-180s)...\n")
    try:
        result = deliberate(challenge, preset["challenge_type"], preset.get("additional_context", ""), preset_id="genesis")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    print("=" * 65)
    print(result.get("sovereign_directive", ""))
    print("=" * 65)
    out = write_report(result, "ACASO GENESIS ENGINE - INVENTION BRIEF",
                       f"genesis_invention_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    print(f"\nInvention brief saved: {out}")
    print(f"Also stored server-side: {result.get('deliberation_id')} (open the Council tab -> Past deliberations)")


if __name__ == "__main__":
    main()

```


### `handoff/scripts/script_03_sovereign_hunter.py`
```python
"""
ACASO KING - SCRIPT 03: THE SOVEREIGN HUNTER  (ACASO Omniverse edition)
Client / Contract / Job Profile Builder + Outreach Engine.

EDIT HUNT_MODE, YOUR_OFFER, TARGET_MARKET below, then:
    pip install httpx
    export ACASO_URL=https://<your-acaso-host>
    python script_03_sovereign_hunter.py
"""
import sys
from datetime import datetime
from acaso_client import require_online, deliberate, write_report

HUNT_MODE = "clients"  # "clients" | "contracts" | "jobs"

YOUR_OFFER = """
Product/Service: OmniTrackX - AI-powered logistics SaaS for courier delivery,
furniture moving, and office relocation companies.
- Real-time job tracking with live map
- AI-powered damage reports and claim filing
- Client-facing dashboard with transparent status updates
- QR + condition-based inventory tracking
Pricing: Starter $149/mo | Growth $349/mo | Pro $749/mo | Enterprise custom
Market: Initially Boston, MA
Founder: Alexander Mojica / MediaLinxS
"""

TARGET_MARKET = """
Boston, MA area logistics and moving companies: last-mile couriers (10-50 drivers),
furniture movers and storage, office relocation specialists, B2B delivery for
medical/legal/tech, companies still on spreadsheets, paper, or basic apps like Track-POD.
"""

HUNT_LABEL = {"clients": "high-value clients", "contracts": "lucrative contracts or RFPs",
              "jobs": "premium job opportunities or partnerships"}

CHALLENGE = f"""SOVEREIGN HUNTER DIRECTIVE - TARGET ACQUISITION

Hunt Mode: {HUNT_MODE.upper()} - Find 3 {HUNT_LABEL.get(HUNT_MODE, 'targets')}

What is being offered:
{YOUR_OFFER}
Target market:
{TARGET_MARKET}
PHASE 1 - TARGET IDENTIFICATION: 3 specific, realistic target categories. For each:
### TARGET [N] - [Category]
**Profile:** type, size, pain points the offer solves, decision maker, where they gather, trigger events, objections + neutralizers.
**Why they need this specifically:** 2-3 sentences.
**Credibility signals that will resonate.**

PHASE 2 - OUTREACH GENERATION (per target): Version A cold email (subject + body <150 words); Version B LinkedIn DM (<80 words); Version C follow-up (day 3).

PHASE 3 - SEQUENCE STRATEGY (per target): Day 1 / Day 3 / Day 7 / Day 14.

PHASE 4 - EXECUTION TOOLKIT: search strings, associations, directories, events; the single highest-leverage near-zero-cost action for TODAY.

## SOVEREIGN VERDICT
Which target is the highest-probability first close and exactly what to send tomorrow morning.
"""

CHECKLIST = """
---
## NEXT ACTIONS CHECKLIST
- [ ] Review Target 1 profile and send Version A outreach
- [ ] Review Target 2 profile and send Version A outreach
- [ ] Review Target 3 profile and send Version A outreach
- [ ] Calendar: Day 3 follow-ups
- [ ] Calendar: Day 7 pattern interrupt
- [ ] Calendar: Day 14 breakup messages
"""


def main():
    print(f"ACASO SOVEREIGN HUNTER - hunt mode: {HUNT_MODE.upper()}")
    require_online()
    print("Profiling targets and drafting outreach via the Council (60-180s)...\n")
    try:
        result = deliberate(CHALLENGE, "market_entry",
                            f"Sovereign Hunter mode - {HUNT_MODE}. Identify 3 real, specific, high-value targets. "
                            "Outreach must be specific, human, conversion-optimized. No generic templates.",
                            preset_id="hunter")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    print("=" * 65)
    print(result.get("sovereign_directive", ""))
    print("=" * 65)
    out = write_report(result, f"ACASO SOVEREIGN HUNTER - TARGET ACQUISITION PACKAGE ({HUNT_MODE.upper()})",
                       f"sovereign_hunter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md", CHECKLIST)
    print(f"\nOutreach package saved: {out}")
    print(f"Also stored server-side: {result.get('deliberation_id')}")


if __name__ == "__main__":
    main()

```
