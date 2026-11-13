"""Publish a Saladi release: python .claude/desk/app/release.py 1.1.0 "What changed"

Writes version.txt, builds Saladi-Setup.exe with PyInstaller, writes its
SHA-256, commits and pushes the version bump, and creates the GitHub release
(tag v1.1.0) with both files. Every installed copy then shows "Saladi 1.1.0
is available" within a few hours, or at once on its next start.

Needs: PyInstaller, git, and the GitHub CLI (gh) logged in. --dry-run builds
without committing or publishing.
"""
import hashlib
import os
import re
import subprocess
import sys
import tempfile

APP = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(APP, "..", "..", ".."))


def run(*cmd, **kw):
    print("> " + " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT, **kw)


def build(out):
    work = os.path.join(tempfile.gettempdir(), "saladi-build")
    run(sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--noconsole",
        "--name", "Saladi-Setup", "--icon", os.path.join(APP, "saladi.ico"),
        "--distpath", out, "--workpath", work, "--specpath", work,
        "--paths", os.path.join(ROOT, "trader-scanner"), "--paths", APP,
        "--hidden-import", "scan", "--hidden-import", "live", "--hidden-import", "update",
        "--collect-data", "tzdata",
        "--add-data", os.path.join(APP, "index.html") + ";.", "--add-data", os.path.join(APP, "saladi.ico") + ";.",
        "--add-data", os.path.join(APP, "saladi.png") + ";.", "--add-data", os.path.join(APP, "version.txt") + ";.",
        os.path.join(APP, "server.py"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    exe = os.path.join(out, "Saladi-Setup.exe")
    with open(exe, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    with open(exe + ".sha256", "w", encoding="ascii") as fh:
        fh.write("%s  Saladi-Setup.exe\n" % digest)
    return exe, digest


def main(argv):
    dry = "--dry-run" in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args or not re.match(r"^\d+\.\d+\.\d+$", args[0]):
        print(__doc__)
        return 1
    ver, notes = args[0], (args[1] if len(args) > 1 else "Saladi %s" % args[0])
    with open(os.path.join(APP, "version.txt"), "w", encoding="ascii") as fh:
        fh.write(ver + "\n")
    out = os.path.join(tempfile.gettempdir(), "saladi-release", ver)
    os.makedirs(out, exist_ok=True)
    exe, digest = build(out)
    print("Built %s (%d KB)\nSHA-256 %s" % (exe, os.path.getsize(exe) // 1024, digest))
    if dry:
        return 0
    run("git", "add", os.path.join(APP, "version.txt"))
    subprocess.run(["git", "commit", "-q", "-m", "Saladi %s" % ver], cwd=ROOT)  # no-op if unchanged
    run("git", "push", "-q")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    run("gh", "release", "create", "v" + ver, exe, exe + ".sha256", "--title", "Saladi " + ver,
        "--notes", notes + "\n\nInstall: download Saladi-Setup.exe and run it. No admin rights needed.\n"
        "SHA-256: `%s`" % digest, "--target", head)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
