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
