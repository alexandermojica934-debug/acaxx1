import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic, MicOff, Square, Volume2, VolumeX, Send, Radio, Hand, Keyboard, Zap, Crown,
  Loader2, Trash2, AlertTriangle, Ear, Waves
} from "lucide-react";
import { API } from "../App";
import { Markdown } from "./FileAnalyzer";

const SR = typeof window !== "undefined" ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null;
const TTS = typeof window !== "undefined" ? window.speechSynthesis : null;

const INTERACTION = [
  { key: "handsfree", label: "Hands-free", icon: Radio, hint: "Listens, replies aloud, listens again until you stop." },
  { key: "ptt", label: "Push-to-talk", icon: Hand, hint: "Hold the button to speak, release to send. Reply spoken once." },
  { key: "text", label: "Text-first", icon: Keyboard, hint: "Type or dictate; click the speaker to hear a reply." },
];

const getSession = () => {
  try {
    let s = localStorage.getItem("acaso_voice_session");
    if (!s) { s = crypto.randomUUID(); localStorage.setItem("acaso_voice_session", s); }
    return s;
  } catch { return "voice-default"; }
};

export default function VoiceChat() {
  const [sessionId, setSessionId] = useState(getSession);
  const [interaction, setInteraction] = useState("handsfree");
  const [answerMode, setAnswerMode] = useState("fast");
  const [messages, setMessages] = useState([]);
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState("");
  const [thinking, setThinking] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [speakReplies, setSpeakReplies] = useState(true);
  const [voices, setVoices] = useState([]);
  const [voiceName, setVoiceName] = useState(() => localStorage.getItem("acaso_voice_name") || "");
  const [text, setText] = useState("");
  const [active, setActive] = useState(false); // hands-free loop on/off

  const recRef = useRef(null);
  const activeRef = useRef(false);
  const interactionRef = useRef(interaction);
  const modeRef = useRef(answerMode);
  const endRef = useRef(null);
  const finalRef = useRef("");
  useEffect(() => { interactionRef.current = interaction; }, [interaction]);
  useEffect(() => { modeRef.current = answerMode; }, [answerMode]);
  useEffect(() => { activeRef.current = active; }, [active]);

  const supported = !!SR && !!TTS;

  // ---- voices ----
  useEffect(() => {
    if (!TTS) return;
    const load = () => {
      const v = TTS.getVoices().filter((x) => x.lang && x.lang.toLowerCase().startsWith("en"));
      setVoices(v.length ? v : TTS.getVoices());
    };
    load();
    TTS.addEventListener?.("voiceschanged", load);
    return () => TTS.removeEventListener?.("voiceschanged", load);
  }, []);

  // ---- history ----
  useEffect(() => {
    (async () => {
      try { const r = await axios.get(`${API}/voice/history`, { params: { session_id: sessionId } }); setMessages(r.data); }
      catch { /* silent */ }
    })();
  }, [sessionId]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, interim, thinking]);

  // ---- TTS ----
  const stopSpeaking = useCallback(() => { try { TTS?.cancel(); } catch { /* ignore */ } setSpeaking(false); }, []);

  const speak = useCallback((content, onDone) => {
    if (!TTS || !content) { onDone?.(); return; }
    TTS.cancel();
    const u = new SpeechSynthesisUtterance(content);
    const v = voices.find((x) => x.name === voiceName);
    if (v) u.voice = v;
    u.rate = 1.02; u.pitch = 1;
    u.onstart = () => setSpeaking(true);
    u.onend = () => { setSpeaking(false); onDone?.(); };
    u.onerror = () => { setSpeaking(false); onDone?.(); };
    TTS.speak(u);
  }, [voices, voiceName]);

  // ---- STT ----
  const stopListening = useCallback(() => {
    try { recRef.current?.stop(); } catch { /* ignore */ }
    setListening(false); setInterim("");
  }, []);

  const send = useCallback(async (msg, { speakIt } = { speakIt: true }) => {
    const content = (msg || "").trim();
    if (!content) return;
    const mode = modeRef.current;
    setMessages((m) => [...m, { id: `tmp-${Date.now()}`, role: "user", content, mode, created_at: new Date().toISOString() }]);
    setThinking(true);
    if (mode === "council") toast("Council convened - this takes 1-3 minutes", { icon: <Crown size={14} /> });
    try {
      const r = await axios.post(`${API}/voice/chat`, { message: content, session_id: sessionId, mode }, { timeout: 320000 });
      const reply = r.data.reply;
      setMessages((m) => [...m, reply]);
      setThinking(false);
      const after = () => {
        if (interactionRef.current === "handsfree" && activeRef.current) startListening(); // eslint-disable-line no-use-before-define
      };
      if (speakIt && speakReplies) speak(reply.content, after); else after();
    } catch (e) {
      setThinking(false);
      toast.error(e?.response?.data?.detail || "ACASO could not answer");
      if (interactionRef.current === "handsfree" && activeRef.current) setTimeout(() => startListening(), 800); // eslint-disable-line no-use-before-define
    }
  }, [sessionId, speak, speakReplies]);

  const startListening = useCallback(() => {
    if (!SR) return;
    stopSpeaking();
    try { recRef.current?.abort(); } catch { /* ignore */ }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = true;
    rec.continuous = interactionRef.current === "ptt";
    finalRef.current = "";
    rec.onstart = () => { setListening(true); setInterim(""); };
    rec.onresult = (ev) => {
      let fin = "", inter = "";
      for (let i = 0; i < ev.results.length; i++) {
        const t = ev.results[i][0].transcript;
        if (ev.results[i].isFinal) fin += t + " "; else inter += t;
      }
      finalRef.current = fin.trim();
      setInterim((fin + inter).trim());
    };
    rec.onerror = (ev) => {
      setListening(false); setInterim("");
      if (ev.error === "not-allowed") { toast.error("Microphone permission denied"); setActive(false); }
      else if (ev.error !== "aborted" && ev.error !== "no-speech") toast.error(`Mic error: ${ev.error}`);
      if (ev.error === "no-speech" && interactionRef.current === "handsfree" && activeRef.current) setTimeout(() => startListening(), 400);
    };
    rec.onend = () => {
      setListening(false);
      const heard = finalRef.current;
      setInterim("");
      if (interactionRef.current === "text") { if (heard) setText((t) => (t ? t + " " : "") + heard); return; }
      if (heard) send(heard);
      else if (interactionRef.current === "handsfree" && activeRef.current && !thinking) setTimeout(() => startListening(), 300);
    };
    recRef.current = rec;
    try { rec.start(); } catch { /* already started */ }
  }, [send, stopSpeaking, thinking]);

  const toggleHandsFree = () => {
    if (active) { setActive(false); activeRef.current = false; stopListening(); stopSpeaking(); }
    else { setActive(true); activeRef.current = true; startListening(); }
  };

  const clearHistory = async () => {
    try { await axios.delete(`${API}/voice/history`, { params: { session_id: sessionId } }); } catch { /* ignore */ }
    const s = crypto.randomUUID(); localStorage.setItem("acaso_voice_session", s); setSessionId(s); setMessages([]);
  };

  useEffect(() => () => { try { recRef.current?.abort(); TTS?.cancel(); } catch { /* ignore */ } }, []);

  const changeInteraction = (k) => { setActive(false); activeRef.current = false; stopListening(); setInteraction(k); };

  return (
    <div className="vc-wrap" data-testid="voice-page">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><Waves size={18} /> Voice Channel</div>
          <p>Talk to ACASO out loud. Speech recognition and speech synthesis run <b>in your browser</b> (Web Speech API - no keys, no audio sent to the server; only the transcript is). Choose how you want to talk, and per message whether the <b>fast</b> voice or the full <b>Council of Weavers</b> answers.</p>
        </div>
        <div className="chr-hero-stats">
          <div className="chr-stat"><span className="v">{messages.filter((m) => m.role === "user").length}</span><span className="l">Turns</span></div>
          <div className={`chr-stat ${listening ? "gold" : ""}`}><span className="v">{listening ? "LIVE" : speaking ? "TALK" : "IDLE"}</span><span className="l">Mic state</span></div>
        </div>
      </div>

      {!supported && (
        <div className="cw-honesty" data-testid="voice-unsupported"><AlertTriangle size={14} />
          This browser lacks the Web Speech API. Use Chrome, Edge or Safari for voice; typing still works below.
        </div>
      )}

      <div className="fa-console">
        <div className="vc-controls">
          <div className="vc-seg" role="tablist" aria-label="Interaction mode">
            {INTERACTION.map((m) => { const I = m.icon; return (
              <button key={m.key} data-testid={`voice-mode-${m.key}`} className={interaction === m.key ? "vc-seg-btn active" : "vc-seg-btn"} onClick={() => changeInteraction(m.key)} title={m.hint}>
                <I size={14} /> {m.label}
              </button>); })}
          </div>
          <div className="vc-seg" aria-label="Who answers">
            <button data-testid="answer-fast" className={answerMode === "fast" ? "vc-seg-btn active" : "vc-seg-btn"} onClick={() => setAnswerMode("fast")}><Zap size={14} /> Fast</button>
            <button data-testid="answer-council" className={answerMode === "council" ? "vc-seg-btn active council" : "vc-seg-btn"} onClick={() => setAnswerMode("council")}><Crown size={14} /> Council</button>
          </div>
          <select data-testid="voice-select" className="cw-input vc-voice" value={voiceName} onChange={(e) => { setVoiceName(e.target.value); localStorage.setItem("acaso_voice_name", e.target.value); }}>
            <option value="">Default voice</option>
            {voices.map((v) => <option key={v.name} value={v.name}>{v.name}</option>)}
          </select>
          <button data-testid="voice-mute" className="attach-btn" title={speakReplies ? "Mute spoken replies" : "Unmute spoken replies"} onClick={() => { setSpeakReplies((s) => !s); stopSpeaking(); }}>
            {speakReplies ? <Volume2 size={14} /> : <VolumeX size={14} />}
          </button>
          <button data-testid="voice-clear" className="attach-btn danger" title="Clear conversation" onClick={clearHistory}><Trash2 size={14} /></button>
        </div>
        <div className="vc-hint">{INTERACTION.find((m) => m.key === interaction)?.hint} {answerMode === "council" ? "Council answers take 1-3 minutes and are summarized aloud; the full directive appears in the transcript." : ""}</div>
      </div>

      <div className="vc-transcript" data-testid="voice-transcript">
        {messages.length === 0 && !interim && !thinking && (
          <div className="attach-empty" data-testid="voice-empty"><Ear size={13} /> Nothing said yet. Start the mic or type below.</div>
        )}
        <AnimatePresence initial={false}>
          {messages.map((m) => (
            <motion.div key={m.id} className={`vc-msg ${m.role}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} data-testid={`voice-msg-${m.role}`}>
              <div className="vc-msg-meta">{m.role === "user" ? "You" : "ACASO"}{m.mode === "council" ? " · Council" : ""}{m.model_label ? ` · ${m.model_label}` : ""}</div>
              <div className="vc-msg-body">{m.content}</div>
              {m.full_text && (
                <details className="vc-full"><summary>Full Sovereign Directive</summary><Markdown text={m.full_text} /></details>
              )}
              {m.role === "assistant" && (
                <button className="vc-replay" onClick={() => speak(m.content)} title="Speak this reply" data-testid="voice-replay"><Volume2 size={12} /> speak</button>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        {interim && <div className="vc-msg user interim" data-testid="voice-interim"><div className="vc-msg-meta">You (hearing...)</div><div className="vc-msg-body">{interim}</div></div>}
        {thinking && <div className="vc-thinking" data-testid="voice-thinking"><Loader2 className="spin" size={14} /> {answerMode === "council" ? "Council of Weavers in session..." : "ACASO is thinking..."}</div>}
        <div ref={endRef} />
      </div>

      <div className="vc-dock">
        {interaction === "handsfree" && (
          <button data-testid="voice-handsfree-toggle" className={`vc-big ${active ? "on" : ""}`} onClick={toggleHandsFree} disabled={!supported}>
            {active ? <Square size={22} /> : <Mic size={22} />}
            <span>{active ? (listening ? "Listening - tap to stop" : speaking ? "Speaking - tap to stop" : thinking ? "Thinking - tap to stop" : "Resuming...") : "Start conversation"}</span>
          </button>
        )}
        {interaction === "ptt" && (
          <button data-testid="voice-ptt" className={`vc-big ${listening ? "on" : ""}`} disabled={!supported}
            onMouseDown={startListening} onMouseUp={stopListening} onMouseLeave={() => listening && stopListening()}
            onTouchStart={(e) => { e.preventDefault(); startListening(); }} onTouchEnd={(e) => { e.preventDefault(); stopListening(); }}>
            {listening ? <Mic size={22} /> : <MicOff size={22} />}
            <span>{listening ? "Release to send" : "Hold to talk"}</span>
          </button>
        )}
        {interaction === "text" && (
          <form className="vc-textrow" onSubmit={(e) => { e.preventDefault(); const t = text; setText(""); send(t, { speakIt: speakReplies }); }}>
            <button type="button" data-testid="voice-dictate" className={`attach-btn ${listening ? "live" : ""}`} title="Dictate" onClick={() => (listening ? stopListening() : startListening())} disabled={!supported}>
              {listening ? <Square size={14} /> : <Mic size={14} />}
            </button>
            <input data-testid="voice-text-input" className="cw-input grow" value={text} onChange={(e) => setText(e.target.value)} placeholder="Type or dictate a message..." />
            <button type="submit" data-testid="voice-text-send" className="fa-btn primary" disabled={!text.trim() || thinking}><Send size={14} /> Send</button>
          </form>
        )}
        {speaking && <button className="fa-btn" data-testid="voice-stop-speaking" onClick={stopSpeaking}><VolumeX size={14} /> Stop voice</button>}
      </div>
    </div>
  );
}
