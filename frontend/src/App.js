import React, { useEffect, useState, useCallback } from "react";
import "./App.css";
import axios from "axios";
import { Toaster } from "sonner";
import SovereignHome from "./components/SovereignHome";
import AskAllAIs from "./components/AskAllAIs";
import { Sparkles, LayoutGrid, MessagesSquare } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

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
          <button
            data-testid="tab-home"
            className={tab === "home" ? "tab active" : "tab"}
            onClick={() => setTab("home")}
          >
            <LayoutGrid size={16} /> Sovereign Home
          </button>
          <button
            data-testid="tab-askai"
            className={tab === "askai" ? "tab active" : "tab"}
            onClick={() => setTab("askai")}
          >
            <MessagesSquare size={16} /> Ask All AIs
          </button>
        </nav>
        <div className="owner-badge">
          <span className="dot" /> Owner · Sovereign
        </div>
      </header>

      <main className="stage">
        {tab === "home" ? <SovereignHome /> : <AskAllAIs />}
      </main>

      <footer className="footof">
        <span>Closed Action Loop — Directive › Discovery › Deliverable › Outreach › Payment › Receipt › Learning</span>
      </footer>
    </div>
  );
}

export default App;
