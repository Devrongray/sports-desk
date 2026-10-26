# Desk scorecard 2026-10-26T14:00:43+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 62 | +0.0385 | 0.0029 | 13.47 | P&L $+486.89 on 62 settled, 32 winners |
| paper posts (every flagged post, at post price, fill unknown) | 24 | +0.0370 | 0.0020 | 18.84 |  |
| live-action candidates (scanner, at post price) | 86 | +0.0493 | 0.0021 | 23.00 |  |
| all referenced candidates (at mid) | 634 | +0.0039 | 0.0012 | 3.18 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 4 | +0.0232 | 0.0092 | 2.53 |
| nhl | 82 | +0.0506 | 0.0021 | 23.90 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 70 | +0.0526 | 0.0024 | 21.52 |
| wide | 16 | +0.0350 | 0.0018 | 19.80 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 3 | +0.0319 | 0.0041 | 7.76 |
| FULL_GAME | 1 | -0.0029 |  |  |
| REGULATION | 74 | +0.0524 | 0.0022 | 23.38 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 634; slope 1.072 (95% CI 0.74–1.40); intercept +0.070. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
