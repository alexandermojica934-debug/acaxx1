"""
ACASO Apex Nexus - zero-capital digital products with an order -> pay -> unlock flow.

Products (Oracle Cortex vectors chosen by the owner):
  #6  rfp_kit         - proposal response kit for a real RFP/grant (from Radar or pasted text)
  #2  prompt_library  - packaged domain prompt library (Markdown + JSON, gated API endpoint)
  #10 seo_pack        - programmatic local landing-page copy pack for high-intent B2B terms

Integrity:
  * Generators use only the owner's Radar profile (capability facts) + the inputs the owner typed + the opportunity's
    stored source text. Unknown facts become [FILL: ...] placeholders. Nothing is auto-submitted anywhere.
  * Payment: Stripe Checkout when STRIPE_API_KEY is configured (wired separately with the owner's keys via the
    integration playbook). Until then, orders are unlocked manually by the owner ("Mark paid"). The UI shows which.
"""
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Callable, Awaitable

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

logger = logging.getLogger("apex")
router = APIRouter(prefix="/apex")

db = None
llm_call_failover: Optional[Callable[..., Awaitable]] = None
extract_json: Optional[Callable] = None


def init(_db, _llm_failover, _extract_json):
    global db, llm_call_failover, extract_json
    db, llm_call_failover, extract_json = _db, _llm_failover, _extract_json


def now_iso():
    return datetime.now(timezone.utc).isoformat()


PRODUCTS = {
    "rfp_kit": {
        "id": "rfp_kit", "vector": 6, "name": "RFP Response Kit", "price_usd": 149,
        "tagline": "A complete first-draft proposal package for a specific public RFP or grant - cover letter, executive summary, approach, compliance matrix, pricing skeleton, submission checklist.",
        "buyer": "Small contractors and nonprofits chasing a specific solicitation",
        "inputs": ["opportunity_id (from Radar) OR rfp_text", "bidder_name", "bidder_capabilities", "differentiators", "price_basis"],
        "deliverable": "Markdown kit + compliance matrix JSON",
    },
    "prompt_library": {
        "id": "prompt_library", "vector": 2, "name": "Prompt Library", "price_usd": 49,
        "tagline": "A curated, tested-format library of domain prompts with variables and examples, delivered as Markdown + JSON and a gated API endpoint.",
        "buyer": "Teams standardising AI use in one domain (legal intake, logistics ops, real-estate marketing...)",
        "inputs": ["domain", "audience", "use_cases", "count (10-30)", "tone"],
        "deliverable": "Markdown + JSON + API access key",
    },
    "seo_pack": {
        "id": "seo_pack", "vector": 10, "name": "Local SEO Content Pack", "price_usd": 199,
        "tagline": "Landing-page copy for zero-volume, high-intent local B2B terms: title, meta, H1, sections, FAQ, CTA and LocalBusiness schema per page.",
        "buyer": "Local B2B service businesses and agencies",
        "inputs": ["business", "service", "city_region", "terms (or let ACASO propose)", "count (5-15)", "proof_points"],
        "deliverable": "Markdown pages + JSON + JSON-LD",
    },
}

INTEGRITY = ("INTEGRITY: Use only the facts provided (owner profile, inputs, source text). Never invent past performance, "
             "clients, revenue, certifications, metrics, addresses or phone numbers - write [FILL: what is needed] instead. "
             "No guarantees of award, ranking or results.")


class GenerateRequest(BaseModel):
    product: str
    inputs: dict = {}


class OrderCreate(BaseModel):
    product: str
    buyer_email: str
    buyer_name: Optional[str] = None
    deliverable_id: Optional[str] = None
    price_usd: Optional[float] = None
    note: Optional[str] = None


class OrderPatch(BaseModel):
    status: Optional[str] = None  # pending_payment | paid | refunded | cancelled
    deliverable_id: Optional[str] = None
    note: Optional[str] = None


