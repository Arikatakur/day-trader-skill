# Machine Learning

A running log of what went wrong (and right) in each live trading session, and
the rule each one taught. Claude reads this before every session and adds to it
after. Newest session first. Rules that have been learned are collected in
**Standing rules** at the top so they are applied, not just remembered.

## Standing rules

1. **Check the live broker quote before ranking or planning a late entry.**
   Yahoo's 5-minute bars lag. The watchlist scan can show a stock holding above
   its breakout level when the live quote is already back below it.
   Rank candidates on Alpaca's `get_stock_latest_quote`, not the watchlist's
   `last` column. *(2026-11-12, MSFT)*
2. **Plan the exit from the live ask, not the old trigger price.** For a late
   entry run `exit.py plan --symbol X --entry <live ask> --or-high H --or-low L`.
   The `--from trader/entry.json` default uses a trigger price from hours ago.
   *(2026-11-12)*
3. **On the free IEX feed, ignore wide spreads.** Some IEX quotes show
   $10–$20 spreads (LYV, ABNB, EXPE on 2026-11-12). Don't size off them. Use
   the mid on tight quotes only, or check the last trade. *(2026-11-12)*
4. **Windows shell: `TZ=America/New_York date` is ignored in Git Bash.** It
   printed GMT. Work out New York time in Python with `zoneinfo`, or use
   `alerts.py clock`. Don't hard-code UTC-5, because daylight saving changes
   the offset. *(2026-11-12)*
5. **Test monitoring scripts once before the long loop.** A price regex
   `([\d.]+)` grabbed the sentence's trailing period ("406.44.") and crashed
   the first watch. Use `(\d+\.\d+)`. *(2026-11-12)*
6. **A 2R target late in the day rarely fills.** ROK, entered at 1:52 PM,
   never got within $6 of its 2R target. For entries after 1:00 PM ET use
   `--target 1R`. *(2026-11-12)*
7. **Don't take ORB breakouts more than about 2 hours after they trigger.**
   ROK (breakout at 9:50 AM, entered at 1:52 PM) chopped sideways, then slid
   back under the breakout level. By mid-afternoon the opening range is no
   longer the level that matters. For late trades, use the day's high and a
   fresh 30-minute structure. *(2026-11-12)*
8. **Cut a trade early once it closes back under its breakout level.** That
   is the failed-breakout signal. Closing ROK there lost $12.42 instead of
   risking the full $29.52. *(2026-11-12)*
9. **Screen late-day setups at about 11:00 AM–1:30 PM, not at 3:00 PM.** By
   3:00 PM there are 30 minutes of entry window left, and the 3 parallel
   screeners found nothing that passed. Run the agents earlier, while there
   is still time to act. *(2026-11-12)*
10. **The free IEX quote feed is unusable for most names.** About 80% of
    symbols showed spreads of 1–11%. Screen spread and size on liquid
    large-caps only, or check `get_stock_latest_trade`. Treat "no quote" as
    unknown, not as wide. *(2026-11-12)*
11. **Buy-stop triggers beat chasing.** Placing bracket buy-stops just above
    the day high (DVN, XOM, CVX) meant no fill unless the breakout happened.
    None triggered, so the cost was zero, which beats buying a fade. Cancel
    unfilled triggers at `no_entries_after` (3:30 PM). Stage them with
    `exit.py --stop price:X --target 1R`, then `size.py --write`, then set
    `type: stop` and `stop_price` in orders.json, then run `check.py`.
    *(2026-11-12)*
12. **Keep `trader/portfolio.json` cash in line with the budget.** After raising
    `budget`, also raise the portfolio cash, or `size.py` stays bound by the
    old cash. *(2026-11-12)*
13. **The Allow card is the slowest step, so set the trigger with room.** An
    order call waits on the user's Allow card, which took 10 to 25 minutes
    on 2026-11-13. Alpaca rejects a buy-stop whose trigger is already below
    the market (422 "stop price must be greater than current price"). That
    lost APP twice and CL once. Right before each call, re-read the live
    trade. Put the trigger above BOTH the high of day and the live price by
    about 0.1%. If the price is already through the setup, skip it rather
    than chase. *(2026-11-13)*
14. **Stage the 9:45 tickets in advance.** Have `orscan.py` (opening-range
    table) and the staging script tested before 9:30. At 9:45:00, compute the
    ranges and send the orders immediately. On 2026-11-13 the first order went
    out at 9:58, and by then APP had already broken out. *(2026-11-13)*
