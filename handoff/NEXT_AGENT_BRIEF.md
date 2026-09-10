# ACASO — Next Agent Brief
_Generated: 2026-09-10T01:47:03.648779+00:00_

Read this first. The app is a Directive-to-Payment OS (FastAPI+React+Mongo). All routes under `/api`.

## Smoke test (one command)
```
BURL=$(grep REACT_APP_BACKEND_URL frontend/.env | cut -d= -f2)
curl -s $BURL/api/self/manifest | head -c 300
```

## What's built & verified
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

## Models
- openai: `gpt-4o-mini` (do NOT downgrade)
- gemini: `gemini-3.6-flash` (do NOT downgrade)
- anthropic: `claude-haiku-4-5` (do NOT downgrade)

## Deferred (blocked on user credentials)
- Google Drive: fully implemented; needs a user-created Google Cloud *Web application* OAuth client (Desktop client won't work) with redirect `/api/oauth/drive/callback` + the chosen scope in backend/.env (GOOGLE_CLIENT_ID/SECRET/REDIRECT/SCOPE).
- GitHub PR creation: needs GitHub App/PAT + repo.
- Real HackerOne submission: needs authorized program credentials.

## Guardrails
- Never change frontend `REACT_APP_BACKEND_URL` or backend `MONGO_URL`.
- Self-Directive is preview-only, approval-gated, snapshot+rollback, compile+import validated.
- Use `emergentintegrations` + `EMERGENT_LLM_KEY`; call integration agent before any new 3rd-party service.
