import React, { useEffect, useState, useCallback, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send, Hammer, Search, MoveRight, Banknote, Sparkles, CheckCircle2,
  Circle, Trash2, PauseCircle, PlayCircle, Compass, ShieldCheck, Loader2,
  ScrollText, Target, Wallet, Zap, Activity, Play, AlertTriangle
} from "lucide-react";
import { API } from "../App";

const MODES = [
  { key: "Make", icon: Hammer, desc: "Create assets" },
  { key: "Find", icon: Search, desc: "Discover opportunity" },
  { key: "Move", icon: MoveRight, desc: "Advance a mission" },
  { key: "Collect", icon: Banknote, desc: "Get paid" },
];

const STAGES = ["Directive", "Discovery", "Deliverable", "Outreach", "Payment", "Receipt"];

const SAMPLES = [
  "Land a $750 freelance logo design client this week",
  "Turn my Python skills into a paid automation gig",
  "Sell a Notion productivity template pack online",
  "Get 3 paying newsletter sponsors for my tech blog",
];

const fmtTime = (iso) => {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch { return ""; }
};

export default function SovereignHome() {
  const [directive, setDirective] = useState("");
  const [mode, setMode] = useState("Move");
  const [missions, setMissions] = useState([]);
  const [stats, setStats] = useState(null);
  const [feed, setFeed] = useState([]);
  const [compiling, setCompiling] = useState(false);
  const [nextRec, setNextRec] = useState(null);
  const [loadingNext, setLoadingNext] = useState(false);
  const [runningId, setRunningId] = useState(null);
  const runningRef = useRef(false);

  const load = useCallback(async () => {
    try {
      const [m, s, f] = await Promise.all([
        axios.get(`${API}/missions?kind=revenue`),
        axios.get(`${API}/stats`),
        axios.get(`${API}/action-feed?limit=40`),
      ]);
      setMissions(m.data);
      setStats(s.data);
      setFeed(f.data);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const getPerfectNext = useCallback(async () => {
    setLoadingNext(true);
    try {
      const r = await axios.get(`${API}/perfect-next`);
      setNextRec(r.data);
    } catch (e) { /* silent */ } finally { setLoadingNext(false); }
  }, []);

  useEffect(() => { getPerfectNext(); }, [getPerfectNext, missions.length]);

  const compile = async () => {
    if (!directive.trim()) { toast.error("Speak a directive first"); return; }
    setCompiling(true);
    try {
      const r = await axios.post(`${API}/compile-directive`, { directive, mode });
      toast.success(`Mission compiled: ${r.data.title}`);
      setDirective("");
      await load();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Compilation failed");
    } finally { setCompiling(false); }
  };

  const executeNext = async (mid) => {
    const r = await axios.post(`${API}/missions/${mid}/execute-step`, {});
    return r.data; // { mission, log }
  };

  const runOne = async (mid) => {
    setRunningId(mid);
    try {
      const data = await executeNext(mid);
      if (data.log) {
        if (data.log.status === "approval_required") {
          toast.warning(`Owner approval required: ${data.log.step_title}`);
        } else {
          toast.success(`NEXUS: ${data.log.action.slice(0, 60)}`);
        }
      } else {
        toast("All steps already executed");
      }
      await load();
    } catch (e) {
      toast.error("NEXUS action failed");
    } finally { setRunningId(null); }
  };

  const autoRun = async (m) => {
    if (runningRef.current) return;
    runningRef.current = true;
    setRunningId(m.id);
    try {
      let remaining = m.steps.filter((s) => !s.done).length;
      while (remaining > 0) {
        const data = await executeNext(m.id);
        await load();
        if (!data.log || data.log.status === "approval_required") {
          if (data.log?.status === "approval_required") {
            toast.warning(`Paused: owner approval required at "${data.log.step_title}"`);
          }
          break;
        }
        remaining -= 1;
        await new Promise((res) => setTimeout(res, 650));
      }
      toast.success("NEXUS run complete");
    } catch (e) {
      toast.error("Auto-run interrupted");
    } finally {
      runningRef.current = false;
      setRunningId(null);
    }
  };

  const advance = async (mid, stepId, done) => {
    try {
      await axios.patch(`${API}/missions/${mid}/advance`, { step_id: stepId, done });
      await load();
    } catch (e) { toast.error("Could not advance"); }
  };

  const toggleStatus = async (m) => {
    const next = m.status === "paused" ? "active" : "paused";
    try {
      await axios.patch(`${API}/missions/${m.id}/status?status=${next}`);
      await load();
    } catch (e) { toast.error("Failed"); }
  };

  const remove = async (mid) => {
    try {
      await axios.delete(`${API}/missions/${mid}`);
      toast("Mission archived");
      await load();
    } catch (e) { toast.error("Failed"); }
  };

  const money = (n) => `$${Number(n || 0).toLocaleString()}`;

  return (
    <div className="home-wrap">
      {/* Directive console */}
      <section className="directive-console">
        <div className="dc-head">
          <Compass size={16} />
          <span>Directive Console</span>
          <em>Speak an outcome that ends in a payment.</em>
        </div>
        <div className="dc-input">
          <textarea
            data-testid="directive-input"
            value={directive}
            onChange={(e) => setDirective(e.target.value)}
            placeholder="e.g. Land a $750 logo client this week and get them to pay via Stripe"
            rows={2}
            onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) compile(); }}
          />
          <button data-testid="compile-btn" className="compile" onClick={compile} disabled={compiling}>
            {compiling ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
            {compiling ? "Compiling…" : "Compile Mission"}
          </button>
        </div>
        <div className="mode-row">
          {MODES.map((m) => {
            const Icon = m.icon;
            return (
              <button
                key={m.key}
                data-testid={`mode-${m.key}`}
                className={mode === m.key ? "mode active" : "mode"}
                onClick={() => setMode(m.key)}
                title={m.desc}
              >
                <Icon size={15} /> {m.key}
              </button>
            );
          })}
        </div>
        <div className="samples">
          {SAMPLES.map((s) => (
            <button key={s} className="sample" onClick={() => setDirective(s)}>{s}</button>
          ))}
        </div>
      </section>

      {/* Metrics + Perfect Next */}
      <section className="row-2">
        <div className="metrics">
          <Metric icon={Target} label="Active Missions" value={stats?.active ?? 0} />
          <Metric icon={CheckCircle2} label="Completed" value={stats?.complete ?? 0} />
          <Metric icon={Wallet} label="Projected" value={money(stats?.projected_revenue)} accent />
          <Metric icon={Banknote} label="Collected" value={money(stats?.collected_revenue)} gold />
        </div>

        <div className="perfect-next" data-testid="perfect-next">
          <div className="pn-head"><Sparkles size={15} /> Perfect Next <span className="gov">Soul Brain</span></div>
          {loadingNext ? (
            <div className="pn-loading"><Loader2 className="spin" size={16} /> Governing…</div>
          ) : (
            <p className="pn-body">{nextRec?.recommendation || "Awaiting your first directive."}</p>
          )}
          {nextRec?.mission_title && <div className="pn-target">→ {nextRec.mission_title}</div>}
        </div>
      </section>

      {/* Payment pipeline */}
      <section className="pipeline">
        <div className="pl-head"><Banknote size={15} /> Payment Pipeline</div>
        <div className="pl-track">
          {STAGES.map((st, i) => {
            const count = stats?.pipeline?.[st] || 0;
            return (
              <div key={st} className={`pl-stage ${count ? "lit" : ""}`}>
                <div className="pl-dot">{count}</div>
                <span>{st}</span>
                {i < STAGES.length - 1 && <div className="pl-line" />}
              </div>
            );
          })}
        </div>
      </section>

      {/* NEXUS Action Bus feed */}
      <section className="nexus" data-testid="nexus-feed">
        <div className="nx-head">
          <Zap size={15} /> NEXUS Action Bus
          <span className="nx-sub">trusted execution surface</span>
          <span className={`nx-live ${runningId ? "on" : ""}`}>
            <span className="pulse" /> {runningId ? "executing" : "idle"}
          </span>
        </div>
        {feed.length === 0 ? (
          <div className="nx-empty">No actions executed yet. Run a mission step and NEXUS logs verifiable evidence here.</div>
        ) : (
          <div className="nx-log">
            <AnimatePresence initial={false}>
              {feed.map((f) => (
                <motion.div
                  key={f.id}
                  className={`nx-row ${f.status}`}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  layout
                >
                  <span className="nx-time">{fmtTime(f.timestamp)}</span>
                  <span className={`nx-badge ${f.status}`}>
                    {f.status === "approval_required" ? <AlertTriangle size={11} /> : <Activity size={11} />}
                  </span>
                  <span className="nx-body">
                    <b>{f.mission_title}</b> · {f.action}
                    <em> ⟶ evidence: {f.evidence}</em>
                  </span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </section>

      {/* Mission board */}
      <section className="board">
        <div className="board-head"><ScrollText size={16} /> Mission Board</div>
        {missions.length === 0 ? (
          <div className="empty">
            <Sparkles size={26} />
            <p>No missions yet. Issue a directive above and ACASO will compile a full mission graph — steps, evidence, payment path and outcome metric.</p>
          </div>
        ) : (
          <div className="mission-grid">
            <AnimatePresence>
              {missions.map((m) => {
                const undone = m.steps.filter((s) => !s.done).length;
                const busy = runningId === m.id;
                return (
                <motion.div
                  key={m.id}
                  data-testid="mission-card"
                  className={`mission ${m.status}`}
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.96 }}
                  layout
                >
                  <div className="m-top">
                    <span className={`m-mode mode-${m.mode}`}>{m.mode}</span>
                    <span className={`m-status s-${m.status}`}>{m.status}</span>
                  </div>
                  <h3>{m.title}</h3>
                  <p className="m-summary">{m.summary}</p>

                  <div className="m-steps">
                    {m.steps.map((s) => (
                      <button
                        key={s.id}
                        className={`step ${s.done ? "done" : ""} ${busy && !s.done ? "pending" : ""}`}
                        onClick={() => advance(m.id, s.id, !s.done)}
                        title={s.detail}
                      >
                        {s.done ? <CheckCircle2 size={15} /> : (busy ? <Loader2 className="spin" size={15} /> : <Circle size={15} />)}
                        <span>{s.title}</span>
                      </button>
                    ))}
                  </div>

                  {m.status !== "complete" && (
                    <div className="m-run">
                      <button data-testid="run-next-btn" className="run" onClick={() => runOne(m.id)} disabled={busy || undone === 0}>
                        <Play size={14} /> Run Next
                      </button>
                      <button data-testid="autorun-btn" className="run auto" onClick={() => autoRun(m)} disabled={busy || undone === 0}>
                        {busy ? <Loader2 className="spin" size={14} /> : <Zap size={14} />} Auto-run ({undone})
                      </button>
                    </div>
                  )}

                  <div className="m-meta">
                    <div><Banknote size={13} /> {m.payment_path || "—"}</div>
                    <div><Target size={13} /> {m.outcome_metric || "—"}</div>
                    <div className="m-auth"><ShieldCheck size={13} /> {m.authority}</div>
                  </div>

                  {m.evidence?.length > 0 && (
                    <div className="m-evidence">
                      {m.evidence.map((e, i) => <span key={i}>{e}</span>)}
                    </div>
                  )}

                  <div className="m-foot">
                    <span className="m-amount">{money(m.amount)}</span>
                    <span className="m-stage">{m.stage}</span>
                    <div className="m-actions">
                      <button onClick={() => toggleStatus(m)} title={m.status === "paused" ? "Resume" : "Pause"}>
                        {m.status === "paused" ? <PlayCircle size={17} /> : <PauseCircle size={17} />}
                      </button>
                      <button onClick={() => remove(m.id)} title="Archive"><Trash2 size={16} /></button>
                    </div>
                  </div>
                </motion.div>
              );})}
            </AnimatePresence>
          </div>
        )}
      </section>
    </div>
  );
}

function Metric({ icon: Icon, label, value, accent, gold }) {
  return (
    <div className={`metric ${accent ? "accent" : ""} ${gold ? "gold" : ""}`}>
      <Icon size={16} />
      <div>
        <span className="m-val">{value}</span>
        <span className="m-lab">{label}</span>
      </div>
    </div>
  );
}
