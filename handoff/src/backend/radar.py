"""
ACASO Opportunity Radar - real public-opportunity discovery with strict data integrity.

Rules enforced here:
  * AI never invents an opportunity, amount, deadline, agency or eligibility rule. Adapters only
    normalize what a source returned; every record carries source_url, retrieved_at, http_status,
    parser_version and evidence excerpts with a source_location for each important field.
  * Unknown fields stay None and are rendered "Not verified" by the UI.
  * Scores and classifications are explicitly labelled as inferred, with a full breakdown.
  * "Strong fit" requires the Skeptic persona to have run and not blocked.
  * Drafts (emails, grant narratives, packets, form answers) use only the owner's profile and the
    opportunity's source text; anything unknown becomes a [FILL: ...] placeholder. No auto-submission.
"""
import asyncio
import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Callable, Awaitable

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("radar")
router = APIRouter(prefix="/radar")

PARSER_VERSION = "radar-1.0"
UA = "ACASO-Opportunity-Radar/1.0 (+public data client; contact owner)"

# injected by server.py
db = None
llm_call_failover: Optional[Callable[..., Awaitable]] = None
compile_mission_from_text: Optional[Callable[..., Awaitable]] = None
extract_json: Optional[Callable] = None


def init(_db, _llm_failover, _compile_mission, _extract_json):
    global db, llm_call_failover, compile_mission_from_text, extract_json
    db, llm_call_failover, compile_mission_from_text, extract_json = _db, _llm_failover, _compile_mission, _extract_json


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ----------------------------------------------------------------------------------------------
# Profile
# ----------------------------------------------------------------------------------------------
ENTITY_TYPES = ["individual", "sole_proprietor", "llc", "corporation", "nonprofit", "startup", "creator",
                "contractor", "community_org", "government", "university"]
OPP_TYPES = ["grant", "contract", "subcontract", "procurement", "sponsorship", "rfp", "funding", "technical_bounty"]


class RadarProfile(BaseModel):
    id: str = "owner"
    entity_type: Optional[str] = None
    org_name: Optional[str] = None
    country: Optional[str] = "US"
    state: Optional[str] = None
    city: Optional[str] = None
    service_area: Optional[str] = None  # local | state | national | international
    industries: List[str] = []
    naics_codes: List[str] = []
    skills: List[str] = []
    keywords: List[str] = []
    years_experience: Optional[int] = None
    revenue_range: Optional[str] = None
    team_size: Optional[int] = None
    certifications: List[str] = []
    set_asides: List[str] = []  # minority, veteran, woman, disability, hubzone, 8a, sdvosb, disadvantaged
    nonprofit_status: Optional[bool] = None
    budget: Optional[float] = None
    hours_per_week: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    willing_travel: Optional[bool] = None
    willing_subcontract: Optional[bool] = None
    preferred_types: List[str] = []
    bio: Optional[str] = None  # owner-written capability statement; used verbatim as the only "claims" source
    updated_at: str = Field(default_factory=now_iso)


async def get_profile() -> dict:
    doc = await db.radar_profile.find_one({"id": "owner"}, {"_id": 0})
    return doc or RadarProfile().model_dump()


@router.get("/profile")
async def read_profile():
    return await get_profile()


@router.put("/profile")
async def write_profile(p: RadarProfile):
    p.id = "owner"
    p.updated_at = now_iso()
    await db.radar_profile.update_one({"id": "owner"}, {"$set": p.model_dump()}, upsert=True)
    return p


# ----------------------------------------------------------------------------------------------
# Helpers: text, money, dates, evidence
# ----------------------------------------------------------------------------------------------
MONEY_RE = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(k|m|million|thousand)?", re.I)


def parse_money(text: str):
    if not text:
        return None, None
    m = MONEY_RE.search(text)
    if not m:
        return None, None
    n = float(m.group(1).replace(",", ""))
    suf = (m.group(2) or "").lower()
    if suf in ("k", "thousand"):
        n *= 1_000
    elif suf in ("m", "million"):
        n *= 1_000_000
    start = max(0, m.start() - 60)
    return n, text[start:m.end() + 60].strip()


def parse_date(s):
    if not s:
        return None
    s = str(s).strip()
    fmts = ["%m/%d/%Y", "%b %d, %Y %I:%M:%S %p", "%b %d, %Y", "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"]
    s2 = re.sub(r"\s(EDT|EST|CDT|CST|MDT|MST|PDT|PST)$", "", s)
    for f in fmts:
        for cand in (s, s2):
            try:
                d = datetime.strptime(cand, f)
                if d.tzinfo is None:
                    d = d.replace(tzinfo=timezone.utc)
                return d.isoformat()
            except Exception:
                continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).isoformat()
    except Exception:
        return None


def days_until(iso):
    if not iso:
        return None
    try:
        d = datetime.fromisoformat(iso)
        return (d - datetime.now(timezone.utc)).days
    except Exception:
        return None


def ev(field, excerpt, location):
    if excerpt is None or excerpt == "":
        return None
    return {"field": field, "excerpt": str(excerpt)[:400], "source_location": location}


def strip_html(t):
    if not t:
        return ""
    t = re.sub(r"<[^>]+>", " ", str(t))
    return re.sub(r"\s+", " ", t).strip()


