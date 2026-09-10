"""
ACASO Omniverse - shared client for the runner scripts.

Set ACASO_URL to your deployment, e.g.
    export ACASO_URL=https://contest-ready-app.preview.emergentagent.com
Defaults to the hosted preview. All routes live under /api.
"""
import os, sys
from datetime import datetime
import httpx

ACASO_URL = os.environ.get("ACASO_URL", "https://contest-ready-app.preview.emergentagent.com").rstrip("/")
API = f"{ACASO_URL}/api"


def check_online() -> bool:
    try:
        return httpx.get(f"{API}/acaso/presets", timeout=10.0).status_code == 200
    except Exception:
        return False


def deliberate(challenge: str, challenge_type: str, additional_context: str = "", preset_id: str | None = None) -> dict:
    with httpx.Client(timeout=320.0) as client:
        r = client.post(f"{API}/acaso/deliberate", json={
            "challenge": challenge,
            "challenge_type": challenge_type,
            "preset_id": preset_id,
            "context": {"additional_context": additional_context} if additional_context else None,
        })
        r.raise_for_status()
        return r.json()


def fetch_preset(preset_id: str) -> dict:
    r = httpx.get(f"{API}/acaso/presets", timeout=10.0)
    r.raise_for_status()
    for p in r.json():
        if p["id"] == preset_id:
            return p
    raise SystemExit(f"preset {preset_id!r} not found on server")


def write_report(result: dict, title: str, out_file: str, extra_sections: str = "") -> str:
    council = result.get("council_consulted", [])
    md = f"""# {title}
Generated: {result.get('timestamp', datetime.now().isoformat())[:19]} | Deliberation: {result.get('deliberation_id')}
Council: {', '.join(council) if council else 'n/a'} | Shadow veto: {'YES' if result.get('shadow_veto') else 'no'}

> {result.get('data_provenance', '')}

---
## WEAK SIGNALS (inferred)
{result.get('weak_signals') or '_none_'}

---
{result.get('sovereign_directive', '')}

---
## INTERNAL WEAVERS ANALYSIS
{result.get('weavers_synthesis', '')}
{extra_sections}
---
*ACASO Omniverse - Council of Weavers - (c) 2026 Alexander Mojica / MediaLinxS*
"""
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md)
    return out_file


def require_online():
    print(f"Checking ACASO at {ACASO_URL} ...")
    if not check_online():
        print("ACASO is not reachable. Set ACASO_URL to your running deployment.")
        sys.exit(1)
    print("ACASO Omniverse online.\n")