async def _profile_text() -> str:
    p = await db.radar_profile.find_one({"id": "owner"}, {"_id": 0}) or {}
    keys = ["org_name", "entity_type", "city", "state", "industries", "skills", "certifications", "years_experience", "team_size", "bio"]
    return "OWNER PROFILE (only permitted source of claims about the seller/bidder):\n" + "\n".join(
        [f"{k}: {p.get(k) if p.get(k) not in (None, [], '') else 'NOT PROVIDED'}" for k in keys])


# ----------------------------------------------------------------------------------------------
@router.get("/products")
async def products():
    stripe = bool(os.environ.get("STRIPE_API_KEY"))
    out = []
    for p in PRODUCTS.values():
        n_del = await db.apex_deliverables.count_documents({"product": p["id"]})
        n_ord = await db.apex_orders.count_documents({"product": p["id"]})
        paid = await db.apex_orders.count_documents({"product": p["id"], "status": "paid"})
        out.append({**p, "deliverables": n_del, "orders": n_ord, "paid_orders": paid})
    return {"products": out, "payments": {"provider": "stripe" if stripe else "manual",
                                          "stripe_configured": stripe,
                                          "note": ("Stripe Checkout active." if stripe else
                                                   "Stripe not connected: set STRIPE_API_KEY (and the webhook secret) in backend/.env to enable "
                                                   "checkout links. Until then, mark orders paid manually after you receive payment.")}}


# ---- generators ----
async def gen_rfp_kit(inp: dict) -> dict:
    opp_text = ""
    opp = None
    if inp.get("opportunity_id"):
        opp = await db.radar_opportunities.find_one({"id": inp["opportunity_id"]}, {"_id": 0})
        if not opp:
            raise HTTPException(404, "Radar opportunity not found")
        opp_text = (f"TITLE: {opp.get('title')}\nISSUER: {opp.get('organization_name')}\nTYPE: {opp.get('opportunity_type')}\n"
                    f"DEADLINE: {opp.get('deadline') or 'Not stated'}\nAMOUNT: {opp.get('funding_amount') or opp.get('estimated_value') or 'Not stated'}\n"
                    f"SET-ASIDE: {opp.get('set_aside') or 'none stated'}\nELIGIBILITY: {opp.get('eligibility_text') or 'Not stated'}\n"
                    f"REQUIRED REGISTRATIONS: {opp.get('required_registrations')}\nSOURCE: {opp.get('source_url')}\n"
                    f"DESCRIPTION:\n{(opp.get('description') or 'Not provided - see source')[:5000]}")
    elif inp.get("rfp_text"):
        opp_text = inp["rfp_text"][:12000]
    else:
        raise HTTPException(400, "Provide opportunity_id (from Radar) or rfp_text")
    system = ("You are ACASO's Proposal Architect producing a sellable RFP RESPONSE KIT in Markdown. " + INTEGRITY +
              " Sections, in order: # Cover Letter; # Executive Summary; # Understanding of the Requirement; # Technical / Service Approach; "
              "# Management & Staffing Plan; # Past Performance (profile facts only, else [FILL]); # Compliance Matrix (a Markdown table: "
              "Requirement | Where addressed | Status); # Pricing Skeleton (table with line items and [FILL: price] cells, plus assumptions); "
              "# Questions to Ask the Contracting Officer / Funder; # Submission Checklist (registrations, forms, formats, deadline); "
              "# Before Sending (every [FILL] and every claim to verify). After the Markdown, on its own line write ===JSON=== then a minified "
              "JSON object {\"compliance_matrix\": [{\"requirement\":..., \"addressed_in\":..., \"status\": \"draft|fill|n/a\"}], \"placeholders\": int, "
              "\"deadline\": string|null, \"issuer\": string|null}.")
    prompt = (f"SOLICITATION / OPPORTUNITY (source text):\n{opp_text}\n\n{await _profile_text()}\n\n"
              f"BIDDER NAME: {inp.get('bidder_name') or 'from profile'}\nBIDDER CAPABILITIES (owner-stated): {inp.get('bidder_capabilities') or 'from profile'}\n"
              f"DIFFERENTIATORS (owner-stated): {inp.get('differentiators') or 'NOT PROVIDED'}\nPRICE BASIS: {inp.get('price_basis') or 'NOT PROVIDED - use [FILL]'}\n\n"
              "Produce the kit.")
    text, _, label = await llm_call_failover(system, prompt, ["openai", "anthropic", "gemini"])
    md, data = _split_json(text)
    title = f"RFP Kit - {(opp or {}).get('title') or (inp.get('rfp_text') or '')[:60].strip()}"
    return {"title": title, "markdown": md, "data": data, "model_label": label, "source_url": (opp or {}).get("source_url")}


