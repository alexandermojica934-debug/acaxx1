import React, { useState } from "react";
import "./App.css";
import { Toaster } from "sonner";
import SovereignHome from "./components/SovereignHome";
import AskAllAIs from "./components/AskAllAIs";
import Chronicle from "./components/Chronicle";
import BugBounty from "./components/BugBounty";
import AgentBridge from "./components/AgentBridge";
import FileAnalyzer from "./components/FileAnalyzer";
import SelfDirective from "./components/SelfDirective";
import Council from "./components/Council";
import VoiceChat from "./components/VoiceChat";
import Radar from "./components/Radar";
import VoiceCommander from "./components/VoiceCommander";
import LocalNode from "./components/LocalNode";
import Companion, { openCompanionWindow } from "./components/Companion";
import { Sparkles, LayoutGrid, MessagesSquare, BookOpen, ShieldAlert, Plug, Boxes, Wand2, Crown, Waves, Radar as RadarIcon, MonitorSmartphone, Castle } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const TABS = [
  { key: "home", label: "Sovereign Home", icon: LayoutGrid },
  { key: "bounty", label: "Bug Bounty", icon: ShieldAlert },
  { key: "council", label: "Council", icon: Crown },
  { key: "voice", label: "Voice", icon: Waves },
  { key: "radar", label: "Radar", icon: RadarIcon },
  { key: "askai", label: "Ask All AIs", icon: MessagesSquare },
  { key: "analyzer", label: "File Analyzer", icon: Boxes },
  { key: "self", label: "Self-Directive", icon: Wand2 },
  { key: "chronicle", label: "Chronicle", icon: BookOpen },
  { key: "node", label: "Local Node", icon: MonitorSmartphone },
  { key: "bridge", label: "Agent Bridge", icon: Plug },
];

function App() {
  const [tab, setTab] = useState(() => {
    try {
      const t = new URLSearchParams(window.location.search).get("tab");
      return TABS.some((x) => x.key === t) ? t : "home";
    } catch { return "home"; }
  });

  const companionMode = typeof window !== "undefined" && new URLSearchParams(window.location.search).get("mode") === "companion";
  if (companionMode) {
    return (
      <div className="acaso-root companion-root">
        <Toaster position="top-center" theme="dark" richColors />
        <Companion standalone />
      </div>
    );
  }

  return (
    <div className="acaso-root">
      <Toaster position="top-center" theme="dark" richColors />
      <div className="aurora" aria-hidden />
      <div className="grid-overlay" aria-hidden />

      <header className="topbar">
        <div className="brand">
          <div className="sigil"><Sparkles size={18} /></div>
          <div className="brand-text">
            <h1>ACASO</h1>
            <span>Synarchy Aetheris · Directive-to-Payment OS</span>
          </div>
        </div>
        <nav className="tabs">
          {TABS.map((t) => {
            const Icon = t.icon;
            return (
              <button
                key={t.key}
                data-testid={`tab-${t.key}`}
                className={tab === t.key ? "tab active" : "tab"}
                onClick={() => setTab(t.key)}
              >
                <Icon size={16} /> {t.label}
              </button>
            );
          })}
        </nav>
        <button className="companion-launch" onClick={openCompanionWindow} title="Open ACASO Companion in its own small window" data-testid="companion-launch"><Castle size={14} /> Companion</button>
        <div className="owner-badge"><span className="dot" /> Owner · Sovereign</div>
      </header>

      <main className="stage">
        {tab === "home" && <SovereignHome />}
        {tab === "bounty" && <BugBounty />}
        {tab === "council" && <Council />}
        {tab === "voice" && <VoiceChat />}
        {tab === "radar" && <Radar />}
        {tab === "askai" && <AskAllAIs />}
        {tab === "analyzer" && <FileAnalyzer />}
        {tab === "self" && <SelfDirective />}
        {tab === "chronicle" && <Chronicle />}
        {tab === "node" && <LocalNode />}
        {tab === "bridge" && <AgentBridge />}
      </main>

      <VoiceCommander setTab={setTab} />

      <footer className="footof">
        <span>Closed Action Loop — Directive › Discovery › Deliverable › Outreach › Payment › Receipt › Learning</span>
      </footer>
    </div>
  );
}

export default App;
