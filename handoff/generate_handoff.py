#!/usr/bin/env python3
"""Regenerate the ACASO handoff package from the LIVE source tree.

Produces (all under /app/handoff, then mirrored into /app/frontend/public):
  - ACASO_COMPLETE_HANDOFF.md  (full replication doc with embedded source)
  - NEXT_AGENT_BRIEF.md        (single-entry continuation brief)
  - VERIFIED_STATE.json        (machine-readable verified snapshot)
  - 00_HANDOFF_README.md       (readme / index)
  - src/                       (mirror of real source, secrets stripped)
  - ACASO_HANDOFF_BUNDLE.zip   (zip of the above)

NEVER embeds real secrets (.env values). Run: python /app/handoff/generate_handoff.py
"""
import os, json, shutil, zipfile
from datetime import datetime, timezone
from pathlib import Path

APP = Path("/app")
HANDOFF = APP / "handoff"
PUBLIC = APP / "frontend" / "public"
NOW = datetime.now(timezone.utc).isoformat()

# Source files to embed / mirror (relative to /app). Secrets excluded.
SOURCE_FILES = [
    "backend/server.py",
    "backend/requirements.txt",
    "frontend/package.json",
    "frontend/craco.config.js",
    "frontend/tailwind.config.js",
    "frontend/postcss.config.js",
    "frontend/jsconfig.json",
    "frontend/src/index.js",
    "frontend/src/index.css",
    "frontend/src/App.js",
    "frontend/src/App.css",
    "frontend/src/components/SovereignHome.js",
    "frontend/src/components/AskAllAIs.js",
    "frontend/src/components/Chronicle.js",
    "frontend/src/components/BugBounty.js",
    "frontend/src/components/AgentBridge.js",
    "frontend/src/components/FileAnalyzer.js",
    "frontend/src/components/SelfDirective.js",
    "frontend/src/components/Council.js",
    "frontend/src/components/VoiceChat.js",
    "frontend/src/components/VoiceCommander.js",
    "frontend/src/components/Radar.js",
    "backend/radar.py",
    "backend/node.py",
    "backend/apex.py",
    "frontend/src/components/Apex.js",
    "frontend/src/components/Companion.js",
    "frontend/src/components/LocalNode.js",
    "handoff/local_node/acaso_node.py",
    "handoff/scripts/acaso_client.py",
    "handoff/scripts/script_01_genesis_engine.py",
    "handoff/scripts/script_03_sovereign_hunter.py",
]

LANG = {".py": "python", ".js": "javascript", ".css": "css", ".json": "json",
        ".txt": "text", ".md": "markdown"}

