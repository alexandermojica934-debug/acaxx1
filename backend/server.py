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
}
COMMAND_SCHEMA = (
    "Return ONLY minified JSON {\"intent\": ..., \"args\": {...}} with intent one of: "
    "open_tab {tab: home|bounty|council|voice|radar|askai|analyzer|self|chronicle|bridge|node}; "
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

@app.on_event("startup")
async def _startup_self_scan():
    global _self_scan_task
    if _self_scan_task is None:
        _self_scan_task = asyncio.create_task(_self_scan_loop())
        logger.info("Self-scan scheduler started (propose-only)")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
