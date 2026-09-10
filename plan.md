
## Phase: Actionability Pass (Status: COMPLETED)

Closed the "make the handoff actually actionable" gap raised by the user:

- **Soul Dissent View** — Throne prompt/schema extended with `{topic, positions{vision,fusion,rebirth}, reconciliation}`; frontend renders per-soul stances color-coded + gold reconciliation callout (`data-testid="soul-dissent-<mid>"`).
- **Fix Export** — Throne now returns a full markdown `patch_note` (Title / Summary / Root Cause / Changes / Verification / Risk & Rollout); frontend shows it in a monospace block with a Copy button (`data-testid="fix-export-copy-<mid>"`) + Sonner toast.
- **Soul Debate Mode** — one round of rebuttals before final Throne verdict; optional inline transcript UI (`data-testid="soul-debate-<mid>"`).
- **Agent Bridge auth verified** — earlier "405" was a test-side method mismatch. POST /api/agent/directive and GET /api/agent/missions both correctly return 401 with no/invalid X-ACASO-Key. Confirmed via curl AND urllib.
- **Model IDs re-verified live** — OpenAI `gpt-4o-mini`, Gemini `gemini-3.6-flash`, Anthropic `claude-haiku-4-5` all returned successful answers + synthesis.
- **Real object storage (backend)** — integrated Emergent-managed object storage in backend; mission attachments support real upload/list/download/delete; invalid `.exe` rejected; attachment excerpts are injected into Soul Council prompt context.
- **Actionable handoff artifacts** — added `NEXT_AGENT_BRIEF.md` (single entrypoint w/ one-command smoke test) and `VERIFIED_STATE.json` (real captured response shapes + do-not-retry ledger). Bundled into `ACASO_HANDOFF_BUNDLE.zip` and served publicly.

Public artifacts (all HTTP 200) **(NOTE: likely stale vs. latest object-storage backend changes; refresh planned in next phase)**:
- /acaso-next-agent-brief.md (8.5 KB) — read this first
- /acaso-verified-state.json (1.4 KB) — machine-readable smoke-test snapshot
- /acaso-handoff.md (161 KB) — full replication doc
- /acaso-handoff.zip (148 KB) — full source tree + docs

---

## Phase: Files + Self-Directive (Status: COMPLETED — verified 100% by testing agent, iteration_1)

