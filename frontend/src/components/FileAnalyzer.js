import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  FolderUp, FilePlus, Loader2, Sparkles, Trash2, Download, FileText,
  Image as ImageIcon, Play, X, Plus, HardDriveUpload, Files, Boxes
} from "lucide-react";
import { API } from "../App";

const fmtBytes = (n) => {
  if (!n && n !== 0) return "";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
};

function Markdown({ text }) {
  if (!text) return null;
  const blocks = text.split(/```/);
  return (
    <div className="fa-md">
      {blocks.map((blk, bi) => {
        if (bi % 2 === 1) return <pre key={bi} className="fa-code">{blk.replace(/^\w+\n/, "")}</pre>;
        return blk.split("\n").map((ln, i) => {
          const t = ln.trim();
          if (!t) return <div key={`${bi}-${i}`} className="fa-gap" />;
          if (t.startsWith("## ")) return <h4 key={`${bi}-${i}`}>{t.replace(/^##\s*/, "")}</h4>;
          if (t.startsWith("# ")) return <h3 key={`${bi}-${i}`}>{t.replace(/^#\s*/, "")}</h3>;
          if (t.startsWith("- ") || t.startsWith("* ")) return <li key={`${bi}-${i}`}>{t.replace(/^[-*]\s*/, "")}</li>;
          return <p key={`${bi}-${i}`}>{t.replace(/`([^`]+)`/g, "$1")}</p>;
        });
      })}
    </div>
  );
}

