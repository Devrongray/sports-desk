# Pre-registration — sports-desk

**Frozen 15 Oct 2026 (America/Los_Angeles), before the first order.**
Every number here is also the live value in `config/desk.yaml`. A change to any
rule is made by adding a dated line to the Amendment log at the bottom *first*,
then editing the config. Git history is the tamper evidence.

## 1. What is being tested

One claim: on Polymarket US, a small maker who rests orders at Pinnacle-referenced
prices in markets that the market makers quote wide or not at all earns positive
closing-line value after fees, and that CLV converts to profit over hundreds of
fills.

What is **not** being tested: that any model, AI, expert or feeling predicts
winners better than Pinnacle. Two days of recorded data (14–15 Oct 2026) show
full-game winner, total and spread lines on Polymarket US sit within 1–2¢ of
Pinnacle's de-vigged price with 0.5–1¢ spreads and tens of thousands of
contracts at the touch; the taker edge there was negative in 87–100% of
snapshots. Those lines are scanned and logged but are expected to produce no
actions.

## 2. Separation

This desk is a separate track from (a) the "Begin" daily picks and the Daily
Picks Playbook/Tracker, which stay as they are, and (b) the sports-method
research pipeline and its 90-day tests. It reads sports-method's public data
branch and never writes to it. Its own trigger word in chat is **"Desk"**.

## 3. Universe

| Sport | Classes | Note |
|---|---|---|
| NHL | winner, total, spread; full game and periods 1–3 | periods are the primary target |
| NBA | winner, total, spread; full game, first half, first quarter | |
| MLB (postseason) | winner, total, spread; full game and first five innings | dark from early Nov to late Mar |
| College basketball | winner, total, spread | from November; no low-major game without a Pinnacle price |
| NFL | totals only (full game, halves, quarters) | your standing rule: no NFL sides or spreads |
| CS2, LoL | match winner | scanned; no action until a Pinnacle esports reference exists |

Excluded by rule: combos/parlays of any kind, player props, table tennis,
lower-tier tennis, lower-league soccer, tier-2/3 esports, any market under an
integrity flag.

## 4. Reference price

Pinnacle, de-vigged **additive** (sports-method test (c), 14 Oct 2026: additive,
power and Shin equivalent on two-way markets; multiplicative worse). Full-game
lines from sports-method's recorder; period/half/quarter/inning lines from this
repo's own per-event Odds API poll (`totals_p1`, `spreads_p1`, `h2h_3_way_p1`,
`totals_h1`, `totals_q1`, `totals_1st_5_innings`, `h2h_3_way_1st_5_innings`, …).
A reference older than 60 minutes is not used. A spread references the same
signed line; a total the same line; otherwise no reference.

Winner legs of a segment that Polymarket US quotes as three contracts (home /
away / tie: period winners, first-five-innings winner, "lead after regulation")
are referenced against Pinnacle's **three-way** market for that segment
(`h2h_3_way_*`), the tie contract against its Draw outcome. The two-way
period/innings moneyline (`h2h_p1`, `h2h_1st_5_innings`), in which a tie is a
push, is never a reference for them: it overstates each team by
1/(1 − P(tie)), 15–20¢ on an NHL period. Full-game winners include overtime
and are two-way on both venues; they keep `h2h`. (Amendment 1.)

## 5. Quote state (Polymarket US best bid/ask, never the displayed probability)

| State | Spread | Reading |
|---|---|---|
| tight | ≤ 2¢ | machine-quoted, anchored to the sharp price |
| wide | 3–29¢ | quoted, but with room |
| unquoted | ≥ 30¢ | dust at 0.01/0.99; nobody is the price |

## 6. Actions and thresholds

| Action | Rule |
|---|---|
| **post_bid** (buy Yes as maker) | price = min(fair − 0.03, ask − tick) rounded down to tick; must be ≥ best bid + tick; edge = fair − price ≥ 0.01; price ≥ 0.10 |
| **post_ask** (sell Yes = buy No as maker) | price = max(fair + 0.03, bid + tick) rounded up to tick; must be ≤ best ask − tick; edge = price − fair ≥ 0.01; 1 − price ≥ 0.10 |
| **take_long** (buy at the ask) | fair − ask − 0.0695·ask·(1−ask) ≥ 0.01 + half the spread; ask ≥ 0.10; ≥ $50 showing at the ask |
| **take_short** (sell at the bid) | bid − fair − 0.0695·bid·(1−bid) ≥ 0.01 + half the spread; 1 − bid ≥ 0.10; ≥ $50 showing at the bid |
| **pass** | inside the window and nothing qualifies, or Pinnacle moved > 0.02 in the last 15 minutes |
| **watch** | outside the posting window, or no reference |

Maker before taker: a taker action is considered only when no maker action qualifies.
Posting window: 15 to 180 minutes before start. Orders are pulled 15 minutes
before start and immediately on lineup, injury or goalie news for that game.

## 7. Sizing

Flat **$20** per position (2% of the $1,000 trial bankroll). At most 10 posted
orders alive at once; at most 20% of bankroll committed in a day. Taker size is
capped at 25% of the contracts showing on the other side. No Kelly of any kind
until Gate A passes; after Gate A, ¼ Kelly on the fee-adjusted edge, never more.
Never buy a contract under 10¢; buys under 20¢ are flagged.

## 8. Scoring

- **Primary:** closing-line value in probability points per $1 contract against
  Pinnacle's last de-vigged price before start, fee-adjusted:
  long = fair_close − fill − fee; short = fill − fair_close − fee.
- **Would-have CLV:** every unfilled post at its post price, and every live-action
  candidate at its post price, so the scanner is judged on everything it surfaced.