def dedupe_key(source, source_id, title, org, deadline):
    if source_id:
        return f"{source}:{source_id}"
    base = f"{re.sub(r'[^a-z0-9]', '', (title or '').lower())[:80]}|{(org or '').lower()[:40]}|{deadline or ''}"
    return "h:" + hashlib.sha1(base.encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
# Barrier signals (observable text only)
# ----------------------------------------------------------------------------------------------
LOW_SIGNALS = [
    ("micro-purchase", r"micro[- ]?purchase"),
    ("simplified acquisition", r"simplified acquisition"),
    ("request for quote", r"\brfq\b|request for quot"),
    ("small business set-aside", r"small business set[- ]aside|total small business"),
    ("no cost sharing", r"cost sharing[^.]{0,20}(no|not required)"),
    ("beginner-friendly label", r"good first issue|beginner|starter|easy"),
    ("subcontracting opportunity", r"subcontract"),
    ("remote/virtual delivery", r"\bremote\b|virtual"),
    ("open registration", r"open (vendor )?registration|register (as|to become) a vendor"),
]
HIGH_SIGNALS = [
    ("past performance required", r"past performance"),
    ("bonding requirement", r"\bbond(ing)?\b"),
    ("security clearance", r"security clearance|top secret|\bsecret\b clearance"),
    ("insurance requirement", r"insurance"),
    ("cost sharing / matching funds", r"cost[- ]sharing (is )?required|matching (funds|requirement)|\bmatch\b required"),
    ("restricted to governments/institutions", r"only (state|local|tribal) governments|institutions of higher education only|eligible applicants are (state|county|city)"),
    ("large staffing", r"minimum of \d{2,} (staff|employees|personnel)"),
    ("clinical trial", r"clinical trial"),
    ("in-person delivery", r"on[- ]site|in[- ]person"),
]


def barrier_signals(text: str, value, cost_sharing):
    t = (text or "").lower()
    low, high = [], []
    for name, rx in LOW_SIGNALS:
        if re.search(rx, t):
            low.append(name)
    for name, rx in HIGH_SIGNALS:
        if re.search(rx, t):
            high.append(name)
    if cost_sharing is True and "cost sharing / matching funds" not in high:
        high.append("cost sharing / matching funds")
    if cost_sharing is False and "no cost sharing" not in low:
        low.append("no cost sharing")
    if value is not None:
        if value <= 25_000:
            low.append("small dollar value")
        elif value >= 1_000_000:
            high.append("large dollar value")
    score = 0.5 + 0.12 * len(low) - 0.15 * len(high)
    score = max(0.0, min(1.0, score))
    label = "lower observed barrier" if score >= 0.6 else ("higher observed barrier" if score <= 0.35 else "mixed barrier signals")
    return {"low": low, "high": high, "score": round(score, 2), "label": label}


# ----------------------------------------------------------------------------------------------
# Scoring (transparent, 0-100, labelled inferred)
# ----------------------------------------------------------------------------------------------
WEIGHTS = {"profile_fit": 30, "eligibility_confidence": 20, "barrier": 15, "deadline_feasibility": 10,
           "effort_to_value": 10, "geographic_fit": 5, "competition": 5, "source_freshness": 5}

ENTITY_MAP = {  # profile entity -> words that indicate match in required entity types text
    "nonprofit": ["nonprofit", "non-profit", "501"],
    "llc": ["small business", "for-profit", "for profit", "business"],
    "corporation": ["small business", "for-profit", "for profit", "business"],
    "sole_proprietor": ["small business", "individual", "for-profit", "business"],
    "individual": ["individual", "unrestricted", "others"],
    "startup": ["small business", "for-profit", "business"],
    "creator": ["individual", "small business"],
    "contractor": ["small business", "for-profit", "business"],
    "community_org": ["nonprofit", "community", "others"],
    "university": ["institutions of higher education", "university"],
    "government": ["state governments", "county governments", "city or township", "government"],
}


def tokens(s):
    return {w for w in re.findall(r"[a-z0-9]{3,}", (s or "").lower())}


def score_opportunity(o: dict, profile: dict) -> dict:
    notes = []
    text = " ".join(filter(None, [o.get("title"), o.get("description"), o.get("eligibility_text"),
                                  " ".join(o.get("keywords") or []), " ".join(o.get("industry_codes") or [])]))
    tt = tokens(text)

    # profile fit
    prof_terms = set()
    for k in ("skills", "industries", "keywords", "naics_codes"):
        for v in profile.get(k) or []:
            prof_terms |= tokens(v)
    if not prof_terms:
        fit = 0.4
        notes.append("Profile has no skills/industries/keywords yet - fit defaulted to 0.4")
    else:
        hits = len(prof_terms & tt)
        fit = min(1.0, hits / 4.0)
        if hits:
            notes.append(f"{hits} profile term(s) appear in the source text")
    pref = profile.get("preferred_types") or []
    if pref and o.get("opportunity_type") in pref:
        fit = min(1.0, fit + 0.15)

    # eligibility confidence
    req = " ".join(o.get("required_entity_types") or []).lower()
    et = profile.get("entity_type")
    if not req:
        elig = 0.5
        notes.append("Eligibility not stated by source - Not verified")
    elif not et:
        elig = 0.5
        notes.append("Set your entity type to evaluate eligibility")
    else:
        words = ENTITY_MAP.get(et, [])
        if any(w in req for w in words) or "unrestricted" in req:
            elig = 0.9
            notes.append("Your entity type appears in the stated applicant types")
        else:
            elig = 0.2
            notes.append("Stated applicant types do not appear to include your entity type")
    sa = (o.get("set_aside") or "").lower()
    if sa and sa not in ("none", "n/a"):
        mine = [s.lower() for s in profile.get("set_asides") or []]
        if any(k in sa for k in ("women", "woman")) and "woman" not in mine:
            elig = min(elig, 0.25); notes.append("Set-aside requires woman-owned status not in your profile")
        if "veteran" in sa and not any("veteran" in m or "sdvosb" in m for m in mine):
            elig = min(elig, 0.25); notes.append("Set-aside requires veteran-owned status not in your profile")
        if "8(a)" in sa and "8a" not in mine:
            elig = min(elig, 0.25); notes.append("Set-aside requires 8(a) certification not in your profile")
        if "hubzone" in sa and "hubzone" not in mine:
            elig = min(elig, 0.25); notes.append("Set-aside requires HUBZone certification not in your profile")

    barrier = (o.get("barrier") or {}).get("score", 0.5)

    d = days_until(o.get("deadline"))
    if d is None:
        dl = 0.5; notes.append("No deadline stated - Not verified")
    elif d < 0:
        dl = 0.0; notes.append("Deadline has passed")
    elif d < 3:
        dl = 0.1
    elif d < 14:
        dl = 0.5
    elif d < 45:
        dl = 0.8
    else:
        dl = 1.0

    val = o.get("estimated_value") if o.get("estimated_value") is not None else o.get("funding_amount")
    mn, mx = profile.get("min_value"), profile.get("max_value")
    if val is None:
        e2v = 0.5; notes.append("Value/amount not stated - Not verified")
    elif mn is not None and val < mn:
        e2v = 0.3
    elif mx is not None and val > mx:
        e2v = 0.6
    else:
        e2v = 1.0

    rs = (o.get("remote_status") or "").lower()
    loc = (o.get("location") or "").lower()
    st = (profile.get("state") or "").lower()
    if rs in ("remote", "national", "international"):
        geo = 1.0
    elif st and st in loc:
        geo = 1.0
    elif not loc:
        geo = 0.5
    else:
        geo = 0.2 if not profile.get("willing_travel") else 0.6

    if sa and sa not in ("none", "n/a"):
        comp = 0.8
    elif o.get("opportunity_type") == "technical_bounty":
        comp = 0.5
    elif o.get("opportunity_type") == "grant":
        comp = 0.4
    else:
        comp = 0.5

    try:
        age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(o["retrieved_at"])).total_seconds() / 3600
    except Exception:
        age_h = 999
    fresh = 1.0 if (age_h < 24 and o.get("http_status") == 200) else (0.6 if age_h < 24 * 7 else 0.3)

    comps = {"profile_fit": fit, "eligibility_confidence": elig, "barrier": barrier, "deadline_feasibility": dl,
             "effort_to_value": e2v, "geographic_fit": geo, "competition": comp, "source_freshness": fresh}
    breakdown = {k: {"weight": WEIGHTS[k], "value": round(v, 2), "points": round(WEIGHTS[k] * v, 1)} for k, v in comps.items()}
    total = round(sum(b["points"] for b in breakdown.values()))

    skeptic = ((o.get("ai") or {}).get("skeptic") or {})
    if total >= 75:
        if skeptic.get("verdict") in ("clear", "caution"):
            label = "Strong fit"
        elif skeptic.get("verdict") == "block":
            label = "Needs verification"
        else:
            label = "Possible fit (Skeptic pending)"
    elif total >= 50:
        label = "Needs verification" if elig == 0.5 else "Possible fit"
    else:
        label = "Poor fit"
    return {"total": total, "label": label, "breakdown": breakdown, "notes": notes, "inferred": True,
            "eligibility_confidence": round(elig, 2), "scored_at": now_iso()}