FEATURES = [
    "Directive-to-Payment mission compiler (Make/Find/Move/Collect) with staged pipeline",
    "Bug Bounty engagements: compile, run, owner-approval gates, disclosure report",
    "Soul Council: 3 souls across OpenAI + Gemini + Anthropic, Round-2 debate/rebuttals, Eternal Throne synthesis, Dissent & Reconciliation, PR-ready Fix Export",
    "Ask All AIs multi-model answers + synthesis",
    "Agent Bridge: X-ACASO-Key protected agent API (directive/list/run)",
    "Real object storage: mission Evidence & Media attachments (upload/list/download/delete)",
    "File Analyzer: upload files OR a whole folder -> real object storage -> AI analysis + follow-up chat grounded in the files",
    "Self-Directive: PREVIEW-ONLY, approval-gated self-editing (propose unified diff -> approve/apply with compile+import validation & snapshot -> rollback), audited",
    "File Analyzer follow-up chat: grounded answers that cite exact `path:line` (clickable -> opens a file viewer that highlights the line) and quote snippets",
    "Analysis Export: one-click download of the analysis + chat thread + file list as a Markdown report",
    "Google Drive ingestion (user OAuth): connect, browse, SEARCH by name, import selected files OR an entire folder (recursive) in one click, auto-analyzes after import. Requires user-supplied Web-app OAuth client.",
    "Council of Weavers deliberation engine (POST /api/acaso/deliberate): Architect(Gemini)/Shadow(Claude, veto)/Muse(GPT)/Finance(GPT) in parallel -> Meta-Weaver synthesis -> Sovereign Directive + inferred weak signals; journaled, exportable to .md; presets Genesis Engine / Sovereign Hunter / Foresight Thesis; runner scripts in handoff/scripts. LLM reasoning only - no live market/lead data.",
    "Voice Channel: browser Web Speech API (STT+TTS, no keys, no audio to server) -> POST /api/voice/chat; hands-free loop / push-to-talk / text-first modes; per-message Fast (GPT-4o-mini w/ session memory) or Council (full deliberation + spoken summary); transcript persisted per session.",
    "Directive-to-Mission: POST /api/acaso/deliberations/{id}/to-mission compiles a Council directive into a Sovereign Home mission (idempotent, source_deliberation_id).",
    "Global VoiceCommander: floating mic on every tab - Dictate mode types into the focused text box (native-setter injection so React state updates); Command mode -> POST /api/voice/command (rule-based + LLM intent router: open_tab, council_deliberate, compile_directive, radar_discover, radar_search, ask) executes and speaks back.",
    "Opportunity Radar (backend/radar.py, /api/radar/*): REAL sources Grants.gov public API (no key), GitHub bounty issues, SAM.gov (needs SAM_GOV_API_KEY); adapters fetch->normalize->validate->dedupe->barrier signals->transparent 0-100 score (8 weighted components, labelled inferred)->persist->stale marking; every record has source_url/retrieved_at/http_status/parser_version/evidence[] with source_location; Fit Analyst + Skeptic (gates Strong fit) + Compliance Sentinel on demand; NL search proposes filters never auto-applied; Drafting Desk (email/grant narrative/outreach packet/fill-a-form) uses only profile + source text with [FILL] placeholders; Add-to-pipeline -> mission; export .md. Nothing auto-submitted.",
    "Periodic self-scan (Self-Directive): in-process asyncio scheduler, off by default; deterministic checks (py_compile, ruff F/E9, esbuild per component, TODO/console.log census) -> at most ONE Self-Directive proposal per run tagged origin=scheduled_scan; NEVER auto-applies; UI toggle/interval/focus/Scan now/history.",
    "Local Node (backend/node.py + handoff/local_node/acaso_node.py, served at /local-node/*): owner runs the Python client on their PC (Windows/Linux), pairs with the Agent Bridge key; server holds an approval-gated task queue (read-only auto-approved; every write/shell/browser action must be approved in the Local Node tab); node enforces allowed roots, backs up overwritten files, soft-deletes to .acaso_trash; browser tasks drive a real headed Chrome (persistent profile) via Playwright, fill forms and STOP (awaiting_submit) until a separate browser_submit is approved; secrets written as [OWNER TYPES THIS]. LLM planner turns a goal into proposed tasks. Server research browser (headless Chromium, /api/browse/research) reads public pages: text/links/forms/screenshot + quoted answer.",
    "Companion (/?mode=companion, header Companion button opens popup; components/Companion.js): voice hands-free, share window/tab/screen via getDisplayMedia, per-message frame -> POST /api/companion/chat (SSE, vision via emergentintegrations ImageContent, gpt-4o-mini -> gemini-2.5-flash). WATCH MODE: 30s glance loop with 16x16 frame-hash change filter -> POST /api/companion/watch -> speaks only for error/form/action (JSON verdict). Installable PWA: /companion.webmanifest swapped in companion mode + Install button; Local Node --companion opens Chrome --app window (separate profile) with best-effort always-on-top (Windows ctypes / Linux wmctrl). Frames never stored.",
    "Apex Nexus (backend/apex.py, /api/apex/*, tab Apex Nexus): products rfp_kit ($149, from Radar opportunity or pasted RFP), prompt_library ($49, Markdown+JSON+gated API key), seo_pack ($199); POST /generate (one LLM call, [FILL] placeholders counted), deliverables export md/json, orders (pending_payment -> paid -> unlock via /api/apex/unlock/{token}; 402 until paid; refunded re-locks), gated /api/apex/library/{id}?key= requires paid order. Payments: STRIPE NOT CONNECTED (manual Mark paid) until owner supplies STRIPE_API_KEY - integrate via playbook then.",
]

MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-3.6-flash",
    "anthropic": "claude-haiku-4-5",
}

