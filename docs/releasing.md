# Releasing Saladi

```
python .claude/desk/app/release.py 1.1.0 "What changed"
```

That one command:

1. writes the version to `.claude/desk/app/version.txt`;
2. builds `Saladi-Setup.exe` with PyInstaller (one file, with the icon);
3. writes `Saladi-Setup.exe.sha256`;
4. commits and pushes the version bump;
5. creates GitHub release `v1.1.0` with both files.

Add `--dry-run` to build without committing or publishing. It needs
PyInstaller, git and the GitHub CLI (`gh`), logged in.

## What users see

Installed copies ask GitHub for the latest release at start and every 3 hours.
A newer version shows a bar: "Saladi 1.1.0 is available", with What's new,
Update and restart, and Later (which hides it for that version). Settings,
App, Version has a "Check for updates" button.

## How an update is applied

1. Download `Saladi-Setup.exe` and its `.sha256` from the release.
2. Compare the SHA-256. On a mismatch nothing is changed.
3. A small script waits for the app to close, copies the new exe over the
   installed one, and starts it.

A copy running from source is not replaced; it is told to `git pull`.

## Signing

Releases are not code-signed, so Windows may warn or, with Smart App Control
on, block the exe. With a code-signing certificate, sign the exe in
`release.py` after the build and before the checksum is written.

## Where things live

| Path | What |
| --- | --- |
| `.claude/desk/app/server.py` | Local server, API, install and launch logic. |
| `.claude/desk/app/live.py` | Alpaca polling, desk chat, agent loop supervisor, connections. |
| `.claude/desk/app/update.py` | Install, uninstall, update check, download and swap. |
| `.claude/desk/app/index.html` | The whole interface. |
| `.claude/desk/app/release.py`, `build_exe.bat` | Release and local build. |
| `tests/test_app_update.py` | Tests for versions, checksum refusal, install and swap. |