# ----------------------------------------------------------------------------------------------
# Source adapters
# ----------------------------------------------------------------------------------------------
class SourceResult:
    def __init__(self, source, url, access_method):
        self.source, self.url, self.access_method = source, url, access_method
        self.http_status = None
        self.error = None
        self.records: List[dict] = []
        self.started = now_iso()
        self.usage_notes = ""


def profile_keywords(profile: dict, fallback: str) -> str:
    """One focused phrase per run: first keyword, else first skill, else first industry (broad ORs return noise)."""
    for k in ("keywords", "skills", "industries"):
        vals = profile.get(k) or []
        if vals:
            return str(vals[0])
    return fallback


async def adapter_grants_gov(profile: dict, keyword: Optional[str], limit: int) -> SourceResult:
    res = SourceResult("grants_gov", "https://api.grants.gov/v1/api/search2", "official public REST API (no key)")
    res.usage_notes = "Grants.gov public search API; detail via fetchOpportunity. Verify on grants.gov before applying."
    kw = keyword or profile_keywords(profile, "small business technology")
    payload = {"keyword": kw, "oppStatuses": "posted", "rows": min(limit, 50), "sortBy": "openDate|desc"}
    try:
        async with httpx.AsyncClient(timeout=25, headers={"User-Agent": UA}) as cx:
            r = await cx.post(res.url, json=payload)
            res.http_status = r.status_code
            r.raise_for_status()
            hits = (r.json().get("data") or {}).get("oppHits") or []
            sem = asyncio.Semaphore(4)

            async def detail(h):
                async with sem:
                    try:
                        d = await cx.post("https://api.grants.gov/v1/api/fetchOpportunity", json={"opportunityId": int(h["id"])})
                        return h, (d.json().get("data") or {}) if d.status_code == 200 else {}
                    except Exception as e:
                        logger.warning(f"grants detail {h.get('id')} failed: {e}")
                        return h, {}

            pairs = await asyncio.gather(*[detail(h) for h in hits[:limit]])
        retrieved = now_iso()
        for h, d in pairs:
            syn = d.get("synopsis") or {}
            oid = str(h.get("id"))
            src_url = f"https://www.grants.gov/search-results-detail/{oid}"
            desc = strip_html(syn.get("synopsisDesc"))
            elig_text = strip_html(syn.get("applicantEligibilityDesc"))
            app_types = [a.get("description") for a in (syn.get("applicantTypes") or []) if a.get("description")]
            ceiling = syn.get("awardCeiling")
            floor = syn.get("awardFloor")
            amt = None
            if ceiling not in (None, "", "none"):
                try:
                    amt = float(str(ceiling).replace(",", "").replace("$", ""))
                except Exception:
                    amt = None
            deadline = parse_date(syn.get("responseDate") or h.get("closeDate"))
            evidence = [x for x in [
                ev("title", h.get("title"), "search2.oppHits[].title"),
                ev("organization_name", h.get("agency"), "search2.oppHits[].agency"),
                ev("deadline", syn.get("responseDate") or h.get("closeDate"), "synopsis.responseDate | oppHits[].closeDate"),
                ev("funding_amount", f"awardCeiling={ceiling} awardFloor={floor}" if (ceiling or floor) else None, "synopsis.awardCeiling/awardFloor"),
                ev("required_entity_types", "; ".join(app_types) if app_types else None, "synopsis.applicantTypes[].description"),
                ev("eligibility_text", elig_text[:400] if elig_text else None, "synopsis.applicantEligibilityDesc"),
                ev("description", desc[:400] if desc else None, "synopsis.synopsisDesc"),
                ev("cost_sharing", syn.get("costSharing"), "synopsis.costSharing"),
            ] if x]
            contact = {k: v for k, v in {"name": syn.get("agencyContactName"), "email": syn.get("agencyContactEmail"),
                                        "phone": syn.get("agencyContactPhone")}.items() if v}
            res.records.append({
                "source": "grants_gov", "source_id": oid, "source_url": src_url, "submission_url": src_url,
                "title": h.get("title"), "description": desc or None, "opportunity_type": "grant",
                "organization_name": h.get("agency") or syn.get("agencyName"), "organization_type": "federal agency",
                "issuing_department": h.get("agencyCode"), "location": "United States", "remote_status": "national",
                "estimated_value": None, "funding_amount": amt, "funding_floor": floor if floor not in ("", "none") else None,
                "currency": "USD", "posted_date": parse_date(h.get("openDate") or syn.get("postingDate")), "deadline": deadline,
                "eligibility_text": elig_text or None, "required_entity_types": app_types, "required_certifications": [],
                "required_registrations": ["SAM.gov UEI registration (standard for federal grants - verify)", "Grants.gov applicant account (verify)"],
                "required_experience": None, "industry_codes": h.get("cfdaList") or [],
                "keywords": [c.get("description") for c in (syn.get("fundingActivityCategories") or []) if c.get("description")],
                "set_aside": None, "cost_sharing": syn.get("costSharing"), "contact_information": contact or None,
                "attachments": [u for u in (d.get("synopsisDocumentURLs") or []) if isinstance(u, str)][:5],
                "evidence": evidence, "source_reliability": "official government API", "http_status": res.http_status,
                "retrieved_at": retrieved, "raw_status": h.get("oppStatus"),
            })
    except Exception as e:
        res.error = str(e)[:400]
        logger.error(f"grants_gov adapter failed: {e}")
    return res


