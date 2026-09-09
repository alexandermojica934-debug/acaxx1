# ACASO Omniverse — Round 1: Files that Read, Live Bounty Loop, Pop-out Chat

## New reference docs from the user

Two files were uploaded and analyzed. They do not change Round 1. They do reshape
Round 2+ and are worth flagging before build starts.

### `capabilities.json` — the ten-vertical product catalog

A list of ten named product-line modules with the human role each replaces and the
labor cost each saves. In order:

| # | Module              | Vertical                                      | Labor replaced          |
|---|---------------------|-----------------------------------------------|-------------------------|
| 1 | Bio-Signature Charting | Medical scribing                           | $45–60k/yr              |
| 2 | Ghost-Protocol      | Off-market real-estate deal modeling          | $70–85k/yr              |
| 3 | Privilege-Sentinel  | Legal document review                         | $65–90k/yr              |
| 4 | Ancestral Advocate  | Grant / proposal writing                      | $50–80k/yr              |
| 5 | Sovereign Ledger    | Autonomous CRM + lead ledger                  | $55k/yr + SaaS savings  |
| 6 | Genesis Armor       | Architectural drafting + IT security          | $70k/yr                 |
| 7 | Contract Sentinel   | Real-time contract auditing                   | $300–500/hr             |
| 8 | High-Frequency Masking | Quantitative analysis                      | $120–150k+/yr           |
| 9 | Scorch Protocol     | Crisis IT / breach response                   | $150k–$3M/incident      |
| 10| Prince Protocol     | Intelligence succession / transition training | $30–50k/transition      |

What this means for the plan:

- ACASO is not one product — it is a platform hosting ten vertical modules. None of
  the ten are built today. Each is a future round (some, like Bio-Signature Charting,
  carry regulatory workloads — HIPAA — that are as big as the code itself).
- The bug-bounty loop being built in Round 1 is not one of these ten. It is a
  cross-vertical demonstration flow. The closest fits are Genesis Armor (IT security)
  and Scorch Protocol (breach response).
- **The crypto trading bot the user asked for is module #8, High-Frequency Masking.**
  This gives it a home in the catalog. It is still deferred to its own round,
  still blocked on the Foresight + APEX design docs.
- A Round 2 fast-add: surface the ten verticals as a grid on Sovereign Home, each as
  a "coming soon" tile that clicks into a static module page. Cheap (~5 credits),
  makes the platform positioning legible, does not require building any of the ten.

### `ai_soul_brain_module.py` — the Perfect Next scaffold

A Python module (`AISoulBrain` class) implementing the observe-analyze-forecast loop
described in the Synarchy spec as "Perfect Next." Its shape:

1. `omni_observe(subject_id, data)` — gathers observations across four dimensions:
   biological/physical, sociological/story, mental/decision-making,
   vibrational/universal.
2. `compare_and_learn(subject_id, target_state)` — compares current state to a
   target future state, produces gaps and trajectories.
3. `engineer_future(subject_id, comparison)` — builds a predictive roadmap of
   critical junctures and optimal interventions.
4. `soul_brain_synthesis(subject_id, roadmap)` — collapses everything into a single
   unified insight sentence.
5. `calculate_perfect_next_step(subject_id, data, target_state)` — the full pipeline.

Honest read of the code as delivered:

- Every method is a placeholder returning hardcoded strings. There is no analysis
  logic yet.
- The four observation dimensions are unequal in tractability. Biological/physical
  and sociological/story map to real data (health records, LinkedIn, prior actions).
  Mental/decision-making maps to logged decisions and past choices. Vibrational/
  universal has no obvious data source — it either becomes a soft/qualitative
  dimension driven by LLM inference over the other three, or it is scoped down.
- The `Michael Davis / High-Ticket Real Estate` example is realistic — it maps
  cleanly to the Ghost-Protocol vertical from `capabilities.json`.

What this means for the plan:

- The scaffold is the intended shape of the "Perfect Next" item that was already on
  the Round 2 menu. The Round 2 build ports this scaffold, replaces the placeholders
  with real logic, and wires it into Sovereign Home.
- The four-dimension model needs a decision when Round 2 starts: keep all four
  (with vibrational/universal being LLM-inferred, marked as soft), reduce to three
  concrete dimensions, or rename. This can be answered at Round 2 kickoff — it does
  not affect Round 1.
- Perfect Next is subject-forecasting, distinct from the Soul Council's
  decision-arbitration pattern. Both are "souls" in the ACASO cosmology but they do
  different jobs. The plan keeps them as separate engines rather than trying to
  merge them.

