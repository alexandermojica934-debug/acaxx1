# ACASO — Next Agent Brief
_Generated: 2026-09-10T00:00:28.675868+00:00_

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
- File Analyzer follow-up chat: ask questions grounded in the uploaded files; cites exact `path:line` locations and quotes snippets (line-numbered context)
- Google Drive ingestion (user OAuth): connect Drive, browse folders, SEARCH by name, import selected files into an analysis set (auto-analyzes right after import). Requires user-supplied Web-app OAuth client.

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