async def adapter_sam_gov(profile: dict, keyword: Optional[str], limit: int) -> SourceResult:
    res = SourceResult("sam_gov", "https://api.sam.gov/opportunities/v2/search", "official REST API (api.data.gov key)")
    res.usage_notes = "Requires SAM_GOV_API_KEY (free at api.data.gov / sam.gov account). Rate-limited by SAM.gov."
    key = os.environ.get("SAM_GOV_API_KEY")
    if not key:
        res.error = "not_configured: set SAM_GOV_API_KEY in backend/.env (free key from your SAM.gov account -> Account Details -> API key)"
        return res
    today = datetime.now(timezone.utc)
    params = {"api_key": key, "limit": min(limit, 50), "postedFrom": (today - timedelta(days=30)).strftime("%m/%d/%Y"),
              "postedTo": today.strftime("%m/%d/%Y"), "ptype": "o,k,p", "active": "true"}
    kw = keyword or profile_keywords(profile, "")
    if kw:
        params["title"] = kw
    if profile.get("naics_codes"):
        params["ncode"] = profile["naics_codes"][0]
    if profile.get("state") and (profile.get("service_area") in ("local", "state")):
        params["state"] = profile["state"]
    try:
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": UA}) as cx:
            r = await cx.get(res.url, params=params)
            res.http_status = r.status_code
            r.raise_for_status()
            data = r.json().get("opportunitiesData") or []
            retrieved = now_iso()
            for o in data[:limit]:
                nid = o.get("noticeId")
                ui = o.get("uiLink") or f"https://sam.gov/opp/{nid}/view"
                pop = o.get("placeOfPerformance") or {}
                loc = ", ".join(filter(None, [(pop.get("city") or {}).get("name"), (pop.get("state") or {}).get("code")])) or None
                contacts = [{"name": c.get("fullName"), "email": c.get("email"), "phone": c.get("phone"), "type": c.get("type")}
                            for c in (o.get("pointOfContact") or []) if c.get("email") or c.get("fullName")]
                sa = o.get("typeOfSetAsideDescription")
                evidence = [x for x in [
                    ev("title", o.get("title"), "opportunitiesData[].title"),
                    ev("organization_name", o.get("fullParentPathName"), "opportunitiesData[].fullParentPathName"),
                    ev("deadline", o.get("responseDeadLine"), "opportunitiesData[].responseDeadLine"),
                    ev("set_aside", sa, "opportunitiesData[].typeOfSetAsideDescription"),
                    ev("industry_codes", o.get("naicsCode"), "opportunitiesData[].naicsCode"),
                    ev("notice_type", o.get("type"), "opportunitiesData[].type"),
                    ev("location", loc, "opportunitiesData[].placeOfPerformance"),
                ] if x]
                res.records.append({
                    "source": "sam_gov", "source_id": nid, "source_url": ui, "submission_url": ui,
                    "title": o.get("title"), "description": None, "opportunity_type": "contract",
                    "organization_name": o.get("fullParentPathName"), "organization_type": "federal agency",
                    "issuing_department": (o.get("fullParentPathName") or "").split(".")[-1] or None,
                    "location": loc, "remote_status": None, "estimated_value": None, "funding_amount": None, "currency": "USD",
                    "posted_date": parse_date(o.get("postedDate")), "deadline": parse_date(o.get("responseDeadLine")),
                    "eligibility_text": (f"Set-aside: {sa}" if sa else None), "required_entity_types": (["small business"] if sa and "small business" in sa.lower() else []),
                    "required_certifications": [], "required_registrations": ["Active SAM.gov entity registration (UEI) - verify"],
                    "required_experience": None, "industry_codes": [c for c in [o.get("naicsCode"), o.get("classificationCode")] if c],
                    "keywords": [o.get("type")] if o.get("type") else [], "set_aside": sa, "cost_sharing": None,
                    "contact_information": contacts or None, "attachments": [], "notice_type": o.get("type"),
                    "solicitation_number": o.get("solicitationNumber"),
                    "evidence": evidence, "source_reliability": "official government API", "http_status": res.http_status,
                    "retrieved_at": retrieved, "raw_status": "active" if str(o.get("active")).lower() == "yes" else o.get("active"),
                })
    except Exception as e:
        res.error = str(e)[:400]
        logger.error(f"sam_gov adapter failed: {e}")
    return res


async def adapter_github_bounties(profile: dict, keyword: Optional[str], limit: int) -> SourceResult:
    res = SourceResult("github_bounties", "https://api.github.com/search/issues", "official public REST API (optional GITHUB_TOKEN)")
    res.usage_notes = "GitHub issue search for open issues labelled bounty. 10 req/min unauthenticated. Amounts are extracted from issue text and marked as such."
    q = "label:bounty state:open is:issue"
    kw = keyword or " ".join((profile.get("skills") or [])[:2])
    if kw:
        q += f" {kw}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": UA}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    try:
        async with httpx.AsyncClient(timeout=25, headers=headers) as cx:
            r = await cx.get(res.url, params={"q": q, "sort": "created", "order": "desc", "per_page": min(limit, 30)})
            res.http_status = r.status_code
            r.raise_for_status()
            items = r.json().get("items") or []
        retrieved = now_iso()
        for it in items[:limit]:
            body = (it.get("body") or "")[:3000]
            amt, amt_ev = parse_money(it.get("title") or "")
            if amt is None:
                amt, amt_ev = parse_money(body)
            repo = (it.get("repository_url") or "").replace("https://api.github.com/repos/", "")
            labels = [l.get("name") for l in (it.get("labels") or []) if l.get("name")]
            evidence = [x for x in [
                ev("title", it.get("title"), "issue.title"),
                ev("estimated_value", amt_ev, "issue.title/body (regex-extracted $ amount)"),
                ev("labels", ", ".join(labels), "issue.labels[].name"),
                ev("description", strip_html(body)[:400], "issue.body"),
            ] if x]
            res.records.append({
                "source": "github_bounties", "source_id": str(it.get("id")), "source_url": it.get("html_url"), "submission_url": it.get("html_url"),
                "title": it.get("title"), "description": strip_html(body)[:2000] or None, "opportunity_type": "technical_bounty",
                "organization_name": repo.split("/")[0] if repo else None, "organization_type": "open-source project",
                "issuing_department": repo or None, "location": None, "remote_status": "remote",
                "estimated_value": amt, "funding_amount": None, "currency": "USD" if amt else None,
                "posted_date": parse_date(it.get("created_at")), "deadline": None, "eligibility_text": None,
                "required_entity_types": ["individual", "unrestricted"], "required_certifications": [], "required_registrations": ["GitHub account"],
                "required_experience": None, "industry_codes": [], "keywords": labels, "set_aside": None, "cost_sharing": None,
                "contact_information": None, "attachments": [], "evidence": evidence,
                "source_reliability": "official platform API (community-posted bounty; payout terms unverified)",
                "http_status": res.http_status, "retrieved_at": retrieved, "raw_status": it.get("state"),
            })
    except Exception as e:
        res.error = str(e)[:400]
        logger.error(f"github adapter failed: {e}")
    return res


