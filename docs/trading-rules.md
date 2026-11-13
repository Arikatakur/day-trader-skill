# Trading rules and safety

Education and tooling, not financial advice. Paper trading is the default.

## The gates in front of every order

1. **trader-risk PASS** for that exact order in the last 15 minutes. Never
   switched off.
2. **Your yes** for that one order, typed in the chat.
3. **Allow once** on Claude Code's permission card.

## Autotrade (paper only)

```
python3 trader-broker/ticket.py auto on       # Claude trades the paper account with no approval
python3 trader-broker/ticket.py auto off      # your yes and the card are back
python3 trader-broker/ticket.py auto status
```

`on` flips gates 2 and 3 together and refuses unless the config says
`"paper": true` and Alpaca. Gate 1 still applies to every entry. Turn it off
before pointing the Alpaca connection at live keys: the permission rule cannot
tell paper from live. The same switch is in Saladi's top bar and Settings.

## One trader at a time

The main session and Saladi's desk chat can both stage orders. `ticket.py
approve` takes a shared order lock and `result` or `decline` releases it (it
expires after 5 minutes), so two orders cannot pass the daily limits at once.

```
python3 trader-broker/ticket.py lock status
python3 trader-broker/ticket.py lock release --force
```

## Limits (trader/config.json)

| Key | Meaning |
| --- | --- |
| `max_loss_per_trade_usd` | Most a single trade may lose at its stop. |
| `max_daily_loss_usd` | Sum of the max losses of today's entries, win or lose. |
| `max_trades_per_day` | Entries per day. |
| `no_entries_before`, `no_entries_after` | The entry window, New York time. |
| `flat_by` | Everything is closed by this time. |

`size.py --max-loss 30` risks less than the configured cap on one trade. It
can only lower the cap. An order canceled before it filled is recorded with
`ticket.py canceled --broker-id ID` and no longer counts toward the limits.

## Learning from each session

`MACHINE_LEARNING.md` holds standing rules and a log of every session: what
went wrong, the rule it taught, and the trades. Claude reads it before a
session and adds to it after.

## What is never committed

`trader/` (account state, orders, the broker log) and API keys. Both stay on
your PC.
