#!/usr/bin/env python3
"""
ACASO Local Node - runs ON YOUR PC and lets the hosted ACASO app work with your files and your browser.

    Windows:  set ACASO_URL=https://<your-acaso> && set ACASO_KEY=<Agent Bridge key> && python acaso_node.py --root "C:\\Users\\you\\ACASO" --shell --browser
    Linux:    ACASO_URL=https://<your-acaso> ACASO_KEY=<Agent Bridge key> python3 acaso_node.py --root ~/ACASO --shell --browser

Requirements:  python -m pip install httpx
Browser (opt): python -m pip install playwright && python -m playwright install chrome

Safety, enforced HERE on your machine (the server enforces the same rules again):
  * Only paths inside the --root folder(s) you pass are ever read or written.
  * The node only executes tasks you APPROVED in the ACASO "Local Node" tab. Read-only tasks are auto-approved.
  * Browser tasks fill forms and STOP. Nothing is submitted until you approve a separate submit step.
  * Passwords / 2FA: type them yourself in the Chrome window that opens. This program never sees or stores them.
  * --shell is off unless you pass it. Shell commands run inside the allowed root with a timeout.
  * --companion opens the ACASO Companion as its own small always-on-top desktop window (real Chrome in app mode,
    separate profile, so it survives closing your normal browser). Works with or without pairing.
"""
import argparse
import base64
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Missing dependency: python -m pip install httpx")
    sys.exit(1)

NODE_VERSION = "1.0.0"
STATE_FILE = Path.home() / ".acaso_node.json"


