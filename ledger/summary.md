# Desk scorecard 2026-11-03T12:30:33+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 85 | +0.0365 | 0.0025 | 14.38 | P&L $+461.76 on 85 settled, 43 winners |
| paper posts (every flagged post, at post price, fill unknown) | 94 | +0.0374 | 0.0008 | 46.71 |  |
| live-action candidates (scanner, at post price) | 179 | +0.0442 | 0.0013 | 33.58 |  |
| all referenced candidates (at mid) | 1081 | +0.0065 | 0.0009 | 7.03 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 9 | +0.0283 | 0.0047 | 6.03 |
| nhl | 170 | +0.0451 | 0.0013 | 33.74 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 96 | +0.0511 | 0.0022 | 23.68 |
| unquoted | 23 | +0.0379 | 0.0017 | 22.40 |
| wide | 60 | +0.0357 | 0.0007 | 51.14 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 3 | +0.0376 | 0.0022 | 16.71 |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 4 | +0.0322 | 0.0029 | 11.02 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 162 | +0.0456 | 0.0014 | 32.92 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 1081; slope 1.183 (95% CI 0.93–1.43); intercept +0.101. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