async def gen_prompt_library(inp: dict) -> dict:
    domain = (inp.get("domain") or "").strip()
    if not domain:
        raise HTTPException(400, "domain is required")
    count = max(10, min(int(inp.get("count") or 15), 30))
    system = ("You are ACASO's Prompt Engineer producing a sellable PROMPT LIBRARY. Every prompt must be concrete, reusable, and use "
              "{{double_curly_variables}} for every part the buyer changes (names, dates, amounts, addresses) - these are TEMPLATE VARIABLES, "
              "not missing facts, so do NOT write [FILL] inside prompts. Reserve [FILL: ...] only for claims about the seller. " + INTEGRITY +
              " Output Markdown: # <Library name>; ## How to use; then one ### section per prompt with: **Use case**, **Prompt** (code block), "
              "**Variables**, **Example input**, **Tips**. After the Markdown write ===JSON=== then minified JSON "
              "{\"name\":..., \"domain\":..., \"prompts\":[{\"id\":\"p01\",\"title\":...,\"use_case\":...,\"prompt\":...,\"variables\":[...],\"example_input\":...,\"tips\":...}]}.")
    prompt = (f"DOMAIN: {domain}\nAUDIENCE: {inp.get('audience') or 'practitioners in this domain'}\nUSE CASES TO COVER: {inp.get('use_cases') or 'the most valuable everyday tasks'}\n"
              f"TONE: {inp.get('tone') or 'professional'}\nCOUNT: exactly {count} prompts, no filler.")
    text, _, label = await llm_call_failover(system, prompt, ["openai", "gemini", "anthropic"])
    md, data = _split_json(text)
    return {"title": f"Prompt Library - {domain}", "markdown": md, "data": data, "model_label": label, "count": len((data or {}).get("prompts") or [])}


async def gen_seo_pack(inp: dict) -> dict:
    business = (inp.get("business") or "").strip()
    service = (inp.get("service") or "").strip()
    region = (inp.get("city_region") or "").strip()
    if not (business and service and region):
        raise HTTPException(400, "business, service and city_region are required")
    count = max(5, min(int(inp.get("count") or 8), 15))
    terms = inp.get("terms")
    system = ("You are ACASO's Programmatic SEO writer producing a sellable LOCAL SEO CONTENT PACK: one landing page per zero-volume, "
              "high-intent B2B search term. " + INTEGRITY + " Never invent reviews, ratings, addresses, phone numbers or client names; "
              "use [FILL: ...]. Output Markdown: # Pack overview (terms + intent); then per page: ## <Term> with **Slug**, **Title tag** (<=60 chars), "
              "**Meta description** (<=155 chars), **H1**, 3-4 H2 sections with 60-120 words each, **FAQ** (3 Q/A), **CTA**. "
              "After the Markdown write ===JSON=== then minified JSON {\"pages\":[{\"term\":...,\"slug\":...,\"title\":...,\"meta\":...,\"h1\":...,"
              "\"sections\":[{\"h2\":...,\"copy\":...}],\"faq\":[{\"q\":...,\"a\":...}],\"cta\":...,\"jsonld\":{\"@context\":\"https://schema.org\",\"@type\":\"LocalBusiness\",\"name\":...,\"areaServed\":...,\"description\":...}}]}.")
    prompt = (f"BUSINESS: {business}\nSERVICE: {service}\nCITY/REGION: {region}\nPROOF POINTS (owner-stated, use verbatim or [FILL]): {inp.get('proof_points') or 'NOT PROVIDED'}\n"
              + (f"TERMS (use these): {terms}\n" if terms else f"TERMS: propose {count} zero-volume, high-intent local B2B terms (e.g. '<service> for <niche> in <city>', 'emergency <service> <city> commercial').\n")
              + f"COUNT: {count} pages.\n{await _profile_text()}")
    text, _, label = await llm_call_failover(system, prompt, ["openai", "gemini", "anthropic"])
    md, data = _split_json(text)
    return {"title": f"SEO Pack - {service} in {region}", "markdown": md, "data": data, "model_label": label, "count": len((data or {}).get("pages") or [])}


