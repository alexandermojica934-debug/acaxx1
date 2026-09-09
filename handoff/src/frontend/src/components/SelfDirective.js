import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Wand2, Loader2, ShieldAlert, Lock, FileCode, Check, X, RotateCcw,
  Search, History, AlertTriangle, GitCommitHorizontal, CheckCircle2, ScrollText
} from "lucide-react";
import { API } from "../App";

function DiffView({ diff }) {
  const lines = (diff || "").split("\n");
  return (
    <pre className="sd-diff">
      {lines.map((ln, i) => {
        let cls = "sd-dl";
        if (ln.startsWith("+++") || ln.startsWith("---")) cls = "sd-dl meta";
        else if (ln.startsWith("@@")) cls = "sd-dl hunk";
        else if (ln.startsWith("+")) cls = "sd-dl add";
        else if (ln.startsWith("-")) cls = "sd-dl del";
        return <div key={i} className={cls}>{ln || " "}</div>;
      })}
    </pre>
  );
}

export default function SelfDirective() {
  const [manifest, setManifest] = useState(null);
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState([]);
  const [instruction, setInstruction] = useState("");
  const [proposing, setProposing] = useState(false);
  const [proposal, setProposal] = useState(null);
  const [applying, setApplying] = useState(false);
  const [rolling, setRolling] = useState(false);
  const [history, setHistory] = useState([]);

  const loadManifest = useCallback(async () => {
    try { const r = await axios.get(`${API}/self/manifest`); setManifest(r.data); }
    catch (e) { console.error(e); }
  }, []);
  const loadHistory = useCallback(async () => {
    try { const r = await axios.get(`${API}/self/history`); setHistory(r.data); }
    catch (e) { console.error(e); }
  }, []);

  useEffect(() => { loadManifest(); loadHistory(); }, [loadManifest, loadHistory]);

  const toggle = (path) => {
    setSelected((s) => s.includes(path) ? s.filter((x) => x !== path) : (s.length >= 5 ? (toast.warning("Max 5 files per directive"), s) : [...s, path]));
  };

  const propose = async () => {
    if (!instruction.trim()) { toast.error("Describe what you want changed"); return; }
    if (!selected.length) { toast.error("Select at least one file"); return; }
    setProposing(true);
    setProposal(null);
    try {
      const r = await axios.post(`${API}/self/propose`, { instruction: instruction.trim(), paths: selected });
      setProposal(r.data);
      toast.success("Patch proposal ready — review the diff");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Proposal failed");
    } finally { setProposing(false); }
  };

  const apply = async () => {
    if (!proposal) return;
    setApplying(true);
    try {
      const r = await axios.post(`${API}/self/apply`, { id: proposal.id, approved: true });
      setProposal((p) => ({ ...p, status: r.data.status }));
      toast.success("Applied to preview source — hot-reload will pick it up");
      await loadHistory();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Apply failed");
    } finally { setApplying(false); }
  };

  const rollback = async (id) => {
    setRolling(true);
    try {
      await axios.post(`${API}/self/rollback`, { id });
      if (proposal?.id === id) setProposal((p) => ({ ...p, status: "rolled_back" }));
      toast.success("Rolled back — original source restored");
      await loadHistory();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Rollback failed");
    } finally { setRolling(false); }
  };

  const files = (manifest?.files || []).filter((f) => f.path.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div className="sd-wrap" data-testid="self-directive">
      <section className="sd-console">
        <div className="sd-head">
          <Wand2 size={17} /> <span>Self-Directive</span>
          <em>Instruct ACASO to modify its own source — reviewed, approved, reversible.</em>
        </div>
        <div className="sd-warn" data-testid="self-preview-warning">
          <Lock size={14} />
          <div>
            <b>Preview-only & approval-gated.</b> This edits source in the live preview workspace and is <b>disabled after production deployment</b>. Every change is shown as a diff first, applied only on your approval, and can be rolled back.
          </div>
        </div>
      </section>

      <div className="sd-grid">
        <section className="sd-picker">
          <div className="sd-sub-head"><FileCode size={14} /> Source Allowlist <span className="sd-count">{selected.length}/5</span></div>
          <div className="sd-search"><Search size={13} /><input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Filter files…" data-testid="self-file-filter" /></div>
          <div className="sd-files" data-testid="self-file-list">
            {files.map((f) => (
              <label key={f.path} className={selected.includes(f.path) ? "sd-file sel" : "sd-file"} data-testid={`self-file-${f.path}`}>
                <input type="checkbox" checked={selected.includes(f.path)} onChange={() => toggle(f.path)} />
                <span className="sd-fpath">{f.path}</span>
                <span className="sd-fsize">{(f.size / 1024).toFixed(1)}k</span>
              </label>
            ))}
            {files.length === 0 && <div className="sd-empty-sm">No files match.</div>}
          </div>
          {manifest && (
            <div className="sd-deny"><ShieldAlert size={12} /> Blocked: {manifest.denylist.slice(0, 6).join(", ")}…</div>
          )}
        </section>

        <section className="sd-main">
          <textarea
            data-testid="self-instruction"
            className="sd-instruction"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="Describe the change in plain English. e.g. 'On the Bug Bounty tab, rename the Run Engagement button to Launch Engagement' or 'Add a subtitle under the ACASO title in the header'"
            rows={3}
          />
          <button className="sd-propose" data-testid="self-propose" onClick={propose} disabled={proposing}>
            {proposing ? <Loader2 className="spin" size={16} /> : <Wand2 size={16} />}
            {proposing ? "Generating patch…" : "Generate Patch Proposal"}
          </button>

          {proposing && (
            <div className="sd-skeleton">{[...Array(6)].map((_, i) => <div key={i} className="sd-sk" style={{ width: `${88 - i * 7}%` }} />)}</div>
          )}

          <AnimatePresence>
            {proposal && (
              <motion.div className="sd-proposal" data-testid="self-proposal" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                <div className="sd-prop-head">
                  <GitCommitHorizontal size={15} /> Patch Proposal
                  <span className={`sd-status s-${proposal.status}`}>{proposal.status}</span>
                  <span className="sd-model">{proposal.model_label}</span>
                </div>
                {proposal.explanation && <p className="sd-expl">{proposal.explanation}</p>}
                {proposal.test_plan && <div className="sd-testplan"><ScrollText size={12} /> <span><b>Test plan:</b> {proposal.test_plan}</span></div>}
                {proposal.diffs?.map((d) => (
                  <div key={d.path} className="sd-diff-block">
                    <div className="sd-diff-head"><FileCode size={12} /> {d.path} <span className="sd-add">+{d.added}</span> <span className="sd-del">-{d.removed}</span></div>
                    <DiffView diff={d.diff} />
                  </div>
                ))}

                <div className="sd-prop-actions">
                  {proposal.status === "proposed" && (
                    <button className="sd-apply" data-testid="self-apply" onClick={apply} disabled={applying}>
                      {applying ? <Loader2 className="spin" size={15} /> : <Check size={15} />} Approve & Apply
                    </button>
                  )}
                  {proposal.status === "applied" && (
                    <>
                      <span className="sd-applied"><CheckCircle2 size={15} /> Applied to preview</span>
                      <button className="sd-rollback" data-testid="self-rollback" onClick={() => rollback(proposal.id)} disabled={rolling}>
                        {rolling ? <Loader2 className="spin" size={15} /> : <RotateCcw size={15} />} Rollback
                      </button>
                    </>
                  )}
                  {proposal.status === "rolled_back" && <span className="sd-rolled"><RotateCcw size={15} /> Rolled back</span>}
                  <button className="sd-discard" onClick={() => setProposal(null)}><X size={14} /> Dismiss</button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {history.length > 0 && (
            <div className="sd-history" data-testid="self-history">
              <div className="sd-sub-head"><History size={14} /> Directive History</div>
              {history.map((h) => (
                <div key={h.id} className="sd-hrow">
                  <span className={`sd-status s-${h.status}`}>{h.status}</span>
                  <span className="sd-hinstr" title={h.instruction}>{h.instruction}</span>
                  <span className="sd-hpaths">{(h.paths || []).join(", ")}</span>
                  {h.status === "applied" && (
                    <button className="sd-hroll" onClick={() => rollback(h.id)} disabled={rolling} title="Rollback"><RotateCcw size={12} /></button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
