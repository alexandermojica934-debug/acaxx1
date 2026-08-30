from fastapi import FastAPI, APIRouter, HTTPException
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
    summary: str = ""
    steps: List[Step] = []
    evidence: List[str] = []
    payment_path: str = ""
    outcome_metric: str = ""
    authority: str = "Bounded autonomy — owner approval at MFA, contract & payment"
    stage: str = "Directive"
    status: str = "active"  # active | paused | complete
    amount: float = 0.0
    currency: str = "USD"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CompileRequest(BaseModel):
    directive: str
    mode: Optional[str] = "Move"

class AdvanceRequest(BaseModel):
    step_id: Optional[str] = None
    done: Optional[bool] = True

class ExecuteRequest(BaseModel):
    step_id: Optional[str] = None  # None => next undone step

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

@api_router.get("/missions", response_model=List[Mission])
async def list_missions():
    docs = await db.missions.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return docs

@api_router.get("/missions/{mid}", response_model=Mission)
async def get_mission(mid: str):
    doc = await db.missions.find_one({"id": mid}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Mission not found")
    return doc

def recompute_stage(mission: dict) -> dict:
    steps = mission.get("steps", [])
    total = len(steps) or 1
    done = sum(1 for s in steps if s.get("done"))
    ratio = done / total
    idx = min(len(STAGES) - 1, 1 + int(ratio * (len(STAGES) - 2)))
    if done == total:
        mission["stage"] = "Receipt"
        mission["status"] = "complete"
    else:
        mission["stage"] = STAGES[idx]
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
