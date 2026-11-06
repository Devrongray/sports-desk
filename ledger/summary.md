# Desk scorecard 2026-11-06T12:31:32+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 115 | +0.0376 | 0.0021 | 18.19 | P&L $+404.54 on 115 settled, 55 winners |
| paper posts (every flagged post, at post price, fill unknown) | 141 | +0.0372 | 0.0007 | 55.35 |  |
| live-action candidates (scanner, at post price) | 256 | +0.0444 | 0.0011 | 41.80 |  |
| all referenced candidates (at mid) | 1285 | +0.0079 | 0.0008 | 9.40 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 10 | +0.0294 | 0.0044 | 6.77 |
| nhl | 246 | +0.0451 | 0.0011 | 41.88 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 128 | +0.0517 | 0.0018 | 28.64 |
| unquoted | 23 | +0.0379 | 0.0017 | 22.40 |
| wide | 105 | +0.0370 | 0.0007 | 51.14 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 3 | +0.0376 | 0.0022 | 16.71 |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 5 | +0.0338 | 0.0027 | 12.29 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 238 | +0.0454 | 0.0011 | 41.19 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 1285; slope 1.211 (95% CI 0.98–1.44); intercept +0.099. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
