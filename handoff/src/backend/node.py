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
    return await db.research_pages.find({}, {"_id": 0, "text_excerpt": 0, "links": 0, "forms": 0}).sort("retrieved_at", -1).to_list(limit)
