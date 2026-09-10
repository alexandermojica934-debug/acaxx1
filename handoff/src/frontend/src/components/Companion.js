import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  Castle, Mic, Square, MonitorUp, MonitorOff, Send, Volume2, VolumeX, Loader2, Trash2, Camera, Radio, ExternalLink, Pin, Eye, EyeOff, Download
} from "lucide-react";
import { API } from "../App";

const SR = typeof window !== "undefined" ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null;
const TTS = typeof window !== "undefined" ? window.speechSynthesis : null;
const getSession = () => { try { let s = localStorage.getItem("acaso_companion_session"); if (!s) { s = crypto.randomUUID(); localStorage.setItem("acaso_companion_session", s); } return s; } catch { return "companion"; } };

/** Open the Companion as its own small desktop window (popup). Used by the launcher button in the main app. */
export function openCompanionWindow() {
  const url = `${window.location.origin}/?mode=companion`;
  const w = window.open(url, "acaso-companion", "popup=yes,width=440,height=760,left=" + Math.max(0, window.screen.availWidth - 470) + ",top=60,resizable=yes");
  if (!w) toast.error("Popup blocked - allow popups for this site, or open /?mode=companion in a new window");
  return w;
}

export default function Companion({ standalone = true }) {
  const [sessionId, setSessionId] = useState(getSession);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [streaming, setStreaming] = useState("");
  const [busy, setBusy] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [shareLabel, setShareLabel] = useState("");
  const [includeFrame, setIncludeFrame] = useState(true);
  const [listening, setListening] = useState(false);
  const [handsFree, setHandsFree] = useState(false);
  const [speak, setSpeak] = useState(true);
  const [speaking, setSpeaking] = useState(false);
  const [watch, setWatch] = useState(false);
  const [watchState, setWatchState] = useState({ glances: 0, skipped: 0, last: null, checking: false });
  const watchRef = useRef({ prevHash: null, prevSummary: null, lastSpoken: null, busy: false });
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const recRef = useRef(null);
  const endRef = useRef(null);
  const handsFreeRef = useRef(false);
  useEffect(() => { handsFreeRef.current = handsFree; }, [handsFree]);

  useEffect(() => {
    (async () => { try { setMessages((await axios.get(`${API}/companion/history`, { params: { session_id: sessionId } })).data); } catch { /* silent */ } })();
  }, [sessionId]);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streaming]);
  const [installEvt, setInstallEvt] = useState(null);
  const [installed, setInstalled] = useState(() => typeof window !== "undefined" && window.matchMedia?.("(display-mode: standalone)").matches);
  useEffect(() => {
    if (!standalone) return undefined;
    document.title = "ACASO Companion";
    // swap the page manifest so Chrome offers to install *the Companion* as its own desktop app
    document.querySelectorAll('link[rel="manifest"]').forEach((l) => l.remove());
    const link = document.createElement("link"); link.rel = "manifest"; link.href = "/companion.webmanifest"; document.head.appendChild(link);
    const onPrompt = (e) => { e.preventDefault(); setInstallEvt(e); };
    const onInstalled = () => { setInstalled(true); setInstallEvt(null); toast.success("ACASO Companion installed - find it in your Start menu / dock"); };
    window.addEventListener("beforeinstallprompt", onPrompt);
    window.addEventListener("appinstalled", onInstalled);
    return () => { window.removeEventListener("beforeinstallprompt", onPrompt); window.removeEventListener("appinstalled", onInstalled); };
  }, [standalone]);
  const install = async () => {
    if (installEvt) { installEvt.prompt(); const r = await installEvt.userChoice.catch(() => null); if (r?.outcome === "accepted") setInstallEvt(null); return; }
    toast("Chrome: menu (⋮) → Cast, save and share → Install page as app. Or run the Local Node with --companion for an always-on-top window.", { duration: 9000 });
  };

  // ---- screen / window share ----
  const startShare = async () => {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: { frameRate: 5 }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) { videoRef.current.srcObject = stream; await videoRef.current.play(); }
      const track = stream.getVideoTracks()[0];
      const s = track.getSettings();
      setShareLabel(track.label || (s.displaySurface ? `${s.displaySurface}` : "shared screen"));
      setSharing(true);
      track.onended = () => stopShare();
      toast.success("Sharing started - ask anything about what you see");
    } catch (e) { if (e?.name !== "NotAllowedError") toast.error("Could not start sharing"); }
  };
  const stopShare = useCallback(() => {
    try { streamRef.current?.getTracks().forEach((t) => t.stop()); } catch { /* ignore */ }
    streamRef.current = null; setSharing(false); setShareLabel(""); setWatch(false);
    if (videoRef.current) videoRef.current.srcObject = null;
  }, []);
  const captureFrame = () => {
    const v = videoRef.current;
    if (!v || !streamRef.current || !v.videoWidth) return null;
    const maxW = 1280;
    const scale = Math.min(1, maxW / v.videoWidth);
    const c = document.createElement("canvas");
    c.width = Math.round(v.videoWidth * scale); c.height = Math.round(v.videoHeight * scale);
    c.getContext("2d").drawImage(v, 0, 0, c.width, c.height);
    return c.toDataURL("image/jpeg", 0.72).split(",")[1];
  };
  /** 16x16 grayscale fingerprint - lets watch mode skip frames that barely changed (no model call). */
  const frameHash = () => {
    const v = videoRef.current;
    if (!v || !v.videoWidth) return null;
    const c = document.createElement("canvas"); c.width = 16; c.height = 16;
    const ctx = c.getContext("2d"); ctx.drawImage(v, 0, 0, 16, 16);
    const d = ctx.getImageData(0, 0, 16, 16).data; const out = [];
    for (let i = 0; i < d.length; i += 4) out.push((d[i] + d[i + 1] + d[i + 2]) / 3);
    return out;
  };
  const hashDiff = (a, b) => { if (!a || !b) return 1; let s = 0; for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s / (a.length * 255); };


  // ---- TTS ----
  const say = useCallback((t, onDone) => {
    if (!TTS || !t) { onDone?.(); return; }
    TTS.cancel();
    const u = new SpeechSynthesisUtterance(t.replace(/\*\*/g, ""));
    const pref = localStorage.getItem("acaso_voice_name");
    const v = TTS.getVoices().find((x) => x.name === pref);
    if (v) u.voice = v;
    u.onstart = () => setSpeaking(true);
    u.onend = () => { setSpeaking(false); onDone?.(); };
    u.onerror = () => { setSpeaking(false); onDone?.(); };
    TTS.speak(u);
  }, []);

  // ---- watch mode loop: glance every 30s, only call the model when the screen changed, speak only if notable ----
  useEffect(() => {
    if (!watch || !sharing) return undefined;
    let cancelled = false;
    const glance = async () => {
      if (cancelled || watchRef.current.busy || busy) return;
      const h = frameHash();
      if (!h) return;
      const changed = hashDiff(watchRef.current.prevHash, h) > 0.04; // ~4% average pixel change
      if (!changed) { setWatchState((w) => ({ ...w, skipped: w.skipped + 1, last: new Date() })); return; }
      const frame = captureFrame();
      if (!frame) return;
      watchRef.current.busy = true; setWatchState((w) => ({ ...w, checking: true }));
      try {
        const r = await axios.post(`${API}/companion/watch`, { image_b64: frame, session_id: sessionId, share_label: shareLabel,
          previous_summary: watchRef.current.prevSummary, last_spoken: watchRef.current.lastSpoken }, { timeout: 60000 });
        watchRef.current.prevHash = h; watchRef.current.prevSummary = r.data.summary;
        setWatchState((w) => ({ ...w, glances: w.glances + 1, last: new Date(), checking: false }));
        if (r.data.notable && r.data.message) {
          watchRef.current.lastSpoken = r.data.message;
          setMessages((m) => [...m, { id: `w-${Date.now()}`, role: "assistant", content: r.data.message, model_label: r.data.model_label, watch: true, kind: r.data.kind, created_at: r.data.at }]);
          if (speak) say(r.data.message);
        }
      } catch { setWatchState((w) => ({ ...w, checking: false })); }
      finally { watchRef.current.busy = false; }
    };
    const t0 = setTimeout(glance, 1500);
    const iv = setInterval(glance, 30000);
    return () => { cancelled = true; clearTimeout(t0); clearInterval(iv); };
  }, [watch, sharing, sessionId, shareLabel, speak, say, busy]);

  // ---- send (SSE stream) ----
  const send = useCallback(async (msg, withFrame = includeFrame) => {
    const content = (msg || "").trim();
    const frame = withFrame && sharing ? captureFrame() : null;
    if (!content && !frame) return;
    setBusy(true); setStreaming("");
    setMessages((m) => [...m, { id: `u-${Date.now()}`, role: "user", content: content || "(shared screen)", had_image: !!frame, created_at: new Date().toISOString() }]);
    try {
      const res = await fetch(`${API}/companion/chat`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content, session_id: sessionId, image_b64: frame, share_label: frame ? shareLabel : null }) });
      if (!res.ok) throw new Error((await res.json().catch(() => ({})))?.detail || `HTTP ${res.status}`);
      const reader = res.body.getReader(); const dec = new TextDecoder(); let buf = ""; let full = ""; let label = null;
      for (;;) {
        const { value, done } = await reader.read(); if (done) break;
        buf += dec.decode(value, { stream: true });
        const parts = buf.split("\n\n"); buf = parts.pop();
        for (const p of parts) {
          if (!p.startsWith("data: ")) continue;
          const ev = JSON.parse(p.slice(6));
          if (ev.type === "delta") { full += ev.content; setStreaming(full); }
          else if (ev.type === "done") { full = ev.content || full; label = ev.model_label; }
        }
      }
      setStreaming("");
      setMessages((m) => [...m, { id: `a-${Date.now()}`, role: "assistant", content: full, model_label: label, created_at: new Date().toISOString() }]);
      const after = () => { if (handsFreeRef.current) startListening(); }; // eslint-disable-line no-use-before-define
      if (speak) say(full, after); else after();
    } catch (e) {
      toast.error(e.message || "Companion failed");
      setStreaming("");
    } finally { setBusy(false); }
  }, [includeFrame, sharing, sessionId, shareLabel, speak, say]);

  // ---- STT ----
  const stopListening = useCallback(() => { try { recRef.current?.stop(); } catch { /* ignore */ } setListening(false); }, []);
  const startListening = useCallback(() => {
    if (!SR) { toast.error("Speech recognition needs Chrome, Edge or Safari"); return; }
    try { TTS?.cancel(); } catch { /* ignore */ }
    const rec = new SR(); rec.lang = "en-US"; rec.interimResults = true; rec.continuous = false;
    let fin = "";
    rec.onstart = () => setListening(true);
    rec.onresult = (ev) => { fin = ""; let inter = ""; for (let i = 0; i < ev.results.length; i++) { const t = ev.results[i][0].transcript; if (ev.results[i].isFinal) fin += t + " "; else inter += t; } setText((fin + inter).trim()); };
    rec.onerror = (ev) => { setListening(false); if (ev.error === "not-allowed") { toast.error("Microphone permission denied"); setHandsFree(false); } else if (ev.error === "no-speech" && handsFreeRef.current) setTimeout(() => startListening(), 400); };
    rec.onend = () => { setListening(false); const heard = fin.trim(); if (heard) { setText(""); send(heard); } else if (handsFreeRef.current && !busy) setTimeout(() => startListening(), 300); };
    recRef.current = rec;
    try { rec.start(); } catch { /* ignore */ }
  }, [send, busy]);

  const toggleHandsFree = () => {
    if (handsFree) { setHandsFree(false); handsFreeRef.current = false; stopListening(); TTS?.cancel(); }
    else { setHandsFree(true); handsFreeRef.current = true; startListening(); }
  };
  const clear = async () => { try { await axios.delete(`${API}/companion/history`, { params: { session_id: sessionId } }); } catch { /* ignore */ } const s = crypto.randomUUID(); localStorage.setItem("acaso_companion_session", s); setSessionId(s); setMessages([]); };
  useEffect(() => () => { stopShare(); try { recRef.current?.abort(); TTS?.cancel(); } catch { /* ignore */ } }, [stopShare]);

  return (
    <div className={`cp ${standalone ? "standalone" : ""}`} data-testid="companion">
      <header className="cp-head">
        <div className="cp-brand"><Castle size={16} /> ACASO Companion <span className={`cp-dot ${busy ? "busy" : sharing ? "on" : ""}`} /></div>
        <div className="cp-head-actions">
          <button className="cp-ic" title={speak ? "Mute replies" : "Speak replies"} onClick={() => { setSpeak((s) => !s); TTS?.cancel(); }} data-testid="cp-mute">{speak ? <Volume2 size={14} /> : <VolumeX size={14} />}</button>
          <button className="cp-ic" title="Clear conversation" onClick={clear} data-testid="cp-clear"><Trash2 size={14} /></button>
          {!standalone && <button className="cp-ic" title="Open as its own window" onClick={openCompanionWindow} data-testid="cp-popout"><ExternalLink size={14} /></button>}
          {standalone && !installed && <button className="cp-install" onClick={install} title="Install as a desktop app" data-testid="cp-install"><Download size={12} /> Install app</button>}
          {standalone && installed && <span className="cp-pin" title="Running as an installed desktop app"><Pin size={12} /> desktop app</span>}
        </div>
      </header>

      <div className={`cp-share ${sharing ? "on" : ""}`} data-testid="cp-share">
        <video ref={videoRef} muted playsInline className="cp-video" style={{ display: sharing ? "block" : "none" }} />
        {!sharing ? (
          <button className="cp-share-btn" onClick={startShare} data-testid="cp-share-start"><MonitorUp size={16} /> Share a window, tab or screen</button>
        ) : (
          <div className="cp-share-bar">
            <span title={shareLabel}><Radio size={11} /> {shareLabel.slice(0, 38) || "sharing"}</span>
            <label className="cp-chk" title="Attach a frame of the shared window to each message"><input type="checkbox" checked={includeFrame} onChange={(e) => setIncludeFrame(e.target.checked)} data-testid="cp-include-frame" /> see it</label>
            <button className={`cp-ic ${watch ? "on" : ""}`} title={watch ? "Watch mode on - glances every 30s, speaks only for errors, forms or action prompts" : "Watch mode: glance every 30s and speak up only when something notable appears"} onClick={() => setWatch((w) => !w)} data-testid="cp-watch">{watch ? <Eye size={14} /> : <EyeOff size={14} />}</button>
            <button className="cp-ic" title="Describe what's on screen now" onClick={() => send("", true)} disabled={busy} data-testid="cp-look"><Camera size={14} /></button>
            <button className="cp-ic" title="Stop sharing" onClick={stopShare} data-testid="cp-share-stop"><MonitorOff size={14} /></button>
          </div>
        )}
      </div>

      {watch && sharing && (
        <div className="cp-watchbar" data-testid="cp-watch-status">
          <Eye size={11} /> watching · {watchState.glances} glance{watchState.glances === 1 ? "" : "s"} · {watchState.skipped} unchanged skipped{watchState.checking ? " · checking..." : ""}
        </div>
      )}
      <div className="cp-log" data-testid="cp-log">
        {messages.length === 0 && !streaming && (
          <div className="cp-empty">Talk or type. Share a window and I can read what's on it - errors, forms, documents, dashboards - and tell you what to do next.</div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`cp-msg ${m.role}`} data-testid={`cp-msg-${m.role}`}>
            {m.had_image && <span className="cp-tag"><Camera size={10} /> frame</span>}
            {m.watch && <span className={`cp-tag k-${m.kind}`}><Eye size={10} /> watch · {m.kind}</span>}
            <div>{m.content}</div>
            {m.role === "assistant" && <button className="cp-replay" onClick={() => say(m.content)} title="Speak"><Volume2 size={11} /></button>}
          </div>
        ))}
        {streaming && <div className="cp-msg assistant streaming" data-testid="cp-streaming">{streaming}</div>}
        {busy && !streaming && <div className="cp-thinking"><Loader2 className="spin" size={12} /> looking...</div>}
        <div ref={endRef} />
      </div>

      <form className="cp-input" onSubmit={(e) => { e.preventDefault(); const t = text; setText(""); send(t); }}>
        <button type="button" className={`cp-mic ${handsFree ? "on" : ""} ${listening ? "live" : ""}`} onClick={toggleHandsFree} title={handsFree ? "Stop hands-free" : "Hands-free conversation"} data-testid="cp-handsfree">
          {handsFree ? <Square size={15} /> : <Mic size={15} />}
        </button>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder={listening ? "listening..." : sharing ? "Ask about what you see..." : "Ask ACASO..."} data-testid="cp-text" />
        <button type="submit" className="cp-send" disabled={busy || (!text.trim() && !sharing)} data-testid="cp-send">{busy ? <Loader2 className="spin" size={15} /> : <Send size={15} />}</button>
      </form>
      {speaking && <button className="cp-stopvoice" onClick={() => TTS?.cancel()}>stop voice</button>}
    </div>
  );
}