# ----------------------------------------------------------------------------------------------
class Node:
    def __init__(self, url, key, roots, shell, browser, name):
        self.api = url.rstrip("/") + "/api"
        self.h = {"X-ACASO-Key": key, "Content-Type": "application/json"}
        self.roots = [Path(r).expanduser().resolve() for r in roots]
        for r in self.roots:
            r.mkdir(parents=True, exist_ok=True)
        self.shell = shell
        self.browser = browser
        self.name = name or f"{platform.node()}-node"
        self.node_id = None
        self.pw = None
        self.browser_ctx = None
        self.pages = {}  # session_id -> page
        self.cx = httpx.Client(timeout=60)

    # ---- path safety ----
    def safe(self, p: str) -> Path:
        rp = Path(p).expanduser().resolve()
        for r in self.roots:
            try:
                rp.relative_to(r)
                return rp
            except ValueError:
                continue
        raise PermissionError(f"Path outside allowed roots: {p}")

    # ---- pairing ----
    def register(self):
        saved = {}
        if STATE_FILE.exists():
            try:
                saved = json.loads(STATE_FILE.read_text())
            except Exception:
                saved = {}
        caps = ["files"] + (["shell"] if self.shell else []) + (["browser"] if self.browser else [])
        body = {"name": self.name, "os": f"{platform.system()} {platform.release()}", "hostname": socket.gethostname(),
                "allowed_roots": [str(r) for r in self.roots], "capabilities": caps, "node_version": NODE_VERSION,
                "node_id": saved.get("node_id")}
        r = self.cx.post(f"{self.api}/node/register", headers=self.h, json=body)
        if r.status_code == 401:
            print("Rejected: bad ACASO_KEY. Copy it from the Agent Bridge tab.")
            sys.exit(1)
        r.raise_for_status()
        self.node_id = r.json()["id"]
        STATE_FILE.write_text(json.dumps({"node_id": self.node_id}))
        print(f"Paired as '{self.name}' ({self.node_id[:8]}) | roots={[str(x) for x in self.roots]} | caps={caps}")

    # ---- main loop ----
    def run(self):
        self.register()
        print("Waiting for approved tasks... (Ctrl+C to stop)")
        beat = 0
        while True:
            try:
                r = self.cx.post(f"{self.api}/node/{self.node_id}/claim", headers=self.h)
                if r.status_code == 404:
                    self.register()
                    continue
                task = r.json() if r.status_code == 200 else {}
                if task and task.get("id"):
                    self.execute(task)
                    continue
                beat += 1
                if beat % 8 == 0:
                    self.cx.post(f"{self.api}/node/{self.node_id}/heartbeat", headers=self.h)
            except KeyboardInterrupt:
                print("\nStopping node.")
                self.close_browser()
                return
            except Exception as e:
                print(f"[net] {e}")
                time.sleep(5)
            time.sleep(3)

    def report(self, tid, status, result=None, error=None, shot=None):
        body = {"status": status, "result": result, "error": error, "screenshot_b64": shot}
        self.cx.post(f"{self.api}/node/tasks/{tid}/result", headers=self.h, json=body)

    # ---- execution ----
    def execute(self, t):
        kind, p, tid = t["kind"], t.get("params") or {}, t["id"]
        print(f"-> {kind} {json.dumps(p)[:120]}")
        try:
            fn = getattr(self, "do_" + kind, None)
            if not fn:
                raise ValueError(f"unsupported task kind {kind}")
            out = fn(p)
            if isinstance(out, tuple):  # (status, result, screenshot)
                self.report(tid, out[0], out[1], None, out[2] if len(out) > 2 else None)
            else:
                self.report(tid, "done", out)
            print("   done")
        except Exception as e:
            print(f"   FAILED: {e}")
            self.report(tid, "failed", None, str(e)[:800])

    def do_sys_info(self, p):
        return {"os": platform.platform(), "python": sys.version.split()[0], "cwd": os.getcwd(), "roots": [str(r) for r in self.roots],
                "disk_free_gb": round(shutil.disk_usage(str(self.roots[0])).free / 1e9, 1) if self.roots else None}

    def do_file_list(self, p):
        d = self.safe(p.get("path") or str(self.roots[0]))
        if not d.is_dir():
            raise FileNotFoundError(f"not a directory: {d}")
        items = []
        for c in sorted(d.iterdir())[:500]:
            st = c.stat()
            items.append({"name": c.name, "type": "dir" if c.is_dir() else "file", "size": st.st_size, "modified": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(st.st_mtime))})
        return {"path": str(d), "count": len(items), "items": items}

    def do_file_stat(self, p):
        f = self.safe(p["path"])
        if not f.exists():
            return {"path": str(f), "exists": False}
        st = f.stat()
        return {"path": str(f), "exists": True, "type": "dir" if f.is_dir() else "file", "size": st.st_size}

    def do_file_read(self, p):
        f = self.safe(p["path"])
        data = f.read_bytes()
        limit = int(p.get("max_bytes") or 200_000)
        try:
            text = data[:limit].decode("utf-8")
            return {"path": str(f), "size": len(data), "truncated": len(data) > limit, "content": text}
        except UnicodeDecodeError:
            return {"path": str(f), "size": len(data), "binary": True, "b64_head": base64.b64encode(data[:4096]).decode()}

    def do_mkdir(self, p):
        d = self.safe(p["path"]); d.mkdir(parents=True, exist_ok=True)
        return {"path": str(d), "created": True}

    def do_file_write(self, p):
        f = self.safe(p["path"]); f.parent.mkdir(parents=True, exist_ok=True)
        existed = f.exists()
        if existed and p.get("backup", True):
            shutil.copy2(f, f.with_suffix(f.suffix + ".acaso.bak"))
        f.write_text(p.get("content") or "", encoding="utf-8")
        return {"path": str(f), "bytes": f.stat().st_size, "overwrote": existed, "backup": str(f.with_suffix(f.suffix + '.acaso.bak')) if existed else None}

    def do_file_append(self, p):
        f = self.safe(p["path"]); f.parent.mkdir(parents=True, exist_ok=True)
        with f.open("a", encoding="utf-8") as fh:
            fh.write(p.get("content") or "")
        return {"path": str(f), "bytes": f.stat().st_size}

    def do_file_move(self, p):
        s, d = self.safe(p["src"]), self.safe(p["dst"])
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
        return {"src": str(s), "dst": str(d)}

    def do_file_delete(self, p):
        f = self.safe(p["path"])
        trash = self.roots[0] / ".acaso_trash"; trash.mkdir(exist_ok=True)
        dest = trash / f"{int(time.time())}_{f.name}"
        shutil.move(str(f), str(dest))
        return {"path": str(f), "moved_to_trash": str(dest), "note": "soft-deleted; restore from .acaso_trash"}

    def do_shell(self, p):
        if not self.shell:
            raise PermissionError("node started without --shell")
        cwd = self.safe(p.get("cwd") or str(self.roots[0]))
        cmd = p["command"]
        r = subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True, text=True, timeout=int(p.get("timeout") or 120))
        return {"command": cmd, "cwd": str(cwd), "returncode": r.returncode, "stdout": r.stdout[-8000:], "stderr": r.stderr[-4000:]}

    # ---- browser (real Chrome on this PC, headed) ----
    def ensure_browser(self):
        if not self.browser:
            raise PermissionError("node started without --browser")
        if self.browser_ctx:
            return
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        profile = Path.home() / ".acaso_chrome_profile"
        try:
            self.browser_ctx = self.pw.chromium.launch_persistent_context(str(profile), channel="chrome", headless=False, viewport={"width": 1280, "height": 900})
        except Exception:
            self.browser_ctx = self.pw.chromium.launch_persistent_context(str(profile), headless=False, viewport={"width": 1280, "height": 900})
        print("   Chrome opened (persistent profile: logins you do here are kept between runs)")

    def close_browser(self):
        try:
            if self.browser_ctx:
                self.browser_ctx.close()
            if self.pw:
                self.pw.stop()
        except Exception:
            pass
        self.browser_ctx = None; self.pw = None; self.pages = {}

    def page(self, sid):
        self.ensure_browser()
        if sid not in self.pages or self.pages[sid].is_closed():
            self.pages[sid] = self.browser_ctx.new_page()
        return self.pages[sid]

    def shot(self, pg):
        return base64.b64encode(pg.screenshot(type="jpeg", quality=45)).decode()

    def do_browser_open(self, p):
        sid = p.get("session_id") or str(uuid.uuid4())[:8]
        pg = self.page(sid)
        pg.goto(p["url"], timeout=60000, wait_until="domcontentloaded")
        pg.wait_for_timeout(1000)
        return ("done", {"session_id": sid, "url": pg.url, "title": pg.title()}, self.shot(pg))

    def do_browser_screenshot(self, p):
        pg = self.page(p["session_id"])
        return ("done", {"session_id": p["session_id"], "url": pg.url, "title": pg.title()}, self.shot(pg))

    def _locate(self, pg, ref):
        ref = str(ref)
        for cand in (lambda: pg.get_by_label(ref, exact=False), lambda: pg.get_by_placeholder(ref, exact=False),
                     lambda: pg.locator(f"[name='{ref}']"), lambda: pg.locator(ref)):
            try:
                loc = cand()
                if loc.count() > 0:
                    return loc.first
            except Exception:
                continue
        raise LookupError(f"field not found: {ref}")

    def do_browser_fill(self, p):
        sid = p.get("session_id") or str(uuid.uuid4())[:8]
        pg = self.page(sid)
        if p.get("url"):
            pg.goto(p["url"], timeout=60000, wait_until="domcontentloaded"); pg.wait_for_timeout(800)
        filled, skipped = [], []
        for f in p.get("fields") or []:
            ref, val = f.get("label_or_selector"), f.get("value")
            if val is None or "[OWNER TYPES THIS]" in str(val):
                skipped.append({"field": ref, "reason": "owner types this manually (password/2FA/secret)"}); continue
            try:
                loc = self._locate(pg, ref)
                tag = loc.evaluate("e => e.tagName.toLowerCase()")
                typ = loc.evaluate("e => e.type || ''")
                if tag == "select":
                    loc.select_option(label=str(val))
                elif typ in ("checkbox", "radio"):
                    loc.check() if str(val).lower() in ("true", "yes", "1", "on") else loc.uncheck()
                else:
                    loc.fill(str(val))
                filled.append(ref)
            except Exception as e:
                skipped.append({"field": ref, "reason": str(e)[:120]})
        return ("awaiting_submit", {"session_id": sid, "url": pg.url, "title": pg.title(), "filled": filled, "skipped": skipped,
                                    "note": "Form filled, NOT submitted. Review the screenshot, finish any manual fields in the Chrome window, then approve a browser_submit task."}, self.shot(pg))

    def do_browser_submit(self, p):
        pg = self.page(p["session_id"])
        ref = p.get("label_or_selector")
        btn = self._locate(pg, ref) if ref else pg.locator("button[type=submit], input[type=submit], button:has-text('Submit'), button:has-text('Sign up'), button:has-text('Create account'), button:has-text('Continue')").first
        btn.click(timeout=15000)
        pg.wait_for_timeout(2500)
        return ("done", {"session_id": p["session_id"], "url": pg.url, "title": pg.title()}, self.shot(pg))

    def do_browser_close(self, p):
        sid = p.get("session_id")
        if sid and sid in self.pages:
            try: self.pages[sid].close()
            except Exception: pass
            self.pages.pop(sid, None)
        else:
            self.close_browser()
        return {"closed": sid or "all"}


