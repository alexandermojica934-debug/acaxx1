import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Mic, Square, Loader2, Command, Keyboard, Volume2 } from "lucide-react";
import { API } from "../App";

const SR = typeof window !== "undefined" ? (window.SpeechRecognition || window.webkitSpeechRecognition) : null;
const TTS = typeof window !== "undefined" ? window.speechSynthesis : null;

const isTextField = (el) =>
  !!el && ((el.tagName === "TEXTAREA") || (el.tagName === "INPUT" && /^(text|search|email|url|tel|number|)$/.test(el.type || "text"))) && !el.readOnly && !el.disabled;

/** Write into a React-controlled input so React's onChange fires. */
function injectText(el, text, replaceFrom) {
  const proto = el.tagName === "TEXTAREA" ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
  const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
  const base = replaceFrom !== null && replaceFrom !== undefined ? el.value.slice(0, replaceFrom) : el.value;
  const sep = base && !/\s$/.test(base) ? " " : "";
  setter.call(el, base + sep + text);
  el.dispatchEvent(new Event("input", { bubbles: true }));
  return base.length + sep.length;
}

const fieldLabel = (el) => el?.getAttribute("placeholder") || el?.getAttribute("aria-label") || el?.getAttribute("data-testid") || el?.name || "focused text box";

/**
 * VoiceCommander - floating mic available on every tab.
 *  - Dictate mode: speaks into whichever text box was last focused (interim results shown live, finalized in place).
 *  - Command mode: transcript -> POST /api/voice/command -> executes (navigate / council / radar / mission / ask) and speaks back.
 */