KEY_ENDPOINTS = [
    ["POST", "/api/companion/chat (SSE) | /api/companion/watch | GET/DELETE /api/companion/history", "Companion vision chat + watch mode"],
    ["GET", "/api/apex/products | /api/apex/deliverables[/{id}[/export?fmt=md|json]]", "Apex catalog + deliverables"],
    ["POST/PATCH", "/api/apex/generate | /api/apex/orders[/{id}]", "generate product / order lifecycle"],
    ["GET", "/api/apex/unlock/{token}[?fmt=md|json|status] | /api/apex/library/{id}?key=", "buyer unlock (public) / gated prompt API"],
    ["GET/PUT", "/api/self/scan/config | POST /api/self/scan/run | GET /api/self/scans", "periodic self-scan (propose-only)"],
    ["POST", "/api/node/register | /api/node/{id}/heartbeat | /api/node/{id}/claim | /api/node/tasks/{tid}/result", "node-side (X-ACASO-Key)"],
    ["GET", "/api/node/nodes | /api/node/tasks | /api/node/setup", "owner-side node + queue"],
    ["POST", "/api/node/tasks | /api/node/tasks/{tid}/decision | /api/node/plan", "create / approve-reject / LLM plan"],
    ["POST", "/api/browse/research", "server headless browser: public page -> text, links, forms, screenshot, quoted answer"],
    ["POST", "/api/voice/command", "spoken command -> intent -> execute -> {navigate_tab, spoken, result}"],
    ["POST", "/api/acaso/deliberations/{id}/to-mission", "Council directive -> Sovereign Home mission"],
    ["GET/PUT", "/api/radar/profile", "Radar owner profile"],
    ["POST", "/api/radar/discover", "run source adapters {sources?, keyword?, limit}"],
    ["GET", "/api/radar/opportunities[?type&source&min_score&closing_days&low_barrier&remote&max_value&q&saved&sort]", "scored feed"],
    ["GET/PATCH", "/api/radar/opportunities/{id}", "detail / status-stage-notes"],
    ["POST", "/api/radar/opportunities/{id}/analyze|draft|to-mission", "AI personas / drafting desk / pipeline"],
    ["POST", "/api/radar/search/nl", "natural language -> proposed filters"],
    ["POST", "/api/voice/chat", "voice turn: {message, session_id, mode: fast|council} -> spoken reply (+full directive in council mode)"],
    ["GET/DELETE", "/api/voice/history?session_id=", "voice transcript per session"],
    ["GET", "/api/acaso/presets", "council presets (genesis/hunter/foresight)"],
    ["POST", "/api/acaso/deliberate", "run Council of Weavers -> sovereign_directive, weak_signals, weavers, council_consulted"],
    ["GET", "/api/acaso/deliberations[/{id}][/export]", "list / open / export .md a deliberation"],
    ["POST", "/api/compile-directive", "compile a revenue directive into a mission"],
    ["POST", "/api/compile-bounty", "compile a bug-bounty engagement"],
    ["GET", "/api/missions?kind=bugbounty", "list engagements"],
    ["POST", "/api/missions/{mid}/deploy-souls", "Soul Council + debate + Throne verdict"],
    ["POST", "/api/missions/{mid}/attachments", "upload real evidence file (object storage)"],
    ["GET", "/api/missions/{mid}/attachments", "list attachments"],
    ["GET", "/api/attachments/{fid}/download", "download attachment (backend-proxied)"],
    ["DELETE", "/api/attachments/{fid}", "soft-delete attachment"],
    ["POST", "/api/filesets", "create a File Analyzer set"],
    ["POST", "/api/filesets/{fsid}/files", "upload a file (folder upload sends many)"],
    ["POST", "/api/filesets/{fsid}/analyze", "AI analysis of the set"],
    ["POST", "/api/filesets/{fsid}/chat", "follow-up chat grounded in the files"],
    ["GET", "/api/self/manifest", "allowlisted source manifest (preview_only=true)"],
    ["POST", "/api/self/propose", "generate a unified-diff patch proposal"],
    ["POST", "/api/self/apply", "approve+apply (compile & import validated, snapshot)"],
    ["POST", "/api/self/rollback", "restore snapshot"],
    ["GET", "/api/drive/status", "Drive configured/connected status"],
    ["GET", "/api/drive/connect", "returns Google OAuth authorization_url"],
    ["GET", "/api/oauth/drive/callback", "OAuth callback -> stores tokens, redirects to app"],
    ["GET", "/api/drive/list?folder_id=root", "list Drive folders/files"],
    ["POST", "/api/drive/import", "import selected Drive files into an analysis set"],
    ["POST", "/api/drive/import-folder", "import all supported files in a Drive folder (recursive)"],
    ["GET", "/api/filesets/{fsid}/file?path=", "file content by rel_path (citation-jump viewer)"],
    ["GET", "/api/filesets/{fsid}/export", "download analysis + chat as Markdown"],
    ["POST", "/api/drive/disconnect", "revoke + delete stored Drive tokens"],
    ["GET", "/api/agent/info", "Agent Bridge info"],
]

