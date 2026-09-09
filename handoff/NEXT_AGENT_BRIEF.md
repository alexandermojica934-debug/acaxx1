# ACASO Omniverse — Next-Agent Brief

**Read this first.** This is the single actionable entrypoint. Everything below is verified against
the running preview at the timestamp in `VERIFIED_STATE.json`. If a claim here isn't in that file,
treat it as unverified.

---

## 1. What this app is (30 seconds)

A "Directive-to-Payment Operating System." A user types a natural-language goal ("find and report
an IDOR on a fintech API"), and the app:

1. Compiles it into a **Mission Graph** (stages + steps + payment path + outcome metric).
2. Executes steps on the **NEXUS Action Bus** with timestamped simulated evidence.
3. For bug-bounty missions, convenes a **Soul Council** (Gemini + OpenAI + Claude, each as a distinct
   persona) and synthesizes an **Eternal Throne** verdict — now including a **Soul Dissent View**
   and a **PR-ready Fix Export**.
4. Records outcomes to the **Chronicle**; future compilations reuse those lessons.
5. Exposes an authenticated **Agent Bridge** (`X-ACASO-Key`) so external agents (Manus / Gemini /
   ChatGPT / cURL) can issue and run missions.

**Demo scope:** all "execution" is simulated. No real bounty submissions, no real payments.

---

## 2. Stack & invariants (do not violate)

| Layer     | Choice                                                                |
| --------- | --------------------------------------------------------------------- |
| Backend   | FastAPI + Motor + MongoDB, single file `backend/server.py`            |
| Frontend  | React 19 + CRACO + Tailwind + Shadcn UI + Framer Motion + Sonner      |
| LLMs      | `emergentintegrations` universal key across OpenAI / Gemini / Claude  |
| IDs       | UUIDs only — never `ObjectId`                                         |
| Datetimes | `datetime.now(timezone.utc).isoformat()` only                         |
| Routes    | All backend routes prefixed with `/api`                               |
| Env       | Frontend uses `REACT_APP_BACKEND_URL`; backend uses `MONGO_URL`       |
| Process   | supervisorctl restart backend / frontend — never run servers by hand  |
| Package   | `yarn add` — never npm                                                |

---

## 3. Working model IDs (verified live, do NOT change without re-testing)

| Provider  | Model ID              | Used for                                     |
| --------- | --------------------- | -------------------------------------------- |
| OpenAI    | `gpt-4o-mini`         | Fusion Engine, Ask All AIs, synthesis        |
| Gemini    | `gemini-3.6-flash`    | Vision Command, Ask All AIs, Throne default  |
| Anthropic | `claude-haiku-4-5`    | Rebirth Protocol, Ask All AIs, failover      |

**Do-not-retry ledger** (models that returned 404 / not-found — do not re-use):

- ❌ `gemini-2.0-flash`
- ❌ `claude-3-5-haiku-20241022`

---

## 4. One-command smoke test (proves the whole stack works)

Set `BE` to the backend URL, then run:

```bash
BE="$REACT_APP_BACKEND_URL"     # e.g. https://<your>.preview.emergentagent.com

# 1) All three LLMs
curl -s -X POST "$BE/api/chat" -H "Content-Type: application/json" \
  -d '{"message":"one word: color of sky?","models":["openai","gemini","anthropic"]}' \
  | python3 -c "import sys,json;d=json.load(sys.stdin);[print(r['provider'],r['ok'],r['answer'][:40]) for r in d['results']];print('synth ok:',bool(d.get('synthesis')))"

# 2) Compile a bug-bounty directive
RESP=$(curl -s -X POST "$BE/api/compile-bounty" -H "Content-Type: application/json" \
       -d '{"directive":"Find and report an IDOR on a fintech API via HackerOne","platform":"HackerOne"}')
MID=$(python3 -c "import sys,json;print(json.loads(sys.argv[1])['id'])" "$RESP")

# 3) Deploy Soul Council + verify NEW fields (dissent + patch_note)
curl -s -X POST "$BE/api/missions/$MID/deploy-souls" \
  | python3 -c "
import sys,json
r=json.load(sys.stdin)['council']['resolution']
assert r['status']=='RESOLVED', r
assert len(r['dissent'])>=1, 'dissent missing'
assert 'root_cause' in r['patch_note'].lower() or '## Root Cause' in r['patch_note'], 'patch_note malformed'
print('OK — dissent entries:',len(r['dissent']),'| patch_note chars:',len(r['patch_note']))"

# 4) Agent Bridge auth (must return 401 without key)
test $(curl -s -o /dev/null -w '%{http_code}' -X POST "$BE/api/agent/directive" \
       -H "Content-Type: application/json" -d '{"directive":"x"}') = "401" && echo "OK — bridge rejects no-key"
```

If all four checks print `OK`, the app is healthy end-to-end.

---

## 5. What's shipped, what's mocked, what's next

### ✅ Shipped & verified

- Sovereign Home directive compilation → Mission Graph
- Ask All AIs (3 providers + synthesis)
- NEXUS Action Bus (step execution, auto-run, approval gates, evidence)
- Chronicle / Outcome Ledger (lessons flow back into future compilations)
- Bug-bounty compilation (program / asset / severity / CVSS / report / payout)
- Soul Council with per-provider failover
- Eternal Throne synthesis
- **Soul Dissent View** — structured `{topic, positions{vision,fusion,rebirth}, reconciliation}`
- **Fix Export** — PR-ready markdown patch note with a Copy button (`data-testid="fix-export-copy-<mid>"`)
- Agent Bridge — key issue/regenerate/activity + protected `/api/agent/*` endpoints (401 on no key)

### ⚠️ Explicitly mocked (do not "fix" without user approval)

- **Action execution** — evidence is LLM-generated narrative, not real system calls.
- **Payments** — payout amounts are simulated; no Stripe/bank/HackerOne wallet integration.
- **Bounty submission** — no real HackerOne/Bugcrowd/Intigriti API calls.
- **Manus / ChatGPT / Gemini connectors** — schema + cURL guidance is provided; the Bridge itself
  is real, but the *counterparty* integrations are documentation-only.

### 🎯 Suggested next work (ordered by leverage)

1. **Persist dissent history** — show how many times each soul "wins" the reconciliation over time.
2. **Fix Export → GitHub PR** — one-click "Open PR" via GitHub App / OAuth, using the patch note.
3. **Real bounty submission** — HackerOne API integration behind an explicit user opt-in gate.
4. **Payment rail** — Stripe Connect for real payouts (currently `amount` is display-only).
5. **Multi-tenant auth** — currently single-owner; add user accounts if going beyond demo.

---

## 6. Where to make each type of change

| I want to change…                         | File                                                       |
| ----------------------------------------- | ---------------------------------------------------------- |
| Any backend logic / prompt / endpoint     | `backend/server.py` (monolithic — search by section header)|
| Which model handles which soul            | `SOULS` list in `server.py` (~line 483)                    |
| Throne output schema (dissent/patch_note) | `throne_prompt` + `resolution` default (~line 547)         |
| Dissent / Fix Export UI                   | `frontend/src/components/BugBounty.js` (~line 320+)        |
| Dissent / Fix Export styling              | `frontend/src/App.css` under `/* Soul Dissent */`          |
| Agent Bridge UI                           | `frontend/src/components/AgentBridge.js`                   |
| Ask All AIs UI                            | `frontend/src/components/AskAllAIs.js`                     |
| Chronicle UI                              | `frontend/src/components/Chronicle.js`                     |
| Sovereign Home UI                         | `frontend/src/components/SovereignHome.js`                 |
| Design tokens (colors, radii, fonts)      | `frontend/src/App.css` `:root` block                       |

---

## 7. Secrets you must set (never commit)

`backend/.env` (copy from `backend/.env.example`):

```
MONGO_URL=mongodb://localhost:27017
DB_NAME=acaso
EMERGENT_LLM_KEY=<get from Emergent profile → Universal Key>
CORS_ORIGINS=*
```

`frontend/.env` (copy from `frontend/.env.example`):

```
REACT_APP_BACKEND_URL=<your backend URL, no trailing slash>
```

---

## 8. When you're stuck

1. `tail -n 100 /var/log/supervisor/backend.*.log /var/log/supervisor/frontend.*.log`
2. Re-run section 4's smoke test — if it passes, the issue is in the change you just made.
3. Check `VERIFIED_STATE.json` in this handoff for the last-known-good response shapes.
4. Do not silently swap model IDs — record the failure in the do-not-retry ledger above.

That's it. Everything else in this handoff (the full `.md` companion + `src/` tree) is reference
material. This brief is the actionable core.
