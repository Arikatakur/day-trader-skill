"""Install, update and uninstall for Saladi (Windows, per-user, no admin rights).

Releases live on GitHub: each one carries Saladi-Setup.exe and its SHA-256.
The app asks GitHub for the latest release, shows an "update available" bar,
and on the user's yes downloads the new exe, checks the SHA-256, swaps it in
and restarts. Standard library only.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

SLUG = "Arikatakur/saladi"
API = "https://api.github.com/repos/%s/releases/latest" % SLUG
ASSET = "Saladi-Setup.exe"
HERE = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
FROZEN = getattr(sys, "frozen", False)
_state = {"at": 0, "info": None}
_lock = threading.Lock()


def version():
    try:
        with open(os.path.join(HERE, "version.txt"), encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return "0.0.0"


def _key(v):
    out = []
    for part in str(v).lstrip("vV").split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits or 0))
    return tuple(out + [0] * (3 - len(out)))


def newer(latest, current):
    return _key(latest) > _key(current)


def _get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "Saladi-updater", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def check(force=False):
    """Latest release vs this copy. Cached for an hour; never raises."""
    with _lock:
        if not force and _state["info"] is not None and time.time() - _state["at"] < 3600:
            return _state["info"]
    cur = version()
    info = {"current": cur, "latest": None, "available": False, "notes": "", "page": None, "asset": None,
            "sha": None, "can_apply": FROZEN, "error": None, "checked": time.strftime("%Y-%m-%d %H:%M")}
    try:
        rel = json.loads(_get(API).decode("utf-8"))
        info["latest"] = str(rel.get("tag_name", "")).lstrip("vV") or None
        info["notes"] = (rel.get("body") or "")[:1500]
        info["page"] = rel.get("html_url")
        for a in rel.get("assets") or []:
            if a.get("name") == ASSET:
                info["asset"] = a.get("browser_download_url")
            elif a.get("name") == ASSET + ".sha256":
                info["sha"] = a.get("browser_download_url")
        info["available"] = bool(info["latest"] and info["asset"] and newer(info["latest"], cur))
    except Exception as e:  # noqa: BLE001
        info["error"] = "could not reach GitHub: %s" % str(e)[:120]
    with _lock:
        _state.update({"at": time.time(), "info": info})
    return info


def cached():
    return _state["info"] or {"current": version(), "latest": None, "available": False, "can_apply": FROZEN}


def watch(on_change, every=3 * 3600):
    """Background check at start and every few hours; calls on_change() when the answer changes."""
    last = None
    while True:
        info = check(force=True)
        sig = (info.get("latest"), info.get("available"))
        if sig != last:
            last = sig
            on_change()
        time.sleep(every)


# ------------------------------------------------------------------ install

def install_dir():
    return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "Programs", "Saladi")


def installed_exe():
    return os.path.join(install_dir(), "Saladi.exe")


def is_installed_copy(exe=None):
    exe = os.path.abspath(exe or sys.executable)
    return os.path.normcase(exe) == os.path.normcase(os.path.abspath(installed_exe()))


def _shortcuts():
    start = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs", "Saladi.lnk")
    desk = os.path.join(os.path.expanduser("~"), "Desktop", "Saladi.lnk")
    return [start, desk]


def _make_shortcuts(target):
    ps = "; ".join(
        "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%s'); $s.TargetPath='%s'; "
        "$s.WorkingDirectory='%s'; $s.IconLocation='%s,0'; $s.Description='Saladi'; $s.Save()"
        % (lnk.replace("'", "''"), target.replace("'", "''"), os.path.dirname(target).replace("'", "''"),
           target.replace("'", "''")) for lnk in _shortcuts())
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, timeout=60,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def _register(target, ver):
    try:
        import winreg
    except ImportError:
        return
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Saladi") as k:
        for name, val in (("DisplayName", "Saladi"), ("DisplayVersion", ver), ("Publisher", "Saladi"),
                          ("DisplayIcon", target), ("InstallLocation", os.path.dirname(target)),
                          ("UninstallString", '"%s" --uninstall' % target)):
            winreg.SetValueEx(k, name, 0, winreg.REG_SZ, val)
        winreg.SetValueEx(k, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(k, "NoRepair", 0, winreg.REG_DWORD, 1)


def install(src_exe, shortcuts=True, register=True):
    """Copy this exe to %LOCALAPPDATA%\\Programs\\Saladi, add Start Menu + Desktop shortcuts and an
    Apps & features entry. Returns the installed path."""
    dst = installed_exe()
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.normcase(os.path.abspath(src_exe)) != os.path.normcase(os.path.abspath(dst)):
        for _ in range(20):  # an older copy may still be closing
            try:
                shutil.copy2(src_exe, dst)
                break
            except PermissionError:
                time.sleep(0.5)
        else:
            raise RuntimeError("Saladi is still running: close it and run the installer again")
    if shortcuts:
        _make_shortcuts(dst)
    if register:
        _register(dst, version())
    return dst


def uninstall():
    for lnk in _shortcuts():
        try:
            os.remove(lnk)
        except OSError:
            pass
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Saladi")
    except (ImportError, OSError):
        pass
    d = install_dir()  # the exe cannot delete itself while running: a detached cmd does it a moment later
    subprocess.Popen('cmd /c "ping -n 3 127.0.0.1 >nul & rmdir /s /q "%s""' % d, shell=True,
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return d


# ------------------------------------------------------------------ update

def download(info, dest_dir=None):
    """Download the release exe and verify its SHA-256 against the release's .sha256 file."""
    if not info.get("asset"):
        raise RuntimeError("this release has no %s" % ASSET)
    if not info.get("sha"):
        raise RuntimeError("this release has no checksum; not installing it")
    want = _get(info["sha"], timeout=30).decode("utf-8", "replace").split()[0].strip().lower()
    data = _get(info["asset"], timeout=300)
    got = hashlib.sha256(data).hexdigest()
    if got != want:
        raise RuntimeError("the download does not match its checksum; nothing was changed")
    dest_dir = dest_dir or tempfile.mkdtemp(prefix="saladi-update-")
    path = os.path.join(dest_dir, ASSET)
    with open(path, "wb") as fh:
        fh.write(data)
    return path