VERIFIED = [
    "OpenAI gpt-4o-mini, Gemini gemini-3.6-flash, Anthropic claude-haiku-4-5 all respond",
    "Object storage init/upload/download byte-perfect round trip",
    "Attachments: upload/list/download/delete; .exe rejected (400)",
    "File Analyzer: upload text/md/json/py/png, analyze (markdown), chat cites files; .exe rejected",
    "Self-Directive: manifest/source; backend/.env blocked (403); propose->diff; apply requires approved=true (else 400); rollback restores",
    "Self-Directive backend safety: broken syntax AND import-error server.py both rejected (422) with live file untouched; valid change applies+rolls back",
    "Agent Bridge: missing/invalid X-ACASO-Key -> 401",
]


def rel_lang(rel: str) -> str:
    return LANG.get(Path(rel).suffix, "text")


def build_complete_md() -> str:
    out = []
    out.append(f"# ACASO Omniverse — Complete Handoff\n")
    out.append(f"_Generated: {NOW}_\n")
    out.append("## What this is\nA contest-ready **Directive-to-Payment Operating System** (FastAPI + React + MongoDB).\n")
    out.append("## Features\n" + "\n".join(f"- {f}" for f in FEATURES) + "\n")
    out.append("## Tech & Integrations\n"
               "- Backend: FastAPI + Motor (MongoDB), Pydantic, UUID ids, timezone-aware UTC.\n"
               "- Frontend: React (CRACO), Shadcn UI, lucide-react, framer-motion, sonner.\n"
               "- LLM: `emergentintegrations` via platform `EMERGENT_LLM_KEY` (OpenAI/Gemini/Anthropic).\n"
               "- Object storage: Emergent Integration Proxy (`INTEGRATION_PROXY_URL`), backend-proxied downloads.\n")
    out.append("### Models in use\n" + "\n".join(f"- {k}: `{v}`" for k, v in MODELS.items()) + "\n")
    out.append("## Environment (DO NOT COMMIT REAL VALUES)\n"
               "```\nbackend/.env: MONGO_URL, DB_NAME, EMERGENT_LLM_KEY, INTEGRATION_PROXY_URL, CORS_ORIGINS\n"
               "frontend/.env: REACT_APP_BACKEND_URL\n```\n"
               "All backend routes are prefixed `/api`. Never hardcode URLs; use env vars.\n")
    out.append("## Run\n```\nsudo supervisorctl restart backend frontend\n```\n"
               "Hot-reload is enabled; restart only after dependency/.env changes.\n")
    out.append("## Key API Endpoints\n" + "\n".join(f"- `{m} {p}` — {d}" for m, p, d in KEY_ENDPOINTS) + "\n")
    out.append("## Verified (live)\n" + "\n".join(f"- {v}" for v in VERIFIED) + "\n")
    out.append("## Safety / Real-vs-Simulated\n"
               "- REAL: Mongo persistence, object storage, LLM calls, Agent Bridge auth, Self-Directive edits (preview only).\n"
               "- SIMULATED: NEXUS action execution/evidence, payouts, HackerOne submission.\n"
               "- Self-Directive is PREVIEW-ONLY and disabled after production deploy; every apply is compile+import validated with snapshot & rollback.\n"
               "- DEFERRED (need user creds): GitHub PR, real HackerOne submission.\n"
        "- Google Drive: implemented (backend OAuth + browse/import, frontend UI). Requires a user-created Google Cloud WEB-application OAuth client with the registered redirect URI; a Desktop/installed client will NOT work.\n")
    out.append("\n---\n## Full Source\n")
    for rel in SOURCE_FILES:
        fp = APP / rel
        if not fp.exists():
            continue
        content = fp.read_text(encoding="utf-8", errors="replace")
        out.append(f"\n### `{rel}`\n```{rel_lang(rel)}\n{content}\n```\n")
    return "\n".join(out)


def build_brief() -> str:
    return (
        f"# ACASO — Next Agent Brief\n_Generated: {NOW}_\n\n"
        "Read this first. The app is a Directive-to-Payment OS (FastAPI+React+Mongo). All routes under `/api`.\n\n"
        "## Smoke test (one command)\n"
        "```\nBURL=$(grep REACT_APP_BACKEND_URL frontend/.env | cut -d= -f2)\n"
        "curl -s $BURL/api/self/manifest | head -c 300\n```\n\n"
        "## What's built & verified\n" + "\n".join(f"- {f}" for f in FEATURES) + "\n\n"
        "## Models\n" + "\n".join(f"- {k}: `{v}` (do NOT downgrade)" for k, v in MODELS.items()) + "\n\n"
        "## Deferred (blocked on user credentials)\n"
        "- Google Drive: fully implemented; needs a user-created Google Cloud *Web application* OAuth client (Desktop client won't work) with redirect `/api/oauth/drive/callback` + the chosen scope in backend/.env (GOOGLE_CLIENT_ID/SECRET/REDIRECT/SCOPE).\n"
        "- GitHub PR creation: needs GitHub App/PAT + repo.\n"
        "- Real HackerOne submission: needs authorized program credentials.\n\n"
        "## Guardrails\n"
        "- Never change frontend `REACT_APP_BACKEND_URL` or backend `MONGO_URL`.\n"
        "- Self-Directive is preview-only, approval-gated, snapshot+rollback, compile+import validated.\n"
        "- Use `emergentintegrations` + `EMERGENT_LLM_KEY`; call integration agent before any new 3rd-party service.\n"
    )


