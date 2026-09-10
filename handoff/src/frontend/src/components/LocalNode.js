import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  MonitorSmartphone, Wifi, WifiOff, Download, KeyRound, ShieldCheck, Check, X, Loader2, Play, Sparkles,
  FolderOpen, FileText, TerminalSquare, Globe, Camera, Trash2, RefreshCw, AlertTriangle, ChevronDown, ChevronUp, ExternalLink, Search
} from "lucide-react";
import { API } from "../App";

const KIND_ICON = { file_list: FolderOpen, file_read: FileText, file_stat: FileText, file_write: FileText, file_append: FileText, mkdir: FolderOpen,
  file_move: FolderOpen, file_delete: Trash2, shell: TerminalSquare, browser_open: Globe, browser_fill: Globe, browser_submit: Globe, browser_screenshot: Camera, browser_close: Globe, sys_info: MonitorSmartphone };
const KINDS = ["file_list", "file_read", "file_stat", "mkdir", "file_write", "file_append", "file_move", "file_delete", "shell", "browser_open", "browser_fill", "browser_screenshot", "browser_close"];
const fmt = (iso) => { try { return iso ? new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : ""; } catch { return ""; } };

export default function LocalNode() {
  const [nodes, setNodes] = useState([]);
  const [nodeId, setNodeId] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [setup, setSetup] = useState(null);
  const [bridgeKey, setBridgeKey] = useState(null);
  const [showKey, setShowKey] = useState(false);
  const [goal, setGoal] = useState("");
  const [planning, setPlanning] = useState(false);
  const [plan, setPlan] = useState(null);
  const [manual, setManual] = useState({ kind: "file_list", params: '{"path": ""}' });
  const [open, setOpen] = useState(null);
  const [detail, setDetail] = useState(null);
  const [research, setResearch] = useState({ url: "", question: "" });
  const [researching, setResearching] = useState(false);
  const [page, setPage] = useState(null);
  const [showSetup, setShowSetup] = useState(true);

  const load = useCallback(async () => {
    try {
      const [n, s] = await Promise.all([axios.get(`${API}/node/nodes`), setup ? Promise.resolve({ data: setup }) : axios.get(`${API}/node/setup`)]);
      setNodes(n.data); setSetup(s.data);
      if (!nodeId && n.data[0]) setNodeId(n.data[0].id);
      if (n.data.length) setShowSetup(false);
    } catch { /* silent */ }
  }, [nodeId, setup]);
  const loadTasks = useCallback(async () => {
    if (!nodeId) { setTasks([]); return; }
    try { setTasks((await axios.get(`${API}/node/tasks`, { params: { node_id: nodeId, limit: 80 } })).data); } catch { /* silent */ }
  }, [nodeId]);

  useEffect(() => { load(); const t = setInterval(load, 10000); return () => clearInterval(t); }, [load]);
  useEffect(() => { loadTasks(); const t = setInterval(loadTasks, 4000); return () => clearInterval(t); }, [loadTasks]);

  const revealKey = async () => {
    try { const r = await axios.get(`${API}/bridge/info`); setBridgeKey(r.data.api_key); setShowKey(true); } catch { toast.error("Could not fetch key"); }
  };
  const decide = async (id, approved) => {
    try { await axios.post(`${API}/node/tasks/${id}/decision`, { approved }); toast[approved ? "success" : "info"](approved ? "Approved - the node will run it" : "Rejected"); loadTasks(); }
    catch (e) { toast.error(e?.response?.data?.detail || "Failed"); }
  };
  const cancel = async (id) => { try { await axios.post(`${API}/node/tasks/${id}/cancel`); loadTasks(); } catch { /* ignore */ } };
  const approveAll = async () => { for (const t of tasks.filter((x) => x.status === "proposed")) await axios.post(`${API}/node/tasks/${t.id}/decision`, { approved: true }); toast.success("All pending tasks approved"); loadTasks(); };

  const doPlan = async () => {
    if (!goal.trim() || !nodeId) return;
    setPlanning(true);
    try { const r = await axios.post(`${API}/node/plan`, { node_id: nodeId, goal }, { timeout: 120000 }); setPlan(r.data); toast.success(`${r.data.tasks.length} task(s) proposed - review and approve below`); loadTasks(); }
    catch (e) { toast.error(e?.response?.data?.detail || "Planner failed"); }
    finally { setPlanning(false); }
  };
  const addManual = async () => {
    let params;
    try { params = JSON.parse(manual.params || "{}"); } catch { toast.error("Params must be valid JSON"); return; }
    try { await axios.post(`${API}/node/tasks`, { node_id: nodeId, kind: manual.kind, params }); toast.success("Task created"); loadTasks(); }
    catch (e) { toast.error(e?.response?.data?.detail || "Rejected"); }
  };
  const openDetail = async (id) => { try { setDetail((await axios.get(`${API}/node/tasks/${id}`)).data); } catch { /* ignore */ } };
  const submitFor = async (t) => {
    const sid = t.result?.session_id;
    if (!sid) return;
    try { await axios.post(`${API}/node/tasks`, { node_id: t.node_id, kind: "browser_submit", params: { session_id: sid }, title: `submit form in session ${sid}` }); toast.success("Submit step proposed - approve it in the queue to actually submit"); loadTasks(); }
    catch (e) { toast.error(e?.response?.data?.detail || "Failed"); }
  };
  const doResearch = async () => {
    if (!research.url.trim()) return;
    setResearching(true); setPage(null);
    try { setPage((await axios.post(`${API}/browse/research`, { url: research.url, question: research.question || null, screenshot: true }, { timeout: 120000 })).data); }
    catch (e) { toast.error(e?.response?.data?.detail || "Could not load page"); }
    finally { setResearching(false); }
  };

  const node = nodes.find((n) => n.id === nodeId);
  const pending = tasks.filter((t) => t.status === "proposed");
  const awaiting = tasks.filter((t) => t.status === "awaiting_submit");

  return (
    <div className="ln-wrap" data-testid="localnode-page">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><MonitorSmartphone size={18} /> Local Node</div>
          <p>ACASO cannot reach your PC from this server - so a small program you run <b>on your machine</b> pairs with your Agent Bridge key and executes tasks there: create and fix files inside folders you allow, run scripts, and drive a real Chrome window for sign-ups and forms. <b>Every write, command and browser action waits for your approval here.</b> Forms are filled but never submitted until you approve the submit step; you type passwords and 2FA yourself.</p>
        </div>
        <div className="chr-hero-stats">
          <div className={`chr-stat ${node?.online ? "gold" : ""}`}><span className="v">{node ? (node.online ? "ONLINE" : "OFFLINE") : "—"}</span><span className="l">{node?.name || "no node paired"}</span></div>
          <div className="chr-stat"><span className="v">{pending.length}</span><span className="l">awaiting approval</span></div>
        </div>
      </div>

      {/* Setup */}
      <div className="fa-console">
        <div className="fa-head" role="button" tabIndex={0} onClick={() => setShowSetup((s) => !s)} onKeyDown={(e) => e.key === "Enter" && setShowSetup((s) => !s)}><Download size={16} /> Install & pair {showSetup ? <ChevronUp size={14} /> : <ChevronDown size={14} />} <em>{nodes.length ? `${nodes.length} node(s) paired` : "no node yet"}</em></div>
        {showSetup && setup && (
          <div className="ln-setup" data-testid="localnode-setup">
            <ol>
              <li>Download <a href="/local-node/acaso_node.py" download data-testid="ln-download-py">acaso_node.py</a>, the <a href="/local-node/README.md" download>README</a>, and a launcher: <a href="/local-node/run_node.bat" download>run_node.bat</a> (Windows) / <a href="/local-node/run_node.sh" download>run_node.sh</a> (Linux).</li>
              <li>Install: <code>python -m pip install httpx</code> — for browser tasks also <code>python -m pip install playwright && python -m playwright install chrome</code>.</li>
              <li>Your key: {showKey && bridgeKey ? <code className="ln-key" data-testid="ln-key">{bridgeKey}</code> : <button className="fa-btn" onClick={revealKey} data-testid="ln-reveal-key"><KeyRound size={13} /> Reveal Agent Bridge key</button>} — paste it into the launcher or <code>ACASO_KEY</code>.</li>
              <li>Run it. Windows: <code>{setup.run_windows}</code></li>
              <li className="ln-dim">Linux: <code>{setup.run_linux}</code></li>
            </ol>
            <div className="ln-safety">{setup.safety.map((s) => <span key={s}><ShieldCheck size={12} /> {s}</span>)}</div>
          </div>
        )}
      </div>

      {/* Nodes */}
      {nodes.length > 0 && (
        <div className="ln-nodes" data-testid="ln-nodes">
          {nodes.map((n) => (
            <button key={n.id} className={`ln-node ${n.id === nodeId ? "active" : ""} ${n.online ? "on" : ""}`} onClick={() => setNodeId(n.id)} data-testid={`ln-node-${n.id}`}>
              {n.online ? <Wifi size={14} /> : <WifiOff size={14} />}
              <span><b>{n.name}</b><small>{n.os} · {n.hostname} · {(n.capabilities || []).join(", ")}</small><small>roots: {(n.allowed_roots || []).join(" | ")}</small><small>last seen {fmt(n.last_seen)}</small></span>
              {n.pending_approvals > 0 && <em>{n.pending_approvals}</em>}
            </button>
          ))}
        </div>
      )}

      {node && (
        <>
          {/* Planner + manual */}
          <div className="fa-console">
            <div className="fa-head"><Sparkles size={16} /> Give the node a goal <em>ACASO plans the steps; nothing runs until you approve each one</em></div>
            <div className="cw-row">
              <input data-testid="ln-goal" className="cw-input grow" value={goal} onChange={(e) => setGoal(e.target.value)} placeholder='e.g. "Organize my ACASO folder: move all PDFs into /invoices and write an index.md listing them"' onKeyDown={(e) => e.key === "Enter" && doPlan()} />
              <button data-testid="ln-plan" className="fa-btn primary" onClick={doPlan} disabled={planning || !goal.trim()}>{planning ? <Loader2 className="spin" size={14} /> : <Sparkles size={14} />} Plan tasks</button>
            </div>
            {plan && <div className="ln-plan" data-testid="ln-plan-summary"><b>Plan:</b> {plan.summary} <small>({plan.model_label})</small></div>}
            <details className="ln-manual">
              <summary>Add a single task manually</summary>
              <div className="cw-row">
                <select className="cw-input" value={manual.kind} onChange={(e) => setManual({ ...manual, kind: e.target.value })} data-testid="ln-manual-kind">{KINDS.map((k) => <option key={k}>{k}</option>)}</select>
                <input className="cw-input grow" value={manual.params} onChange={(e) => setManual({ ...manual, params: e.target.value })} placeholder='{"path": "C:\\Users\\you\\ACASO\\notes.txt", "content": "..."}' data-testid="ln-manual-params" />
                <button className="fa-btn" onClick={addManual} data-testid="ln-manual-add"><Play size={14} /> Queue</button>
              </div>
            </details>
          </div>

          {/* Awaiting submit */}
          {awaiting.length > 0 && (
            <div className="ln-await" data-testid="ln-awaiting">
              <div className="fa-head"><Globe size={16} /> Forms filled - waiting for your submit decision</div>
              {awaiting.map((t) => (
                <div key={t.id} className="ln-await-row">
                  <span>{t.title} · session <code>{t.result?.session_id}</code> · filled {t.result?.filled?.length || 0} field(s){t.result?.skipped?.length ? ` · ${t.result.skipped.length} for you to type` : ""}</span>
                  <button className="fa-btn" onClick={() => openDetail(t.id)}><Camera size={13} /> View screenshot</button>
                  <button className="fa-btn primary" onClick={() => submitFor(t)} data-testid="ln-propose-submit"><Check size={13} /> Propose submit</button>
                </div>
              ))}
            </div>
          )}

          {/* Queue */}
          <div className="fa-console">
            <div className="fa-head"><ShieldCheck size={16} /> Task queue {pending.length > 0 && <button className="fa-btn" style={{ marginLeft: 10 }} onClick={approveAll} data-testid="ln-approve-all"><Check size={13} /> Approve all {pending.length}</button>} <em><button className="attach-btn" onClick={loadTasks} title="Refresh"><RefreshCw size={13} /></button></em></div>
            {tasks.length === 0 ? <div className="attach-empty" data-testid="ln-empty">No tasks yet. Give the node a goal above.</div> : (
              <div className="ln-tasks" data-testid="ln-tasks">
                <AnimatePresence initial={false}>
                  {tasks.map((t) => { const I = KIND_ICON[t.kind] || FileText; const isOpen = open === t.id; return (
                    <motion.div key={t.id} className={`ln-task s-${t.status}`} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} data-testid={`ln-task-${t.id}`}>
                      <div className="ln-task-h">
                        <I size={14} />
                        <span className="ln-task-title" onClick={() => setOpen(isOpen ? null : t.id)} role="button" tabIndex={0} onKeyDown={(e) => e.key === "Enter" && setOpen(isOpen ? null : t.id)}>{t.title}</span>
                        <span className={`ln-status s-${t.status}`} data-testid="ln-task-status">{t.status.replace("_", " ")}</span>
                        <span className="ln-when">{fmt(t.created_at)}</span>
                        {t.status === "proposed" && <>
                          <button className="ln-ok" onClick={() => decide(t.id, true)} data-testid="ln-approve" title="Approve"><Check size={14} /></button>
                          <button className="ln-no" onClick={() => decide(t.id, false)} data-testid="ln-reject" title="Reject"><X size={14} /></button>
                        </>}
                        {t.status === "queued" && <button className="ln-no" onClick={() => cancel(t.id)} title="Cancel"><X size={14} /></button>}
                        {(t.status === "done" || t.status === "failed" || t.status === "awaiting_submit") && <button className="attach-btn" onClick={() => openDetail(t.id)} title="Result"><Search size={13} /></button>}
                      </div>
                      {isOpen && <pre className="ln-params">{JSON.stringify(t.params, null, 1)}</pre>}
                      {t.error && <div className="ln-err"><AlertTriangle size={12} /> {t.error}</div>}
                    </motion.div>); })}
                </AnimatePresence>
              </div>
            )}
          </div>
        </>
      )}

      {/* Server research browser */}
      <div className="fa-console">
        <div className="fa-head"><Globe size={16} /> Research browser (server) <em>headless Chromium here - public pages only; datacenter IP; no logins</em></div>
        <div className="cw-row">
          <input className="cw-input grow" data-testid="ln-research-url" value={research.url} onChange={(e) => setResearch({ ...research, url: e.target.value })} placeholder="https://..." />
          <input className="cw-input grow" data-testid="ln-research-q" value={research.question} onChange={(e) => setResearch({ ...research, question: e.target.value })} placeholder="Question about the page (optional)" />
          <button className="fa-btn primary" data-testid="ln-research-run" onClick={doResearch} disabled={researching || !research.url.trim()}>{researching ? <Loader2 className="spin" size={14} /> : <Globe size={14} />} Read page</button>
        </div>
        {page && (
          <div className="ln-page" data-testid="ln-research-result">
            <div className="ln-page-h"><b>{page.title}</b> · HTTP {page.http_status} · {page.chars} chars · {page.links.length} links · {page.forms.length} form(s) <a href={page.url} target="_blank" rel="noreferrer"><ExternalLink size={12} /></a></div>
            {page.answer && <div className="ln-answer"><Sparkles size={12} /> {page.answer.text || page.answer.error} <small>{page.answer.model_label}</small></div>}
            <div className="ln-page-grid">
              {page.screenshot_b64 && <img alt="page screenshot" src={`data:image/jpeg;base64,${page.screenshot_b64}`} className="ln-shot" />}
              <pre className="ln-text">{page.text_excerpt.slice(0, 3000)}</pre>
            </div>
            {page.forms.length > 0 && <div className="ln-forms">Forms detected: {page.forms.map((f, i) => <code key={i}>{f.fields.map((x) => x.name || x.placeholder || x.type).filter(Boolean).slice(0, 8).join(", ")}</code>)} — to fill one with your account, use the Local Node browser (browser_fill).</div>}
          </div>
        )}
      </div>

      <AnimatePresence>
        {detail && (
          <motion.div className="rd-modal-bg" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setDetail(null)} data-testid="ln-detail-modal">
            <motion.div className="rd-modal ln-detail" initial={{ y: 16 }} animate={{ y: 0 }} exit={{ y: 16 }} onClick={(e) => e.stopPropagation()}>
              <div className="rd-modal-h"><div><h2>{detail.title}</h2><div className="ln-when">{detail.kind} · {detail.status} · {fmt(detail.finished_at || detail.created_at)}</div></div><button className="rd-ic" onClick={() => setDetail(null)}><X size={16} /></button></div>
              {detail.screenshot_b64 && <img alt="node screenshot" className="ln-shot big" src={`data:image/jpeg;base64,${detail.screenshot_b64}`} />}
              {detail.result?.content !== undefined && <pre className="ln-text">{detail.result.content}</pre>}
              {detail.result?.stdout !== undefined && <pre className="ln-text">$ {detail.result.command}{"\n"}{detail.result.stdout}{detail.result.stderr ? `\n[stderr]\n${detail.result.stderr}` : ""}</pre>}
              {detail.result?.items && <pre className="ln-text">{detail.result.items.map((i) => `${i.type === "dir" ? "📁" : "  "} ${i.name}  ${i.size}`).join("\n")}</pre>}
              {detail.result && !detail.result.content && !detail.result.stdout && !detail.result.items && <pre className="ln-text">{JSON.stringify(detail.result, null, 1)}</pre>}
              {detail.error && <div className="ln-err"><AlertTriangle size={12} /> {detail.error}</div>}
              <details><summary className="ln-dim">Audit trail</summary><pre className="ln-text">{JSON.stringify(detail.audit, null, 1)}</pre></details>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