15. **In a weak tape, breakouts fail fast. Two failures in a day mean stop.**
    With SPY -1% and QQQ -2%, 3 of 4 filled breakouts (FISV, ABT, COP) closed
    back under their level within 10-25 minutes. Once two breakouts have
    failed in a session, place no new breakout entries until SPY is back
    above its open. Cancel the waiting triggers too. *(2026-11-13)*
16. **Rule 8 is not free: cut on a failed breakout only when the stop is also
    close.** On 2026-11-13 the early cut helped on ABT and COP (both went on
    to hit their stops; it saved about $17) and hurt on FISV (cut at 62.51 for
    -$17.64; the 62.22 stop was never touched and the stock traded 63.68 by
    2:29 PM, about +$31 if held). Net, the rule cost money that day. Cut early
    when price closes under the level AND has already given back more than
    half the distance to the stop, or when the market is falling with it.
    Otherwise let the bracket work. *(2026-11-13, time machine review)*
17. **Move the stop to breakeven once the trade is up and the tape turns.**
    Use `replace_order_by_id` on the bracket's stop leg. A working stop leg
    shows `held`, and `get_orders status=open` does NOT list held legs.
    Check it with `get_order_by_id`. *(2026-11-13)*
18. **Size the risk with `size.py --max-loss 30`.** It can only lower
    `max_loss_per_trade_usd`. With a $150 daily limit that counts every
    entry in full, $30 a trade allows 5 entries. *(2026-11-13)*
19. **Flatten one position at a time.** `ticket.py flatten` replaces
    `trader/orders.json`, so record each exit's `result` before staging the
    next flatten. Otherwise use `ticket.py fill` for the earlier one, which
    is what happened to ABT. *(2026-11-13)*

20. **Desk agents that only do arithmetic should be script loops.** Live
    model agents stopped after a few cycles (broker, exit, entry, risk and
    pelosi all handed back early). The ones rebuilt as a Python `loop.py`
    kept running at no token cost. Start the desk with script loops; keep
    live agents only for the broker and news. *(2026-11-13)*
21. **Check that a report's fields are real before trusting the pipeline.**
    desk-budget reported "plans sized" while every item was null, so the risk
    dry-run had nothing to check for 30 minutes. Print one full item when a
    new agent first reports. *(2026-11-13)*

## Session log

### 2026-11-13 (Fri), paper account

**Setup.** The session started on schedule at 8:57 AM ET. Pre-market scan:
535 liquid names, 74 setups. Opening ranges at 9:45, bracket buy-stops from
9:58. SPY fell about 1% from its open and tech fell about 3% (Nvidia's CEO
left); money rotated into staples, utilities and healthcare.

**Mistakes.**
- First order at 9:58, not 9:45: the opening-range script was written and
  debugged after the bell. APP broke out in that gap. -> Rule 14.
- Three buy-stops were rejected (APP twice, CL once) because the price had
  passed the trigger by the time the order call went through. -> Rule 13.
- Took two more breakouts (ABT, COP) after the first one had already failed
  in a falling market. Both failed within 25 minutes. -> Rule 15.
- Cut FISV on the first close under its level; it then ran without touching
  the stop. -> Rule 16.
- Recorded the ABT exit with `ticket.py fill` because a second `flatten` had
  replaced its ticket. -> Rule 19.

**Trades.**
| symbol | entry | stop | target | qty | max loss | result |
| --- | --- | --- | --- | --- | --- | --- |
| LVS | 40.15 (10:03, buy-stop 40.14) | 39.79, raised to 40.15 at 11:31 | 40.84 (2R) | 85 | $29.75 | stopped at breakeven 12:08: **$0.00** |
| FISV | 62.93 (10:02, buy-stop 62.92) | 62.22 | 64.32 (2R) | 42 | $29.40 | cut at 62.51 (10:15): **-$17.64** |
| ABT | 109.22 (11:04, buy-stop 109.18) | 108.55 | 110.44 (2R) | 36 | $22.68 | cut at 108.85 (11:30): **-$13.32** |
| COP | 142.44 (11:14, buy-stop 142.40) | 141.67 | 143.86 (2R) | 28 | $20.44 | cut at 141.89 (11:30): **-$15.40** |
| V | buy-stop 427.05 | 424.86 | 431.43 | 9 | $19.71 | never triggered, canceled 11:31 |
| APP, CL | rejected by Alpaca (422) | | | | | not placed |

