import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  Plug, KeyRound, RefreshCw, Copy, Check, Terminal, Bot, Play, Loader2,
  Radio, Braces, ShieldCheck
} from "lucide-react";
import { API } from "../App";

const BACKEND = process.env.REACT_APP_BACKEND_URL;

function Copyable({ label, value, testid }) {
  const [done, setDone] = useState(false);
  const copy = async () => {
    try { await navigator.clipboard.writeText(value); setDone(true); setTimeout(() => setDone(false), 1500); }
    catch { toast.error("Copy failed"); }
  };
  return (
    <button className="copy-block" onClick={copy} data-testid={testid} title="Copy">
      <span className="cb-label">{label}</span>
      <span className="cb-val">{value}</span>
      <span className="cb-icon">{done ? <Check size={15} /> : <Copy size={15} />}</span>
    </button>
  );
}

export default function AgentBridge() {
  const [info, setInfo] = useState(null);
  const [activity, setActivity] = useState([]);
  const [tab, setTab] = useState("gemini");
  const [pgDirective, setPgDirective] = useState("Land a $500 landing-page copywriting client and collect payment");
  const [pgKind, setPgKind] = useState("revenue");
  const [pgOut, setPgOut] = useState(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [i, a] = await Promise.all([
        axios.get(`${API}/bridge/info`),
        axios.get(`${API}/bridge/activity?limit=25`),
      ]);
      setInfo(i.data);
      setActivity(a.data);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const regenerate = async () => {
    try { const r = await axios.post(`${API}/bridge/regenerate`); setInfo((p) => ({ ...p, api_key: r.data.api_key })); toast.success("New API key minted"); }
    catch (e) { toast.error("Failed"); }
  };

  const key = info?.api_key || "…";
  const base = `${BACKEND}/api/agent`;

  const curlSnippet = `curl -X POST ${base}/directive \\
  -H "Content-Type: application/json" \\
  -H "X-ACASO-Key: ${key}" \\
  -d '{"directive":"Land a $500 client and collect payment","kind":"revenue","agent":"Manus"}'`;

  const toolSchema = {
    name: "acaso_issue_directive",
    description: "Send a plain-language money-making directive to the ACASO Directive-to-Payment OS. ACASO compiles it into a mission graph (steps, evidence, payment path) and can execute it. Use kind='bugbounty' for authorized security research.",
    parameters: {
      type: "object",
      properties: {
        directive: { type: "string", description: "The outcome to achieve, ending in a payment." },
        kind: { type: "string", enum: ["revenue", "bugbounty"], description: "Mission type." },
        mode: { type: "string", enum: ["Make", "Find", "Move", "Collect"], description: "Operating mode (revenue only)." },
        platform: { type: "string", description: "Bug bounty platform (bugbounty only): HackerOne, Bugcrowd, Intigriti, Self-hosted VDP." },
        agent: { type: "string", description: "Your agent name, e.g. Gemini or Manus." },
      },
      required: ["directive"],
    },
  };

  const geminiConfig = JSON.stringify({
    tools: [{ function_declarations: [toolSchema] }],
    _endpoint: `${base}/directive`,
    _auth_header: { "X-ACASO-Key": key },
  }, null, 2);

  const openaiConfig = JSON.stringify({
    tools: [{ type: "function", function: toolSchema }],
    _endpoint: `${base}/directive`,
    _auth_header: { "X-ACASO-Key": key },
  }, null, 2);

  const manusConfig = JSON.stringify({
    name: "ACASO Directive-to-Payment",
    base_url: base,
    auth: { header: "X-ACASO-Key", value: key },
    actions: {
      issue_directive: { method: "POST", path: "/directive", body: { directive: "string", kind: "revenue|bugbounty", agent: "string" } },
      list_missions: { method: "GET", path: "/missions" },
      get_mission: { method: "GET", path: "/missions/{id}" },
      run_mission: { method: "POST", path: "/missions/{id}/run", body: { run: "next|all", approved: "boolean" } },
    },
  }, null, 2);

  const configs = { gemini: geminiConfig, openai: openaiConfig, manus: manusConfig, curl: curlSnippet };
  const copyConfig = async () => {
    try { await navigator.clipboard.writeText(configs[tab]); toast.success("Connector copied"); }
    catch { toast.error("Copy failed"); }
  };

  const runPlayground = async () => {
    setBusy(true); setPgOut(null);
    try {
      const r = await axios.post(`${API}/agent/directive`, {
        directive: pgDirective, kind: pgKind, agent: "Playground",
      }, { headers: { "X-ACASO-Key": key } });
      setPgOut(r.data);
      toast.success(`Mission created: ${r.data.title}`);
      await load();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Bridge call failed");
    } finally { setBusy(false); }
  };

  const fmt = (iso) => { try { return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }); } catch { return ""; } };

  return (
    <div className="bridge-wrap">
      <div className="br-hero">
        <div>
          <div className="br-title"><Plug size={18} /> Agent Bridge</div>
          <p>Let external agents — <b>Manus</b>, <b>Gemini</b>, <b>ChatGPT</b> — drive ACASO. They send directives and run missions through one authenticated API. Paste a connector below into your agent's tool config.</p>
        </div>
        <div className="br-live"><Radio size={14} /> Bridge online</div>
      </div>

      <div className="br-grid">
        <div className="br-col">
          <div className="br-card">
            <div className="br-card-h"><KeyRound size={15} /> Credentials <button className="br-regen" onClick={regenerate} data-testid="regen-key"><RefreshCw size={13} /> Regenerate</button></div>
            <Copyable label="API Key" value={key} testid="api-key" />
            <Copyable label="Auth Header" value={`X-ACASO-Key: ${key}`} />
            <Copyable label="Base URL" value={base} />
          </div>

          <div className="br-card">
            <div className="br-card-h"><Braces size={15} /> Connector / Tool Schema</div>
            <div className="br-conn-tabs">
              {[["gemini", "Gemini"], ["openai", "OpenAI / ChatGPT"], ["manus", "Manus / MCP"], ["curl", "cURL"]].map(([k, l]) => (
                <button key={k} className={tab === k ? "ct on" : "ct"} onClick={() => setTab(k)}>{l}</button>
              ))}
            </div>
            <pre className="br-code" data-testid="connector-code">{configs[tab]}</pre>
            <button className="br-copy" onClick={copyConfig}><Copy size={14} /> Copy connector</button>
          </div>
        </div>

        <div className="br-col">
          <div className="br-card">
            <div className="br-card-h"><Terminal size={15} /> Live Playground <span className="br-hint">acts as an external agent</span></div>
            <textarea className="br-pg-input" value={pgDirective} onChange={(e) => setPgDirective(e.target.value)} rows={2} data-testid="pg-input" />
            <div className="br-pg-row">
              <div className="br-kind">
                <button className={pgKind === "revenue" ? "on" : ""} onClick={() => setPgKind("revenue")}>Revenue</button>
                <button className={pgKind === "bugbounty" ? "on" : ""} onClick={() => setPgKind("bugbounty")}>Bug Bounty</button>
              </div>
              <button className="br-run" onClick={runPlayground} disabled={busy} data-testid="pg-run">
                {busy ? <Loader2 className="spin" size={15} /> : <Play size={15} />} Send via Bridge
              </button>
            </div>
            {pgOut && (
              <motion.div className="br-pg-out" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <div className="br-ok"><Check size={13} /> 200 · mission created</div>
                <div className="br-pg-title">{pgOut.title}</div>
                <div className="br-pg-sub">{pgOut.kind} · ${Number(pgOut.amount).toLocaleString()} · {pgOut.steps.length} steps</div>
              </motion.div>
            )}
          </div>

          <div className="br-card">
            <div className="br-card-h"><Bot size={15} /> External Agent Activity</div>
            {activity.length === 0 ? (
              <div className="nx-empty">No external calls yet. Run the playground or call the API from Manus/Gemini.</div>
            ) : (
              <div className="br-activity">
                {activity.map((a) => (
                  <div key={a.id} className="br-act-row">
                    <span className="br-agent">{a.agent}</span>
                    <span className="br-act">{a.action}</span>
                    <span className="br-detail">{a.detail}</span>
                    <span className="br-time">{fmt(a.timestamp)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="br-foot-note"><ShieldCheck size={13} /> Every bridge call is key-authenticated and recorded in the activity ledger. Regenerate the key to instantly revoke external access.</div>
    </div>
  );
}
