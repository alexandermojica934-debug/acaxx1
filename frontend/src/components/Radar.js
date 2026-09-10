import React, { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Radar as RadarIcon, RefreshCw, Loader2, Search, Bookmark, BookmarkCheck, EyeOff, Rocket, ExternalLink,
  ShieldCheck, ShieldAlert, AlertTriangle, ChevronDown, ChevronUp, X, FileText, Mail, PenLine, Package,
  ClipboardList, Download, Sparkles, KeyRound, CheckCircle2, Clock, MapPin, Landmark, Coins, Info, Copy
} from "lucide-react";
import { API } from "../App";
import { Markdown } from "./FileAnalyzer";

const ENTITY = ["individual", "sole_proprietor", "llc", "corporation", "nonprofit", "startup", "creator", "contractor", "community_org", "university", "government"];
const TYPES = ["grant", "contract", "subcontract", "procurement", "sponsorship", "rfp", "funding", "technical_bounty"];
const SET_ASIDES = ["minority", "veteran", "sdvosb", "woman", "disability", "hubzone", "8a", "disadvantaged"];
const STAGES = ["Discovered", "Reviewed", "Qualified", "Preparing", "Submitted", "Awarded", "Not Awarded"];
const VIEWS = [
  { key: "all", label: "All open" }, { key: "high", label: "High fit" }, { key: "low", label: "Lower barrier" },
  { key: "closing", label: "Closing soon" }, { key: "new", label: "Newest" }, { key: "saved", label: "Saved" }, { key: "dismissed", label: "Dismissed" },
];
const DRAFTS = [
  { key: "email", label: "Intro email", icon: Mail },
  { key: "grant_narrative", label: "Grant narrative", icon: PenLine },
  { key: "outreach_packet", label: "Outreach packet", icon: Package },
  { key: "form_answers", label: "Fill a form", icon: ClipboardList },
];

