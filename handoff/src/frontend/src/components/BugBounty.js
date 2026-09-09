import React, { useEffect, useState, useCallback, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldAlert, Send, Loader2, Zap, Play, CheckCircle2, Circle, Trash2,
  Bug, Crosshair, FileText, ChevronDown, ChevronUp, ShieldCheck, Banknote,
  Target, Activity, AlertTriangle, Radar, Users, Crown, Eye, Cpu, Flame
} from "lucide-react";
import { API } from "../App";

const SOUL_ICON = { vision: Eye, fusion: Cpu, rebirth: Flame };
const SOUL_COLOR = { vision: "#4fd1ff", fusion: "#8b7cff", rebirth: "#ff7a90" };

const PLATFORMS = ["Auto", "HackerOne", "Bugcrowd", "Intigriti", "Self-hosted VDP"];
const BB_STAGES = ["Program", "Recon", "Vuln Found", "PoC", "Disclosure", "Triage", "Payout"];
const SAMPLES = [
  "Find and responsibly disclose an IDOR on a fintech API and collect the bounty",
  "Hunt a stored XSS on a SaaS dashboard within an authorized HackerOne program",
  "Report an SSRF on a cloud provider's metadata endpoint for a Critical payout",
  "Discover a broken-auth flaw on a public VDP and get it triaged & paid",
];
const SEV_COLOR = { Critical: "#ff5470", High: "#f5843c", Medium: "#f5c451", Low: "#4fd1ff", Info: "#9aa0c8" };

const fmtTime = (iso) => { try { return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }); } catch { return ""; } };

