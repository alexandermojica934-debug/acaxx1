from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import logging
import asyncio
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

def soul_problem(mission: dict) -> str:
    return (f"Program: {mission.get('program')} on {mission.get('platform')}\n"
            f"In-scope asset: {mission.get('asset')}\n"
            f"Vulnerability class: {mission.get('vuln_type')} | Severity: {mission.get('severity')} | CVSS: {mission.get('cvss')}\n"
            f"Context report:\n{(mission.get('report') or '')[:1200]}")

@api_router.post("/missions/{mid}/deploy-souls")
async def deploy_souls(mid: str):
    doc = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Mission not found")
    if doc.get("kind") != "bugbounty":
        raise HTTPException(400, "Soul Council deploys on bug-bounty engagements")

    problem = soul_problem(doc)

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

    ok_souls = [s for s in souls if s["ok"]]
    council_text = "\n\n".join([f"[{s['name']} · {s['role']} · {s['model_label']}]\n{s['analysis']}" for s in ok_souls])
    throne_system = (
        "You are ETERNAL THRONE — the Soul Brain and sovereign arbiter of ACASO (House of Nova). "
        "You command a council of specialist AI souls, each running on a different model. Fuse their findings into "
        "the FINAL VERIFIED RESOLUTION that truly fixes the problem. Respond ONLY with valid minified JSON, no prose."
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

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