---

## What changed since the previous plan

Corrections and additions after clarification:

- **"Castle" and "Aether Weaver" scrapped.** Those were mishearings on the assistant's
  part. The bounty flow is ACASO-native, points at a real target URL, and does not
  host a fake vulnerable app inside ACASO.
- **File upload widened to "upload + read."** Not just storage — the AI actually
  ingests the file's content (extracted text from PDFs and docs, vision on images)
  and uses it in the compiler, the Souls, and the new chat.
- **Pop-out chat panel added.** A Gemini-style chat surface that lives on every ACASO
  screen and can pop out into its own always-on-top browser window.
- **ElevenLabs voice — speech-to-text added, TTS deferred.** Every dictation surface
  (Sovereign Home directive, chat panel, bounty writeup) gets a mic button that
  transcribes speech into the field. Chosen because half this conversation's
  errors came from speech-to-text (that is how "Castle" and "Aether Weaver"
  appeared — speech recognition failure), so the highest-value ElevenLabs use is
  fixing dictation, not adding audio output. Text-to-speech and voice cloning
  move to Round 2.
- **Crypto trading bot deferred.** Waiting on the Foresight and APEX design docs from
  the user's Drive. Those Drive links in the Synarchy spec are private and the
  assistant cannot open them — they need to be uploaded here the same way the
  Synarchy file was.

Round 1 is now four features, each scoped as tight as possible to fit inside the
~100-credit guardrail. It is at the edge of that guardrail. If any of the four gets
harder than expected during build, the plan is to ship the working parts, mark the
rest, and hand off to Round 2 — not to overrun silently.

---

## Round 1 — what ships

### 1. File & Media Storage — the primitive

Uses the Emergent-managed object storage integration (no new account, no new secrets,
reuses the existing Emergent key). Files are private, reads flow through an
authenticated app endpoint, soft-delete only, 10 MB per file, allowed types are
images / pdf / txt / log / json / har / md.

### 2. File Reading — the AI actually consumes what is uploaded

When a file is attached anywhere in ACASO, the app extracts its content and makes it
available to the models:

- Text files, markdown, logs, JSON, HAR — read verbatim.
- PDFs — text is extracted server-side.
- Images (PNG, JPG, WEBP) — sent to a vision-capable model for interpretation, with
  the returned description attached to the file record.

The extracted content flows into whichever surface the file was attached from — the
directive compiler on Sovereign Home, the Soul Council on a bounty finding, or the
chat panel.

### 3. The bounty loop, end to end

- **Target.** The program owner points ACASO at a target URL — an app they own, a
  staging site, or a public program's in-scope surface. The URL, program name, scope
  notes, and maximum payout are stored on the bounty mission.
