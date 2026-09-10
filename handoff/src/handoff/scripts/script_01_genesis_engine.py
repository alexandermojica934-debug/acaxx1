"""
ACASO KING - SCRIPT 01: THE GENESIS ENGINE  (ACASO Omniverse edition)
One-Of-A-Kind Product / Service / Invention Generator.

Calls the live Council of Weavers at POST /api/acaso/deliberate using the server-side
'genesis' preset (edit FOUNDER_OVERRIDE below to customise the founder profile).

HOW TO RUN:
    pip install httpx
    export ACASO_URL=https://<your-acaso-host>
    python script_01_genesis_engine.py
"""
import sys
from datetime import datetime
from acaso_client import require_online, fetch_preset, deliberate, write_report

FOUNDER_OVERRIDE = ""  # optional: paste a new 'Founder Profile' block to replace the preset's


def main():
    print("ACASO GENESIS ENGINE - INVENTION DISCOVERY")
    require_online()
    preset = fetch_preset("genesis")
    challenge = preset["challenge"]
    if FOUNDER_OVERRIDE.strip():
        head, _, tail = challenge.partition("MISSION:")
        challenge = f"GENESIS DIRECTIVE - INVENTION MANDATE\n\nFounder Profile:\n{FOUNDER_OVERRIDE.strip()}\n\nMISSION:{tail}"
    print("Convening Architect / Shadow / Muse / Finance -> Meta-Weaver (60-180s)...\n")
    try:
        result = deliberate(challenge, preset["challenge_type"], preset.get("additional_context", ""), preset_id="genesis")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    print("=" * 65)
    print(result.get("sovereign_directive", ""))
    print("=" * 65)
    out = write_report(result, "ACASO GENESIS ENGINE - INVENTION BRIEF",
                       f"genesis_invention_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    print(f"\nInvention brief saved: {out}")
    print(f"Also stored server-side: {result.get('deliberation_id')} (open the Council tab -> Past deliberations)")


if __name__ == "__main__":
    main()