function ReportView({ text }) {
  if (!text) return null;
  const lines = text.split("\n");
  return (
    <div className="bb-report">
      {lines.map((ln, i) => {
        const t = ln.trim();
        if (t.startsWith("## ")) return <h4 key={i}>{t.replace(/^##\s*/, "")}</h4>;
        if (t.startsWith("# ")) return <h3 key={i}>{t.replace(/^#\s*/, "")}</h3>;
        if (!t) return <div key={i} className="bb-gap" />;
        return <p key={i}>{t}</p>;
      })}
    </div>
  );
}

export default function BugBounty() {
  const [directive, setDirective] = useState("");
  const [platform, setPlatform] = useState("Auto");
  const [missions, setMissions] = useState([]);
  const [feed, setFeed] = useState([]);
  const [compiling, setCompiling] = useState(false);
  const [runningId, setRunningId] = useState(null);
  const [gate, setGate] = useState({});      // mid -> step title awaiting approval
  const [openReport, setOpenReport] = useState({});
  const [deploying, setDeploying] = useState(null);
  const [openCouncil, setOpenCouncil] = useState({});
  const runningRef = useRef(false);

  const load = useCallback(async () => {
    try {
      const [m, f] = await Promise.all([
        axios.get(`${API}/missions?kind=bugbounty`),
        axios.get(`${API}/action-feed?limit=40`),
      ]);
      setMissions(m.data);
      const ids = new Set(m.data.map((x) => x.id));
      setFeed(f.data.filter((x) => ids.has(x.mission_id)));
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const compile = async () => {
    if (!directive.trim()) { toast.error("Enter a security directive"); return; }
    setCompiling(true);
    try {
      const body = { directive, platform: platform === "Auto" ? null : platform };
      const r = await axios.post(`${API}/compile-bounty`, body);
      toast.success(`Engagement compiled: ${r.data.title}`);
      setDirective("");
      await load();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Compilation failed");
    } finally { setCompiling(false); }
  };

  const step = async (mid, approved) => {
    const r = await axios.post(`${API}/missions/${mid}/execute-step`, { approved });
    return r.data;
  };

  const autoRun = async (m, approved = false) => {
    if (runningRef.current) return;
    runningRef.current = true;
    setRunningId(m.id);
    setGate((g) => ({ ...g, [m.id]: null }));
    try {
      for (let i = 0; i < m.steps.length + 2; i++) {
        const data = await step(m.id, approved);
        await load();
        if (!data.log) break;
        if (data.log.status === "approval_required") {
          setGate((g) => ({ ...g, [m.id]: data.log.step_title }));
          toast.warning(`Owner sign-off required: "${data.log.step_title}"`);
          break;
        }
        await new Promise((res) => setTimeout(res, 650));
        const done = (await axios.get(`${API}/missions/${m.id}`)).data;
        if (done.status === "complete") { await load(); break; }
      }
    } catch (e) {
      toast.error("Run interrupted");
    } finally {
      runningRef.current = false;
      setRunningId(null);
    }
  };

  const approveContinue = async (m) => {
    setGate((g) => ({ ...g, [m.id]: null }));
    const fresh = (await axios.get(`${API}/missions/${m.id}`)).data;
    await autoRun(fresh, true);
    toast.success("Owner approved — disclosure authorized");
  };

  const remove = async (mid) => {
    try { await axios.delete(`${API}/missions/${mid}`); await load(); toast("Engagement archived"); }
    catch (e) { toast.error("Failed"); }
  };

  const deploySouls = async (mid) => {
    setDeploying(mid);
    try {
      await axios.post(`${API}/missions/${mid}/deploy-souls`);
      setOpenCouncil((o) => ({ ...o, [mid]: true }));
      toast.success("Soul Council convened — Eternal Throne delivered the verdict");
      await load();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Council failed");
    } finally { setDeploying(null); }
  };

  const money = (n) => `$${Number(n || 0).toLocaleString()}`;
  const stageIdx = (m) => Math.max(0, BB_STAGES.indexOf(m.stage));

  return (
    <div className="bb-wrap">
      <section className="bb-console">
        <div className="bb-head">
          <ShieldAlert size={17} /> <span>Bug Bounty Directive</span>
          <em>Authorized, in-scope security research — directive to bounty payout.</em>
        </div>
        <div className="dc-input">
          <textarea
            data-testid="bounty-input"
            value={directive}
            onChange={(e) => setDirective(e.target.value)}
            placeholder="e.g. Find and responsibly disclose an IDOR on a fintech API and collect the bounty"
            rows={2}
          />
          <button data-testid="bounty-compile" className="compile red" onClick={compile} disabled={compiling}>
            {compiling ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
            {compiling ? "Compiling…" : "Compile Engagement"}
          </button>
        </div>
        <div className="mode-row">
          {PLATFORMS.map((p) => (
            <button key={p} className={platform === p ? "mode active" : "mode"} onClick={() => setPlatform(p)}>
              {p}
            </button>
          ))}
        </div>
        <div className="samples">
          {SAMPLES.map((s) => <button key={s} className="sample" onClick={() => setDirective(s)}>{s}</button>)}
        </div>
        <div className="bb-ethic"><ShieldCheck size={13} /> Constitutional guardrail: in-scope assets only, non-weaponized PoCs, and mandatory owner sign-off before any disclosure or payout.</div>
      </section>

      {/* NEXUS security feed */}
      <section className="nexus" data-testid="bb-feed">
        <div className="nx-head">
          <Radar size={15} /> NEXUS Security Ops
          <span className="nx-sub">recon · scanners · report drafter</span>
          <span className={`nx-live ${runningId ? "on" : ""}`}><span className="pulse" /> {runningId ? "executing" : "idle"}</span>
        </div>
        {feed.length === 0 ? (
          <div className="nx-empty">No security actions yet. Compile an engagement and run it — NEXUS logs recon, PoC and disclosure evidence here.</div>
        ) : (
          <div className="nx-log">
            <AnimatePresence initial={false}>
              {feed.map((f) => (
                <motion.div key={f.id} className={`nx-row ${f.status}`} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} layout>
                  <span className="nx-time">{fmtTime(f.timestamp)}</span>
                  <span className={`nx-badge ${f.status}`}>{f.status === "approval_required" ? <AlertTriangle size={11} /> : <Activity size={11} />}</span>
                  <span className="nx-body"><b>{f.mission_title}</b> · {f.action}<em> ⟶ {f.evidence}</em></span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </section>

      <section className="board">
        <div className="board-head"><Bug size={16} /> Active Engagements</div>
        {missions.length === 0 ? (
          <div className="empty"><ShieldAlert size={26} /><p>No engagements yet. Issue a bug-bounty directive and ACASO compiles a full authorized engagement — program, scope, severity, non-weaponized PoC, disclosure report and payout path.</p></div>
        ) : (
          <div className="bb-grid">
            {missions.map((m) => {
              const busy = runningId === m.id;
              const undone = m.steps.filter((s) => !s.done).length;
              const gated = gate[m.id];
              return (
                <motion.div key={m.id} data-testid="bounty-card" className={`bb-card ${m.status}`} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} layout>
                  <div className="bb-card-top">
                    <span className="bb-plat">{m.platform || "VDP"}</span>
                    <span className="bb-sev" style={{ color: SEV_COLOR[m.severity] || "#9aa0c8", borderColor: SEV_COLOR[m.severity] || "#333" }}>
                      {m.severity} · CVSS {m.cvss}
                    </span>
                  </div>
                  <h3>{m.title}</h3>
                  <div className="bb-prog">{m.program}</div>
                  <div className="bb-tags">
                    <span className="bb-tag"><Crosshair size={12} /> {m.asset}</span>
                    <span className="bb-tag"><Bug size={12} /> {m.vuln_type}</span>
                  </div>
                  <p className="m-summary">{m.summary}</p>

                  {/* security pipeline */}
                  <div className="bb-pipe">
                    {BB_STAGES.map((st, i) => (
                      <div key={st} className={`bb-pnode ${i <= stageIdx(m) ? "lit" : ""} ${m.stage === st ? "cur" : ""}`}>
                        <span className="bb-pdot" />
                        <span className="bb-plabel">{st}</span>
                      </div>
                    ))}
                  </div>

                  <div className="m-steps">
                    {m.steps.map((s) => (
                      <div key={s.id} className={`step ${s.done ? "done" : ""} ${busy && !s.done ? "pending" : ""}`} title={s.detail}>
                        {s.done ? <CheckCircle2 size={15} /> : (busy ? <Loader2 className="spin" size={15} /> : <Circle size={15} />)}
                        <span>{s.title}</span>
                      </div>
                    ))}
                  </div>

                  {gated && (
                    <div className="bb-gate">
                      <AlertTriangle size={14} /> Owner sign-off required at “{gated}”
                      <button data-testid="approve-btn" onClick={() => approveContinue(m)}>
                        <ShieldCheck size={14} /> Approve &amp; Continue
                      </button>
                    </div>
                  )}

                  {m.status !== "complete" && !gated && (
                    <div className="m-run">
                      <button className="run" onClick={() => autoRun(m, false)} disabled={busy || undone === 0}>
                        {busy ? <Loader2 className="spin" size={14} /> : <Play size={14} />} Run Engagement
                      </button>
                    </div>
                  )}

                  <div className="bb-meta">
                    <span><Banknote size={13} /> {m.payment_path}</span>
                    <span><Target size={13} /> {m.outcome_metric}</span>
                  </div>

                  <button className="bb-report-toggle" onClick={() => setOpenReport((o) => ({ ...o, [m.id]: !o[m.id] }))}>
                    <FileText size={14} /> Responsible Disclosure Report {openReport[m.id] ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                  {openReport[m.id] && <ReportView text={m.report} />}

                  {/* Soul Council */}
                  <div className="bb-soul-bar">
                    <button
                      data-testid="deploy-souls"
                      className="deploy-souls"
                      onClick={() => deploySouls(m.id)}
                      disabled={deploying === m.id}
                    >
                      {deploying === m.id ? <Loader2 className="spin" size={15} /> : <Users size={15} />}
                      {deploying === m.id ? "Souls convening…" : (m.soul_council ? "Re-convene Soul Council" : "Deploy Soul Council")}
                    </button>
                    {m.soul_council && (
                      <button className="council-toggle" onClick={() => setOpenCouncil((o) => ({ ...o, [m.id]: !o[m.id] }))}>
                        {openCouncil[m.id] ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                      </button>
                    )}
                  </div>

                  {m.soul_council && openCouncil[m.id] && (
                    <motion.div className="council" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}>
                      <div className="council-head"><Users size={13} /> Soul Council — {m.soul_council.souls.filter((s) => s.ok).length} souls across {new Set(m.soul_council.souls.filter((s)=>s.ok).map((s)=>s.provider)).size} AI models</div>
                      <div className="souls-grid">
                        {m.soul_council.souls.map((s) => {
                          const Icon = SOUL_ICON[s.id] || Users;
                          return (
                            <div key={s.id} className={`soul ${s.ok ? "" : "down"}`} style={{ borderColor: SOUL_COLOR[s.id] + "55" }}>
                              <div className="soul-h" style={{ color: SOUL_COLOR[s.id] }}>
                                <Icon size={14} /> {s.name}
                                <span className="soul-model">{s.model_label}</span>
                              </div>
                              <div className="soul-role">{s.role}</div>
                              <p>{s.analysis}</p>
                            </div>
                          );
                        })}
                      </div>
                      <div className="throne">
                        <div className="throne-h"><Crown size={15} /> Eternal Throne · Soul Brain Verdict
                          <span className="throne-status">{m.soul_council.resolution.status}</span>
                        </div>
                        <div className="throne-row"><b>Root cause</b><span>{m.soul_council.resolution.root_cause}</span></div>
                        <div className="throne-row"><b>The fix</b><span>{m.soul_council.resolution.fix}</span></div>
                        <div className="throne-row"><b>Verify</b><span>{m.soul_council.resolution.verification}</span></div>
                        <div className="throne-conf">
                          <span>Confidence</span>
                          <div className="conf-bar"><div style={{ width: `${m.soul_council.resolution.confidence}%` }} /></div>
                          <span className="conf-num">{m.soul_council.resolution.confidence}%</span>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  <div className="m-foot">
                    <span className="m-amount">{money(m.amount)}</span>
                    <span className={`m-status s-${m.status}`}>{m.status === "complete" ? "PAID" : m.stage}</span>
                    <div className="m-actions"><button onClick={() => remove(m.id)} title="Archive"><Trash2 size={16} /></button></div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