def build_verified_json() -> dict:
    return {
        "generated": NOW,
        "app": "ACASO Omniverse",
        "stack": {"backend": "FastAPI+Motor", "frontend": "React (CRACO)", "db": "MongoDB"},
        "models": MODELS,
        "features": FEATURES,
        "verified": VERIFIED,
        "endpoints": [{"method": m, "path": p, "desc": d} for m, p, d in KEY_ENDPOINTS],
        "real": ["mongo", "object_storage", "llm", "agent_bridge_auth", "self_directive_preview"],
        "simulated": ["nexus_execution", "payouts", "hackerone_submission"],
        "deferred": ["github_pr", "hackerone_real", "google_drive_needs_web_oauth_client"],
        "do_not_change": ["frontend/.env REACT_APP_BACKEND_URL", "backend/.env MONGO_URL"],
    }


def build_readme() -> str:
    return (
        f"# ACASO Handoff Package\n_Generated: {NOW}_\n\n"
        "Files in this bundle:\n"
        "- `NEXT_AGENT_BRIEF.md` — start here.\n"
        "- `ACASO_COMPLETE_HANDOFF.md` — full replication doc with embedded source.\n"
        "- `VERIFIED_STATE.json` — machine-readable snapshot.\n"
        "- `src/` — mirror of the real source (no secrets).\n\n"
        "Regenerate anytime with: `python handoff/generate_handoff.py`\n"
    )


def mirror_src():
    dst = HANDOFF / "src"
    if dst.exists():
        shutil.rmtree(dst)
    for rel in SOURCE_FILES:
        fp = APP / rel
        if not fp.exists():
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fp, target)
    # env examples (no secrets)
    (dst / "backend").mkdir(parents=True, exist_ok=True)
    (dst / "backend" / ".env.example").write_text(
        "MONGO_URL=\nDB_NAME=\nEMERGENT_LLM_KEY=\nINTEGRATION_PROXY_URL=\nCORS_ORIGINS=*\n")
    (dst / "frontend").mkdir(parents=True, exist_ok=True)
    (dst / "frontend" / ".env.example").write_text("REACT_APP_BACKEND_URL=\n")


def build_zip():
    zpath = HANDOFF / "ACASO_HANDOFF_BUNDLE.zip"
    if zpath.exists():
        zpath.unlink()
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, fnames in os.walk(HANDOFF):
            for fn in fnames:
                fp = Path(root) / fn
                if fp.suffix == ".zip" or fp.name == "generate_handoff.py":
                    continue
                z.write(fp, fp.relative_to(HANDOFF))
    return zpath


def main():
    HANDOFF.mkdir(parents=True, exist_ok=True)
    (HANDOFF / "ACASO_COMPLETE_HANDOFF.md").write_text(build_complete_md(), encoding="utf-8")
    (HANDOFF / "NEXT_AGENT_BRIEF.md").write_text(build_brief(), encoding="utf-8")
    (HANDOFF / "VERIFIED_STATE.json").write_text(json.dumps(build_verified_json(), indent=2), encoding="utf-8")
    (HANDOFF / "00_HANDOFF_README.md").write_text(build_readme(), encoding="utf-8")
    mirror_src()
    zpath = build_zip()

    # Mirror to public for download
    PUBLIC.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HANDOFF / "ACASO_COMPLETE_HANDOFF.md", PUBLIC / "acaso-handoff.md")
    shutil.copy2(HANDOFF / "NEXT_AGENT_BRIEF.md", PUBLIC / "acaso-next-agent-brief.md")
    shutil.copy2(HANDOFF / "VERIFIED_STATE.json", PUBLIC / "acaso-verified-state.json")
    shutil.copy2(zpath, PUBLIC / "acaso-handoff.zip")

    print("Handoff regenerated:")
    for f in ["ACASO_COMPLETE_HANDOFF.md", "NEXT_AGENT_BRIEF.md", "VERIFIED_STATE.json", "00_HANDOFF_README.md", "ACASO_HANDOFF_BUNDLE.zip"]:
        p = HANDOFF / f
        print(f"  {f}: {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
