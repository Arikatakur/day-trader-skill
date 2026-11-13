# Saladi

Saladi is a desktop control room for the Day Trader skill pack. It runs on
your own PC, shows the whole trading desk in one window, and never places an
order itself. Orders are placed by Claude, through the risk check, on a paper
account by default.

## What you see

| Area | What it holds |
| --- | --- |
| Ticker bar | Day P/L, risk used, the breakout gate, SPY, your positions and every candidate. Hover to pause, click a symbol to chart it. |
| Overview | Six key numbers, the four steps of a trade, the chart, and a "Needs attention" list. |
| Find (step 1) | Candidates from the scanner, with news, earnings checks and congress filings folded below. |
| Plan (step 2) | One row per stock: entry state, trigger, stop, target, shares, cost, max loss and the risk verdict. |
| Trade (step 3) | Open positions, today's orders, alerts, the broker check and the ticket log. |
| Review (step 4) | Realized P/L, closed trades, the Time Machine review and the Machine Learning log. |
| Settings | Connections (Claude, Alpaca, other APIs), autotrade, limits, desk folder, notifications, version. |
| Chat | Hidden behind the round button in the corner. Desk trader answers in seconds; Main session shows the Claude Code conversation. |

## The chart

- Intervals: 1m, 2m, 5m, 15m, 30m, 1h, 1D, 1W.
- Ranges: 1D to All, limited to what each interval supports.
- Types: candles, hollow candles, Heikin Ashi, bars, line, step line, area, baseline.
- Indicators: volume, SMA 20, SMA 50, EMA 9, EMA 21, VWAP, Bollinger bands, RSI 14, previous close, your trades.
- Scale: linear, log or percent. Fit and full screen (Esc exits).
- A plain scroll moves the page. Hold Ctrl and scroll to zoom; drag to pan.

## Urgent alerts

When an agent raises an alert, or recommends acting now, a red bar appears
across the top, the window gets a pulsing red frame, a siren repeats and the
window title flashes. It stops when you press Acknowledge or Show me.

## Install

**From a release (any Windows PC).** Download `Saladi-Setup.exe` from the
Releases page and run it. It installs for the current user, with no admin
rights, adds Start Menu and Desktop shortcuts, and opens the app. Uninstall
from Windows "Apps & features".

The exe is not code-signed. Windows may warn ("Windows protected your PC":
More info, then Run anyway), and PCs with Smart App Control turned on may
block it. Running from source always works.

**From source (needs Python 3.8+).**

```
git clone https://github.com/Arikatakur/saladi
cd saladi
python .claude/desk/app/server.py
```

`.claude\desk\app\start.bat` does the same from a double-click.

## Connect

Open Settings, then Connections.

- **Claude.** Install Claude Code (`npm install -g @anthropic-ai/claude-code`)
  and press Sign in. The login happens in Claude Code's own window; Saladi
  never sees your password. This powers the chat and the agents.
- **Alpaca.** Paste your **paper** API key and secret (key IDs start with PK).
  Saladi reads equity, positions, orders, fills and prices every 2 seconds. It
  is read-only and only talks to Alpaca's paper address.
- **Other APIs.** "Add another API" stores a key for a service added later.

Keys are saved on your PC under `%APPDATA%\TradingDesk`. They are never
written to the repo or sent anywhere except the service they belong to.

## Standalone or full desk

Without a desk folder, Saladi runs standalone: Alpaca data, charts, alerts and
chat. To get the agents, tickets and the Machine Learning log, clone this repo
on that PC and set its path in Settings, App, Desk folder.

## Updates

Every installed copy checks GitHub for a newer release at start and every 3
hours. When one exists, a bar offers "Update and restart" or "Later". The
download is checked against the release's SHA-256 before anything is replaced.
See [releasing.md](releasing.md).

## Security

- The server listens on `127.0.0.1` only.
- Every button needs a token the page receives at launch, so another website
  cannot press it.
- The app has no code path that places, cancels or changes an order.