ADAPTERS = {"grants_gov": adapter_grants_gov, "sam_gov": adapter_sam_gov, "github_bounties": adapter_github_bounties}
SOURCE_META = {
    "grants_gov": {"name": "Grants.gov", "type": "federal grants", "needs_key": False},
    "sam_gov": {"name": "SAM.gov Contract Opportunities", "type": "federal contracts", "needs_key": True, "env": "SAM_GOV_API_KEY"},
    "github_bounties": {"name": "GitHub bounty issues", "type": "technical bounties", "needs_key": False, "env": "GITHUB_TOKEN (optional)"},
}


@router.get("/sources")
async def list_sources():
    out = []
    for k, meta in SOURCE_META.items():
        last = await db.radar_source_runs.find_one({"source": k}, {"_id": 0}, sort=[("retrieved_at", -1)])
        configured = True
        if meta.get("needs_key"):
            configured = bool(os.environ.get(meta["env"]))
        count = await db.radar_opportunities.count_documents({"source": k, "status": {"$ne": "closed"}})
        out.append({"id": k, **meta, "configured": configured, "last_run": last, "active_count": count})
    return out


# ----------------------------------------------------------------------------------------------
# Pipeline: validate -> dedupe -> barrier -> score -> persist -> stale marking
# ----------------------------------------------------------------------------------------------
def validate(rec: dict) -> Optional[str]:
    if not rec.get("title"):
        return "missing title"
    if not rec.get("source_url") or not str(rec["source_url"]).startswith("http"):
        return "missing source_url"
    if not rec.get("retrieved_at"):
        return "missing retrieved_at"
    return None


class DiscoverRequest(BaseModel):
    sources: Optional[List[str]] = None
    keyword: Optional[str] = None
    limit: int = 20


@router.post("/discover")
async def discover(req: DiscoverRequest):
    profile = await get_profile()
    names = [s for s in (req.sources or list(ADAPTERS)) if s in ADAPTERS]
    if not names:
        raise HTTPException(400, "no valid sources")
    limit = max(1, min(req.limit, 50))
    results: List[SourceResult] = await asyncio.gather(*[ADAPTERS[n](profile, req.keyword, limit) for n in names])
    summary = []
    for res in results:
        fetched = len(res.records)
        new = updated = invalid = dup = 0
        for rec in res.records:
            err = validate(rec)
            if err:
                invalid += 1
                continue
            key = dedupe_key(rec["source"], rec.get("source_id"), rec.get("title"), rec.get("organization_name"), rec.get("deadline"))
            rec["dedupe_key"] = key
            rec["parser_version"] = PARSER_VERSION
            rec["last_verified_at"] = rec["retrieved_at"]
            text_blob = " ".join(filter(None, [rec.get("title"), rec.get("description"), rec.get("eligibility_text"), rec.get("set_aside")]))
            rec["barrier"] = barrier_signals(text_blob, rec.get("estimated_value") or rec.get("funding_amount"), rec.get("cost_sharing"))
            d = days_until(rec.get("deadline"))
            rec["status"] = "closed" if (d is not None and d < 0) else "open"
            existing = await db.radar_opportunities.find_one({"$or": [{"dedupe_key": key}, {"source_url": rec["source_url"]}]}, {"_id": 0})
            if existing:
                # cross-source near-duplicate check by title+org
                merged = {**existing, **{k: v for k, v in rec.items() if v not in (None, [], "")}}
                merged["score"] = score_opportunity(merged, profile)
                merged["updated_at"] = now_iso()
                await db.radar_opportunities.update_one({"id": existing["id"]}, {"$set": merged})
                updated += 1
            else:
                near = await db.radar_opportunities.find_one({"title": rec["title"], "organization_name": rec.get("organization_name"),
                                                             "deadline": rec.get("deadline")}, {"_id": 0, "id": 1})
                if near:
                    dup += 1
                    await db.radar_opportunities.update_one({"id": near["id"]}, {"$addToSet": {"also_seen_at": rec["source_url"]}})
                    continue
                rec["id"] = str(uuid.uuid4())
                rec["user_status"] = "new"
                rec["stage"] = "Discovered"
                rec["notes"] = ""
                rec["ai"] = {}
                rec["drafts"] = {}
                rec["created_at"] = now_iso()
                rec["updated_at"] = rec["created_at"]
                rec["is_demo"] = False
                rec["score"] = score_opportunity(rec, profile)
                await db.radar_opportunities.insert_one(dict(rec))
                new += 1
        run = {"id": str(uuid.uuid4()), "source": res.source, "source_url": res.url, "access_method": res.access_method,
               "retrieved_at": res.started, "finished_at": now_iso(), "http_status": res.http_status, "parser_version": PARSER_VERSION,
               "error": res.error, "usage_notes": res.usage_notes, "fetched": fetched, "new": new, "updated": updated,
               "invalid": invalid, "near_duplicates": dup, "keyword": req.keyword}
        await db.radar_source_runs.insert_one(dict(run))
        run.pop("_id", None)
        summary.append(run)
    # stale marking: not re-seen for 7 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    await db.radar_opportunities.update_many({"last_verified_at": {"$lt": cutoff}, "status": "open"}, {"$set": {"status": "stale"}})
    return {"runs": summary, "total_active": await db.radar_opportunities.count_documents({"status": {"$ne": "closed"}})}


