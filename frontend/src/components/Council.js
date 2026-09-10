import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Crown, Loader2, Play, Download, History, Sparkles, ShieldAlert, Lightbulb,
  Compass, Coins, Radar, Trash2, ChevronRight, X, Info
} from "lucide-react";
import { API } from "../App";
import { Markdown } from "./FileAnalyzer";

const WEAVER_ICON = { architect: Compass, shadow: ShieldAlert, muse: Lightbulb, finance: Coins };
const PRESET_ICON = { genesis: Sparkles, hunter: Radar, foresight: Compass };

const fmtDate = (iso) => {
  try { return new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }); }
  catch { return ""; }
};

export default function Council() {
  const [presets, setPresets] = useState([]);
  const [presetId, setPresetId] = useState("genesis");
  const [challenge, setChallenge] = useState("");
  const [challengeType, setChallengeType] = useState("product_strategy");
  const [extra, setExtra] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [openWeaver, setOpenWeaver] = useState(null);

  const applyPreset = useCallback((p) => {
    setPresetId(p.id);
    setChallenge(p.challenge);
    setChallengeType(p.challenge_type);
    setExtra(p.additional_context || "");
  }, []);

  const loadHistory = useCallback(async () => {
    try { const r = await axios.get(`${API}/acaso/deliberations`); setHistory(r.data); } catch { /* silent */ }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const r = await axios.get(`${API}/acaso/presets`);
        setPresets(r.data);
        const g = r.data.find((p) => p.id === "genesis") || r.data[0];
        if (g) applyPreset(g);
      } catch { toast.error("Could not load council presets"); }
      loadHistory();
    })();
  }, [applyPreset, loadHistory]);

  const run = async () => {
    if (challenge.trim().length < 20) { toast.error("Describe the challenge in at least 20 characters"); return; }
    setRunning(true); setResult(null);
    try {
      const r = await axios.post(`${API}/acaso/deliberate`, {
        challenge, challenge_type: challengeType, preset_id: presetId,
        context: extra ? { additional_context: extra } : null,
      }, { timeout: 300000 });
      setResult(r.data);
      toast.success(`Council resolved in ${r.data.duration_s}s`);
      loadHistory();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Deliberation failed");
    } finally { setRunning(false); }
  };

  const openPast = async (id) => {
    try { const r = await axios.get(`${API}/acaso/deliberations/${id}`); setResult(r.data); window.scrollTo({ top: 0, behavior: "smooth" }); }
    catch { toast.error("Could not open deliberation"); }
  };

  const removePast = async (id) => {
    try {
      await axios.delete(`${API}/acaso/deliberations/${id}`);
      if (result?.id === id) setResult(null);
      loadHistory();
    } catch { toast.error("Delete failed"); }
  };

  const exportMd = (id) => { window.open(`${API}/acaso/deliberations/${id}/export`, "_blank"); };

  return (
    <div className="cw-wrap" data-testid="council-page">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><Crown size={18} /> Council of Weavers</div>
          <p>
            Four weavers on four models argue the challenge in parallel - <b>Architect</b> (thesis), <b>Shadow</b> (risk, can veto),
            <b> Muse</b> (contrarian + weak signals), <b>Finance</b> (numbers). The <b>Meta-Weaver</b> reconciles them into a
            Sovereign Directive with invalidation conditions. This is the live <code>/api/acaso/deliberate</code> engine
            the Genesis Engine and Sovereign Hunter scripts call.
          </p>
        </div>
        <div className="chr-hero-stats">
          <div className="chr-stat"><span className="v">{history.length}</span><span className="l">Deliberations</span></div>
          <div className="chr-stat gold"><span className="v">4+1</span><span className="l">Weavers</span></div>
        </div>
      </div>

      <div className="cw-honesty" data-testid="council-honesty">
        <Info size={14} /> Outputs are multi-model reasoning only. No live market feeds, on-chain data or lead databases are connected;
        "weak signals" are inferred, not measured. Not financial advice - the operator owns every decision.
      </div>

      <div className="fa-console">
        <div className="fa-head"><Sparkles size={16} /> Directive <em>pick a preset, edit freely, then convene</em></div>
        <div className="cw-presets">
          {presets.map((p) => {
            const Icon = PRESET_ICON[p.id] || Sparkles;
            return (
              <button key={p.id} data-testid={`preset-${p.id}`}
                className={presetId === p.id ? "cw-preset active" : "cw-preset"} onClick={() => applyPreset(p)}>
                <Icon size={15} />
                <span><b>{p.name}</b><small>{p.tagline}</small></span>
              </button>
            );
          })}
          <button data-testid="preset-custom" className={presetId === "custom" ? "cw-preset active" : "cw-preset"}
            onClick={() => { setPresetId("custom"); setChallenge(""); setChallengeType("general"); setExtra(""); }}>
            <Play size={15} /><span><b>Custom</b><small>Any challenge - strategy, launch, hire, pricing, threat.</small></span>
          </button>
        </div>

        <textarea data-testid="council-challenge" className="cw-textarea" rows={12} value={challenge}
          onChange={(e) => setChallenge(e.target.value)} placeholder="State the challenge the council must resolve..." />
        <div className="cw-row">
          <input data-testid="council-type" className="cw-input" value={challengeType} onChange={(e) => setChallengeType(e.target.value)}
            placeholder="challenge_type (e.g. product_strategy)" />
          <input data-testid="council-context" className="cw-input grow" value={extra} onChange={(e) => setExtra(e.target.value)}
            placeholder="Operator context (optional)" />
          <button data-testid="council-run" className="fa-btn primary" onClick={run} disabled={running}>
            {running ? <Loader2 className="spin" size={15} /> : <Crown size={15} />} {running ? "Council in session..." : "Convene Council"}
          </button>
        </div>
        {running && (
          <div className="cw-running" data-testid="council-running">
            {["Architect", "Shadow", "Muse", "Finance"].map((n, i) => (
              <motion.span key={n} initial={{ opacity: 0.3 }} animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1.6, delay: i * 0.3 }}>{n}</motion.span>
            ))}
            <span className="cw-arrow">→ Meta-Weaver</span>
          </div>
        )}
      </div>

      <AnimatePresence>
        {result && (
          <motion.div className="cw-result" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} data-testid="council-result">
            <div className="cw-result-head">
              <div>
                <div className="fa-head"><Crown size={16} /> Sovereign Directive
                  {result.shadow_veto && <span className="cw-veto" data-testid="shadow-veto">SHADOW VETO</span>}
                </div>
                <div className="cw-meta">
                  {fmtDate(result.timestamp)} · {result.duration_s}s · {result.challenge_type} · Council: {(result.council_consulted || []).join(", ")}
                </div>
              </div>
              <button className="fa-btn" data-testid="council-export" onClick={() => exportMd(result.id)}><Download size={14} /> Export .md</button>
            </div>

            <div className="cw-grid">
              <div className="cw-directive"><Markdown text={result.sovereign_directive} /></div>
              <aside className="cw-side">
                <div className="cw-signals">
                  <div className="cw-side-title"><Radar size={14} /> Weak signals <small>inferred</small></div>
                  <Markdown text={result.weak_signals || "_The council did not surface distinct weak signals._"} />
                </div>
                <div className="cw-side-title"><History size={14} /> Weavers</div>
                {(result.weavers || []).map((w) => {
                  const Icon = WEAVER_ICON[w.id] || Sparkles;
                  const open = openWeaver === w.id;
                  return (
                    <div key={w.id} className={`cw-weaver ${w.ok ? "" : "down"}`} data-testid={`weaver-${w.id}`}>
                      <button className="cw-weaver-h" onClick={() => setOpenWeaver(open ? null : w.id)}>
                        <Icon size={14} /> <b>{w.name}</b> <span>{w.role}</span>
                        <em>{w.model_label}</em> <ChevronRight size={14} className={open ? "rot" : ""} />
                      </button>
                      {open && <div className="cw-weaver-b"><Markdown text={w.analysis} /></div>}
                    </div>
                  );
                })}
              </aside>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="fa-console">
        <div className="fa-head"><History size={16} /> Past deliberations <em>{history.length} stored</em></div>
        {history.length === 0 ? (
          <div className="attach-empty" data-testid="council-history-empty">No deliberations yet. Convene the council above - every session is journaled here.</div>
        ) : (
          <div className="cw-history" data-testid="council-history">
            {history.map((h) => (
              <div key={h.id} className="cw-hrow">
                <button className="cw-hmain" onClick={() => openPast(h.id)} data-testid={`history-${h.id}`}>
                  <span className={`bb-tag`}>{h.preset_id || "custom"}</span>
                  <span className="cw-htitle">{h.title}</span>
                  <span className="cw-hmeta">{fmtDate(h.timestamp)} · {h.duration_s}s{h.shadow_veto ? " · VETO" : ""}</span>
                </button>
                <button className="attach-btn" title="Export" onClick={() => exportMd(h.id)}><Download size={13} /></button>
                <button className="attach-btn danger" title="Delete" onClick={() => removePast(h.id)}><Trash2 size={13} /></button>
              </div>
            ))}
          </div>
        )}
      </div>

      {openWeaver && !result && <button className="cw-close" onClick={() => setOpenWeaver(null)}><X size={14} /></button>}
    </div>
  );
}
