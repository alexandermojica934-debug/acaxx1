import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  FolderUp, FilePlus, Loader2, Sparkles, Trash2, Download, FileText,
  Image as ImageIcon, Play, X, Plus, HardDriveUpload, Files, Boxes,
  MessagesSquare, Send, Cloud, FolderOpen, ChevronRight, Check, Unplug, Folder
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
  const inline = (t) => {
    const nodes = [];
    const re = /(\*\*([^*]+)\*\*|`([^`]+)`)/g;
    let last = 0, m, i = 0;
    while ((m = re.exec(t)) !== null) {
      if (m.index > last) nodes.push(t.slice(last, m.index));
      if (m[2] !== undefined) nodes.push(<strong key={`b${i++}`}>{m[2]}</strong>);
      else if (m[3] !== undefined) nodes.push(<code key={`c${i++}`}>{m[3]}</code>);
      last = m.index + m[0].length;
    }
    if (last < t.length) nodes.push(t.slice(last));
    return nodes;
  };
  const blocks = text.split(/```/);
  return (
    <div className="fa-md">
      {blocks.map((blk, bi) => {
        if (bi % 2 === 1) return <pre key={bi} className="fa-code">{blk.replace(/^\w+\n/, "")}</pre>;
        return blk.split("\n").map((ln, i) => {
          const t = ln.trim();
          const k = `${bi}-${i}`;
          if (!t) return <div key={k} className="fa-gap" />;
          if (t.startsWith("### ")) return <h5 key={k}>{inline(t.replace(/^###\s*/, ""))}</h5>;
          if (t.startsWith("## ")) return <h4 key={k}>{inline(t.replace(/^##\s*/, ""))}</h4>;
          if (t.startsWith("# ")) return <h3 key={k}>{inline(t.replace(/^#\s*/, ""))}</h3>;
          if (t.startsWith("- ") || t.startsWith("* ")) return <li key={k}>{inline(t.replace(/^[-*]\s*/, ""))}</li>;
          return <p key={k}>{inline(t)}</p>;
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
  const [chat, setChat] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatSending, setChatSending] = useState(false);
  // Google Drive
  const [drive, setDrive] = useState({ configured: false, connected: false, email: null });
  const [driveOpen, setDriveOpen] = useState(false);
  const [driveItems, setDriveItems] = useState([]);
  const [driveCrumbs, setDriveCrumbs] = useState([{ id: "root", name: "My Drive" }]);
  const [driveSel, setDriveSel] = useState([]);
  const [driveLoading, setDriveLoading] = useState(false);
  const [driveImporting, setDriveImporting] = useState(false);
  const [driveSearch, setDriveSearch] = useState("");
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
      try { const c = await axios.get(`${API}/filesets/${id}/chat`); setChat(c.data || []); }
      catch { setChat([]); }
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
    setChat([]);
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

  const analyze = async (fsid, q) => {
    const id = (typeof fsid === "string" && fsid) ? fsid : activeId;
    if (!id) { toast.error("Upload files first"); return; }
    setAnalyzing(true);
    try {
      const question_ = (q !== undefined && q !== null) ? q : (question.trim() || null);
      const r = await axios.post(`${API}/filesets/${id}/analyze`, { question: question_ });
      setAnalysis(r.data);
      toast.success(`Analysis complete · ${r.data.model_label}`);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Analysis failed");
    } finally { setAnalyzing(false); }
  };

  const sendChat = async () => {
    const msg = chatInput.trim();
    if (!msg) return;
    if (!activeId || !files.length) { toast.error("Upload files first"); return; }
    setChatInput("");
    const now = new Date().toISOString();
    setChat((c) => [...c, { id: `tmp-${now}`, role: "user", content: msg, created_at: now }]);
    setChatSending(true);
    try {
      const r = await axios.post(`${API}/filesets/${activeId}/chat`, { message: msg });
      setChat((c) => [...c, r.data]);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Chat failed");
    } finally { setChatSending(false); }
  };

  const loadDriveStatus = useCallback(async () => {
    try { const r = await axios.get(`${API}/drive/status`); setDrive(r.data); }
    catch (e) { console.error(e); }
  }, []);

  useEffect(() => {
    loadDriveStatus();
    const params = new URLSearchParams(window.location.search);
    if (params.get("drive_connected")) {
      toast.success("Google Drive connected");
      loadDriveStatus();
      window.history.replaceState({}, "", window.location.pathname);
    } else if (params.get("drive_error")) {
      toast.error(`Drive connection failed: ${params.get("drive_error")}`);
      window.history.replaceState({}, "", window.location.pathname);
    }
  }, [loadDriveStatus]);

  const connectDrive = async () => {
    try {
      const r = await axios.get(`${API}/drive/connect`);
      window.location.href = r.data.authorization_url;
    } catch (e) { toast.error(e?.response?.data?.detail || "Cannot start Drive connect"); }
  };

  const disconnectDrive = async () => {
    try { await axios.post(`${API}/drive/disconnect`); await loadDriveStatus(); toast("Google Drive disconnected"); }
    catch { toast.error("Disconnect failed"); }
  };

  const browseFolder = async (folderId, crumbs) => {
    setDriveLoading(true);
    try {
      const r = await axios.get(`${API}/drive/list?folder_id=${encodeURIComponent(folderId)}`);
      setDriveItems(r.data.items || []);
      if (crumbs) setDriveCrumbs(crumbs);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to list Drive");
    } finally { setDriveLoading(false); }
  };

  const openDrive = async () => {
    setDriveOpen(true);
    setDriveSel([]);
    setDriveSearch("");
    setDriveCrumbs([{ id: "root", name: "My Drive" }]);
    await browseFolder("root", [{ id: "root", name: "My Drive" }]);
  };

  const searchDrive = async (term) => {
    const t = (term ?? driveSearch).trim();
    if (!t) { const cur = driveCrumbs[driveCrumbs.length - 1]; browseFolder(cur.id, driveCrumbs); return; }
    setDriveLoading(true);
    try {
      const r = await axios.get(`${API}/drive/list?search=${encodeURIComponent(t)}`);
      setDriveItems(r.data.items || []);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Drive search failed");
    } finally { setDriveLoading(false); }
  };

  const clearSearch = () => {
    setDriveSearch("");
    const cur = driveCrumbs[driveCrumbs.length - 1];
    browseFolder(cur.id, driveCrumbs);
  };

  const enterFolder = (item) => {
    setDriveSearch("");
    const crumbs = [...driveCrumbs, { id: item.id, name: item.name }];
    browseFolder(item.id, crumbs);
  };

  const gotoCrumb = (idx) => {
    setDriveSearch("");
    const crumbs = driveCrumbs.slice(0, idx + 1);
    browseFolder(crumbs[crumbs.length - 1].id, crumbs);
  };

  const toggleDriveSel = (id) => setDriveSel((s) => s.includes(id) ? s.filter((x) => x !== id) : [...s, id]);

  const importDrive = async () => {
    if (!driveSel.length) { toast.error("Select at least one file"); return; }
    setDriveImporting(true);
    try {
      const r = await axios.post(`${API}/drive/import`, { file_ids: driveSel, fileset_id: activeId });
      setActiveId(r.data.fileset_id);
      await loadSets();
      await loadFiles(r.data.fileset_id);
      const imp = r.data.imported?.length || 0;
      const skp = r.data.skipped?.length || 0;
      toast.success(`Imported ${imp} file${imp !== 1 ? "s" : ""} from Drive${skp ? ` · ${skp} skipped` : ""}`);
      setDriveOpen(false);
      setDriveSel([]);
      if (imp > 0) { toast("Auto-analyzing imported files…"); analyze(r.data.fileset_id, null); }
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Drive import failed");
    } finally { setDriveImporting(false); }
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

        {drive.configured && (
          <div className="fa-drive" data-testid="analyzer-drive-bar">
            <Cloud size={15} />
            {drive.connected ? (
              <>
                <span className="fa-drive-on">Google Drive connected{drive.email ? ` · ${drive.email}` : ""}</span>
                <button className="fa-drive-btn" data-testid="drive-browse" onClick={openDrive}><FolderOpen size={14} /> Browse Drive</button>
                <button className="fa-drive-btn ghost" data-testid="drive-disconnect" onClick={disconnectDrive}><Unplug size={14} /> Disconnect</button>
              </>
            ) : (
              <>
                <span className="fa-drive-off">Import files straight from your Google Drive</span>
                <button className="fa-drive-btn" data-testid="drive-connect" onClick={connectDrive}><Cloud size={14} /> Connect Google Drive</button>
              </>
            )}
          </div>
        )}

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
            <button className="fa-analyze" data-testid="analyzer-run" onClick={() => analyze()} disabled={analyzing || !files.length}>
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

      <section className="fa-chat" data-testid="analyzer-chat">
        <div className="fa-sub-head"><MessagesSquare size={14} /> Follow-up Chat <span className="fa-chat-hint">ask anything about these files</span></div>
        <div className="fa-chat-log" data-testid="analyzer-chat-log">
          {chat.length === 0 ? (
            <div className="fa-chat-empty">Upload files, then ask follow-up questions here. Answers are grounded in your files.</div>
          ) : (
            chat.map((m) => (
              <div key={m.id} className={`fa-msg ${m.role}`} data-testid={`analyzer-chat-msg-${m.role}`}>
                <span className="fa-msg-who">{m.role === "user" ? "You" : "ACASO"}</span>
                <div className="fa-msg-body"><Markdown text={m.content} /></div>
              </div>
            ))
          )}
          {chatSending && <div className="fa-msg assistant"><span className="fa-msg-who">ACASO</span><div className="fa-msg-body"><Loader2 className="spin" size={14} /> thinking...</div></div>}
        </div>
        <div className="fa-chat-input">
          <input
            data-testid="analyzer-chat-input"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendChat(); } }}
            placeholder="Ask a follow-up about your files..."
            disabled={chatSending || !files.length}
          />
          <button data-testid="analyzer-chat-send" onClick={sendChat} disabled={chatSending || !files.length || !chatInput.trim()}>
            {chatSending ? <Loader2 className="spin" size={15} /> : <Send size={15} />}
          </button>
        </div>
      </section>

      <AnimatePresence>
        {driveOpen && (
          <motion.div className="fa-modal-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setDriveOpen(false)}>
            <motion.div className="fa-modal" data-testid="drive-modal" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 14 }} onClick={(e) => e.stopPropagation()}>
              <div className="fa-modal-head">
                <Cloud size={16} /> <span>Google Drive</span>
                <button className="fa-modal-x" onClick={() => setDriveOpen(false)}><X size={16} /></button>
              </div>
              <div className="fa-drive-search">
                <Cloud size={13} className="fa-drive-search-ic" />
                <input
                  data-testid="drive-search-input"
                  value={driveSearch}
                  onChange={(e) => setDriveSearch(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") searchDrive(); }}
                  placeholder="Search your Drive by file name, then press Enter"
                />
                {driveSearch && <button className="fa-drive-search-x" data-testid="drive-search-clear" onClick={clearSearch}><X size={13} /></button>}
                <button className="fa-drive-search-go" data-testid="drive-search-go" onClick={() => searchDrive()}>Search</button>
              </div>
              <div className="fa-crumbs">
                {driveCrumbs.map((c, i) => (
                  <span key={c.id} className="fa-crumb">
                    {i > 0 && <ChevronRight size={12} />}
                    <button onClick={() => gotoCrumb(i)}>{c.name}</button>
                  </span>
                ))}
              </div>
              <div className="fa-drive-list" data-testid="drive-list">
                {driveLoading ? (
                  <div className="fa-empty"><Loader2 className="spin" size={18} /><p>Loading Drive…</p></div>
                ) : driveItems.length === 0 ? (
                  <div className="fa-empty"><Folder size={22} /><p>This folder is empty.</p></div>
                ) : (
                  driveItems.map((it) => (
                    <div key={it.id} className={`fa-drive-row ${!it.supported && !it.is_folder ? "unsupported" : ""}`} data-testid={`drive-item-${it.id}`}>
                      {it.is_folder ? (
                        <button className="fa-drive-folder" onClick={() => enterFolder(it)}>
                          <Folder size={15} /> <span>{it.name}</span> <ChevronRight size={14} />
                        </button>
                      ) : (
                        <label className={`fa-drive-file ${driveSel.includes(it.id) ? "sel" : ""}`}>
                          <input type="checkbox" disabled={!it.supported} checked={driveSel.includes(it.id)} onChange={() => toggleDriveSel(it.id)} />
                          <FileText size={14} />
                          <span className="fa-drive-name">{it.name}</span>
                          {!it.supported && <span className="fa-bin">unsupported</span>}
                        </label>
                      )}
                    </div>
                  ))
                )}
              </div>
              <div className="fa-modal-foot">
                <span className="fa-drive-count">{driveSel.length} selected</span>
                <button className="fa-analyze" data-testid="drive-import" onClick={importDrive} disabled={driveImporting || !driveSel.length}>
                  {driveImporting ? <Loader2 className="spin" size={15} /> : <Check size={15} />}
                  {driveImporting ? "Importing…" : "Import to analysis"}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
