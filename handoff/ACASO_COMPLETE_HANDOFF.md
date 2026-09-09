# ACASO Omniverse — Complete Replication Handoff

> **Purpose of this document:** Give another AI (or developer) everything needed to rebuild
> this app *exactly* — architecture, environment, dependencies, every line of source, API
> contract, LLM prompts/model IDs, known caveats, and the pending roadmap.

---

## 1. What the product is

**ACASO — "Directive-to-Payment Operating System"** (branded *Synarchy Aetheris*).
A contest-ready, demo-mode full-stack app. The owner speaks a plain-language directive
("Land a $750 logo client this week"); ACASO compiles it with an LLM into a **Mission Graph**
(steps, evidence, payment path, outcome metric, authority), then a simulated execution body
(**NEXUS Action Bus**) runs each step and records timestamped evidence. Completed missions are
inscribed in a **Chronicle / Outcome Ledger** with an AI-distilled lesson that feeds back into
future compilations.

### Modules (5 tabs)
| Tab | Component | What it does |
|---|---|---|
| **Sovereign Home** | `SovereignHome.js` | Directive Console (4 modes: Make/Find/Move/Collect), metrics, "Perfect Next" (Soul Brain recommendation), 6-stage Payment Pipeline, NEXUS feed, Mission Board with Run Next / Auto-run |
| **Bug Bounty** | `BugBounty.js` | Authorized responsible-disclosure engagements: program/platform/asset/vuln/severity/CVSS, 7-stage security pipeline, gated steps (`approval_required`) with **Approve & Continue**, disclosure report viewer, **Soul Council** (3 personas on 3 different LLMs) + **Eternal Throne** fused verdict |
| **Ask All AIs** | `AskAllAIs.js` | Sends one question to OpenAI + Gemini + Claude in parallel, then a "Synarchy synthesis" arbiter fuses them |
| **Chronicle** | `Chronicle.js` | Outcome Ledger timeline: completed missions, amounts, lessons learned |
| **Agent Bridge** | `AgentBridge.js` | API-key-protected `/api/agent/*` endpoints so external agents (Manus, Gemini, ChatGPT, cURL) can issue directives & run missions; connector/tool schemas; live playground; activity ledger |

### Operating model
- **DEMO ONLY.** No real payments, accounts, or external attack tooling. NEXUS *simulates* execution via LLM.
- All LLM calls go through the **Emergent universal LLM key** (`emergentintegrations` library).
- Data persisted in **MongoDB** (collections: `missions`, `action_logs`, `chronicle`, `bridge_config`, `agent_calls`).
- All IDs are **UUID strings** (never ObjectId). All datetimes are UTC ISO strings.

---

## 2. Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3, **FastAPI 0.110**, **Motor 3.3** (async Mongo), Pydantic v2, `emergentintegrations==0.2.0`, uvicorn on `0.0.0.0:8001` |
| Frontend | **React 19** (Create React App + **CRACO**), axios, **framer-motion**, **sonner** toasts, **lucide-react** icons, Tailwind 3.4 (present but app styling is in plain `App.css` with CSS variables), Shadcn/UI components available under `src/components/ui/` (not heavily used) |
| DB | MongoDB |
| Routing | Ingress routes `/api/*` → backend :8001, everything else → frontend :3000 |
| Process mgmt | supervisor (`supervisorctl restart backend|frontend`) |

---

## 3. Directory layout

```
/app
├── backend/
│   ├── .env                     # MONGO_URL, DB_NAME, CORS_ORIGINS, EMERGENT_LLM_KEY
│   ├── requirements.txt
│   └── server.py                # ENTIRE backend (806 lines, single file)
├── frontend/
│   ├── .env                     # REACT_APP_BACKEND_URL, WDS_SOCKET_PORT, ENABLE_HEALTH_CHECK
│   ├── package.json
│   ├── craco.config.js          # '@' alias → src, dev-server compat
│   ├── jsconfig.json            # '@/*' path alias
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── components.json          # shadcn config
│   ├── public/index.html
│   └── src/
│       ├── index.js             # React root + react-query provider
│       ├── index.css            # tailwind base + shadcn CSS vars
│       ├── App.js               # tab shell, exports `API` base URL
│       ├── App.css              # ALL app styling (design tokens + every module)
│       ├── lib/utils.js         # cn() helper
│       └── components/
│           ├── SovereignHome.js
│           ├── BugBounty.js
│           ├── AskAllAIs.js
│           ├── Chronicle.js
│           ├── AgentBridge.js
│           └── ui/              # shadcn primitives (stock, unmodified)
```

