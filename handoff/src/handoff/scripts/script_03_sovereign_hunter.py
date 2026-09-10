"""
ACASO KING - SCRIPT 03: THE SOVEREIGN HUNTER  (ACASO Omniverse edition)
Client / Contract / Job Profile Builder + Outreach Engine.

EDIT HUNT_MODE, YOUR_OFFER, TARGET_MARKET below, then:
    pip install httpx
    export ACASO_URL=https://<your-acaso-host>
    python script_03_sovereign_hunter.py
"""
import sys
from datetime import datetime
from acaso_client import require_online, deliberate, write_report

HUNT_MODE = "clients"  # "clients" | "contracts" | "jobs"

YOUR_OFFER = """
Product/Service: OmniTrackX - AI-powered logistics SaaS for courier delivery,
furniture moving, and office relocation companies.
- Real-time job tracking with live map
- AI-powered damage reports and claim filing
- Client-facing dashboard with transparent status updates
- QR + condition-based inventory tracking
Pricing: Starter $149/mo | Growth $349/mo | Pro $749/mo | Enterprise custom
Market: Initially Boston, MA
Founder: Alexander Mojica / MediaLinxS
"""

TARGET_MARKET = """
Boston, MA area logistics and moving companies: last-mile couriers (10-50 drivers),
furniture movers and storage, office relocation specialists, B2B delivery for
medical/legal/tech, companies still on spreadsheets, paper, or basic apps like Track-POD.
"""

HUNT_LABEL = {"clients": "high-value clients", "contracts": "lucrative contracts or RFPs",
              "jobs": "premium job opportunities or partnerships"}

CHALLENGE = f"""SOVEREIGN HUNTER DIRECTIVE - TARGET ACQUISITION

Hunt Mode: {HUNT_MODE.upper()} - Find 3 {HUNT_LABEL.get(HUNT_MODE, 'targets')}

What is being offered:
{YOUR_OFFER}
Target market:
{TARGET_MARKET}
PHASE 1 - TARGET IDENTIFICATION: 3 specific, realistic target categories. For each:
### TARGET [N] - [Category]
**Profile:** type, size, pain points the offer solves, decision maker, where they gather, trigger events, objections + neutralizers.
**Why they need this specifically:** 2-3 sentences.
**Credibility signals that will resonate.**

PHASE 2 - OUTREACH GENERATION (per target): Version A cold email (subject + body <150 words); Version B LinkedIn DM (<80 words); Version C follow-up (day 3).

PHASE 3 - SEQUENCE STRATEGY (per target): Day 1 / Day 3 / Day 7 / Day 14.

PHASE 4 - EXECUTION TOOLKIT: search strings, associations, directories, events; the single highest-leverage near-zero-cost action for TODAY.

## SOVEREIGN VERDICT
Which target is the highest-probability first close and exactly what to send tomorrow morning.
"""

CHECKLIST = """
---
## NEXT ACTIONS CHECKLIST
- [ ] Review Target 1 profile and send Version A outreach
- [ ] Review Target 2 profile and send Version A outreach
- [ ] Review Target 3 profile and send Version A outreach
- [ ] Calendar: Day 3 follow-ups
- [ ] Calendar: Day 7 pattern interrupt
- [ ] Calendar: Day 14 breakup messages
"""


def main():
    print(f"ACASO SOVEREIGN HUNTER - hunt mode: {HUNT_MODE.upper()}")
    require_online()
    print("Profiling targets and drafting outreach via the Council (60-180s)...\n")
    try:
        result = deliberate(CHALLENGE, "market_entry",
                            f"Sovereign Hunter mode - {HUNT_MODE}. Identify 3 real, specific, high-value targets. "
                            "Outreach must be specific, human, conversion-optimized. No generic templates.",
                            preset_id="hunter")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    print("=" * 65)
    print(result.get("sovereign_directive", ""))
    print("=" * 65)
    out = write_report(result, f"ACASO SOVEREIGN HUNTER - TARGET ACQUISITION PACKAGE ({HUNT_MODE.upper()})",
                       f"sovereign_hunter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md", CHECKLIST)
    print(f"\nOutreach package saved: {out}")
    print(f"Also stored server-side: {result.get('deliberation_id')}")


if __name__ == "__main__":
    main()