def _split_json(text: str):
    if "===JSON===" in text:
        md, js = text.split("===JSON===", 1)
        try:
            return md.strip(), extract_json(js)
        except Exception:
            return md.strip(), None
    return text.strip(), None


GENERATORS = {"rfp_kit": gen_rfp_kit, "prompt_library": gen_prompt_library, "seo_pack": gen_seo_pack}


@router.post("/generate")
async def generate(req: GenerateRequest):
    if req.product not in GENERATORS:
        raise HTTPException(400, f"product must be one of {list(GENERATORS)}")
    started = datetime.now(timezone.utc)
    try:
        out = await GENERATORS[req.product](req.inputs or {})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"generation failed: {str(e)[:200]}")
    fills = len(re.findall(r"\[FILL:[^\]]*\]", out["markdown"]))
    doc = {"id": str(uuid.uuid4()), "product": req.product, "title": out["title"], "inputs": req.inputs, "markdown": out["markdown"],
           "data": out.get("data"), "placeholders": fills, "model_label": out.get("model_label"), "source_url": out.get("source_url"),
           "count": out.get("count"), "chars": len(out["markdown"]), "duration_s": round((datetime.now(timezone.utc) - started).total_seconds(), 1),
           "created_at": now_iso(), "api_key": uuid.uuid4().hex if req.product == "prompt_library" else None}
    await db.apex_deliverables.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


@router.get("/deliverables")
async def deliverables(product: Optional[str] = None, limit: int = Query(50, ge=1, le=200)):
    f = {"product": product} if product else {}
    return await db.apex_deliverables.find(f, {"_id": 0, "markdown": 0, "data": 0}).sort("created_at", -1).to_list(limit)