@router.get("/runs")
async def runs(limit: int = Query(30, ge=1, le=200)):
    return await db.radar_source_runs.find({}, {"_id": 0}).sort("retrieved_at", -1).to_list(limit)


# ----------------------------------------------------------------------------------------------
# Feed, detail, actions
# ----------------------------------------------------------------------------------------------
@router.get("/opportunities")
async def list_opportunities(
    type: Optional[str] = None, source: Optional[str] = None, status: Optional[str] = None,
    user_status: Optional[str] = None, min_score: Optional[int] = None, closing_days: Optional[int] = None,
    low_barrier: Optional[bool] = None, remote: Optional[bool] = None, max_value: Optional[float] = None,
    q: Optional[str] = None, saved: Optional[bool] = None, include_dismissed: bool = False,
    sort: str = "score", limit: int = Query(100, ge=1, le=300),
):
    f = {"is_demo": {"$ne": True}}
    if type:
        f["opportunity_type"] = type
    if source:
        f["source"] = source
    if status:
        f["status"] = status
    else:
        f["status"] = {"$ne": "closed"}
    if user_status:
        f["user_status"] = user_status
    elif saved:
        f["user_status"] = {"$in": ["saved", "contacted", "submitted"]}
    elif not include_dismissed:
        f["user_status"] = {"$ne": "dismissed"}
    if min_score is not None:
        f["score.total"] = {"$gte": min_score}
    if low_barrier:
        f["barrier.label"] = "lower observed barrier"
    if remote:
        f["remote_status"] = {"$in": ["remote", "national", "international"]}
    if max_value is not None:
        f["$or"] = [{"estimated_value": {"$lte": max_value}}, {"funding_amount": {"$lte": max_value}},
                    {"estimated_value": None, "funding_amount": None}]
    if closing_days is not None:
        f["deadline"] = {"$lte": (datetime.now(timezone.utc) + timedelta(days=closing_days)).isoformat(), "$ne": None}
    if q:
        rx = {"$regex": re.escape(q), "$options": "i"}
        f["$and"] = [{"$or": [{"title": rx}, {"description": rx}, {"organization_name": rx}, {"eligibility_text": rx}]}]
    docs = await db.radar_opportunities.find(f, {"_id": 0, "description": 0, "drafts": 0}).to_list(2000)
    if sort == "deadline":
        docs.sort(key=lambda d: d.get("deadline") or "9999")
    elif sort == "new":
        docs.sort(key=lambda d: d.get("created_at") or "", reverse=True)
    else:
        docs.sort(key=lambda d: (d.get("score") or {}).get("total", 0), reverse=True)
    docs = docs[:limit]
    for d in docs:
        d["days_remaining"] = days_until(d.get("deadline"))
    return docs


@router.get("/opportunities/{oid}")
async def get_opportunity(oid: str):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    d["days_remaining"] = days_until(d.get("deadline"))
    sim = await db.radar_opportunities.find(
        {"id": {"$ne": oid}, "opportunity_type": d.get("opportunity_type"), "status": {"$ne": "closed"}},
        {"_id": 0, "id": 1, "title": 1, "organization_name": 1, "score": 1, "deadline": 1}).sort("score.total", -1).to_list(5)
    d["similar"] = sim
    return d


STAGES = ["Discovered", "Reviewed", "Qualified", "Preparing", "Submitted", "Awarded", "Not Awarded"]


class PatchOpportunity(BaseModel):
    user_status: Optional[str] = None  # new | saved | dismissed | contacted | submitted
    stage: Optional[str] = None
    notes: Optional[str] = None


@router.patch("/opportunities/{oid}")
async def patch_opportunity(oid: str, p: PatchOpportunity):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0, "id": 1, "user_status": 1, "stage": 1})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    upd = {"updated_at": now_iso()}
    if p.user_status is not None:
        if p.user_status not in ("new", "saved", "dismissed", "contacted", "submitted"):
            raise HTTPException(400, "invalid user_status")
        upd["user_status"] = p.user_status
        if p.user_status == "submitted":
            upd["stage"] = "Submitted"
        elif p.user_status == "contacted" and d.get("stage") in ("Discovered", "Reviewed"):
            upd["stage"] = "Qualified"
        elif p.user_status == "saved" and d.get("stage") == "Discovered":
            upd["stage"] = "Reviewed"
    if p.stage is not None:
        if p.stage not in STAGES:
            raise HTTPException(400, "invalid stage")
        upd["stage"] = p.stage
    if p.notes is not None:
        upd["notes"] = p.notes[:5000]
    await db.radar_opportunities.update_one({"id": oid}, {"$set": upd, "$push": {"audit": {"at": upd["updated_at"], "change": {k: v for k, v in upd.items() if k != "updated_at"}}}})
    return await get_opportunity(oid)


@router.post("/opportunities/{oid}/to-mission")
async def opportunity_to_mission(oid: str):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    if d.get("mission_id"):
        m = await db.missions.find_one({"id": d["mission_id"]}, {"_id": 0})
        if m:
            return m
    val = d.get("funding_amount") or d.get("estimated_value")
    text = (f"Pursue this verified public opportunity (do NOT auto-submit; owner reviews and submits manually):\n"
            f"Title: {d.get('title')}\nType: {d.get('opportunity_type')}\nIssuer: {d.get('organization_name') or 'Not verified'}\n"
            f"Deadline: {d.get('deadline') or 'Not verified'}\nStated amount: {val if val is not None else 'Not verified'}\n"
            f"Eligibility (source text): {(d.get('eligibility_text') or 'Not stated')[:600]}\n"
            f"Required registrations: {', '.join(d.get('required_registrations') or []) or 'Not stated'}\n"
            f"Source: {d.get('source_url')}\n"
            f"Steps must include: verify on original source, confirm eligibility, gather required registrations/documents, "
            f"prepare submission, submit manually before deadline, log outcome.")
    mission = await compile_mission_from_text(text, "Collect" if d.get("opportunity_type") in ("grant", "funding") else "Move",
                                              source_opportunity_id=oid)
    await db.radar_opportunities.update_one({"id": oid}, {"$set": {"mission_id": mission.id, "mission_title": mission.title,
                                                                    "stage": "Preparing", "updated_at": now_iso()}})
    return mission


# ----------------------------------------------------------------------------------------------
# Natural-language search -> proposed structured filters (never applied silently)
# ----------------------------------------------------------------------------------------------
class NLSearch(BaseModel):
    query: str