export default function FileAnalyzer() {
  const [sets, setSets] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState({ done: 0, total: 0 });
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const filesInput = useRef(null);
  const folderInput = useRef(null);

  const loadSets = useCallback(async () => {
    try {
      const r = await axios.get(`${API}/filesets`);
      setSets(r.data);
      if (!activeId && r.data.length) setActiveId(r.data[0].id);
    } catch (e) { console.error(e); }
  }, [activeId]);

  useEffect(() => { loadSets(); }, [loadSets]);

  const loadFiles = useCallback(async (id) => {
    if (!id) { setFiles([]); return; }
    try {
      const [f, a] = await Promise.all([
        axios.get(`${API}/filesets/${id}/files`),
        axios.get(`${API}/filesets/${id}/analyses`),
      ]);
      setFiles(f.data);
      setAnalysis(a.data?.[0] || null);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { loadFiles(activeId); }, [activeId, loadFiles]);

  const ensureSet = async () => {
    if (activeId) return activeId;
    const r = await axios.post(`${API}/filesets`, { title: `Analysis ${new Date().toLocaleString()}` });
    setActiveId(r.data.id);
    await loadSets();
    return r.data.id;
  };

  const newSet = async () => {
    const r = await axios.post(`${API}/filesets`, { title: `Analysis ${new Date().toLocaleString()}` });
    setActiveId(r.data.id);
    setAnalysis(null);
    setFiles([]);
    await loadSets();
    toast.success("New analysis set created");
  };

  const handlePicked = async (fileList) => {
    const arr = Array.from(fileList || []);
    if (!arr.length) return;
    const id = await ensureSet();
    setUploading(true);
    setProgress({ done: 0, total: arr.length });
    let ok = 0, fail = 0;
    for (let i = 0; i < arr.length; i++) {
      const file = arr[i];
      const rel = file.webkitRelativePath || file.name;
      try {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("rel_path", rel);
        await axios.post(`${API}/filesets/${id}/files`, fd, { headers: { "Content-Type": "multipart/form-data" } });
        ok += 1;
      } catch (e) { fail += 1; }
      setProgress({ done: i + 1, total: arr.length });
    }
    setUploading(false);
    await loadFiles(id);
    await loadSets();
    if (ok) toast.success(`Imported ${ok} file${ok > 1 ? "s" : ""}${fail ? ` · ${fail} skipped` : ""}`);
    else toast.error("No files imported (unsupported types or too large)");
  };

  const remove = async (fid) => {
    try { await axios.delete(`${API}/files/${fid}`); await loadFiles(activeId); await loadSets(); toast("File removed"); }
    catch { toast.error("Delete failed"); }
  };

  const download = (fid) => window.open(`${API}/files/${fid}/download`, "_blank", "noopener");

  const analyze = async () => {
    if (!activeId || !files.length) { toast.error("Upload files first"); return; }
    setAnalyzing(true);
    try {
      const r = await axios.post(`${API}/filesets/${activeId}/analyze`, { question: question.trim() || null });
      setAnalysis(r.data);
      toast.success(`Analysis complete · ${r.data.model_label}`);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Analysis failed");
    } finally { setAnalyzing(false); }
  };

  return (
    <div className="fa-wrap" data-testid="file-analyzer">
      <section className="fa-console">
        <div className="fa-head">
          <Boxes size={17} /> <span>File Analyzer</span>
          <em>Upload files or a whole folder — real object storage, then AI analysis.</em>
        </div>
        <div className="fa-note">
          A hosted app can’t read your local drive directly (browser sandbox). Pick files or an entire folder below and ACASO imports them into real storage, then the AI reads and analyzes them.
        </div>

        <div className="fa-actions">
          <button className="fa-btn primary" data-testid="analyzer-add-files" onClick={() => filesInput.current?.click()} disabled={uploading}>
            <FilePlus size={16} /> Add Files
          </button>
          <button className="fa-btn" data-testid="analyzer-add-folder" onClick={() => folderInput.current?.click()} disabled={uploading}>
            <FolderUp size={16} /> Add Folder
          </button>
          <button className="fa-btn ghost" data-testid="analyzer-new-set" onClick={newSet} disabled={uploading}>
            <Plus size={16} /> New Set
          </button>
          <input ref={filesInput} type="file" multiple style={{ display: "none" }}
            data-testid="analyzer-files-input"
            onChange={(e) => { handlePicked(e.target.files); e.target.value = ""; }} />
          <input ref={folderInput} type="file" multiple webkitdirectory="" directory="" style={{ display: "none" }}
            data-testid="analyzer-folder-input"
            onChange={(e) => { handlePicked(e.target.files); e.target.value = ""; }} />
        </div>

        {uploading && (
          <div className="fa-prog" data-testid="analyzer-progress">
            <Loader2 className="spin" size={14} /> Importing {progress.done}/{progress.total}…
            <div className="fa-prog-bar"><div style={{ width: `${progress.total ? (progress.done / progress.total) * 100 : 0}%` }} /></div>
          </div>
        )}

        {sets.length > 1 && (
          <div className="fa-sets">
            {sets.map((s) => (
              <button key={s.id} className={s.id === activeId ? "fa-set active" : "fa-set"} onClick={() => setActiveId(s.id)}>
                <Files size={12} /> {s.title} <span>{s.file_count}</span>
              </button>
            ))}
          </div>
        )}
      </section>

      <div className="fa-grid">
        <section className="fa-files" data-testid="analyzer-file-list">
          <div className="fa-sub-head"><HardDriveUpload size={14} /> Imported Files <span className="fa-count">{files.length}</span></div>
          {files.length === 0 ? (
            <div className="fa-empty"><FolderUp size={24} /><p>No files yet. Add files or a folder to begin.</p></div>
          ) : (
            <div className="fa-list">
              {files.map((f) => {
                const isImg = (f.content_type || "").startsWith("image/");
                return (
                  <div key={f.id} className="fa-row" data-testid={`analyzer-file-${f.id}`}>
                    <span className="fa-fic">{isImg ? <ImageIcon size={14} /> : <FileText size={14} />}</span>
                    <span className="fa-fname" title={f.rel_path}>{f.rel_path}</span>
                    {!f.readable && <span className="fa-bin">binary</span>}
                    <span className="fa-fsize">{fmtBytes(f.size)}</span>
                    <button className="fa-ic" onClick={() => download(f.id)} title="Download"><Download size={13} /></button>
                    <button className="fa-ic danger" data-testid={`analyzer-delete-${f.id}`} onClick={() => remove(f.id)} title="Delete"><Trash2 size={13} /></button>
                  </div>
                );
              })}
            </div>
          )}

          <div className="fa-ask">
            <textarea
              data-testid="analyzer-question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Optional: ask a specific question about these files (e.g. 'find security risks' or 'summarize the API')"
              rows={2}
            />
            <button className="fa-analyze" data-testid="analyzer-run" onClick={analyze} disabled={analyzing || !files.length}>
              {analyzing ? <Loader2 className="spin" size={16} /> : <Sparkles size={16} />}
              {analyzing ? "Analyzing…" : "Analyze with AI"}
            </button>
          </div>
        </section>

        <section className="fa-result" data-testid="analyzer-result">
          <div className="fa-sub-head"><Sparkles size={14} /> AI Analysis {analysis?.model_label && <span className="fa-model">{analysis.model_label}</span>}</div>
          {analyzing ? (
            <div className="fa-skeleton">
              {[...Array(5)].map((_, i) => <div key={i} className="fa-sk-line" style={{ width: `${90 - i * 9}%` }} />)}
            </div>
          ) : analysis ? (
            <>
              {analysis.truncated && <div className="fa-trunc">Note: content was truncated to fit the model context window.</div>}
              {analysis.question && <div className="fa-q">Q: {analysis.question}</div>}
              <Markdown text={analysis.analysis} />
            </>
          ) : (
            <div className="fa-empty"><Play size={24} /><p>Run an analysis to see per-file notes, cross-file insights, risks and recommended actions.</p></div>
          )}
        </section>
      </div>
    </div>
  );
}
