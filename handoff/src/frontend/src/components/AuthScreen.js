import React, { useEffect, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Castle, Mail, Lock, LogIn, UserPlus, Loader2, Eye, EyeOff, ShieldCheck } from "lucide-react";
import { API } from "../App";

export default function AuthScreen({ onAuthed }) {
  const [status, setStatus] = useState(null);
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", name: "", remember_me: true });
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    axios.get(`${API}/auth/status`).then((r) => { setStatus(r.data); setMode(r.data.registration_open ? "register" : "login"); }).catch(() => setStatus({ has_owner: true, registration_open: false }));
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const r = await axios.post(`${API}/auth/${mode}`, form);
      toast.success(mode === "register" ? "Owner account created - welcome, Sovereign" : `Welcome back${r.data.user.name ? `, ${r.data.user.name}` : ""}`);
      onAuthed(r.data.user);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Could not sign in");
    } finally { setBusy(false); }
  };

  return (
    <div className="auth-root" data-testid="auth-screen">
      <motion.div className="auth-card" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}>
        <div className="auth-brand"><Castle size={22} /> ACASO <span>Omniverse</span></div>
        <h1>{mode === "register" ? "Claim the throne" : "Owner sign-in"}</h1>
        <p className="auth-sub">
          {status === null ? "Checking..." : mode === "register"
            ? "No owner exists yet. The first account created here becomes the single owner; registration then closes."
            : "This workspace belongs to its owner. Sign in with your email and password."}
        </p>
        <form onSubmit={submit} className="auth-form">
          {mode === "register" && (
            <label>Name (optional)<input data-testid="auth-name" className="cw-input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} autoComplete="name" /></label>
          )}
          <label><span><Mail size={12} /> Email</span><input data-testid="auth-email" className="cw-input" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} autoComplete="email" /></label>
          <label><span><Lock size={12} /> Password</span>
            <div className="auth-pw">
              <input data-testid="auth-password" className="cw-input" type={show ? "text" : "password"} required minLength={mode === "register" ? 10 : 1} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} autoComplete={mode === "register" ? "new-password" : "current-password"} />
              <button type="button" className="auth-eye" onClick={() => setShow((s) => !s)} aria-label="toggle password">{show ? <EyeOff size={14} /> : <Eye size={14} />}</button>
            </div>
            {mode === "register" && <small className="auth-hint">10+ characters, upper & lower case, and a digit.</small>}
          </label>
          <label className="auth-remember"><input data-testid="auth-remember" type="checkbox" checked={form.remember_me} onChange={(e) => setForm({ ...form, remember_me: e.target.checked })} /> Remember me for 30 days (otherwise 7)</label>
          <button data-testid="auth-submit" className="auth-submit" type="submit" disabled={busy || status === null}>
            {busy ? <Loader2 className="spin" size={15} /> : mode === "register" ? <UserPlus size={15} /> : <LogIn size={15} />} {mode === "register" ? "Create owner account" : "Sign in"}
          </button>
        </form>
        {status?.registration_open && mode === "register" && <button className="auth-link" onClick={() => setMode("login")}>Already have an account? Sign in</button>}
        {status && !status.registration_open && <div className="auth-foot"><ShieldCheck size={12} /> Registration closed - single-owner workspace. Sessions use an httpOnly cookie; passwords are bcrypt-hashed.</div>}
      </motion.div>
    </div>
  );
}
