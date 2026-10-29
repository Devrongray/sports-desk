# upsets

Third track: predicting upsets and unlikely outcomes from pre-registered causal
factors, graded against the Polymarket US price. Rules in
[PREREGISTRATION.md](PREREGISTRATION.md); factor catalogue in
[hypotheses.yaml](hypotheses.yaml); every candidate (bet or not) in
`ledger.csv`; one post-mortem per upset or unlikely prop in `postmortems/`.

## Ledger columns

| column | meaning |
|---|---|
| date_pt | game day (Pacific) |
| league | nba, nhl, nfl, cfb, mlb, cs2, lol, val, dota |
| event | matchup (away at home) or match |
| market | ML, prop description, or segment |
| selection | the outcome priced below 50% / ≤25% |
| pm_price, pm_time_utc | Polymarket US mid (or ask) when scored, and when |
| pin_fair | Pinnacle de-vigged probability if the recorder had it |
| factors_for, factors_against | catalogue ids fired for / against the selection |
| ups | Upset Propensity Score |
| my_prob | probability written before computing edge |
| edge_pp | my_prob − pm_price, in pp |
| tier | A / Watch / Pass / anomaly |
| arm | research (default) or gut (intuition experiment) |
| gut_flag | 1 if a gut read was recorded independently |
| stake_usd | 0 for unbet rows |
| knowable_by | latest time all fired factors were public (UTC) |
| result, brier_mine, brier_market, pin_close, clv_pp | filled at grading |
| notes | sources, caveats |

Grading: fill `result` (1 = selection won) next morning; Brier = (prob − result)².
