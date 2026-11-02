# Desk scorecard 2026-11-02T12:32:21+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 82 | +0.0370 | 0.0026 | 14.18 | P&L $+488.45 on 82 settled, 42 winners |
| paper posts (every flagged post, at post price, fill unknown) | 91 | +0.0375 | 0.0008 | 45.46 |  |
| live-action candidates (scanner, at post price) | 173 | +0.0445 | 0.0014 | 32.83 |  |
| all referenced candidates (at mid) | 1032 | +0.0065 | 0.0010 | 6.82 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 9 | +0.0283 | 0.0047 | 6.03 |
| nhl | 164 | +0.0454 | 0.0014 | 33.00 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 93 | +0.0514 | 0.0022 | 23.30 |
| unquoted | 23 | +0.0379 | 0.0017 | 22.40 |
| wide | 57 | +0.0358 | 0.0007 | 48.92 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 3 | +0.0376 | 0.0022 | 16.71 |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 4 | +0.0322 | 0.0029 | 11.02 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 156 | +0.0460 | 0.0014 | 32.18 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 1032; slope 1.189 (95% CI 0.93–1.45); intercept +0.111. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