---

## 4. Environment variables

### `backend/.env`
```
MONGO_URL=mongodb://localhost:27017        # your Mongo connection string
DB_NAME=acaso_db                           # any db name
CORS_ORIGINS=*                             # comma-separated origins or *
EMERGENT_LLM_KEY=sk-emergent-xxxxxxxx      # Emergent universal LLM key (get from Emergent profile → Universal Key)
```

### `frontend/.env`
```
REACT_APP_BACKEND_URL=https://your-host    # NO trailing slash, NO /api. Frontend appends /api itself.
WDS_SOCKET_PORT=443                        # only needed behind HTTPS proxy
ENABLE_HEALTH_CHECK=false
```

> If you are NOT on the Emergent platform, replace `emergentintegrations` usage in `llm_call()`
> with direct OpenAI / Google / Anthropic SDK calls. The function signature
> `llm_call(system, prompt, provider, model, session)` is the only seam you need to swap.

---

## 5. Install & run

```bash
# backend
cd /app/backend
pip install -r requirements.txt
# emergentintegrations needs the extra index:
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
uvicorn server:app --host 0.0.0.0 --port 8001 --reload     # (in this env: supervisorctl restart backend)

# frontend
cd /app/frontend
yarn install            # NEVER npm
yarn start              # port 3000     (in this env: supervisorctl restart frontend)

# sanity check
curl $REACT_APP_BACKEND_URL/api/            # {"message":"ACASO Omniverse online","modes":[...]}
# frontend compile check
cd /app/frontend && npx esbuild src/ --loader:.js=jsx --bundle --outfile=/dev/null
```

---

## 6. LLM model configuration (CRITICAL — these exact IDs work)

```python
MODEL_MAP = {
    "openai":    ("openai",    "gpt-4o-mini",      "OmniMind · GPT-4o"),
    "gemini":    ("gemini",    "gemini-3.6-flash", "OmniMind · Gemini 3.6"),
    "anthropic": ("anthropic", "claude-haiku-4-5", "OmniMind · Claude Haiku 4.5"),
}
```
**Do NOT use** `gemini-2.0-flash` (404, retired) or `claude-3-5-haiku-20241022` (not found).
Those were the original values and they broke Ask All AIs until replaced.

Default `llm_call()` provider/model = `openai` / `gpt-4o-mini` (used for compile, NEXUS, lessons, Perfect Next, chat synthesis).

`llm_call_failover(system, prompt, order)` = "Rebirth Protocol": tries providers in order until one answers. Used by Soul Council and Eternal Throne.

### Soul Council personas → models
| Soul | Role | Primary model | Failover order |
|---|---|---|---|
| Vision Command | Recon Strategist | Gemini | gemini → openai → anthropic |
| Fusion Engine | Root-Cause Analyst | OpenAI | openai → gemini → anthropic |
| Rebirth Protocol | Remediation Engineer | Claude | anthropic → openai → gemini |
| **Eternal Throne** (synthesis) | Soul Brain arbiter | gemini → openai → anthropic | |

All system prompts are verbatim in `server.py` (see `COMPILE_SYSTEM`, `BOUNTY_SYSTEM`, `NEXUS_SYSTEM`, `SOULS`, `throne_system`).

---

## 7. Data models (Pydantic, stored 1:1 in Mongo)

```
Mission {
  id: uuid, directive, title, mode: Make|Find|Move|Collect, kind: revenue|bugbounty,
  summary, steps: [Step{id(8-char), title, detail, done}], evidence: [str],
  payment_path, outcome_metric, authority,
  stage: str, stage_set: [str], status: active|paused|complete, amount: float, currency: "USD",
  # bug-bounty only:
  program, platform, asset, vuln_type, severity: Critical|High|Medium|Low|Info, cvss: float, report (markdown),
  soul_council: {souls:[...], resolution:{root_cause,fix,verification,confidence,status}, throne_label, deployed_at} | null,
  created_at: iso
}
ActionLog     { id, mission_id, mission_title, step_title, action, evidence, status: success|approval_required, timestamp }
ChronicleEntry{ id, mission_id, title, mode, amount, outcome_metric, lesson, completed_at }
bridge_config { _id:"bridge", api_key:"acaso_<token>", created_at }
agent_calls   { id, agent, action, detail, timestamp }
```