export default function VoiceCommander({ setTab }) {
  const [mode, setMode] = useState(() => localStorage.getItem("acaso_vc_mode") || "dictate");
  const [listening, setListening] = useState(false);
  const [busy, setBusy] = useState(false);
  const [interim, setInterim] = useState("");
  const [target, setTarget] = useState(null);
  const [lastSpoken, setLastSpoken] = useState("");
  const recRef = useRef(null);
  const targetRef = useRef(null);
  const anchorRef = useRef(null); // char index where the current utterance began, for interim replacement
  const modeRef = useRef(mode);
  useEffect(() => { modeRef.current = mode; localStorage.setItem("acaso_vc_mode", mode); }, [mode]);

  // Track the last focused text field anywhere in the app (ignore our own widget).
  useEffect(() => {
    const onFocus = (e) => {
      const el = e.target;
      if (el?.closest?.("[data-voice-commander]")) return;
      if (isTextField(el)) { targetRef.current = el; setTarget(el); }
    };
    document.addEventListener("focusin", onFocus);
    return () => document.removeEventListener("focusin", onFocus);
  }, []);

  const speak = useCallback((t) => {
    if (!TTS || !t) return;
    TTS.cancel();
    const u = new SpeechSynthesisUtterance(t);
    const pref = localStorage.getItem("acaso_voice_name");
    const v = TTS.getVoices().find((x) => x.name === pref);
    if (v) u.voice = v;
    TTS.speak(u);
  }, []);

  const runCommand = useCallback(async (transcript) => {
    if (!transcript) return;
    setBusy(true);
    toast(`Heard: "${transcript}"`, { icon: <Command size={14} /> });
    try {
      const r = await axios.post(`${API}/voice/command`, { transcript, session_id: localStorage.getItem("acaso_voice_session") || null }, { timeout: 320000 });
      const d = r.data;
      if (d.navigate_tab && setTab) setTab(d.navigate_tab);
      setLastSpoken(d.spoken || "");
      speak(d.spoken);
      if (d.error) toast.error(d.spoken); else toast.success(d.spoken?.slice(0, 140) || d.intent);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Command failed");
    } finally { setBusy(false); }
  }, [setTab, speak]);

  const stop = useCallback(() => { try { recRef.current?.stop(); } catch { /* ignore */ } setListening(false); }, []);

  const start = useCallback(() => {
    if (!SR) { toast.error("This browser lacks speech recognition - use Chrome, Edge or Safari"); return; }
    if (modeRef.current === "dictate" && !isTextField(targetRef.current)) {
      toast.error("Click into a text box first, then tap the mic to dictate into it");
      return;
    }
    try { TTS?.cancel(); } catch { /* ignore */ }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = true;
    rec.continuous = modeRef.current === "dictate";
    let finalCmd = "";
    anchorRef.current = null;
    rec.onstart = () => { setListening(true); setInterim(""); };
    rec.onresult = (ev) => {
      let fin = "", inter = "";
      for (let i = ev.resultIndex; i < ev.results.length; i++) {
        const t = ev.results[i][0].transcript;
        if (ev.results[i].isFinal) fin += t; else inter += t;
      }
      if (modeRef.current === "dictate") {
        const el = targetRef.current;
        if (!isTextField(el)) return;
        if (anchorRef.current === null) anchorRef.current = el.value.length;
        const combined = (fin + inter).trim();
        if (combined) {
          const end = injectText(el, combined, anchorRef.current);
          if (fin) { anchorRef.current = end + combined.length; el.setSelectionRange?.(el.value.length, el.value.length); }
        }
        setInterim(inter);
      } else {
        finalCmd = (finalCmd + fin).trim();
        setInterim(inter || finalCmd);
      }
    };
    rec.onerror = (ev) => {
      setListening(false);
      if (ev.error === "not-allowed") toast.error("Microphone permission denied");
      else if (!["aborted", "no-speech"].includes(ev.error)) toast.error(`Mic error: ${ev.error}`);
    };
    rec.onend = () => {
      setListening(false); setInterim("");
      if (modeRef.current === "command" && finalCmd) runCommand(finalCmd);
      else if (modeRef.current === "dictate") targetRef.current?.focus?.();
    };
    recRef.current = rec;
    try { rec.start(); } catch { /* already started */ }
  }, [runCommand]);

  // Keyboard shortcut: Ctrl/Cmd + Shift + Space toggles the mic
  useEffect(() => {
    const onKey = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.code === "Space") { e.preventDefault(); listening ? stop() : start(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [listening, start, stop]);

  const supported = !!SR;

  return (
    <div className={`vcmd ${listening ? "live" : ""}`} data-voice-commander data-testid="voice-commander">
      {(listening || busy || lastSpoken) && (
        <div className="vcmd-panel" data-testid="voice-commander-panel">
          {listening && mode === "dictate" && <div className="vcmd-line"><Keyboard size={12} /> Dictating into <b>{fieldLabel(target)}</b>{interim ? <em> · {interim}</em> : null}</div>}
          {listening && mode === "command" && <div className="vcmd-line"><Command size={12} /> Listening for a command{interim ? <em> · {interim}</em> : <em> · e.g. "open radar", "convene the council on...", "discover grants", "compile a mission to..."</em>}</div>}
          {busy && <div className="vcmd-line"><Loader2 className="spin" size={12} /> Executing...</div>}
          {!listening && !busy && lastSpoken && <div className="vcmd-line"><Volume2 size={12} /> <span>{lastSpoken.slice(0, 220)}</span><button className="vcmd-x" onClick={() => setLastSpoken("")}>dismiss</button></div>}
        </div>
      )}
      <div className="vcmd-bar">
        <div className="vcmd-seg" role="tablist" aria-label="Mic mode">
          <button data-testid="vcmd-mode-dictate" className={mode === "dictate" ? "on" : ""} onClick={() => setMode("dictate")} title="Dictate into the focused text box"><Keyboard size={13} /> Dictate</button>
          <button data-testid="vcmd-mode-command" className={mode === "command" ? "on" : ""} onClick={() => setMode("command")} title="Speak a command ACASO executes"><Command size={13} /> Command</button>
        </div>
        <button data-testid="vcmd-mic" className={`vcmd-mic ${listening ? "on" : ""}`} onClick={() => (listening ? stop() : start())} disabled={!supported || busy}
          title={supported ? (listening ? "Stop (Ctrl+Shift+Space)" : "Start mic (Ctrl+Shift+Space)") : "Speech recognition unsupported in this browser"} aria-pressed={listening}>
          {busy ? <Loader2 className="spin" size={18} /> : listening ? <Square size={18} /> : <Mic size={18} />}
        </button>
      </div>
    </div>
  );
}
