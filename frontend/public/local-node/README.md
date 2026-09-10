# ACASO Local Node

Runs on YOUR computer so the hosted ACASO app can work with your files and your real browser.
The hosted app cannot reach your PC by itself - this program is the bridge, and you stay in control.

## 1. Install (once)
```
python -m pip install httpx
# optional, for browser tasks (sign-ups, forms) in a real Chrome window:
python -m pip install playwright
python -m playwright install chrome
```

## 2. Get your key
Open ACASO -> **Agent Bridge** tab -> copy the `X-ACASO-Key`.

## 3. Run
Windows (PowerShell / cmd):
```
set ACASO_URL=https://contest-ready-app.preview.emergentagent.com
set ACASO_KEY=acaso_xxxxxxxxxxxx
python acaso_node.py --root "C:\Users\you\ACASO" --shell --browser
```
Linux / macOS:
```
ACASO_URL=https://contest-ready-app.preview.emergentagent.com ACASO_KEY=acaso_xxxx python3 acaso_node.py --root ~/ACASO --shell --browser
```
Or edit and double-click `run_node.bat` (Windows) / `run_node.sh` (Linux).

The node appears as **online** in the ACASO **Local Node** tab within seconds.

## What it can do (only after you approve each action in the app)
| Task | Notes |
|---|---|
| list / read / stat files | auto-approved (read-only), only inside `--root` folders |
| create / write / append / move / delete files | approval required; writes back up the old file as `*.acaso.bak`; delete = move to `.acaso_trash` |
| shell command | only with `--shell`; runs inside the root folder with a timeout |
| browser open / fill / screenshot | only with `--browser`; a real Chrome window opens on your PC; forms are filled and **never submitted** |
| browser submit | separate task you approve after reviewing the filled form screenshot |

## Passwords, 2FA, payments
The planner writes `[OWNER TYPES THIS]` for secrets. Type them yourself in the Chrome window. The node never reads or
uploads them. The Chrome profile lives at `~/.acaso_chrome_profile` so your logins persist between runs.

## Stop
Ctrl+C. Nothing runs when the node is off; queued tasks simply wait.
