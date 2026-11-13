# The desk: one agent per skill

A trading session runs eleven desk agents, one per skill, plus the main
Claude session that watches them and is the only one that trades.

| Agent | Skill | Every | Job |
| --- | --- | --- | --- |
| desk-scanner | trader-scanner | 20 min | Rescan for opening-range breakouts and second-leg setups. |
| desk-news | trader-news | 10 min | Headlines and SEC 8-Ks on held stocks and candidates. |
| desk-analyst | trader-analyst | 30 min | Veto stocks with earnings in the next few days. |
| desk-pelosi | trader-pelosi | 60 min | New congressional trade filings that touch our names. |
| desk-entry | trader-entry | 5 min | READY, TRIGGERED, WAITING or INVALID for each candidate. |
| desk-exit | trader-exit | 5 min | Stop and target plans; failed-breakout and breakeven signals. |
| desk-budget | trader-budget | 5 min | Shares per candidate; daily risk and trades left. |
| desk-risk | trader-risk | 5 min | Dry-run of the risk check; daily loss and the entry window. |
| desk-alerts | trader-alerts | 2 min | Clock cutoffs, the SPY breakout gate, distance to stop and target. |
| desk-broker | trader-broker | 3 min | Alpaca against the local records; unprotected positions. |
| desk-timemachine | trader-timemachine | 30 min | Odds for each plan; after the close, a review of the day's trades. |

## Rules every agent follows

The full protocol is `.claude/desk/PROTOCOL.md`. In short:

- **No orders, ever.** Agent definitions in `.claude/agents/` list only
  read-only Alpaca tools. Recommendations are advice.
- **One report file each:** `trader/desk/<agent>.json`, with a status (`ok`,
  `watch`, `alert`, `error`, `done`), a one-line headline, items and optional
  recommendations.
- **Keep looping** until the stop time or until `trader/desk/STOP` exists. An
  agent that hands back after one cycle leaves the desk blind.
- **Pause** when `trader/desk/PAUSE-<agent>` exists.

## Script loops

Most agents do arithmetic and lookups that need no model. Those run as a
plain Python loop (`trader/desk/<agent>/loop.py`) that costs no tokens and can
be started, stopped and inspected from Saladi. Live model agents are kept for
jobs that need judgment or the broker connection.

## Reading the desk without the app

```
python3 .claude/desk/desk.py            # one line per agent, plus recommendations
python3 .claude/desk/desk.py --inbox    # notes left for the main session in the app
```