@router.post("/search/nl")
async def nl_search(req: NLSearch):
    if not req.query.strip():
        raise HTTPException(400, "query required")
    system = ("You translate a natural-language opportunity search into a JSON filter object. Allowed keys ONLY: "
              "type (one of grant, contract, subcontract, procurement, sponsorship, rfp, funding, technical_bounty), "
              "source (grants_gov|sam_gov|github_bounties), min_score (int), closing_days (int), low_barrier (bool), "
              "remote (bool), max_value (number), q (short keyword string), exclusions (list of short strings the user "
              "wants to avoid, e.g. 'five years past performance'). Omit keys you cannot infer. Never add criteria the "
              "user did not state. Respond ONLY with minified JSON.")
    try:
        raw, _, label = await llm_call_failover(system, req.query, ["openai", "gemini", "anthropic"])
        filters = extract_json(raw)
    except Exception as e:
        raise HTTPException(502, f"could not parse query: {e}")
    allowed = {"type", "source", "min_score", "closing_days", "low_barrier", "remote", "max_value", "q", "exclusions"}
    filters = {k: v for k, v in (filters or {}).items() if k in allowed}
    return {"query": req.query, "proposed_filters": filters, "model": label,
            "note": "Review these filters before applying - the AI proposal is not applied automatically."}


# ----------------------------------------------------------------------------------------------
# AI personas on demand: Fit Analyst + Skeptic (+ checklist & questions)
# ----------------------------------------------------------------------------------------------
def source_pack(d: dict) -> str:
    fields = ["title", "opportunity_type", "organization_name", "location", "remote_status", "estimated_value", "funding_amount",
              "deadline", "eligibility_text", "required_entity_types", "required_certifications", "required_registrations",
              "set_aside", "cost_sharing", "industry_codes", "keywords", "notice_type", "source_url", "retrieved_at"]
    lines = [f"{k}: {d.get(k) if d.get(k) not in (None, [], '') else 'NOT STATED BY SOURCE'}" for k in fields]
    desc = (d.get("description") or "NOT STATED BY SOURCE")[:2500]
    evs = "\n".join([f"- [{e['field']}] \"{e['excerpt'][:200]}\" ({e['source_location']})" for e in d.get("evidence") or []])
    return "SOURCE FIELDS:\n" + "\n".join(lines) + f"\n\nSOURCE DESCRIPTION:\n{desc}\n\nEVIDENCE EXCERPTS:\n{evs}"


def profile_pack(p: dict) -> str:
    keys = ["entity_type", "org_name", "country", "state", "city", "service_area", "industries", "naics_codes", "skills", "keywords",
            "years_experience", "revenue_range", "team_size", "certifications", "set_asides", "nonprofit_status", "budget",
            "hours_per_week", "min_value", "max_value", "willing_travel", "willing_subcontract", "preferred_types", "bio"]
    return "OWNER PROFILE (the ONLY permitted source of claims about the owner):\n" + "\n".join(
        [f"{k}: {p.get(k) if p.get(k) not in (None, [], '') else 'NOT PROVIDED'}" for k in keys])


INTEGRITY = ("INTEGRITY RULES: Use only the SOURCE FIELDS/DESCRIPTION/EVIDENCE and the OWNER PROFILE. Never invent amounts, "
             "deadlines, agencies, eligibility rules, or facts about the owner. If something is not stated, say 'Not stated by source' "
             "or 'Not in profile'. Never claim the owner is legally eligible or will win; distinguish 'appears to match stated "
             "requirements' from 'legally eligible' from 'likely to win'. Respond ONLY with minified JSON.")


class AnalyzeRequest(BaseModel):
    include_checklist: bool = True


@router.post("/opportunities/{oid}/analyze")
async def analyze(oid: str, req: AnalyzeRequest = None):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    profile = await get_profile()
    sp, pp = source_pack(d), profile_pack(profile)
    include_ck = req.include_checklist if req else True

    fit_sys = ("You are the FIT ANALYST persona of ACASO Opportunity Radar. Compare the owner profile to the opportunity. " + INTEGRITY +
               " JSON keys: summary (2 sentences), why_it_may_fit (list), why_it_may_not_fit (list), appears_to_match_stated_requirements "
               "(true|false|unknown), missing_information (list), effort_estimate (string labelled 'uncertain estimate'), "
               "recommended_next_action (one sentence).")
    skeptic_sys = ("You are the SKEPTIC persona of ACASO Opportunity Radar. Your job is to find what is missing, stale, suspicious or "
                   "unrealistic before the owner relies on this opportunity. " + INTEGRITY +
                   " JSON keys: verdict (clear|caution|block), concerns (list), missing_requirements (list), stale_or_suspicious (list), "
                   "unrealistic_assumptions (list), verify_at_source (list of exact things to verify on the original page).")
    ck_sys = ("You are the COMPLIANCE SENTINEL + PROPOSAL ARCHITECT personas of ACASO Opportunity Radar. " + INTEGRITY +
              " JSON keys: preparation_checklist (list of {item, why, stated_by_source: true|false}), "
              "questions_for_contracting_officer_or_funder (list of strings), proposal_outline (list of section titles with one-line guidance; no fabricated claims).")

    body = f"{sp}\n\n{pp}"
    tasks = [llm_call_failover(fit_sys, body, ["openai", "gemini", "anthropic"]),
             llm_call_failover(skeptic_sys, body, ["anthropic", "openai", "gemini"])]
    if include_ck:
        tasks.append(llm_call_failover(ck_sys, body, ["gemini", "openai", "anthropic"]))
    outs = await asyncio.gather(*tasks, return_exceptions=True)

    def parse(o, name):
        if isinstance(o, Exception):
            return {"error": str(o)[:200], "persona": name}
        raw, _, label = o
        try:
            j = extract_json(raw)
        except Exception:
            j = {"raw": raw[:1500]}
        j["model_label"] = label
        j["generated_at"] = now_iso()
        j["inferred"] = True
        return j

    ai = dict(d.get("ai") or {})
    ai["fit"] = parse(outs[0], "fit_analyst")
    ai["skeptic"] = parse(outs[1], "skeptic")
    if include_ck:
        ai["checklist"] = parse(outs[2], "compliance_sentinel")
    d["ai"] = ai
    d["score"] = score_opportunity(d, profile)
    if d.get("stage") == "Discovered":
        d["stage"] = "Reviewed"
    await db.radar_opportunities.update_one({"id": oid}, {"$set": {"ai": ai, "score": d["score"], "stage": d["stage"], "updated_at": now_iso()}})
    return {"ai": ai, "score": d["score"], "stage": d["stage"]}


