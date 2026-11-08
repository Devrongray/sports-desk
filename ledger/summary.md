# Desk scorecard 2026-11-08T12:17:47+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 124 | +0.0387 | 0.0020 | 19.35 | P&L $+376.88 on 124 settled, 59 winners |
| paper posts (every flagged post, at post price, fill unknown) | 195 | +0.0372 | 0.0005 | 69.92 |  |
| live-action candidates (scanner, at post price) | 319 | +0.0438 | 0.0009 | 47.64 |  |
| all referenced candidates (at mid) | 1441 | +0.0094 | 0.0008 | 11.61 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 10 | +0.0294 | 0.0044 | 6.77 |
| nhl | 309 | +0.0442 | 0.0009 | 47.71 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 137 | +0.0526 | 0.0018 | 29.86 |
| unquoted | 43 | +0.0378 | 0.0010 | 39.29 |
| wide | 139 | +0.0369 | 0.0006 | 59.90 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 3 | +0.0376 | 0.0022 | 16.71 |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 5 | +0.0338 | 0.0027 | 12.29 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 301 | +0.0445 | 0.0009 | 47.05 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 1441; slope 1.336 (95% CI 1.12–1.55); intercept +0.141. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