const money = (v) => (v === null || v === undefined ? null : `$${Number(v).toLocaleString()}`);
const dateS = (iso) => { try { return iso ? new Date(iso).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" }) : null; } catch { return null; } };
const ago = (iso) => { try { const m = Math.round((Date.now() - new Date(iso)) / 60000); return m < 60 ? `${m}m ago` : m < 1440 ? `${Math.round(m / 60)}h ago` : `${Math.round(m / 1440)}d ago`; } catch { return ""; } };
const NV = <span className="rd-nv">Not verified</span>;
const listToStr = (a) => (a || []).join(", ");
const strToList = (s) => (s || "").split(",").map((x) => x.trim()).filter(Boolean);

function ScoreMeter({ score, size = "sm" }) {
  if (!score) return null;
  const t = score.total ?? 0;
  const tone = t >= 75 ? "hi" : t >= 50 ? "mid" : "lo";
  return (
    <div className={`rd-score ${size} ${tone}`} title="Inferred score - see breakdown in detail view" data-testid="rd-score">
      <div className="rd-score-bar"><span style={{ width: `${t}%` }} /></div>
      <div className="rd-score-txt"><b>{t}</b><small>/100 · {score.label} · inferred</small></div>
    </div>
  );
}

function SourceBadge({ o }) {
  const stale = o.status === "stale";
  return (
    <span className={`rd-src ${stale ? "stale" : ""}`} title={`Source: ${o.source} · retrieved ${o.retrieved_at} · HTTP ${o.http_status}`} data-testid="rd-source-badge">
      <ShieldCheck size={11} /> {o.source.replace("_", ".")} · {stale ? "STALE" : `verified ${ago(o.last_verified_at || o.retrieved_at)}`}
    </span>
  );
}

export default function Radar() {
  const [profile, setProfile] = useState(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const [sources, setSources] = useState([]);
  const [discovering, setDiscovering] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("all");
  const [filters, setFilters] = useState({ type: "", source: "", min_score: "", closing_days: "", low_barrier: false, remote: false, max_value: "", q: "" });
  const [nlq, setNlq] = useState("");
  const [nlProposal, setNlProposal] = useState(null);
  const [nlBusy, setNlBusy] = useState(false);
  const [detail, setDetail] = useState(null);

  const loadSources = useCallback(async () => { try { setSources((await axios.get(`${API}/radar/sources`)).data); } catch { /* silent */ } }, []);
  const loadProfile = useCallback(async () => { try { setProfile((await axios.get(`${API}/radar/profile`)).data); } catch { /* silent */ } }, []);

  const params = useMemo(() => {
    const p = { limit: 150 };
    if (filters.type) p.type = filters.type;
    if (filters.source) p.source = filters.source;
    if (filters.min_score) p.min_score = filters.min_score;
    if (filters.closing_days) p.closing_days = filters.closing_days;
    if (filters.low_barrier) p.low_barrier = true;
    if (filters.remote) p.remote = true;
    if (filters.max_value) p.max_value = filters.max_value;
    if (filters.q) p.q = filters.q;
    if (view === "high") p.min_score = Math.max(70, Number(p.min_score || 0));
    if (view === "low") p.low_barrier = true;
    if (view === "closing") { p.closing_days = Math.min(30, Number(p.closing_days || 30)); p.sort = "deadline"; }
    if (view === "new") p.sort = "new";
    if (view === "saved") p.saved = true;
    if (view === "dismissed") { p.user_status = "dismissed"; p.include_dismissed = true; }
    return p;
  }, [filters, view]);

  const loadItems = useCallback(async () => {
    setLoading(true);
    try { setItems((await axios.get(`${API}/radar/opportunities`, { params })).data); }
    catch { toast.error("Could not load opportunities"); }
    finally { setLoading(false); }
  }, [params]);

  useEffect(() => { loadSources(); loadProfile(); }, [loadSources, loadProfile]);
  useEffect(() => { loadItems(); }, [loadItems]);

  const discover = async () => {
    setDiscovering(true);
    try {
      const r = await axios.post(`${API}/radar/discover`, { keyword: keyword || null, limit: 20 }, { timeout: 120000 });
      const ok = r.data.runs.filter((x) => !x.error);
      const errs = r.data.runs.filter((x) => x.error);
      toast.success(`${ok.reduce((a, x) => a + x.new, 0)} new · ${ok.reduce((a, x) => a + x.updated, 0)} re-verified from ${ok.length} source(s)`);
      errs.forEach((e) => toast.warning(`${e.source}: ${e.error.split(":")[0]}`));
      loadSources(); loadItems();
    } catch (e) { toast.error(e?.response?.data?.detail || "Discovery failed"); }
    finally { setDiscovering(false); }
  };

  const saveProfile = async () => {
    try { const r = await axios.put(`${API}/radar/profile`, profile); setProfile(r.data); toast.success("Profile saved - re-run Discover to rescore"); }
    catch (e) { toast.error(e?.response?.data?.detail?.[0]?.msg || "Profile invalid"); }
  };

  const patch = async (id, body) => {
    try {
      const r = await axios.patch(`${API}/radar/opportunities/${id}`, body);
      setItems((xs) => xs.map((x) => (x.id === id ? { ...x, ...r.data, description: undefined } : x)));
      if (detail?.id === id) setDetail(r.data);
      return r.data;
    } catch { toast.error("Update failed"); }
  };

  const toMission = async (o) => {
    try {
      const r = await axios.post(`${API}/radar/opportunities/${o.id}/to-mission`, {}, { timeout: 120000 });
      toast.success(`Mission "${r.data.title}" added to Sovereign Home`, { action: { label: "Open board", onClick: () => { window.location.href = "/?tab=home"; } } });
      setItems((xs) => xs.map((x) => (x.id === o.id ? { ...x, mission_id: r.data.id, mission_title: r.data.title, stage: "Preparing" } : x)));
      if (detail?.id === o.id) setDetail((d) => ({ ...d, mission_id: r.data.id, mission_title: r.data.title, stage: "Preparing" }));
    } catch (e) { toast.error(e?.response?.data?.detail || "Could not create mission"); }
  };

  const openDetail = async (id) => {
    try { setDetail((await axios.get(`${API}/radar/opportunities/${id}`)).data); } catch { toast.error("Could not open"); }
  };

  const runNl = async () => {
    if (!nlq.trim()) return;
    setNlBusy(true);
    try { setNlProposal((await axios.post(`${API}/radar/search/nl`, { query: nlq })).data); }
    catch (e) { toast.error(e?.response?.data?.detail || "Could not interpret query"); }
    finally { setNlBusy(false); }
  };
  const applyNl = () => {
    const f = nlProposal?.proposed_filters || {};
    setFilters((cur) => ({ ...cur, type: f.type || "", source: f.source || "", min_score: f.min_score ?? "", closing_days: f.closing_days ?? "",
      low_barrier: !!f.low_barrier, remote: !!f.remote, max_value: f.max_value ?? "", q: f.q || "" }));
    setView("all"); setNlProposal(null);
    if (f.exclusions?.length) toast(`Exclusions noted (apply by eye): ${f.exclusions.join("; ")}`);
  };

  const pf = (k) => (profile?.[k] ?? "");
  const setP = (k, v) => setProfile((p) => ({ ...p, [k]: v }));
  const configured = sources.filter((s) => s.configured).length;

  return (
    <div className="rd-wrap" data-testid="radar-page">
      <div className="rd-hero">
        <div>
          <div className="rd-title"><RadarIcon size={18} /> Opportunity Radar</div>
          <p>Finds public contracts, grants, sponsorships and B2B openings that match your capabilities - and shows the <b>real requirements, effort, deadline and next step</b>. Every record comes from an official source with a URL, retrieval time and evidence excerpts. Nothing here is "easy money", and nothing is ever auto-submitted.</p>
        </div>
        <div className="rd-hero-stats">
          <div className="rd-stat"><span className="v">{items.length}</span><span className="l">in view</span></div>
          <div className="rd-stat"><span className="v">{configured}/{sources.length}</span><span className="l">sources live</span></div>
        </div>
      </div>

      <div className="rd-warn" data-testid="radar-disclaimer"><AlertTriangle size={14} /> Verify every opportunity on its original source before relying on it. Scores, fit labels and drafts are AI/heuristic inferences - they are not eligibility determinations and never predict an award.</div>

      {/* Sources + discover */}
      <div className="rd-panel">
        <div className="rd-panel-h"><Landmark size={15} /> Sources <em>official APIs first - no scraping behind logins, CAPTCHAs or rate limits</em></div>
        <div className="rd-sources">
          {sources.map((s) => (
            <div key={s.id} className={`rd-source ${s.configured ? "ok" : "off"}`} data-testid={`source-${s.id}`}>
              <div className="rd-source-top">{s.configured ? <CheckCircle2 size={13} /> : <KeyRound size={13} />} <b>{s.name}</b></div>
              <small>{s.type} · {s.active_count} active</small>
              {!s.configured && <small className="rd-needkey">needs {s.env} in backend/.env</small>}
              {s.last_run && <small>{s.last_run.error ? `last: ${s.last_run.error.split(":")[0]}` : `last: HTTP ${s.last_run.http_status} · ${s.last_run.fetched} fetched · ${ago(s.last_run.retrieved_at)}`}</small>}
            </div>
          ))}
        </div>
        <div className="rd-row">
          <input data-testid="radar-keyword" className="cw-input grow" value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="Focus keyword for this run (optional - defaults to your first profile keyword)" />
          <button data-testid="radar-discover" className="rd-btn primary" onClick={discover} disabled={discovering}>
            {discovering ? <Loader2 className="spin" size={14} /> : <RefreshCw size={14} />} {discovering ? "Fetching sources..." : "Discover now"}
          </button>
          <button data-testid="radar-profile-toggle" className="rd-btn" onClick={() => setProfileOpen((o) => !o)}>
            {profileOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />} Your profile {profile?.entity_type ? `· ${profile.entity_type}` : "· not set"}
          </button>
        </div>

        <AnimatePresence>
          {profileOpen && profile && (
            <motion.div className="rd-profile" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} data-testid="radar-profile">
              <div className="rd-grid3">
                <label>Entity type<select data-testid="profile-entity" className="cw-input" value={pf("entity_type") || ""} onChange={(e) => setP("entity_type", e.target.value || null)}><option value="">Select...</option>{ENTITY.map((x) => <option key={x} value={x}>{x}</option>)}</select></label>
                <label>Organization<input className="cw-input" value={pf("org_name") || ""} onChange={(e) => setP("org_name", e.target.value)} /></label>
                <label>Service area<select className="cw-input" value={pf("service_area") || ""} onChange={(e) => setP("service_area", e.target.value || null)}><option value="">Select...</option>{["local", "state", "national", "international"].map((x) => <option key={x}>{x}</option>)}</select></label>
                <label>State (2-letter)<input className="cw-input" value={pf("state") || ""} onChange={(e) => setP("state", e.target.value.toUpperCase())} maxLength={2} /></label>
                <label>City<input className="cw-input" value={pf("city") || ""} onChange={(e) => setP("city", e.target.value)} /></label>
                <label>Country<input className="cw-input" value={pf("country") || ""} onChange={(e) => setP("country", e.target.value)} /></label>
                <label>Industries (comma)<input data-testid="profile-industries" className="cw-input" value={listToStr(profile.industries)} onChange={(e) => setP("industries", strToList(e.target.value))} /></label>
                <label>Skills (comma)<input data-testid="profile-skills" className="cw-input" value={listToStr(profile.skills)} onChange={(e) => setP("skills", strToList(e.target.value))} /></label>
                <label>Search keywords (comma)<input data-testid="profile-keywords" className="cw-input" value={listToStr(profile.keywords)} onChange={(e) => setP("keywords", strToList(e.target.value))} /></label>
              </div>
              <button className="rd-link" onClick={() => setMoreOpen((m) => !m)}>{moreOpen ? "Hide" : "More"} fields (NAICS, certifications, set-asides, budget, time, value range...)</button>
              {moreOpen && (
                <div className="rd-grid3">
                  <label>NAICS / PSC codes (comma)<input className="cw-input" value={listToStr(profile.naics_codes)} onChange={(e) => setP("naics_codes", strToList(e.target.value))} /></label>
                  <label>Years experience<input type="number" className="cw-input" value={pf("years_experience") ?? ""} onChange={(e) => setP("years_experience", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Team size<input type="number" className="cw-input" value={pf("team_size") ?? ""} onChange={(e) => setP("team_size", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Revenue range<input className="cw-input" value={pf("revenue_range") || ""} onChange={(e) => setP("revenue_range", e.target.value)} placeholder="e.g. <$100K" /></label>
                  <label>Certifications (comma)<input className="cw-input" value={listToStr(profile.certifications)} onChange={(e) => setP("certifications", strToList(e.target.value))} /></label>
                  <label>Budget available ($)<input type="number" className="cw-input" value={pf("budget") ?? ""} onChange={(e) => setP("budget", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Hours / week<input type="number" className="cw-input" value={pf("hours_per_week") ?? ""} onChange={(e) => setP("hours_per_week", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Min value ($)<input type="number" className="cw-input" value={pf("min_value") ?? ""} onChange={(e) => setP("min_value", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <label>Max value ($)<input type="number" className="cw-input" value={pf("max_value") ?? ""} onChange={(e) => setP("max_value", e.target.value === "" ? null : Number(e.target.value))} /></label>
                  <div className="rd-checks">
                    <span>Set-aside certifications you hold:</span>
                    {SET_ASIDES.map((s) => (
                      <label key={s} className="rd-chk"><input type="checkbox" checked={(profile.set_asides || []).includes(s)} onChange={(e) => setP("set_asides", e.target.checked ? [...(profile.set_asides || []), s] : (profile.set_asides || []).filter((x) => x !== s))} /> {s}</label>
                    ))}
                  </div>
                  <div className="rd-checks">
                    <span>Preferred types:</span>
                    {TYPES.map((s) => (
                      <label key={s} className="rd-chk"><input type="checkbox" checked={(profile.preferred_types || []).includes(s)} onChange={(e) => setP("preferred_types", e.target.checked ? [...(profile.preferred_types || []), s] : (profile.preferred_types || []).filter((x) => x !== s))} /> {s}</label>
                    ))}
                  </div>
                  <div className="rd-checks">
                    <label className="rd-chk"><input type="checkbox" checked={!!profile.nonprofit_status} onChange={(e) => setP("nonprofit_status", e.target.checked)} /> Nonprofit status</label>
                    <label className="rd-chk"><input type="checkbox" checked={!!profile.willing_travel} onChange={(e) => setP("willing_travel", e.target.checked)} /> Willing to travel</label>
                    <label className="rd-chk"><input type="checkbox" checked={!!profile.willing_subcontract} onChange={(e) => setP("willing_subcontract", e.target.checked)} /> Willing to subcontract</label>
                  </div>
                  <label className="rd-span3">Capability statement (the ONLY facts drafts may claim about you)<textarea className="cw-textarea" rows={3} value={pf("bio") || ""} onChange={(e) => setP("bio", e.target.value)} /></label>
                </div>
              )}
              <div className="rd-row"><button data-testid="profile-save" className="rd-btn primary" onClick={saveProfile}><CheckCircle2 size={14} /> Save profile</button><small className="rd-dim">No field is required. More detail = better fit and eligibility scoring.</small></div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Filters */}
      <div className="rd-panel">
        <div className="rd-views">
          {VIEWS.map((v) => <button key={v.key} data-testid={`view-${v.key}`} className={view === v.key ? "rd-chip active" : "rd-chip"} onClick={() => setView(v.key)}>{v.label}</button>)}
        </div>
        <div className="rd-filters">
          <select data-testid="filter-type" className="cw-input" value={filters.type} onChange={(e) => setFilters({ ...filters, type: e.target.value })}><option value="">Any type</option>{TYPES.map((t) => <option key={t} value={t}>{t}</option>)}</select>
          <select data-testid="filter-source" className="cw-input" value={filters.source} onChange={(e) => setFilters({ ...filters, source: e.target.value })}><option value="">Any source</option>{sources.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select>
          <input data-testid="filter-min-score" type="number" className="cw-input rd-narrow" placeholder="Min score" value={filters.min_score} onChange={(e) => setFilters({ ...filters, min_score: e.target.value })} />
          <input type="number" className="cw-input rd-narrow" placeholder="Closing ≤ days" value={filters.closing_days} onChange={(e) => setFilters({ ...filters, closing_days: e.target.value })} />
          <input type="number" className="cw-input rd-narrow" placeholder="Max value $" value={filters.max_value} onChange={(e) => setFilters({ ...filters, max_value: e.target.value })} />
          <label className="rd-chk"><input type="checkbox" checked={filters.low_barrier} onChange={(e) => setFilters({ ...filters, low_barrier: e.target.checked })} /> lower barrier</label>
          <label className="rd-chk"><input type="checkbox" checked={filters.remote} onChange={(e) => setFilters({ ...filters, remote: e.target.checked })} /> remote/national</label>
          <div className="rd-search"><Search size={13} /><input data-testid="filter-q" value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} placeholder="keyword in title / issuer / eligibility" /></div>
        </div>
        <div className="rd-row rd-nl">
          <Sparkles size={14} />
          <input data-testid="nl-query" className="cw-input grow" value={nlq} onChange={(e) => setNlq(e.target.value)} placeholder='Natural-language search, e.g. "small technology grants under $250,000 closing in the next 60 days"' onKeyDown={(e) => e.key === "Enter" && runNl()} />
          <button data-testid="nl-run" className="rd-btn" onClick={runNl} disabled={nlBusy}>{nlBusy ? <Loader2 className="spin" size={14} /> : <Search size={14} />} Propose filters</button>
        </div>
        {nlProposal && (
          <div className="rd-proposal" data-testid="nl-proposal">
            <Info size={13} /> <span>AI proposes these filters (not applied yet): <code>{JSON.stringify(nlProposal.proposed_filters)}</code></span>
            <button className="rd-btn primary sm" data-testid="nl-apply" onClick={applyNl}>Apply</button>
            <button className="rd-btn sm" onClick={() => setNlProposal(null)}>Discard</button>
          </div>
        )}
      </div>

      {/* Feed */}
      {loading ? (
        <div className="rd-empty" data-testid="radar-loading"><Loader2 className="spin" size={18} /> Loading opportunities...</div>
      ) : items.length === 0 ? (
        <div className="rd-empty" data-testid="radar-empty"><RadarIcon size={26} /><p>No opportunities match this view yet. Set your profile, then press <b>Discover now</b> to pull live records from the configured sources.</p></div>
      ) : (
        <div className="rd-feed" data-testid="radar-feed">
          {items.map((o, i) => {
            const val = o.funding_amount ?? o.estimated_value;
            const saved = ["saved", "contacted", "submitted"].includes(o.user_status);
            return (
              <motion.article key={o.id} className={`rd-card ${o.status === "stale" ? "stale" : ""}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(i, 12) * 0.03 }} data-testid={`opp-${o.id}`}>
                <div className="rd-card-top">
                  <span className={`rd-type t-${o.opportunity_type}`}>{o.opportunity_type.replace("_", " ")}</span>
                  <SourceBadge o={o} />
                  {o.user_status !== "new" && <span className="rd-ustat">{o.user_status}</span>}
                </div>
                <h3 onClick={() => openDetail(o.id)} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && openDetail(o.id)} data-testid="opp-title">{o.title}</h3>
                <div className="rd-org"><Landmark size={12} /> {o.organization_name || NV}{o.issuing_department && o.source === "github_bounties" ? <span className="rd-dim"> · {o.issuing_department}</span> : null}</div>
                <div className="rd-facts">
                  <span><Coins size={12} /> {money(val) || NV}</span>
                  <span><Clock size={12} /> {o.deadline ? <>{dateS(o.deadline)} · <b className={o.days_remaining !== null && o.days_remaining <= 14 ? "rd-urgent" : ""}>{o.days_remaining}d</b></> : NV}</span>
                  <span><MapPin size={12} /> {o.remote_status || o.location || NV}</span>
                </div>
                <ScoreMeter score={o.score} />
                <div className="rd-barrier" title={`low: ${(o.barrier?.low || []).join(", ") || "-"} | high: ${(o.barrier?.high || []).join(", ") || "-"}`}>
                  <span className={`rd-bar-lbl ${o.barrier?.label?.startsWith("lower") ? "lo" : o.barrier?.label?.startsWith("higher") ? "hi" : ""}`}>{o.barrier?.label}</span>
                  {(o.required_entity_types || []).slice(0, 2).map((t) => <span key={t} className="rd-req">{t}</span>)}
                  {o.set_aside && <span className="rd-req">{o.set_aside}</span>}
                </div>
                <div className="rd-next">{o.ai?.fit?.recommended_next_action || (o.score?.label === "Poor fit" ? "Likely skip - open detail only if the source text reads differently to you." : "Open detail, run Fit + Skeptic analysis, then verify on the original source.")}</div>
                <div className="rd-actions">
                  <button className="rd-ic" data-testid="opp-save" title={saved ? "Unsave" : "Save"} onClick={() => patch(o.id, { user_status: saved ? "new" : "saved" })}>{saved ? <BookmarkCheck size={14} /> : <Bookmark size={14} />}</button>
                  <button className="rd-ic" data-testid="opp-dismiss" title={o.user_status === "dismissed" ? "Restore" : "Dismiss"} onClick={() => patch(o.id, { user_status: o.user_status === "dismissed" ? "new" : "dismissed" })}><EyeOff size={14} /></button>
                  <button className="rd-ic" data-testid="opp-pipeline" title={o.mission_id ? `On board: ${o.mission_title}` : "Add to pipeline (Sovereign Home mission)"} onClick={() => (o.mission_id ? (window.location.href = "/?tab=home") : toMission(o))}><Rocket size={14} /></button>
                  <a className="rd-ic" data-testid="opp-source" href={o.source_url} target="_blank" rel="noreferrer" title="Open original source"><ExternalLink size={14} /></a>
                  <button className="rd-btn sm" data-testid="opp-detail" onClick={() => openDetail(o.id)}><FileText size={13} /> Detail & drafts</button>
                </div>
              </motion.article>
            );
          })}
        </div>
      )}

      <AnimatePresence>{detail && <Detail o={detail} onClose={() => setDetail(null)} patch={patch} toMission={toMission} setDetail={setDetail} />}</AnimatePresence>
    </div>
  );
}

function Detail({ o, onClose, patch, toMission, setDetail }) {
  const [analyzing, setAnalyzing] = useState(false);
  const [draftKind, setDraftKind] = useState("email");
  const [formText, setFormText] = useState("");
  const [extra, setExtra] = useState("");
  const [drafting, setDrafting] = useState(false);
  const [notes, setNotes] = useState(o.notes || "");
  const val = o.funding_amount ?? o.estimated_value;
  const ai = o.ai || {};
  const draft = (o.drafts || {})[draftKind];

  const analyze = async () => {
    setAnalyzing(true);
    try { const r = await axios.post(`${API}/radar/opportunities/${o.id}/analyze`, { include_checklist: true }, { timeout: 180000 }); setDetail({ ...o, ...r.data }); toast.success("Fit Analyst, Skeptic and Compliance Sentinel have reported"); }
    catch (e) { toast.error(e?.response?.data?.detail || "Analysis failed"); }
    finally { setAnalyzing(false); }
  };
  const makeDraft = async () => {
    setDrafting(true);
    try {
      const r = await axios.post(`${API}/radar/opportunities/${o.id}/draft`, { kind: draftKind, form_text: draftKind === "form_answers" ? formText : null, extra_instructions: extra || null }, { timeout: 180000 });
      setDetail({ ...o, drafts: { ...(o.drafts || {}), [draftKind]: r.data }, stage: ["Discovered", "Reviewed", "Qualified"].includes(o.stage) ? "Preparing" : o.stage });
      toast.success(`Draft ready - ${r.data.placeholders} [FILL] placeholder(s) need your input`);
    } catch (e) { toast.error(e?.response?.data?.detail || "Draft failed"); }
    finally { setDrafting(false); }
  };
  const copy = async (t) => { try { await navigator.clipboard.writeText(t); toast.success("Copied"); } catch { toast.error("Copy failed"); } };
  const list = (a) => (Array.isArray(a) && a.length ? <ul>{a.map((x, i) => <li key={i}>{typeof x === "string" ? x : `${x.item || JSON.stringify(x)}${x.why ? ` - ${x.why}` : ""}${x.stated_by_source === false ? " (inferred, not stated by source)" : ""}`}</li>)}</ul> : <span className="rd-dim">none listed</span>);
  const stageIdx = STAGES.indexOf(o.stage || "Discovered");

  return (
    <motion.div className="rd-modal-bg" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose} data-testid="opp-detail-modal">
      <motion.div className="rd-modal" initial={{ y: 20 }} animate={{ y: 0 }} exit={{ y: 20 }} onClick={(e) => e.stopPropagation()}>
        <div className="rd-modal-h">
          <div>
            <div className="rd-card-top"><span className={`rd-type t-${o.opportunity_type}`}>{o.opportunity_type.replace("_", " ")}</span><SourceBadge o={o} /><span className="rd-ustat">{o.user_status}</span></div>
            <h2>{o.title}</h2>
            <div className="rd-org"><Landmark size={12} /> {o.organization_name || NV} {o.issuing_department ? <span className="rd-dim">· {o.issuing_department}</span> : null}</div>
          </div>
          <div className="rd-modal-actions">
            <a className="rd-btn" href={o.source_url} target="_blank" rel="noreferrer" data-testid="detail-source"><ExternalLink size={14} /> Original source</a>
            <a className="rd-btn" href={`${API}/radar/opportunities/${o.id}/export`} target="_blank" rel="noreferrer" data-testid="detail-export"><Download size={14} /> Export .md</a>
            <button className="rd-ic" onClick={onClose} data-testid="detail-close"><X size={16} /></button>
          </div>
        </div>

        <div className="rd-warn"><AlertTriangle size={14} /> <b>Verify before acting.</b> Retrieved {dateS(o.retrieved_at)} ({ago(o.retrieved_at)}) · HTTP {o.http_status} · parser {o.parser_version} · status <b>{o.status}</b>. Confirm deadline, amount and eligibility on the original page; this app never submits anything for you.</div>

        <div className="rd-stages" data-testid="detail-stages">
          {STAGES.map((s, i) => <button key={s} className={`rd-stage ${i <= stageIdx ? "done" : ""} ${s === o.stage ? "cur" : ""}`} onClick={() => patch(o.id, { stage: s })} title="Set stage">{s}</button>)}
        </div>

        <div className="rd-detail-grid">
          <section>
            <h4>Facts from source</h4>
            <dl className="rd-dl">
              <dt>Amount</dt><dd>{money(val) || NV}{o.funding_floor ? <span className="rd-dim"> (floor {money(o.funding_floor)})</span> : null}</dd>
              <dt>Deadline</dt><dd>{o.deadline ? `${dateS(o.deadline)} · ${o.days_remaining} days` : NV}</dd>
              <dt>Posted</dt><dd>{dateS(o.posted_date) || NV}</dd>
              <dt>Location</dt><dd>{o.location || NV} {o.remote_status ? `· ${o.remote_status}` : ""}</dd>
              <dt>Applicant types</dt><dd>{listToStr(o.required_entity_types) || <span className="rd-dim">Not stated by source</span>}</dd>
              <dt>Set-aside</dt><dd>{o.set_aside || <span className="rd-dim">none stated</span>}</dd>
              <dt>Registrations</dt><dd>{listToStr(o.required_registrations) || <span className="rd-dim">Not stated</span>}</dd>
              <dt>Cost sharing</dt><dd>{o.cost_sharing === true ? "Required" : o.cost_sharing === false ? "Not required" : NV}</dd>
              <dt>Codes</dt><dd>{listToStr(o.industry_codes) || <span className="rd-dim">none</span>}</dd>
              <dt>Contact</dt><dd>{o.contact_information ? (Array.isArray(o.contact_information) ? o.contact_information.map((c, i) => <div key={i}>{c.name} {c.email && <a href={`mailto:${c.email}`}>{c.email}</a>}</div>) : <>{o.contact_information.name} {o.contact_information.email && <a href={`mailto:${o.contact_information.email}`}>{o.contact_information.email}</a>}</>) : NV}</dd>
            </dl>
            <h4>Eligibility text (verbatim from source)</h4>
            <p className="rd-quote">{o.eligibility_text || <span className="rd-dim">Not stated by source</span>}</p>
            <h4>Description (from source)</h4>
            <p className="rd-desc">{o.description || <span className="rd-dim">Not provided by source - open the original page</span>}</p>
            {o.attachments?.length > 0 && <><h4>Original documents</h4><ul>{o.attachments.map((a) => <li key={a}><a href={a} target="_blank" rel="noreferrer">{a}</a></li>)}</ul></>}
            <h4>Evidence excerpts</h4>
            <ul className="rd-evidence" data-testid="detail-evidence">{(o.evidence || []).map((e, i) => <li key={i}><b>{e.field}</b> <q>{e.excerpt}</q> <code>{e.source_location}</code></li>)}</ul>
          </section>

          <section>
            <h4>Inferred score <small>heuristic, transparent</small></h4>
            <ScoreMeter score={o.score} size="lg" />
            <div className="rd-breakdown" data-testid="detail-breakdown">
              {Object.entries(o.score?.breakdown || {}).map(([k, b]) => (
                <div key={k} className="rd-bd-row"><span>{k.replace(/_/g, " ")}</span><div className="rd-bd-bar"><span style={{ width: `${(b.points / b.weight) * 100}%` }} /></div><small>{b.points}/{b.weight}</small></div>
              ))}
            </div>
            <ul className="rd-notes">{(o.score?.notes || []).map((n, i) => <li key={i}>{n}</li>)}</ul>
            <div className="rd-lbl-note">"Appears to match stated requirements" ≠ "legally eligible" ≠ "likely to win". Strong fit requires the Skeptic to have run.</div>

            <h4>Barrier signals <small>observed in source text</small></h4>
            <div className="rd-sig"><b className="lo">Lower:</b> {(o.barrier?.low || []).join(", ") || "none observed"}</div>
            <div className="rd-sig"><b className="hi">Higher:</b> {(o.barrier?.high || []).join(", ") || "none observed"}</div>

            <h4>AI personas <small>on demand · inferred</small></h4>
            <button className="rd-btn primary" onClick={analyze} disabled={analyzing} data-testid="detail-analyze">{analyzing ? <Loader2 className="spin" size={14} /> : <Sparkles size={14} />} {ai.fit ? "Re-run" : "Run"} Fit Analyst + Skeptic + Compliance Sentinel</button>
            {ai.fit && (
              <div className="rd-ai" data-testid="detail-fit">
                <div className="rd-ai-h"><ShieldCheck size={13} /> Fit Analyst <small>{ai.fit.model_label}</small></div>
                <p>{ai.fit.summary}</p>
                <div className="rd-two"><div><b>Why it may fit</b>{list(ai.fit.why_it_may_fit)}</div><div><b>Why it may not</b>{list(ai.fit.why_it_may_not_fit)}</div></div>
                <div><b>Matches stated requirements:</b> {String(ai.fit.appears_to_match_stated_requirements)} · <b>Effort:</b> {ai.fit.effort_estimate}</div>
                <div><b>Missing information</b>{list(ai.fit.missing_information)}</div>
                <div className="rd-next"><b>Next action:</b> {ai.fit.recommended_next_action}</div>
              </div>
            )}
            {ai.skeptic && (
              <div className={`rd-ai skeptic v-${ai.skeptic.verdict}`} data-testid="detail-skeptic">
                <div className="rd-ai-h"><ShieldAlert size={13} /> Skeptic <small>{ai.skeptic.model_label}</small> <span className="rd-verdict">{ai.skeptic.verdict}</span></div>
                <div><b>Concerns</b>{list(ai.skeptic.concerns)}</div>
                <div><b>Missing requirements</b>{list(ai.skeptic.missing_requirements)}</div>
                <div><b>Stale / suspicious</b>{list(ai.skeptic.stale_or_suspicious)}</div>
                <div><b>Verify at source</b>{list(ai.skeptic.verify_at_source)}</div>
              </div>
            )}
            {ai.checklist && (
              <div className="rd-ai" data-testid="detail-checklist">
                <div className="rd-ai-h"><ClipboardList size={13} /> Compliance Sentinel + Proposal Architect <small>{ai.checklist.model_label}</small></div>
                <div><b>Preparation checklist</b>{list(ai.checklist.preparation_checklist)}</div>
                <div><b>Questions for the contracting officer / funder</b>{list(ai.checklist.questions_for_contracting_officer_or_funder)}</div>
                <div><b>Proposal outline</b>{list(ai.checklist.proposal_outline)}</div>
              </div>
            )}

            <h4>Similar open opportunities</h4>
            <ul className="rd-similar">{(o.similar || []).map((s) => <li key={s.id}>{s.title} <small>{s.organization_name} · {s.score?.total}</small></li>)}{!o.similar?.length && <li className="rd-dim">none</li>}</ul>
          </section>
        </div>

        {/* Drafting desk */}
        <div className="rd-desk" data-testid="drafting-desk">
          <div className="rd-panel-h"><PenLine size={15} /> Drafting Desk <em>drafts use only your profile + the source text; unknowns become [FILL: ...] - you review and submit manually</em></div>
          <div className="rd-views">
            {DRAFTS.map((d) => { const I = d.icon; return <button key={d.key} data-testid={`draft-${d.key}`} className={draftKind === d.key ? "rd-chip active" : "rd-chip"} onClick={() => setDraftKind(d.key)}><I size={13} /> {d.label}{(o.drafts || {})[d.key] ? " ✓" : ""}</button>; })}
          </div>
          {draftKind === "form_answers" && <textarea data-testid="draft-form-text" className="cw-textarea" rows={5} value={formText} onChange={(e) => setFormText(e.target.value)} placeholder="Paste the application or form questions here, one per line..." />}
          <div className="rd-row">
            <input className="cw-input grow" value={extra} onChange={(e) => setExtra(e.target.value)} placeholder="Optional instructions (tone, emphasis, length)..." />
            <button className="rd-btn primary" data-testid="draft-generate" onClick={makeDraft} disabled={drafting || (draftKind === "form_answers" && !formText.trim())}>{drafting ? <Loader2 className="spin" size={14} /> : <Sparkles size={14} />} {draft ? "Regenerate" : "Generate"} {DRAFTS.find((d) => d.key === draftKind)?.label}</button>
          </div>
          {draft && (
            <div className="rd-draft" data-testid="draft-output">
              <div className="rd-draft-h"><span>{draft.model_label} · {ago(draft.generated_at)} · <b className={draft.placeholders ? "rd-urgent" : ""}>{draft.placeholders} [FILL] placeholder(s)</b></span><button className="rd-btn sm" onClick={() => copy(draft.content)}><Copy size={13} /> Copy</button></div>
              <Markdown text={draft.content} />
            </div>
          )}
        </div>

        <div className="rd-notes-box">
          <h4>Your notes</h4>
          <textarea data-testid="detail-notes" className="cw-textarea" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Calls made, documents gathered, questions asked..." />
          <div className="rd-row">
            <button className="rd-btn" data-testid="notes-save" onClick={() => patch(o.id, { notes })}><CheckCircle2 size={14} /> Save notes</button>
            <button className="rd-btn" data-testid="mark-contacted" onClick={() => patch(o.id, { user_status: "contacted" })}>Mark contacted</button>
            <button className="rd-btn" data-testid="mark-submitted" onClick={() => patch(o.id, { user_status: "submitted" })}>Mark submitted (by you)</button>
            <button className="rd-btn primary" data-testid="detail-pipeline" onClick={() => (o.mission_id ? (window.location.href = "/?tab=home") : toMission(o))}><Rocket size={14} /> {o.mission_id ? `On board: ${o.mission_title}` : "Add to pipeline"}</button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