# ----------------------------------------------------------------------------------------------
# Drafting desk: email / grant narrative / outreach packet / fill-a-form
# ----------------------------------------------------------------------------------------------
DRAFT_KINDS = {
    "email": ("Write a concise, specific introductory email (subject line + body under 180 words) from the owner to the issuing "
              "organization's contact about this opportunity. Ask 1-2 clarifying questions that the source leaves unanswered."),
    "grant_narrative": ("Write a grant proposal narrative draft with these sections: Statement of Need, Project Description, "
                        "Goals & Measurable Objectives, Organizational Capacity, Timeline, Budget Narrative, Evaluation, Sustainability. "
                        "Ground every capacity/experience statement in the owner profile verbatim; anywhere a fact is missing, insert a "
                        "bracketed placeholder like [FILL: past project example] rather than inventing it."),
    "outreach_packet": ("Produce a full outreach packet: (1) one-paragraph capability statement, (2) cold email, (3) LinkedIn/DM version "
                        "under 80 words, (4) follow-up message for day 3, (5) call script opening 60 seconds, (6) list of documents to attach "
                        "based on stated requirements. Use only profile facts; use [FILL: ...] placeholders for anything missing."),
    "form_answers": ("The owner pasted application/form questions. Answer each question using ONLY the owner profile and the opportunity's "
                     "source text. For any answer requiring information not in the profile, write [FILL: what is needed] instead of guessing. "
                     "Output as numbered Q/A pairs."),
}


class DraftRequest(BaseModel):
    kind: str
    form_text: Optional[str] = None
    tone: Optional[str] = "professional, direct, human"
    extra_instructions: Optional[str] = None


@router.post("/opportunities/{oid}/draft")
async def draft(oid: str, req: DraftRequest):
    if req.kind not in DRAFT_KINDS:
        raise HTTPException(400, f"kind must be one of {list(DRAFT_KINDS)}")
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    if req.kind == "form_answers" and not (req.form_text or "").strip():
        raise HTTPException(400, "form_text is required for form_answers")
    profile = await get_profile()
    system = ("You are the PROPOSAL ARCHITECT persona of ACASO Opportunity Radar, drafting on behalf of the owner. "
              "HARD RULES: Never fabricate experience, revenue, credentials, certifications, past performance, partners, or metrics. "
              "The ONLY permitted facts about the owner are in the OWNER PROFILE; the ONLY permitted facts about the opportunity are in "
              "the SOURCE FIELDS/DESCRIPTION/EVIDENCE. Anything else must be a bracketed placeholder [FILL: ...]. Do not claim eligibility "
              "or that funding is likely. The owner will review and submit manually; never state that anything has been submitted. "
              f"Tone: {req.tone}. Output Markdown. End with a short 'Before sending' checklist of every [FILL] placeholder and every "
              "claim the owner must verify.")
    prompt = f"{source_pack(d)}\n\n{profile_pack(profile)}\n\nTASK: {DRAFT_KINDS[req.kind]}"
    if req.form_text:
        prompt += f"\n\nFORM QUESTIONS:\n{req.form_text[:6000]}"
    if req.extra_instructions:
        prompt += f"\n\nOWNER INSTRUCTIONS: {req.extra_instructions[:1000]}"
    try:
        text, _, label = await llm_call_failover(system, prompt, ["openai", "anthropic", "gemini"])
    except Exception as e:
        raise HTTPException(502, f"draft failed: {e}")
    fills = re.findall(r"\[FILL:[^\]]*\]", text)
    item = {"kind": req.kind, "content": text.strip(), "model_label": label, "generated_at": now_iso(),
            "placeholders": len(fills), "form_text": (req.form_text or None)}
    drafts = dict(d.get("drafts") or {})
    drafts[req.kind] = item
    upd = {"drafts": drafts, "updated_at": now_iso()}
    if d.get("stage") in ("Discovered", "Reviewed", "Qualified"):
        upd["stage"] = "Preparing"
    await db.radar_opportunities.update_one({"id": oid}, {"$set": upd})
    return item


@router.get("/opportunities/{oid}/drafts")
async def get_drafts(oid: str):
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0, "drafts": 1})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    return d.get("drafts") or {}


@router.get("/opportunities/{oid}/export")
async def export_opportunity(oid: str):
    from fastapi.responses import Response
    d = await db.radar_opportunities.find_one({"id": oid}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Opportunity not found")
    sc = d.get("score") or {}
    lines = [f"# {d.get('title')}", "",
             f"> VERIFY BEFORE ACTING: confirm every field on the original source: {d.get('source_url')}",
             f"> Retrieved {d.get('retrieved_at')} | parser {d.get('parser_version')} | HTTP {d.get('http_status')} | status {d.get('status')}", "",
             "## Facts from source",
             f"- Type: {d.get('opportunity_type')}", f"- Issuer: {d.get('organization_name') or 'Not verified'}",
             f"- Deadline: {d.get('deadline') or 'Not verified'}",
             f"- Amount: {d.get('funding_amount') if d.get('funding_amount') is not None else (d.get('estimated_value') if d.get('estimated_value') is not None else 'Not verified')}",
             f"- Eligibility text: {d.get('eligibility_text') or 'Not stated by source'}",
             f"- Required registrations: {', '.join(d.get('required_registrations') or []) or 'Not stated'}", "",
             f"## Inferred score: {sc.get('total')} / 100 - {sc.get('label')}"]
    for k, b in (sc.get("breakdown") or {}).items():
        lines.append(f"- {k}: {b['points']} / {b['weight']}")
    lines += ["", "## Evidence excerpts"] + [f"- [{e['field']}] \"{e['excerpt']}\" - {e['source_location']}" for e in d.get("evidence") or []]
    ai = d.get("ai") or {}
    for k in ("fit", "skeptic", "checklist"):
        if ai.get(k):
            lines += ["", f"## AI {k} (inferred, {ai[k].get('model_label','')})", "```json", json.dumps({x: y for x, y in ai[k].items() if x not in ('model_label',)}, indent=1)[:6000], "```"]
    for k, v in (d.get("drafts") or {}).items():
        lines += ["", f"## Draft: {k} ({v.get('placeholders')} placeholders to fill)", v.get("content", "")]
    if d.get("notes"):
        lines += ["", "## Notes", d["notes"]]
    md = "\n".join(lines)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", (d.get("title") or "opportunity"))[:50]
    return Response(content=md, media_type="text/markdown", headers={"Content-Disposition": f'attachment; filename="radar-{safe}.md"'})