# ----------------------------------------------------------------------------------------------
# Companion desktop window: Chrome --app mode + best-effort always-on-top
# ----------------------------------------------------------------------------------------------
def _find_chrome():
    cands = []
    if platform.system() == "Windows":
        pf = [os.environ.get("PROGRAMFILES", r"C:\Program Files"), os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"), os.environ.get("LOCALAPPDATA", "")]
        for base in pf:
            cands += [os.path.join(base, r"Google\Chrome\Application\chrome.exe"), os.path.join(base, r"Microsoft\Edge\Application\msedge.exe"),
                      os.path.join(base, r"BraveSoftware\Brave-Browser\Application\brave.exe")]
    elif platform.system() == "Darwin":
        cands += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    else:
        for n in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
            path = shutil.which(n)
            if path:
                cands.append(path)
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def _keep_on_top_windows(title_part: str, stop):
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE, SWP_NOACTIVATE = -1, 0x0002, 0x0001, 0x0010
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def find():
        found = []
        def cb(hwnd, _):
            n = user32.GetWindowTextLengthW(hwnd)
            if n:
                buf = ctypes.create_unicode_buffer(n + 1); user32.GetWindowTextW(hwnd, buf, n + 1)
                if title_part.lower() in buf.value.lower() and user32.IsWindowVisible(hwnd):
                    found.append(hwnd)
            return True
        user32.EnumWindows(EnumWindowsProc(cb), 0)
        return found
    while not stop.is_set():
        for hwnd in find():
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
        time.sleep(3)


def _keep_on_top_linux(title_part: str, stop):
    if not shutil.which("wmctrl"):
        print("   (install 'wmctrl' for always-on-top on Linux: sudo apt install wmctrl)")
        return
    while not stop.is_set():
        subprocess.run(["wmctrl", "-r", title_part, "-b", "add,above"], capture_output=True)
        time.sleep(3)


def launch_companion(url: str, on_top: bool = True):
    """Open the Companion as its own app window; returns the Popen (or None)."""
    import threading
    chrome = _find_chrome()
    target = url.rstrip("/") + "/?mode=companion"
    if not chrome:
        print("No Chrome/Edge found - opening the Companion in your default browser instead.")
        import webbrowser; webbrowser.open(target)
        return None
    profile = Path.home() / ".acaso_companion_profile"
    args = [chrome, f"--app={target}", f"--user-data-dir={profile}", "--window-size=440,760", "--window-position=40,40",
            "--no-first-run", "--no-default-browser-check", "--disable-features=TranslateUI"]
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Companion window opened ({os.path.basename(chrome)} app mode, profile {profile})")
    if on_top:
        stop = threading.Event()
        fn = _keep_on_top_windows if platform.system() == "Windows" else (_keep_on_top_linux if platform.system() == "Linux" else None)
        if fn:
            threading.Thread(target=fn, args=("ACASO Companion", stop), daemon=True).start()
            print("   always-on-top: enabled")
        else:
            print("   always-on-top: not available on this OS (window still opens as an app)")
    return proc


def main():
    ap = argparse.ArgumentParser(description="ACASO Local Node")
    ap.add_argument("--url", default=os.environ.get("ACASO_URL"), help="ACASO site URL (or env ACASO_URL)")
    ap.add_argument("--key", default=os.environ.get("ACASO_KEY"), help="Agent Bridge key (or env ACASO_KEY)")
    ap.add_argument("--root", action="append", default=[], help="Allowed folder (repeatable). Default: ~/ACASO")
    ap.add_argument("--shell", action="store_true", help="Allow approved shell commands inside the root")
    ap.add_argument("--browser", action="store_true", help="Allow approved browser tasks in a real Chrome window")
    ap.add_argument("--name", default=None)
    ap.add_argument("--companion", action="store_true", help="Open the ACASO Companion as its own always-on-top desktop window")
    ap.add_argument("--no-top", action="store_true", help="With --companion: do not force always-on-top")
    a = ap.parse_args()
    if not a.url:
        print("Need --url or ACASO_URL."); sys.exit(1)
    proc = launch_companion(a.url, on_top=not a.no_top) if a.companion else None
    if not a.key:
        if a.companion:
            print("No ACASO_KEY given - running Companion window only (no file/browser tasks). Ctrl+C to close.")
            try:
                while proc is None or proc.poll() is None:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            return
        print("Need --key/ACASO_KEY (key is on the Agent Bridge tab)."); sys.exit(1)
    roots = a.root or [str(Path.home() / "ACASO")]
    Node(a.url, a.key, roots, a.shell, a.browser, a.name).run()


if __name__ == "__main__":
    main()