def swap_script(new_exe, target, pid):
    """A .cmd that waits for this process to end, copies the new exe over the old one and starts it."""
    path = os.path.join(os.path.dirname(new_exe), "apply-update.cmd")
    lines = [
        "@echo off",
        ":wait",
        '"%SystemRoot%\\System32\\tasklist.exe" /FI "PID eq {pid}" 2>nul | "%SystemRoot%\\System32\\findstr.exe" /C:" {pid} " >nul '
        '&& (ping -n 2 127.0.0.1 >nul & goto wait)'.format(pid=pid),
        "set n=0",
        ":copy",
        'copy /y "{new}" "{dst}" >nul && goto run'.format(new=new_exe, dst=target),
        "set /a n+=1",
        "if %n% lss 30 (ping -n 2 127.0.0.1 >nul & goto copy)",
        "exit /b 1",
        ":run",
        'start "" "{dst}"'.format(dst=target),
    ]
    with open(path, "w", encoding="ascii", errors="replace", newline="") as fh:
        fh.write("\r\n".join(lines) + "\r\n")
    return path


def apply(info=None):
    """Download, verify, then hand over to the swap script. The caller exits right after."""
    if not FROZEN:
        raise RuntimeError("this copy runs from source: update it with git pull")
    info = info or check(force=True)
    if not info.get("available"):
        raise RuntimeError("Saladi is up to date")
    new = download(info)
    target = installed_exe() if os.path.exists(installed_exe()) else os.path.abspath(sys.executable)
    script = swap_script(new, target, os.getpid())
    subprocess.Popen(["cmd", "/c", script], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                     | getattr(subprocess, "DETACHED_PROCESS", 0))
    return info["latest"]