- **Secondary:** Polymarket US's own last pre-game mid (thin; display rule
  undocumented) — reported, never used for decisions.
- **Reported, not judged:** realized P&L and win %.
- **Reference check:** calibration slope of Pinnacle fair_close on Polymarket US
  settlements; read from 200+.

## 9. Gates

| Gate | When | Passes if |
|---|---|---|
| 0 | first live scan | a ranked table with four prices (bid, ask, fair, Pinnacle ts) per candidate exists and the arithmetic matches `tests/` |
| A | 100+ live-action candidates **and** 30+ fills, or 20 Nov 2026, whichever first | candidate CLV mean > 0 with t ≥ 2; fill CLV ≥ candidate CLV; fill rate ≥ 30% of posts |
| B | 300+ fills | CLV > 0 at p < 0.05 in each of the two best sports and in each calendar month; drawdown inside plan; no adverse-selection signature (fills right before Pinnacle moves against them) |

## 10. Kill rules

- Candidate CLV ≤ 0 after 200 live-action candidates: the gap is not there at this size on this venue. Stop or change venue.
- Candidate CLV > 0 but fill CLV ≤ 0: adverse selection. Raise the margin to 0.05 and tighten the window to 15–90 minutes; re-test 100 candidates.
- Fill rate < 20% of posts after 100 posts: the maker route fails. Test taker orders with a 0.03 threshold for 50 candidates, then stop if negative.
- Any month with realized loss > 20% of bankroll: stop, return to paper, review.

## 11. Hypotheses (expected answer written before looking)

| ID | Hypothesis | Expected |
|---|---|---|
| H1 | Maker posts in wide/unquoted derivative markets have positive fee-adjusted CLV at fill | small positive |
| H2 | Low-priced (≤ 25¢) Polymarket US sports contracts are underpriced (Cardozo & Rivero-Wildemauwe 2026 on international Polymarket) | unknown; **observed from the ledger only, no buying under 20¢** (rule 7) |
| H3 | Gaps vs Pinnacle are larger on marquee, nationally televised and local-team games | yes |
| H4 | Gaps are larger in the 15 minutes after Pinnacle moves, and mostly unfillable | yes |
| H0 | The expert-crowd consensus adds nothing after Pinnacle (Benter; Brown & Reade) | nothing |

## 12. Known limits at freeze

- Polymarket US's league events feed stopped embedding non-winner markets at about 20:00 UTC on 15 Oct 2026; the desk fetches each event's full market list itself (`/v1/events/slug/{slug}`). sports-method's recorder needs the same fix for its own tests.
- Esports have no Pinnacle reference yet (The Odds API does not carry CS2/LoL).
- Pinnacle 2nd/3rd-period NHL lines are often not posted pregame; those Polymarket markets will mostly show "no reference".
- Depth figures are contracts at the best level as reported by the BBO endpoint; the unit was not independently verified.

## Amendment log

1. **2026-10-16 (before the first period poll ran and before any order was
   logged).** Reference for three-way winner legs corrected from the two-way
   `h2h_p1` / `h2h_1st_5_innings` to `h2h_3_way_p1` / `h2h_3_way_1st_5_innings`;
   tie contracts (`…-draw`) referenced against the Draw outcome; `REGULATION`
   segment mapped to `h2h_3_way` (winner only; referenced only if that market
   is polled, which it is not yet). Found while confirming Polymarket US quotes
   NHL period winners as three contracts (PIT@COL 16 Oct, 1st period: COL 0.41,
   PIT 0.27, tie 0.31). No rule, threshold, window, size, gate or kill rule
   changed; no candidate, order or fill was produced under the wrong reference.
   Same commit: a daily credit cap (350) and per-run cap (60) on the period
   poll, so the desk cannot exhaust the Odds API key sports-method shares.
2. **2026-10-16, 10:10 PT (still before the first period poll).** `h2h_3_way`
   added to the NHL poll, so the three "lead after regulation" / "tied after
   regulation" contracts (quoted 13–15¢ wide at 16:54 UTC) get their
   reference. These contracts were already inside the pre-registered universe
   (NHL WINNER, all segments); only the reference's availability changes.
   Caps raised to 80 per run / 400 per day to fit a 10-game NHL night at four
   markets; `poll_minutes` now enforced (an event polled within the last 30
   minutes is not polled again). Rules unchanged.
3. **2026-10-19.** Two additions after the first weekend (0 real fills; 24
   scanner signals, every one an NHL "after regulation" leg).
   (a) **Paper series.** Every live action the scanner flags inside the window
   is now also recorded, the first time it appears for that contract/action/game,
   as a paper position in `ledger/paper.csv`: takes at the quoted touch (depth
   already checked), posts at the post price. Graded separately as
   "paper takes" (fee charged, P&L assumed filled) and "paper posts" (fill
   unknown). The paper series never counts toward Gate A/B fill counts; it is
   the "if every signal had been followed" record and exists because the
   operator cannot always trade (travel, geofencing). Backfilled from the
   candidates ledger for 16–18 Oct.
   (b) **Named sub-hypothesis H5.** Polymarket US's regulation-result legs
   (home/away lead after 60 minutes, tied after 60) are priced off a tie
   probability of ~14–18% on some games while Pinnacle's three-way market
   implies ~22%, producing taker edges of 3–9¢ on tight quotes. H5: the
   fee-adjusted CLV of taker actions on REGULATION legs is positive. Read at
   100 paper takes; a mean below +1¢ or a sign flip over any 50 kills it.
   Observed so far: 21 paper takes, mean CLV +3.7¢ after fees — noted, not
   believed, until n is there. No rule, threshold, size, window or gate changed.
