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
import { Sparkles, LayoutGrid, MessagesSquare, BookOpen, ShieldAlert, Plug, Boxes, Wand2 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const TABS = [
  { key: "home", label: "Sovereign Home", icon: LayoutGrid },
  { key: "bounty", label: "Bug Bounty", icon: ShieldAlert },
  { key: "askai", label: "Ask All AIs", icon: MessagesSquare },
  { key: "analyzer", label: "File Analyzer", icon: Boxes },
  { key: "self", label: "Self-Directive", icon: Wand2 },
  { key: "chronicle", label: "Chronicle", icon: BookOpen },
  { key: "bridge", label: "Agent Bridge", icon: Plug },
];

function App() {
  const [tab, setTab] = useState("home");

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
        <div className="owner-badge"><span className="dot" /> Owner · Sovereign</div>
      </header>

      <main className="stage">
        {tab === "home" && <SovereignHome />}
        {tab === "bounty" && <BugBounty />}
        {tab === "askai" && <AskAllAIs />}
        {tab === "analyzer" && <FileAnalyzer />}
        {tab === "self" && <SelfDirective />}
        {tab === "chronicle" && <Chronicle />}
        {tab === "bridge" && <AgentBridge />}
      </main>

      <footer className="footof">
        <span>Closed Action Loop — Directive › Discovery › Deliverable › Outreach › Payment › Receipt › Learning</span>
      </footer>
    </div>
  );
}

export default App;
