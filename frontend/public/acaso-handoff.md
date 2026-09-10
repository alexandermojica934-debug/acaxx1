# ACASO Omniverse — Complete Handoff

_Generated: 2026-09-10T00:24:06.782518+00:00_

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
from datetime import datetime, timezone

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

@api_router.post("/compile-directive", response_model=Mission)
async def compile_directive(req: CompileRequest):
    if not req.directive.strip():
        raise HTTPException(400, "Directive is required")
    mode = req.mode if req.mode in MODES else "Move"
    lesson_docs = await db.chronicle.find({}, {"_id": 0, "lesson": 1}).sort("completed_at", -1).to_list(5)
    lessons = [d["lesson"] for d in lesson_docs if d.get("lesson")]
    try:
        raw = await llm_call(COMPILE_SYSTEM, compile_prompt(req.directive, mode, lessons))
        data = extract_json(raw)
    except Exception as e:
        logger.error(f"compile failed: {e}")
        raise HTTPException(500, f"Directive compilation failed: {e}")

    steps = [Step(title=s.get("title", "Step"), detail=s.get("detail", "")) for s in data.get("steps", [])]
    mission = Mission(
        directive=req.directive,
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
    )
    await db.missions.insert_one(mission.model_dump())
    return mission

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




app.include_router(api_router)

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

```


### `backend/requirements.txt`
```text
fastapi==0.110.1
uvicorn==0.25.0
boto3>=1.34.129
requests-oauthlib>=2.0.0
cryptography>=42.0.8
python-dotenv>=1.0.1
pymongo==4.6.3
pydantic>=2.6.4
email-validator>=2.2.0
pyjwt>=2.10.1
bcrypt==4.1.3
passlib>=1.7.4
tzdata>=2024.2
motor==3.3.1
pytest>=8.0.0
pytest-xdist>=3.6.0
black>=24.1.1
isort>=5.13.2
flake8>=7.0.0
mypy>=1.8.0
python-jose>=3.3.0
requests>=2.31.0
pandas>=2.2.0
numpy>=1.26.0
python-multipart>=0.0.9
jq>=1.6.0
typer>=0.9.0
emergentintegrations==0.2.0
google-api-python-client==2.199.0
google-auth==2.57.0
google-auth-httplib2==0.4.2
google-auth-oauthlib==1.4.1
uritemplate==4.2.0

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
import React, { useState } from "react";
import "./App.css";
import { Toaster } from "sonner";
import SovereignHome from "./components/SovereignHome";
import AskAllAIs from "./components/AskAllAIs";
import Chronicle from "./components/Chronicle";
import BugBounty from "./components/BugBounty";
import AgentBridge from "./components/AgentBridge";
import FileAnalyzer from "./components/FileAnalyzer";
import SelfDirective from "./components/SelfDirective";
import { Sparkles, LayoutGrid, MessagesSquare, BookOpen, ShieldAlert, Plug, Boxes, Wand2 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const TABS = [
  { key: "home", label: "Sovereign Home", icon: LayoutGrid },
  { key: "bounty", label: "Bug Bounty", icon: ShieldAlert },
  { key: "askai", label: "Ask All AIs", icon: MessagesSquare },
  { key: "analyzer", label: "File Analyzer", icon: Boxes },
  { key: "self", label: "Self-Directive", icon: Wand2 },
  { key: "chronicle", label: "Chronicle", icon: BookOpen },
  { key: "bridge", label: "Agent Bridge", icon: Plug },
];

function App() {
  const [tab, setTab] = useState(() => {
    try {
      const t = new URLSearchParams(window.location.search).get("tab");
      return TABS.some((x) => x.key === t) ? t : "home";
    } catch { return "home"; }
  });

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
        <div className="owner-badge"><span className="dot" /> Owner · Sovereign</div>
      </header>

      <main className="stage">
        {tab === "home" && <SovereignHome />}
        {tab === "bounty" && <BugBounty />}
        {tab === "askai" && <AskAllAIs />}
        {tab === "analyzer" && <FileAnalyzer />}
        {tab === "self" && <SelfDirective />}
        {tab === "chronicle" && <Chronicle />}
        {tab === "bridge" && <AgentBridge />}
      </main>

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

function Markdown({ text, onCite }) {
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
  Search, History, AlertTriangle, GitCommitHorizontal, CheckCircle2, ScrollText
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

  const loadManifest = useCallback(async () => {
    try { const r = await axios.get(`${API}/self/manifest`); setManifest(r.data); }
    catch (e) { console.error(e); }
  }, []);
  const loadHistory = useCallback(async () => {
    try { const r = await axios.get(`${API}/self/history`); setHistory(r.data); }
    catch (e) { console.error(e); }
  }, []);

  useEffect(() => { loadManifest(); loadHistory(); }, [loadManifest, loadHistory]);

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
                  <span className="sd-hinstr" title={h.instruction}>{h.instruction}</span>
                  <span className="sd-hpaths">{(h.paths || []).join(", ")}</span>
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