**Stage sets**
- Revenue: `["Directive","Discovery","Deliverable","Outreach","Payment","Receipt"]`
- Bug bounty: `["Program","Recon","Vuln Found","PoC","Disclosure","Triage","Payout"]`

`recompute_stage()` maps done-ratio → stage index within the mission's own `stage_set`; all steps done ⇒ last stage + `status="complete"` ⇒ Chronicle entry auto-created with an LLM lesson.

---

## 8. API reference (all under `/api`)

### Core
| Method | Path | Body / Query | Returns |
|---|---|---|---|
| GET | `/` | | health message |
| POST | `/compile-directive` | `{directive, mode?}` | `Mission` (revenue, stage=Discovery) |
| POST | `/compile-bounty` | `{directive, platform?}` | `Mission` (kind=bugbounty, stage=Recon) |
| GET | `/missions` | `?kind=revenue|bugbounty` | `[Mission]` newest first |
| GET | `/missions/{id}` | | `Mission` |
| PATCH | `/missions/{id}/advance` | `{step_id?, done?}` | `Mission` (manual toggle; no step_id ⇒ next undone) |
| POST | `/missions/{id}/execute-step` | `{step_id?, approved?}` | `{mission, log}` — NEXUS simulated execution; `approval_required` blocks unless `approved:true` |
| POST | `/missions/{id}/deploy-souls` | | `{mission, council}` — bugbounty only, 3 souls in parallel + Throne synthesis |
| PATCH | `/missions/{id}/status?status=active|paused` | | `Mission` |
| DELETE | `/missions/{id}` | | `{deleted}` |
| GET | `/action-feed?limit=40` | | `[ActionLog]` |
| GET | `/chronicle` | | `[ChronicleEntry]` |
| GET | `/stats` | | `{total, active, complete, projected_revenue, collected_revenue, pipeline:{stage:count}, stages}` |
| GET | `/perfect-next` | | `{recommendation, mission_id, mission_title}` |
| POST | `/chat` | `{message, models?:["openai","gemini","anthropic"], session_id?}` | `{session_id, results:[{provider,label,answer,ok}], synthesis}` |