- **Submission.** A hunter (the owner, or an invited persona) submits a finding
  against a target: payload, short writeup, and any PoC files (screenshots, HAR,
  logs). PoC files use the storage integration and are read (see #2) so the Souls
  see their content when they convene.
- **Verification.** The Soul Council auto-convenes on submission. Each Soul analyzes
  the writeup + PoC content + payload for validity, severity, and impact. The Throne
  synthesizes a verdict, produces the dissent summary and Fix Export patch note
  (both already shipped), and signs the verdict + PoC hashes so the receipt is
  tamper-evident.
- **No deterministic probe in Round 1.** The earlier plan included a probe that
  re-ran the submitted exploit against a bundled target. With the bundled target gone,
  the probe cannot run — ACASO does not run real exploits against arbitrary external
  URLs; that would be an actual attack on third-party infrastructure. Verification is
  therefore Soul-driven: the Souls reason about validity and consistency from the
  submitted evidence, and the Throne states its confidence explicitly. If the finding
  is questionable, the confidence drops and the owner can reject.
- **Owner approve payout.** The owner sees a signed verdict card with an
  Approve Payout button. Nothing moves without the tap. Matches the spec's Authority
  Ladder — Collect level requires owner approval.
- **Payout.** Real Stripe API call in **test mode**. Stripe Connect Express, with a
  pre-created "demo hunter" test account so the loop is exercisable without a second
  real human. Real receipt, no real money movement. Flip to live mode is a key
  rotation gated on the compliance workflow described below. On successful transfer
  the signed receipt lands in Chronicle as revenue.

### 4. Pop-out chat panel — Gemini-style

- Floating chat button on every ACASO screen. Click opens a slim chat window that
  minimizes and expands.
- The window can also be popped out into a small browser popup that stays visible
  while other apps are focused — the closest surface to Gemini's floating desktop
  widget without shipping a native app.
- Chat is powered by the same Ask-All-AIs backend that already exists. Users can
  select which model(s) respond.
- Files can be attached to messages and are read via #2. Anything discussed in chat
  can reference the current mission by ID.
- Chat sessions persist so the user can close and reopen without losing history.

### 5. ElevenLabs speech-to-text — dictation everywhere

- A mic button on the Sovereign Home directive field, the pop-out chat, and the
  bounty finding writeup field. Tap to record, tap to stop, transcript lands in the
  field. Uses ElevenLabs `speech_to_text.convert` with model `scribe_v1`.
- Uses the storage integration to briefly hold the recorded audio; the audio is
  deleted after transcription completes (or kept as evidence if attached to a
  bounty finding).
- Requires an ElevenLabs API key from the user. Emergent's universal key does not
  cover ElevenLabs — this is a paid third-party API, billed per second of audio.
- FFmpeg is required as a system dependency for audio format conversion. Adding it
  is a small setup step; not zero cost.
- What ships in Round 1: STT only. Text-to-speech (Soul voices speaking their
  verdicts, Throne narration) and voice cloning (custom voices per Soul) move to
  Round 2. That is a deliberate cost decision.

---

## Reality checks worth surfacing before yes

### Real Stripe money is a compliance workflow, not a code flip

Same as the prior plan. Test mode in Round 1. Flipping to live money requires:

- Platform KYC completed on the Stripe account.
- Stripe Connect enabled with Express onboarding.
- Written bounty program terms of service every hunter agrees to.
- US tax handling — 1099-NEC / W-9 for hunters over $600/year, W-8BEN for non-US.
- Dispute and refund policy.

None of that is code work and none of it is in Round 1. Round 1 makes it reachable by
key rotation.

### Verification without a probe is softer

With no bundled target and no probe running against external URLs, verification is
Soul reasoning plus Throne signature — not a deterministic pass/fail. This is
inherent to pointing ACASO at arbitrary real targets. The Round 2 path back to a
deterministic probe is either (a) narrow-scope target adapters for specific programs
where re-running the exploit is legal and safe, or (b) an opt-in internal practice
target the owner can toggle on for demos (name TBD; the assistant will not invent one
this time).

### Chat is a pop-out, not a native app

Google Gemini's desktop feel comes from a real Mac/Windows app with code signing and
distribution. That is a separate build (~4-5 days, its own round). Round 1 ships the
closest browser-native equivalent: an in-app pop-out window that stays on top of
other windows. If a real native app is required, it moves to a dedicated round.

### Round 1 is at the edge of the guardrail

Four features in one round is tight. If a feature exceeds its budget slice mid-build,
the plan is to ship what works, mark the rest, and continue in Round 2. No silent
overruns.

Adding ElevenLabs STT to the round is a deliberate stretch over the ~100-credit
guardrail — roughly a 15-credit slice — because it fixes a real usability problem
already observed in this conversation. If the guardrail is hard, the first trim is
either ElevenLabs (defers dictation to Round 2) or Sovereign Home directive
attachments (small feature; slides to Round 2 cleanly).

### ElevenLabs requires a real API key and adds a real running cost

The Emergent universal LLM key does not cover ElevenLabs. A separate ElevenLabs
account and API key is required, and every second of transcribed audio is billed
against that account. Reasonable use is a few dollars a month; heavy dictation could
be tens. FFmpeg is also a required system dependency and needs to be installed on
the backend host.

### Deployment health check is blocked by plan mode

The user asked for a deployment agent health check in the same message. Plan mode
disables the deployment_agent tool. After this plan is approved and plan mode exits,
the health check runs before the first build action. If the check reports any
blocker, the build stops until the blocker is fixed.

---

## Assumptions taken (each is a place to push back)

- The chat surface is a **pop-out window inside the app**, not a real native desktop
  app.
- The bounty target is a **URL the user provides**. No fake target hosted inside
  ACASO. No cosmology-named "Castle."
- Verification is **Souls + Throne only** — no deterministic probe in Round 1.
- Stripe ships in **test mode** with Connect + Express + a pre-created demo hunter.
- File reading uses the vision-capable model already in the roster for images, and
  server-side text extraction for PDFs.
- Storage attach points that ship in Round 1: **bounty PoC uploads**, **Sovereign
  Home directive attachments**, **chat message attachments**. Action Bus evidence
  uploads and Fix Export bundle download slide to Round 2.
- External bounty platforms (H1, Bugcrowd, Immunefi) remain Round 2.
- Crypto trading bot is **not** in Round 1 or Round 2 until the Foresight and APEX
  docs are uploaded here — the assistant cannot read the user's Drive.
- **ElevenLabs Round 1 slice = STT only.** Text-to-speech and voice cloning are
  Round 2. The user must supply the ElevenLabs API key before build starts, or the
  feature drops from Round 1 automatically.
- Model roster and Soul personas unchanged.
- ~100-credit guardrail with a clean stop remains in effect, with an explicit ~15
  credit stretch acknowledged for ElevenLabs. If Round 1 finishes under, the
  leftover funds one item from the Round 2 menu below — user's pick.

---

## Round 2+ menu (updated)

Items previously listed stay. Items added or reshaped by this round:

- **Ten-Vertical Catalog on Sovereign Home.** Surface the ten modules from
  `capabilities.json` as a grid, each a placeholder page. Cheap. Makes the platform
  positioning legible.
- **Perfect Next Engine.** Port `ai_soul_brain_module.py`, replace placeholders with
  real logic, decide the four-dimension model at kickoff, wire into Sovereign Home
  as the "one recommended next action" panel.
- **ElevenLabs — Text-to-speech + voice cloning.** Each Soul gets a distinct voice
  (Vision / Fusion / Rebirth), Throne narrates the verdict aloud, chat replies can
  be spoken. Voice cloning uses ElevenLabs IVC (Instant Voice Cloning) from 20-second
  samples — requires explicit owner-consent step in the UI per ElevenLabs terms.
- **Crypto trading bot = High-Frequency Masking vertical.** Blocked on Foresight +
  APEX doc upload. Once received, its own round because it is a full architecture
  on its own — market data ingest, strategy engine, execution, risk limits, paper
  vs. live modes, exchange or DEX integration.
- **Native desktop app (Mac/Windows).** Electron or Tauri build with code signing
  and auto-updates. Its own round.
- **PWA install** — smaller cousin of the native app. Could ship as a small
  follow-up.
- **Deterministic bounty probe.** Requires either narrow-scope adapters for specific
  programs, or an internal opt-in practice target (not to be named "Castle").
- **Stripe live-mode flip** — blocked on the compliance workflow above.
- **External bounty platforms** — HackerOne program-owner integration, Bugcrowd
  Crowdcontrol, Immunefi.
- **Remaining storage attach points** — Action Bus evidence, Fix Export bundle.
- **The wider spec lanes** — Authority Ladder + Mandate Object, Credential Vault,
  Real Email lane, Worker lane, Browser lane, Evidence-backed source connectors,
  Shareable Verdict URL, Agent Bridge rate limit.
- **Individual vertical builds** — each of the ten `capabilities.json` modules is
  its own future round. Some (Bio-Signature Charting, Privilege-Sentinel) carry
  regulatory workloads (HIPAA, legal privilege) that are as big as the code.
- **Prior paused items** — Open GitHub PR (Fix Export → real PR), Soul Debate is
  already shipped, "Real Bounty Submit" is partially superseded by the external
  platforms items.

---

## Out of scope for Round 1

- Any real live-mode Stripe money movement.
- Crypto trading bot.
- Native desktop app.
- Deterministic probe against external targets.
- External bounty platform ingestion.
- Action Bus evidence uploads and Fix Export bundle download.
- Any of the wider spec lanes listed in the Round 2 menu.

---

## Decisions worth challenging

1. **Verification without a probe.** With external URLs as targets, ACASO cannot
   re-run the exploit — that would be a real attack. Round 1 verification is
   Soul-driven. If deterministic verification is required in Round 1, the plan needs
   to reintroduce a bundled opt-in practice target (renamed from the deleted "Castle"
   framing).
2. **Chat surface = pop-out window, not native app.** If a real Mac/Windows app is
   required, this becomes a separate round and Round 1 drops the chat feature entirely
   or keeps only the in-app panel.
3. **Round 1 is over the guardrail.** Five features (Storage, File Reading, Bounty
   Loop, Chat, ElevenLabs STT) instead of four. If tighter scope is preferred, the
   first trim is ElevenLabs (defers dictation to Round 2, saves ~15 credits) or the
   Sovereign Home directive attach point (~5 credits). Both slide to Round 2 without
   breaking the core loop.
4. **ElevenLabs API key on hand.** Build cannot start on the ElevenLabs slice until
   the key is provided. If not available in time, the feature auto-drops to Round 2.
