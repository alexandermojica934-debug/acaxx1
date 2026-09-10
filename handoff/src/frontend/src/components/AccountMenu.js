import React, { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { AnimatePresence, motion } from "framer-motion";
import { User, LogOut, KeyRound, X, Loader2, ShieldCheck } from "lucide-react";
import { API } from "../App";

export const AccountMenu = ({ user, onLogout, onUserChange }) => {
  const [open, setOpen] = useState(false);
  const [pw, setPw] = useState({ current_password: "", new_password: "" });
  const [changing, setChanging] = useState(false);
  const [showPw, setShowPw] = useState(false);

  const change = async (e) => {
    e.preventDefault();
    setChanging(true);
    try {
      const r = await axios.post(`${API}/auth/change-password`, pw);
      toast.success(r.data.note || "Password updated");
      setPw({ current_password: "", new_password: "" }); setShowPw(false);
    } catch (err) { toast.error(err?.response?.data?.detail || "Could not change password"); }
    finally { setChanging(false); }
  };

  return (
    <div className="acct" data-testid="account-menu">
      <button className="owner-badge acct-btn" onClick={() => setOpen((o) => !o)} data-testid="account-toggle" title={user.email}>
        <span className="dot" /> {user.name || "Owner"} · Sovereign
      </button>
      <AnimatePresence>
        {open && (
          <motion.div className="acct-pop" initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} data-testid="account-popover">
            <div className="acct-row"><User size={13} /> <div><b>{user.name || "Owner"}</b><small>{user.email}</small></div><button className="rd-ic" onClick={() => setOpen(false)}><X size={13} /></button></div>
            <div className="acct-meta"><ShieldCheck size={11} /> single-owner workspace · httpOnly session cookie</div>
            {!showPw ? (
              <button className="acct-item" onClick={() => setShowPw(true)} data-testid="account-change-pw"><KeyRound size={13} /> Change password</button>
            ) : (
              <form className="acct-form" onSubmit={change}>
                <input className="cw-input" type="password" placeholder="current password" required value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} data-testid="pw-current" autoComplete="current-password" />
                <input className="cw-input" type="password" placeholder="new password (10+, mixed case, digit)" required minLength={10} value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} data-testid="pw-new" autoComplete="new-password" />
                <div className="cw-row" style={{ marginTop: 6 }}>
                  <button className="rd-btn primary sm" type="submit" disabled={changing} data-testid="pw-submit">{changing ? <Loader2 className="spin" size={13} /> : <KeyRound size={13} />} Update</button>
                  <button className="rd-btn sm" type="button" onClick={() => setShowPw(false)}>Cancel</button>
                </div>
              </form>
            )}
            <button className="acct-item danger" onClick={onLogout} data-testid="account-logout"><LogOut size={13} /> Sign out</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AccountMenu;