@router.get("/deliverables/{did}")
async def deliverable(did: str):
    d = await db.apex_deliverables.find_one({"id": did}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Deliverable not found")
    return d


@router.delete("/deliverables/{did}")
async def delete_deliverable(did: str):
    r = await db.apex_deliverables.delete_one({"id": did})
    if not r.deleted_count:
        raise HTTPException(404, "Deliverable not found")
    return {"ok": True}


@router.get("/deliverables/{did}/export")
async def export_deliverable(did: str, fmt: str = "md"):
    d = await db.apex_deliverables.find_one({"id": did}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Deliverable not found")
    return _export(d, fmt)


def _export(d: dict, fmt: str):
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", d.get("title") or d["product"])[:60]
    if fmt == "json":
        return Response(content=json.dumps({"title": d["title"], "product": d["product"], "generated_at": d["created_at"], "data": d.get("data")}, indent=1),
                        media_type="application/json", headers={"Content-Disposition": f'attachment; filename="{safe}.json"'})
    md = (f"{d['markdown']}\n\n---\n*Generated by ACASO Apex Nexus - {d['created_at'][:10]} - {d.get('placeholders', 0)} [FILL] placeholder(s) to complete before use. "
          "Drafts only; verify every claim; nothing has been submitted on your behalf.*\n")
    return Response(content=md, media_type="text/markdown", headers={"Content-Disposition": f'attachment; filename="{safe}.md"'})


# ---- orders: pending_payment -> paid -> unlocked via token ----
@router.post("/orders")
async def create_order(o: OrderCreate):
    if o.product not in PRODUCTS:
        raise HTTPException(400, "unknown product")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", o.buyer_email or ""):
        raise HTTPException(400, "valid buyer_email required")
    if o.deliverable_id:
        d = await db.apex_deliverables.find_one({"id": o.deliverable_id}, {"_id": 0, "product": 1})
        if not d:
            raise HTTPException(404, "Deliverable not found")
        if d["product"] != o.product:
            raise HTTPException(400, "Deliverable belongs to a different product")
    stripe = bool(os.environ.get("STRIPE_API_KEY"))
    doc = {"id": str(uuid.uuid4()), "product": o.product, "buyer_email": o.buyer_email.lower(), "buyer_name": o.buyer_name,
           "deliverable_id": o.deliverable_id, "price_usd": o.price_usd if o.price_usd is not None else PRODUCTS[o.product]["price_usd"],
           "status": "pending_payment", "payment_provider": "stripe" if stripe else "manual", "checkout_url": None,
           "unlock_token": uuid.uuid4().hex, "note": o.note, "created_at": now_iso(), "paid_at": None,
           "audit": [{"at": now_iso(), "event": "created"}]}
    await db.apex_orders.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


@router.get("/orders")
async def orders(status: Optional[str] = None, limit: int = Query(100, ge=1, le=500)):
    f = {"status": status} if status else {}
    return await db.apex_orders.find(f, {"_id": 0}).sort("created_at", -1).to_list(limit)


@router.patch("/orders/{oid}")
async def patch_order(oid: str, p: OrderPatch):
    o = await db.apex_orders.find_one({"id": oid}, {"_id": 0})
    if not o:
        raise HTTPException(404, "Order not found")
    upd = {}
    if p.status:
        if p.status not in ("pending_payment", "paid", "refunded", "cancelled"):
            raise HTTPException(400, "invalid status")
        upd["status"] = p.status
        if p.status == "paid":
            upd["paid_at"] = now_iso()
    if p.deliverable_id is not None:
        d = await db.apex_deliverables.find_one({"id": p.deliverable_id}, {"_id": 0, "product": 1})
        if not d or d["product"] != o["product"]:
            raise HTTPException(400, "Deliverable missing or wrong product")
        upd["deliverable_id"] = p.deliverable_id
    if p.note is not None:
        upd["note"] = p.note[:2000]
    if not upd:
        raise HTTPException(400, "nothing to update")
    await db.apex_orders.update_one({"id": oid}, {"$set": upd, "$push": {"audit": {"at": now_iso(), "event": "updated", "fields": list(upd)}}})
    return await db.apex_orders.find_one({"id": oid}, {"_id": 0})


# ---- public unlock (buyer link) ----
@router.get("/unlock/{token}")
async def unlock(token: str, fmt: str = "md"):
    o = await db.apex_orders.find_one({"unlock_token": token}, {"_id": 0})
    if not o:
        raise HTTPException(404, "Unknown link")
    if o["status"] != "paid":
        raise HTTPException(402, "This deliverable unlocks after payment is confirmed")
    if not o.get("deliverable_id"):
        raise HTTPException(409, "Payment received - the seller has not attached the deliverable yet")
    d = await db.apex_deliverables.find_one({"id": o["deliverable_id"]}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Deliverable missing")
    await db.apex_orders.update_one({"id": o["id"]}, {"$inc": {"downloads": 1}, "$set": {"last_download_at": now_iso()}})
    if fmt == "status":
        return {"product": o["product"], "title": d["title"], "status": o["status"], "api_key": d.get("api_key")}
    return _export(d, fmt)


# ---- gated prompt-library API (vector #2 payment path: API key unlocked by a paid order) ----
@router.get("/library/{did}")
async def library_api(did: str, key: str = Query(...)):
    d = await db.apex_deliverables.find_one({"id": did, "product": "prompt_library"}, {"_id": 0})
    if not d:
        raise HTTPException(404, "Library not found")
    if not d.get("api_key") or key != d["api_key"]:
        raise HTTPException(401, "invalid key")
    paid = await db.apex_orders.count_documents({"deliverable_id": did, "status": "paid"})
    if not paid:
        raise HTTPException(402, "No paid order for this library")
    return {"title": d["title"], "domain": (d.get("data") or {}).get("domain"), "prompts": (d.get("data") or {}).get("prompts") or []}
