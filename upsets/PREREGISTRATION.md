# Pre-registration — upsets track

**Registered 29 Oct 2026 (America/Los_Angeles), before the first graded pick.**
A rule changes only by adding a dated line to the Amendment log first. Git history is the tamper evidence.

This is a third track, separate from the Desk (maker, `PREREGISTRATION.md` at repo root), the Begin daily picks (Daily Picks Playbook/Tracker), and the sports-method pipeline. It shares the repo's data recordings read-only.

## 1. What is being tested

Claim: a pre-registered catalogue of causal factors (`hypotheses.yaml`), applied to underdogs and long-shot props before a game, identifies outcomes whose true probability is higher than the Polymarket US price implies. The scoreboard is forecast quality against the price, not line-shopping.

Not being tested: that any single upset can be explained after the fact.

## 2. Candidate pool (per day)

- Game lines: every side priced **0.30–0.48** on Polymarket US (mid) at the T-6h check (or the first check of the day when later).
- Props and segment markets: any outcome priced **≤ 0.25**.
- Any league the catalogue covers, esports included. NFL game winners and spreads excluded by standing rule; NFL props allowed.

## 3. Scoring

- Each factor fired is written down with its id, the time it became knowable, and its source.
- **UPS** (Upset Propensity Score) = Σ weights: S/D-tier factor 3, M or P 1, F 0.5 (F counted for tracking only, not for tier). Factors against the dog count negative with the same weights.
- My probability = market no-vig probability (Polymarket US mid; Pinnacle de-vigged when the recorder has it) + the sum of per-factor adjustments in pp, each adjustment capped at the catalogue's prior and the total capped at **+10 pp** until the catalogue has out-of-sample results.
- The probability is written **before** the edge is computed; the price itself is the baseline, so anchoring is by design (logit-offset method).

## 4. Pick rule

- **A candidate**: UPS ≥ 6 with at least two S/D-tier factors, and my probability ≥ price + **4 pp** (game lines) or + **6 pp** (props/segments).
- **Watch**: UPS 3–5 (UPS ≥ 3 required from 2026-10-30), or edge below threshold. Logged, not bet.
- **Pass**: everything else in the pool; still logged with UPS.
- Any market with an integrity anomaly (move ≥ 5 pp in ≤ 15 min with no news; 3× volume on a role-player under or first-half market; tier-2 esports price crossing 0.50) is **not bet** and is logged as `anomaly`.
- Stakes during the trial: the user's standing $10–$20.

## 5. Grading

- Every logged row (A, Watch, Pass) gets: result, Brier score vs my probability, Brier of the Polymarket price at entry, Pinnacle close when available, and CLV in pp.
- Primary metric: mean Brier (mine) − mean Brier (market) on A candidates, then on all rows. Secondary: calibration by band; hit rate by band; ROI at stated stakes.
- A factor is promoted a tier only after ≥ 100 tagged cases where rows with the factor beat the market Brier, with Benjamini–Hochberg control across the batch. A factor stuck within ±1 pp after 500 cases is retired to tracking only.

## 6. Kill rules

- If A candidates trail the market Brier by ≥ 0.02 over the first 150 graded A rows, the pick rule reverts to Watch-only until the catalogue is refit.

## 7. Known limitations at registration

- Prices are Polymarket US mids from the Desk scanner (within 1–2¢ of Pinnacle de-vigged on full-game lines per 14–15 Oct recordings); props quoted wide are logged at mid and ask.
- Effect sizes in `hypotheses.yaml` are priors from literature and practitioners, not fitted.
- Forum sweep not yet automated; text flags come from beat-writer and news searches on the day.

## Amendment log

- 2026-10-29: registered.
- 2026-10-29 (evening): Watch requires UPS ≥ 3 (a +3 pp edge on a 1-point stack is not a Watch). D14 stand-in-quality modifier registered in hypotheses.yaml for testing.
