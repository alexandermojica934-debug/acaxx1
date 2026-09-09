import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Send, Loader2, Sparkles, Layers, Bot } from "lucide-react";
import { API } from "../App";

const PROVIDERS = [
  { key: "openai", label: "GPT-4o", color: "#10a37f" },
  { key: "gemini", label: "Gemini", color: "#4285f4" },
  { key: "anthropic", label: "Claude", color: "#d97757" },
];

export default function AskAllAIs() {
  const [msg, setMsg] = useState("");
  const [selected, setSelected] = useState(["openai", "gemini", "anthropic"]);
  const [loading, setLoading] = useState(false);
  const [thread, setThread] = useState([]);
  const scroller = useRef(null);

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
  }, [thread, loading]);

  const toggle = (k) => {
    setSelected((prev) => prev.includes(k) ? prev.filter((p) => p !== k) : [...prev, k]);
  };

  const send = async () => {
    if (!msg.trim()) return;
    if (selected.length === 0) { toast.error("Select at least one mind"); return; }
    const question = msg;
    setThread((t) => [...t, { role: "user", text: question }]);
    setMsg("");
    setLoading(true);
    try {
      const r = await axios.post(`${API}/chat`, { message: question, models: selected });
      setThread((t) => [...t, { role: "assistant", ...r.data }]);
    } catch (e) {
      toast.error("Ask All AIs failed");
      setThread((t) => t.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="askai-wrap">
      <div className="askai-head">
        <div className="ah-title"><Sparkles size={16} /> Ask All AIs <em>· plural reasoning field</em></div>
        <div className="prov-picker">
          {PROVIDERS.map((p) => (
            <button
              key={p.key}
              data-testid={`prov-${p.key}`}
              className={selected.includes(p.key) ? "prov on" : "prov"}
              style={selected.includes(p.key) ? { borderColor: p.color, color: p.color } : {}}
              onClick={() => toggle(p.key)}
            >
              <Bot size={14} /> {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="thread" ref={scroller}>
        {thread.length === 0 && (
          <div className="askai-empty">
            <Layers size={28} />
            <p>Ask one question. OmniMind queries every selected mind in parallel, then the Synarchy arbiter fuses them into one superior answer.</p>
          </div>
        )}
        {thread.map((item, i) => item.role === "user" ? (
          <div key={i} className="bubble user">{item.text}</div>
        ) : (
          <motion.div key={i} className="answer-block" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            {item.synthesis && (
              <div className="synthesis">
                <div className="syn-head"><Sparkles size={14} /> Synarchy Synthesis</div>
                <p>{item.synthesis}</p>
              </div>
            )}
            <div className="models-grid">
              {item.results?.map((r) => (
                <div key={r.provider} className={`model-card ${r.ok ? "" : "failed"}`}>
                  <div className="mc-head">{r.label}</div>
                  <p>{r.answer}</p>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
        {loading && <div className="bubble thinking"><Loader2 className="spin" size={15} /> The minds are reasoning…</div>}
      </div>

      <div className="askai-input">
        <input
          data-testid="askai-input"
          value={msg}
          onChange={(e) => setMsg(e.target.value)}
          placeholder="Ask all the AIs anything…"
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
        />
        <button data-testid="askai-send" onClick={send} disabled={loading}>
          {loading ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
        </button>
      </div>
    </div>
  );
}
