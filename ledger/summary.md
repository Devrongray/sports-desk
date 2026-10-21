# Desk scorecard 2026-10-21T12:08:35+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 29 | +0.0350 | 0.0035 | 9.95 | P&L $+470.39 on 29 settled, 18 winners |
| paper posts (every flagged post, at post price, fill unknown) | 10 | +0.0346 | 0.0036 | 9.63 |  |
| live-action candidates (scanner, at post price) | 39 | +0.0480 | 0.0027 | 17.86 |  |
| all referenced candidates (at mid) | 290 | +0.0018 | 0.0017 | 1.04 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nhl | 39 | +0.0480 | 0.0027 | 17.86 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 34 | +0.0504 | 0.0028 | 17.96 |
| wide | 5 | +0.0322 | 0.0049 | 6.63 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_PERIOD | 1 | +0.0279 |  |  |
| REGULATION | 38 | +0.0486 | 0.0027 | 17.94 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 290; slope 0.793 (95% CI 0.34–1.24); intercept +0.054. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