**Day:** -$46.36 (paper equity $99,941.13). Four filled trades, none won.
$102.27 of the $150 daily risk was used. No entries after 11:14: the breakout
gate (SPY above its open) stayed closed for the rest of the session.

**Time machine review (as of 2:29 PM).** Holding the original brackets: ABT
and COP hit their stops (-1.0R each, worse than the cuts); FISV was at +1.06R
and LVS at +0.1R, both still open. The early cuts cost about $31 on FISV and
saved about $17 on ABT and COP.

**Process changes made today.**
- Autotrade switch: `ticket.py auto on|off|status` (paper only).
- `size.py --max-loss`, `ticket.py lock`, and a shared order lock so the main
  session and the app's chat cannot both stage an order at once.
- A trading desk of eleven agents, one per skill, reporting to
  `trader/desk/`, with the main session as the only trader. See
  `docs/desk-agents.md`.
- Saladi, the desktop app: live ticker, charts, the desk by step, chat,
  urgent alerts, installer and in-app updates. See `docs/saladi.md`.

**Plan for the next session.**
1. Before 9:30: start the desk as script loops; have the opening-range table
   and the staging script tested (Rule 14).
2. 9:45:00: stage the best two or three breakouts at once, triggers 0.1%
   above both the range high and the live price (Rule 13).
3. Trade breakouts only while SPY is above its open; stop after two failures
   (Rule 15).
4. Let brackets work unless the cut test in Rule 16 is met.
5. 3:30 PM: cancel unfilled triggers. 3:55 PM: flat.

### 2026-11-12 (Thu), paper account

**Setup.** The scan ran at 1:39 PM ET: 145 opening-range breakouts, all
triggered between 9:50 AM and 1:25 PM. I ranked the ones still holding above
the range high by the distance from the live price to the range-midpoint stop.

**Mistakes.**
- Chose MSFT from the Yahoo-based list, then the live Alpaca quote ($523.84)
  showed it back under its $525.83 breakout. That wasted a step and nearly
  planned a failed breakout. → Rule 1.
- The first watch script crashed on a regex bug. → Rule 5.
- Assumed `TZ=` worked in Git Bash. It didn't. → Rule 4.
- Entered ROK about 4 hours after its breakout. That is a late, weaker trade,
  and it started drifting toward the breakout level right after the fill.
  Lesson: late breakouts need a clear reason to still work (a fresh push or
  new highs), not just "still above the level".

**Trades.**
| symbol | entry | stop | target | qty | max loss | result |
| --- | --- | --- | --- | --- | --- | --- |
| ROK | 406.60 (1:52 PM, market) | 403.60 | 413.44 (2R) | 9 | $29.52 | closed early at 405.22 (2:54 PM): **-$12.42** |
| DVN | buy-stop 46.52 | 46.27 | 46.77 (1R) | 85 | $21.25 | never triggered (high 46.47), canceled 3:30 PM |
| XOM | buy-stop 170.93 | 170.40 | 171.46 (1R) | 23 | $12.19 | never triggered (high about 170.78), canceled 3:30 PM |
| CVX | buy-stop 218.10 | 217.37 | 218.83 (1R) | 18 | $13.14 | never triggered (high about 217.93), canceled 3:30 PM |

**Day:** -$12.42 (paper equity $99,987.58). One filled trade, a loss.

**Process changes made today.** The user gave standing approval for paper
orders (`auto_approve`, `ticket.py approve --auto`). Research fanned out to 3
parallel screener agents, and all orders were placed centrally. The budget was
raised to $20,000 with the $50/trade and $150/day loss limits unchanged.

**Tooling gap (fixed the same day).** `ticket.py` had no way to record a
canceled order. Added `ticket.py canceled --broker-id ID`. trader-risk now
leaves an order canceled before it filled out of the day's trade count and
max loss. Use it for every unfilled trigger canceled at the cutoff.

**Plan for the next session.**
1. 9:00–9:30 AM ET: run the scanner pre-market. Read the Standing rules.
2. 9:45 AM–11:00 AM: opening-range breakouts with buy-stop triggers just
   above the range high. Check the live Alpaca quote first (Rule 1).
3. 11:00 AM–1:30 PM: parallel screener agents for second-leg setups
   (Rule 9), with 1R targets after 1:00 PM (Rule 6).
4. 3:30 PM: cancel unfilled triggers and run `ticket.py canceled`.
   3:55 PM: flat.

**What went right.** All three gates held (risk PASS, explicit yes, Allow
once). The bracket put the stop at the broker the moment the entry filled, and
the max loss was known before entry.