Shipped & verified:
- **Sub-Feature A (Attachment UI):** Bug Bounty mission cards now have a real Evidence & Media panel (upload/list/download/delete) backed by real object storage. data-testids added.
- **Sub-Feature B (File Analyzer tab):** Upload individual files or an ENTIRE FOLDER (webkitdirectory) into real object storage; Mongo metadata; AI analysis (Overview / Per-File Notes / Cross-File Insights / Risks / Recommended Actions) via Emergent LLM. Rejects unsupported types (.exe -> 400).
- **Sub-Feature C (Self-Directive tab):** PREVIEW-ONLY, APPROVAL-GATED, ROLLBACK-CAPABLE self-editing. Allowlist = frontend/src/** + backend/server.py; denylist blocks .env/lockfiles/manifests/.git (backend/.env -> 403). Flow: select files -> instruction -> LLM patch proposal (unified diff) -> Approve & Apply (snapshots originals; py_compile-validates .py with auto-rollback on failure) -> Rollback. Audit in Mongo self_directives. apply requires approved=true else 400.
- Safe scratch target left in repo: frontend/src/_playground_notes.md (non-imported) for demoing self-directive.
- Model IDs: OpenAI gpt-4o-mini, Gemini gemini-3.6-flash, Anthropic claude-haiku-4-5.

---

## Phase: Follow-ups (Status: COMPLETED except Google Drive)

- **Self-Directive on Server (DONE, verified):** backend/server.py is in the allowlist; apply now PRE-VALIDATES every Python change (py_compile + real import smoke-test in a sibling temp file using sys.executable) BEFORE touching the live file, so a broken server.py can never crash the app. 3/3 safety tests passed (bad syntax -> 422, import error -> 422, live file untouched; valid change applies + rolls back).
- **Analyzer Chat (DONE, verified):** POST/GET /api/filesets/{fsid}/chat; grounded in uploaded files, cites filenames, persists to Mongo file_chats. Frontend chat panel in File Analyzer verified by testing agent (user + assistant messages render).
- **Refresh Handoff (DONE):** reproducible generator at /app/handoff/generate_handoff.py rebuilds ACASO_COMPLETE_HANDOFF.md (now 231KB, includes FileAnalyzer/SelfDirective + new endpoints), NEXT_AGENT_BRIEF.md, VERIFIED_STATE.json, src mirror (secrets stripped) and the zip; mirrored to /app/frontend/public (all HTTP 200).
- **Google Drive (BUILT — pending Web-app creds):** Full backend OAuth (connect/callback/list/import/disconnect, single-owner, token refresh, google-docs export) + frontend (Connect button, folder browser modal with breadcrumbs, multi-select import into an analysis set). Uses google-api-python-client/google-auth-oauthlib. Creds stored in backend/.env. NOTE: user-provided client was a Desktop/"installed" type; Google requires a *Web application* OAuth client for the hosted https redirect. Connect URL generation + status verified; full login blocked until a Web-app Client ID/Secret is supplied. Scope chosen: full drive.
- **Analyzer Chat & Self-Directive server safety:** completed & verified (see above).
- **Handoff:** regenerated (256KB) including Drive endpoints/components; reproducible via handoff/generate_handoff.py.



Deliver real, permissioned file analysis and a safe, approval-gated "work on itself" workflow under a **~100 credit** budget.

Defaults chosen (per user skipping decisions):
- **File source default:** browser user-initiated file/folder upload (not Google Drive; no local filesystem claims).
- **Drive:** deferred (requires user OAuth Client ID/Secret + scope decisions).
- **Self-editing:** **preview-only**, **approval-gated**, **auditable**, **rollback-capable**; no silent/autonomous production self-modification.

### Objectives

1) **Close the real attachment loop in the UI** (no/low LLM cost)
- Make backend-complete real object storage usable from the Bug Bounty mission UI.

2) **Add a File Analyzer module** (moderate LLM cost)
- Upload files or an entire folder (via `webkitdirectory`) into real object storage, store metadata in Mongo, and run targeted LLM analysis producing:
  - per-file summaries
  - cross-file insights (patterns, risks, action items)
  - citations back to file names/paths

3) **Add a Self-Directive console** (moderate LLM cost)
- Accept natural-language instructions, read allowlisted source files, propose a patch as a unified diff, and apply only after explicit approval with backup + rollback.

4) **Budget discipline and truth-in-integrations**
- Avoid repeated expensive multi-model council cycles.
- Prefer direct curl tests + screenshots.
- Do one consolidated testing-agent pass at the end.
- Notify and stop near ~100 credits.

### Sub-Feature A: Attachment UI (Bug Bounty) — (Status: NOT STARTED)

Implementation steps:
- Frontend (target: `/app/frontend/src/components/BugBounty.js`):
  - Add an "Attachments" panel per mission card (or inside the expanded council section) with:
    - file picker + upload button
    - list attachments (filename, type, size, created_at)
    - download action (open/save) using backend-proxied download route
    - delete action
  - Add `data-testid`s:
    - `attachment-upload-<mid>`
    - `attachment-file-input-<mid>`
    - `attachment-row-<fid>`
    - `attachment-download-<fid>`
    - `attachment-delete-<fid>`
- Backend: no new routes expected (already present):
  - `POST /api/missions/{mid}/attachments`
  - `GET /api/missions/{mid}/attachments`
  - `GET /api/attachments/{fid}/download`
  - `DELETE /api/attachments/{fid}`

Testing:
- Direct curl:
  - upload allowed type (e.g., `.txt`, `.png`), list, download, delete
  - confirm invalid ext rejected (e.g., `.exe`)
- Frontend:
  - compile
  - screenshot verification of upload/list/download/delete flow and error states

Deliverable:
- Real, end-to-end attachment UX with Mongo metadata + object storage bytes; attachments are visibly present and demonstrably downloadable.

### Sub-Feature B: File Analyzer tab (Folder upload → storage → analysis) — (Status: NOT STARTED)

Default behavior (safe + real):
- Hosted app cannot access arbitrary local directories.
- Provide user-initiated folder upload (browser) as the default “local directory” equivalent.

Implementation steps:
- Frontend:
  - Add new tab `file_analyzer` in `/app/frontend/src/App.js`.
  - Create `/app/frontend/src/components/FileAnalyzer.js`:
    - file upload (multiple) + folder upload (`webkitdirectory`)
    - show upload progress, list imported files
    - start analysis button
    - show per-file summary + cross-file rollup
- Backend:
  - Add Mongo collections (names flexible, but consistent):
    - `file_sets` (id, title, created_at)
    - `files` (id, file_set_id, mission_id optional, storage_path, original_filename, content_type, size, text_excerpt, created_at)
    - `file_analyses` (file_set_id, analysis, created_at, model_label)
  - Add API routes:
    - `POST /api/filesets` (create)
    - `POST /api/filesets/{fsid}/files` (upload one file, uses object storage)
    - `GET /api/filesets/{fsid}/files` (list)
    - `POST /api/filesets/{fsid}/analyze` (LLM analysis; includes excerpts only, never raw binaries)
  - Analysis prompt policy:
    - Only include text excerpts (bounded length), filenames, and types.
    - If file is binary, either skip or require explicit user conversion.
    - Output must cite filenames and avoid leaking secrets.

Testing:
- Upload a small folder with a few `.md/.txt/.json` files.
- Confirm storage round-trip through list + download endpoints (either reuse attachment download route or add file download route).
- Run analysis once (single provider by default to reduce cost; use existing failover only on error).

Deliverable:
- A real ingestion + analysis loop that is permissioned, reproducible, and honest about local-access constraints.

### Sub-Feature C: Self-Directive console (Patch propose + approve apply + rollback) — (Status: NOT STARTED)

Safety defaults:
- Preview-only; **explicit approval** required before applying.
- Allowlist file reading:
  - `/app/frontend/src/**`
  - `/app/backend/server.py`
- Denylist (hard block):
  - any `.env`
  - dependency manifests / lockfiles (`package.json`, `yarn.lock`, `requirements.txt`)
  - `.git/**`
  - deployment/infra configs (unless later explicitly approved)
- Never send secrets to the LLM (redact obvious patterns; do not include env vars).

Implementation steps:
- Frontend:
  - Add new tab `self_directive` in `/app/frontend/src/App.js`.
  - Create `/app/frontend/src/components/SelfDirective.js`:
    - instruction textarea
    - “Generate Patch Proposal” button
    - diff viewer (unified diff)
    - explicit “Approve & Apply” with confirmation
    - “Rollback” button for last applied patch
    - show audit history
- Backend:
  - Add endpoints:
    - `POST /api/self_directive/propose` (reads allowlisted files, calls LLM, returns proposed diff + test plan)
    - `POST /api/self_directive/apply` (requires proposal_id + explicit approval flag)
    - `POST /api/self_directive/rollback` (rollback last snapshot)
    - `GET /api/self_directive/history`
  - Store audit in Mongo `self_directives`:
    - proposal_id, instruction, allowlist manifest hash, diff, created_at
    - apply status, applied_at, backup snapshot id
    - rollback status, rolled_back_at
  - Apply mechanics:
    - create snapshot (copy affected files to timestamped backup folder)
    - apply patch (server-side)
    - run lightweight validation:
      - backend: `python -m py_compile server.py`
      - frontend: `yarn -s build` (or `yarn -s test` if configured)
    - if validation fails, auto-rollback and mark audit failed

Testing:
- Create a trivial safe change (e.g., UI copy string).
- Ensure propose does not apply.
- Apply with approval → file changes persist → validation passes.
- Trigger a controlled failure → verify rollback.

Deliverable:
- A real, auditable, reversible self-edit workflow that never claims autonomy in production.

### Budget & Process Controls (Status: IN PROGRESS)

- Hard guideline: **stop near ~100 credits** and notify user before any bulk analysis.
- Prefer:
  - minimal LLM calls (single-provider analysis by default)
  - no repeated Council runs
  - direct curl tests for backend
  - screenshot verification for UI
- One consolidated testing-agent pass at end:
  - attachment UI
  - file analyzer upload + analysis
  - self-directive propose/apply/rollback

### Deferred / Blocked (Status: DEFERRED)

- **Google Drive OAuth ingestion** — blocked pending user OAuth Client ID/Secret, consent screen readiness, redirect URI setup, and scope selection.
- **GitHub PR creation** — blocked pending GitHub App/PAT and repo/permission details.
- **Real HackerOne submission** — blocked pending authorized credentials + program scope; current workflow remains simulated.

### Packaging Sync (Status: NOT STARTED)

After Sub-Features A–C are complete and tests pass:
- Regenerate handoff bundle and public artifacts to include:
  - object storage backend changes
  - attachment UI
  - file analyzer + self-directive modules
  - updated verified-state + smoke tests
- Ensure no secrets are included in artifacts.

## Phase: Council of Weavers Deliberation Engine (Status: COMPLETED)
Triggered by user-uploaded artifacts (Foresight Engine spec, evolving.skill, Core Engine v5 manual,
script_01_genesis_engine.py, script_03_sovereign_hunter.py). Both scripts call POST /acaso/deliberate,
which did not exist -> built it for real.
- Backend (server.py): WEAVERS (Architect/Gemini, Shadow/Claude w/ veto, Muse/GPT, Finance/GPT) run in
  parallel via llm_call_failover -> Meta-Weaver synthesis -> sovereign_directive + weak_signals
  (===WEAK_SIGNALS=== marker, Muse fallback). Persisted in db.deliberations (UUID, UTC).
  Routes: GET /api/acaso/presets, POST /api/acaso/deliberate, GET/DELETE /api/acaso/deliberations[/{id}],
  GET /api/acaso/deliberations/{id}/export (.md).
- Frontend: components/Council.js + "Council" tab (App.js), CSS .cw-* in App.css. Markdown renderer
  exported from FileAnalyzer.js and reused.
- Runner scripts re-targeted to /api: handoff/scripts/* (also served at /scripts/* from frontend/public).
- Source specs kept at handoff/specs/. Handoff bundle regenerated (181 KB).
- Verified (agent): live run 54s, 4/4 weavers ok on 3 distinct models, meta synthesis, weak signals parsed,
  Shadow veto flagged, export headers correct, UI screenshot OK. Testing agent skipped to honor the user's
  credit cap; direct curl + screenshot verification used instead.
- Honesty: LLM reasoning only; no market/on-chain/lead data connected. Not implemented from the specs:
  Foresight Layer 1-3 data ingestion/nowcast/regime ML, ElevenLabs/Whisper/ChromaDB local kiosk (v5 manual).
- Google Drive OAuth: still connected:false - user must click Connect Google Drive in File Analyzer.
