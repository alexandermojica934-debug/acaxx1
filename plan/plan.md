# Plan: Claim the Throne (owner registration)

## What this is
Registering the single owner account is a step only the owner can take; nothing needs to be built for it. The app is live and waiting: the first visit shows **"Claim the throne"**, and the account created there becomes the sole owner. Registration closes the moment that happens.

## What the owner does
1. Open https://contest-ready-app.preview.emergentagent.com in Chrome or Edge.
2. Enter a name (optional), an email, and a password of at least 10 characters with upper and lower case letters and a digit. "Remember me" keeps the session 30 days instead of 7.
3. Press **Create owner account**. The app opens signed in; from then on every visit asks for that email and password.

## What is true after registration
- No one else can register. Anyone reaching the site sees only a sign-in form.
- Every API route requires the owner session, except buyer unlock links, the gated Prompt Library API, the Google Drive callback, and requests carrying the Agent Bridge key (Local Node, Agent Bridge, runner scripts keep working).
- Password can be changed from the account menu; doing so signs out every other device.
- Eight wrong passwords lock sign-in for 10 minutes.

## One decision worth making now
There is no "forgot password" today (email recovery was declined earlier because it needs an email provider). If the password is lost, the only recovery is a manual database reset by whoever operates the server.

**Proposed (small, no email provider needed):** at registration, show a set of 8 one-time **recovery codes** to download or copy. Any code can be used once on the sign-in screen to set a new password. Codes are stored hashed like passwords; the account menu can regenerate them (which invalidates the old set).

- Approve: recovery codes are added before or right after the owner registers (an existing owner can generate them from the account menu).
- Decline: registration proceeds as is; recovery remains a manual server-side reset.

## Assumptions
- One owner, no team invites, unchanged from the earlier decision.
- The owner registers on the preview URL; if the app is later deployed to a production URL, the same account carries over only if the database is the same.
- Email-based password reset stays out unless the owner supplies an email provider key (Resend or SendGrid) later.
