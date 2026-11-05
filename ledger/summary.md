# Desk scorecard 2026-11-05T12:34:23+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 108 | +0.0374 | 0.0022 | 17.13 | P&L $+471.92 on 108 settled, 53 winners |
| paper posts (every flagged post, at post price, fill unknown) | 111 | +0.0373 | 0.0007 | 54.13 |  |
| live-action candidates (scanner, at post price) | 219 | +0.0448 | 0.0012 | 37.53 |  |
| all referenced candidates (at mid) | 1205 | +0.0072 | 0.0009 | 8.20 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 10 | +0.0294 | 0.0044 | 6.77 |
| nhl | 209 | +0.0456 | 0.0012 | 37.57 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 120 | +0.0518 | 0.0019 | 27.15 |
| unquoted | 23 | +0.0379 | 0.0017 | 22.40 |
| wide | 76 | +0.0360 | 0.0006 | 60.57 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 3 | +0.0376 | 0.0022 | 16.71 |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 5 | +0.0338 | 0.0027 | 12.29 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 201 | +0.0461 | 0.0012 | 36.86 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 1205; slope 1.212 (95% CI 0.98–1.45); intercept +0.107. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
