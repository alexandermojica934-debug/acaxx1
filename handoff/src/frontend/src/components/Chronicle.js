import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { ScrollText, BookOpen, Banknote, Target, Sparkles, Loader2, TrendingUp } from "lucide-react";
import { API } from "../App";

const fmtDate = (iso) => {
  try { return new Date(iso).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }); }
  catch { return ""; }
};

export default function Chronicle() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/chronicle`);
      setEntries(r.data);
    } catch (e) { /* silent */ } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const totalCollected = entries.reduce((a, e) => a + Number(e.amount || 0), 0);

  return (
    <div className="chronicle-wrap">
      <div className="chr-hero">
        <div className="chr-hero-left">
          <div className="chr-title"><BookOpen size={18} /> Outcome Ledger</div>
          <p>Every completed mission is recorded here as verified proof. The Chronicle distils a reusable lesson from each win — and ACASO feeds these lessons back into every new directive it compiles.</p>
        </div>
        <div className="chr-hero-stats">
          <div className="chr-stat"><span className="v">{entries.length}</span><span className="l">Missions Closed</span></div>
          <div className="chr-stat gold"><span className="v">${totalCollected.toLocaleString()}</span><span className="l">Total Collected</span></div>
        </div>
      </div>

      {loading ? (
        <div className="chr-loading"><Loader2 className="spin" size={20} /> Reading the Chronicle…</div>
      ) : entries.length === 0 ? (
        <div className="chr-empty">
          <ScrollText size={28} />
          <p>No completed missions yet. Finish a mission on the Sovereign Home board (run every step) and its outcome + learned lesson will be inscribed here.</p>
        </div>
      ) : (
        <div className="chr-timeline">
          {entries.map((e, i) => (
            <motion.div
              key={e.id}
              className="chr-entry"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <div className="chr-node"><TrendingUp size={14} /></div>
              <div className="chr-card">
                <div className="chr-card-top">
                  <span className={`m-mode mode-${e.mode}`}>{e.mode}</span>
                  <span className="chr-date">{fmtDate(e.completed_at)}</span>
                </div>
                <h3>{e.title}</h3>
                <div className="chr-metrics">
                  <span><Banknote size={13} /> ${Number(e.amount).toLocaleString()}</span>
                  <span><Target size={13} /> {e.outcome_metric || "outcome verified"}</span>
                </div>
                <div className="chr-lesson">
                  <Sparkles size={13} /> <b>Lesson learned:</b> {e.lesson}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