### Agent Bridge
| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/bridge/info` | none | returns `api_key`, header name, endpoint map |
| POST | `/bridge/regenerate` | none | mints new key (revokes old) |
| GET | `/bridge/activity?limit=25` | none | external call ledger |
| POST | `/agent/directive` | `X-ACASO-Key` | `{directive, kind?, mode?, platform?, agent?}` → `Mission` |
| GET | `/agent/missions?kind=` | `X-ACASO-Key` | `[Mission]` |
| GET | `/agent/missions/{id}` | `X-ACASO-Key` | `Mission` |
| POST | `/agent/missions/{id}/run` | `X-ACASO-Key` | `{run:"next"|"all", approved?, agent?}` → `{mission, logs}` |

Missing/invalid key ⇒ `401`. (Note: a POST to a GET-only path returns `405` before auth runs — test with the correct verb.)

### Example calls
```bash
B=$REACT_APP_BACKEND_URL/api
curl -X POST $B/compile-directive -H 'Content-Type: application/json' -d '{"directive":"Land a $750 logo client this week","mode":"Move"}'
curl -X POST $B/compile-bounty   -H 'Content-Type: application/json' -d '{"directive":"Find and responsibly disclose an IDOR on a fintech API","platform":"HackerOne"}'
curl -X POST $B/missions/<id>/execute-step -H 'Content-Type: application/json' -d '{"approved":false}'
curl -X POST $B/missions/<id>/deploy-souls
curl -X POST $B/chat -H 'Content-Type: application/json' -d '{"message":"Best way to price a logo?","models":["openai","gemini","anthropic"]}'
KEY=$(curl -s $B/bridge/info | python3 -c 'import sys,json;print(json.load(sys.stdin)["api_key"])')
curl -X POST $B/agent/directive -H "X-ACASO-Key: $KEY" -H 'Content-Type: application/json' -d '{"directive":"Get 3 newsletter sponsors","kind":"revenue","agent":"Gemini"}'
```

---

## 9. Frontend behaviour notes

- `App.js` exports `API = ${REACT_APP_BACKEND_URL}/api`; every component imports it.
- Tabs are plain state (`home | bounty | askai | chronicle | bridge`), no router.
- **Sovereign Home** fetches `/missions?kind=revenue`, `/stats`, `/action-feed`; `/perfect-next` refreshes when mission count changes. Auto-run loops `execute-step` with 650 ms delay, stops on `approval_required`.
- **Bug Bounty** fetches `/missions?kind=bugbounty` and filters the action feed to those mission ids. `gate[mid]` holds the step title awaiting owner approval; **Approve & Continue** re-runs with `approved:true`. Soul Council panel renders `soul_council.souls[]` cards (icon/colour by soul id) and the Throne verdict with a confidence bar.
- **Agent Bridge** builds Gemini `function_declarations`, OpenAI `tools`, Manus/MCP action map, and a cURL snippet from the live key; playground POSTs to `/agent/directive` with `agent:"Playground"`.
- Toasts: `sonner` `<Toaster position="top-center" theme="dark" richColors />`.
- Every key interactive element has a `data-testid` (e.g. `directive-input`, `compile-btn`, `autorun-btn`, `bounty-compile`, `approve-btn`, `deploy-souls`, `askai-send`, `regen-key`, `pg-run`, `tab-*`, `mode-*`, `prov-*`).

### Design tokens (App.css `:root`)
```
--bg #060814 · --bg2 #0a0e22 · --panel rgba(18,22,46,.72) · --panel-solid #10142e
--border rgba(130,140,220,.16) · --border-lit rgba(150,130,255,.4)
--violet #8b7cff · --violet2 #a78bfa · --cyan #4fd1ff · --gold #f5c451 · --green #48d597
--text #eef0ff · --muted #9aa0c8 · --dim #6b708f
Bug-bounty accent: #ff5470 → #f5843c ; Soul colours: vision #4fd1ff, fusion #8b7cff, rebirth #ff7a90
```
Dark, glass-morphic panels, aurora radial gradients, 48 px grid overlay, Inter font.

---

## 10. Verification status (honest)

| Feature | Status |
|---|---|
| Compile directive / bounty | Implemented, curl-tested — real LLM output |
| Ask All AIs (3 models + synthesis) | Implemented, curl-tested after model-ID fix |
| NEXUS execute-step / Auto-run / approval gates | Implemented, curl + screenshot tested |
| Chronicle + lessons fed back into compile | Implemented, curl tested |
| Agent Bridge authenticated flows | Implemented, curl tested (401 on missing key **not yet re-verified** — earlier test hit 405 due to wrong verb) |
| Soul Council + Eternal Throne | Implemented, curl + screenshot tested |
| Automated test suite (`testing_agent`) | **Never run** — all verification was manual curl/screenshot |
| User browser confirmation | Not recorded |

---

## 11. Pending roadmap (user's latest request — NOT started)

1. **Soul Dissent View** — extend the Throne synthesis JSON with
   `"dissent":[{topic, positions:{vision,fusion,rebirth}, reconciliation, chosen}]`
   and render a "Dissent & Reconciliation" panel under the verdict.
2. **Fix Export** — add `"pr_export":{title, summary, root_cause, changes:[..], tests:[..], risk_rollout}`
   to the same Throne call; add a copy-to-clipboard "Export as PR / patch note" button that renders it as markdown.
   Safely default both fields if the LLM omits them. Add `data-testid="dissent-panel"`, `data-testid="export-fix-btn"`.
3. Re-verify `/api/agent/*` returns 401 without key (use POST on `/agent/directive`).
4. Run a full automated test pass.

---

## 12. Reproduction checklist for another AI

1. Create the directory tree in §3.
2. Copy the files in `01_backend_server.py`, `02_frontend_*` **verbatim** (they follow in this package).
3. Fill in the two `.env` files (§4). Never commit real keys.
4. `pip install -r requirements.txt` (+ emergentintegrations extra index) and `yarn install`.
5. Start backend on 8001, frontend on 3000; proxy `/api/*` to backend.
6. Hit `GET /api/` then `POST /api/compile-directive`. If LLM errors, check `EMERGENT_LLM_KEY` and model IDs in §6.
7. Open the UI; compile a mission; Auto-run it; check Chronicle; compile a bounty; Deploy Soul Council; open Agent Bridge and run the playground.


# PART 2 — COMPLETE SOURCE CODE (verbatim)

Every application file below is the exact current content. Recreate each at the given path.

## FILE: `backend/.env` (template — fill in your own values)

```
MONGO_URL=mongodb://localhost:27017
DB_NAME=acaso_db
CORS_ORIGINS=*
EMERGENT_LLM_KEY=<YOUR_EMERGENT_LLM_KEY>
```

## FILE: `frontend/.env` (template — fill in your own values)

```
REACT_APP_BACKEND_URL=https://your-backend-host
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```


---

## FILE: `backend/requirements.txt`

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

```


---

## FILE: `backend/server.py`

```python
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
        f"Vulnerability context:\n{problem}\n\nCouncil findings:\n{council_text}\n\n"
        "Return JSON: {\"root_cause\":\"confirmed one-line root cause\","
        "\"fix\":\"the exact fix/patch to deploy (2-4 sentences, code/config level, non-weaponized)\","
        "\"verification\":\"how to retest & confirm it is resolved (1-2 sentences)\","
        "\"confidence\":92,\"status\":\"RESOLVED\"}"
    )
    resolution = {"root_cause": "", "fix": "", "verification": "", "confidence": 90, "status": "RESOLVED"}
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

```


---

## FILE: `frontend/package.json`

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


---

## FILE: `frontend/craco.config.js`

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


---

## FILE: `frontend/jsconfig.json`

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


---

## FILE: `frontend/postcss.config.js`

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

```


---

## FILE: `frontend/tailwind.config.js`

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


---

## FILE: `frontend/components.json`

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": false,
  "tsx": false,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "iconLibrary": "lucide"
}
```


---

## FILE: `frontend/public/index.html`

```html
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#000000" />
        <meta name="description" content="A product of emergent.sh" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@600&display=swap" rel="stylesheet" />
        <!--
        manifest.json provides metadata used when your web app is installed on a
        user's mobile device or desktop. See https://developers.google.com/web/fundamentals/web-app-manifest/
        -->
        <!--
        Notice the use of %PUBLIC_URL% in the tags above.
        It will be replaced with the URL of the `public` folder during the build.
        Only files inside the `public` folder can be referenced from the HTML.

        Unlike "/favicon.ico" or "favicon.ico", "%PUBLIC_URL%/favicon.ico" will
        work correctly both with client-side routing and a non-root public URL.
        Learn how to configure a non-root public URL by running `npm run build`.
        -->
        <title>Emergent | Fullstack App</title>
        <script>window.addEventListener("error",function(e){if(e.error instanceof DOMException&&e.error.name==="DataCloneError"&&e.message&&e.message.includes("PerformanceServerTiming")){e.stopImmediatePropagation();e.preventDefault()}},true);</script>
        <script src="https://assets.emergent.sh/scripts/emergent-main.js"></script>
    </head>
    <body>
        <noscript>You need to enable JavaScript to run this app.</noscript>
        <div id="root"></div>
        <!--
      This HTML file is a template.
      If you open it directly in the browser, you will see an empty page.

      You can add webfonts, meta tags, or analytics to this file.
      The build step will place the bundled scripts into the <body> tag.

      To begin the development, run `npm start` or `yarn start`.
      To create a production bundle, use `npm run build` or `yarn build`.
    -->
        <script>
            !(function (t, e) {
                var o, n, p, r;
                e.__SV ||
                    ((window.posthog = e),
                    (e._i = []),
                    (e.init = function (i, s, a) {
                        function g(t, e) {
                            var o = e.split(".");
                            2 == o.length && ((t = t[o[0]]), (e = o[1])),
                                (t[e] = function () {
                                    t.push(
                                        [e].concat(
                                            Array.prototype.slice.call(
                                                arguments,
                                                0,
                                            ),
                                        ),
                                    );
                                });
                        }
                        ((p = t.createElement("script")).type =
                            "text/javascript"),
                            (p.crossOrigin = "anonymous"),
                            (p.async = !0),
                            (p.src =
                                s.api_host.replace(
                                    ".i.posthog.com",
                                    "-assets.i.posthog.com",
                                ) + "/static/array.js"),
                            (r =
                                t.getElementsByTagName(
                                    "script",
                                )[0]).parentNode.insertBefore(p, r);
                        var u = e;
                        for (
                            void 0 !== a ? (u = e[a] = []) : (a = "posthog"),
                                u.people = u.people || [],
                                u.toString = function (t) {
                                    var e = "posthog";
                                    return (
                                        "posthog" !== a && (e += "." + a),
                                        t || (e += " (stub)"),
                                        e
                                    );
                                },
                                u.people.toString = function () {
                                    return u.toString(1) + ".people (stub)";
                                },
                                o =
                                    "init me ws ys ps bs capture je Di ks register register_once register_for_session unregister unregister_for_session Ps getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSurveysLoaded onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey canRenderSurveyAsync identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty Es $s createPersonProfile Is opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing Ss debug xs getPageViewId captureTraceFeedback captureTraceMetric".split(
                                        " ",
                                    ),
                                n = 0;
                            n < o.length;
                            n++
                        )
                            g(u, o[n]);
                        e._i.push([i, s, a]);
                    }),
                    (e.__SV = 1));
            })(document, window.posthog || []);
            posthog.init("phc_DbsPb39SRc8z3EiQ6Dhj6ikv4H4rTKcht9d4sZSesceP", {
                api_host: "https://ap.emergent.sh",
                person_profiles: "identified_only", // or 'always' to create profiles for anonymous users as well,
                session_recording: {
                    recordCrossOriginIframes: true,
                    capturePerformance: false,
                },
            });
        </script>
    </body>
</html>

```


---

## FILE: `frontend/src/index.js`

```jsx
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


---

## FILE: `frontend/src/index.css`

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


---

## FILE: `frontend/src/App.js`

```jsx
import React, { useState } from "react";
import "./App.css";
import { Toaster } from "sonner";
import SovereignHome from "./components/SovereignHome";
import AskAllAIs from "./components/AskAllAIs";
import Chronicle from "./components/Chronicle";
import BugBounty from "./components/BugBounty";
import AgentBridge from "./components/AgentBridge";
import { Sparkles, LayoutGrid, MessagesSquare, BookOpen, ShieldAlert, Plug } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const TABS = [
  { key: "home", label: "Sovereign Home", icon: LayoutGrid },
  { key: "bounty", label: "Bug Bounty", icon: ShieldAlert },
  { key: "askai", label: "Ask All AIs", icon: MessagesSquare },
  { key: "chronicle", label: "Chronicle", icon: BookOpen },
  { key: "bridge", label: "Agent Bridge", icon: Plug },
];

function App() {
  const [tab, setTab] = useState("home");

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


---

## FILE: `frontend/src/App.css`

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

```


---

## FILE: `frontend/src/lib/utils.js`

```javascript
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

```


---

## FILE: `frontend/src/components/SovereignHome.js`

```jsx
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


---

## FILE: `frontend/src/components/BugBounty.js`

```jsx
import React, { useEffect, useState, useCallback, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldAlert, Send, Loader2, Zap, Play, CheckCircle2, Circle, Trash2,
  Bug, Crosshair, FileText, ChevronDown, ChevronUp, ShieldCheck, Banknote,
  Target, Activity, AlertTriangle, Radar, Users, Crown, Eye, Cpu, Flame
} from "lucide-react";
import { API } from "../App";

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
                            </div>
                          );
                        })}
                      </div>
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


---

## FILE: `frontend/src/components/AskAllAIs.js`

```jsx
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


---

## FILE: `frontend/src/components/Chronicle.js`

```jsx
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


---

## FILE: `frontend/src/components/AgentBridge.js`

```jsx
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


---

## NOTE on `frontend/src/components/ui/`

These are stock, unmodified **shadcn/ui** primitives (accordion, button, card, dialog, ... toast, tooltip). They are included in the ZIP. If rebuilding from this markdown alone, generate them with `npx shadcn@latest add <component>` using the `components.json` above — the app currently only imports `sonner` directly, so they are not required for the app to compile.
