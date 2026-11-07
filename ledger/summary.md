# Desk scorecard 2026-11-07T12:16:58+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 119 | +0.0379 | 0.0020 | 18.71 | P&L $+387.45 on 119 settled, 57 winners |
| paper posts (every flagged post, at post price, fill unknown) | 148 | +0.0372 | 0.0006 | 57.83 |  |
| live-action candidates (scanner, at post price) | 267 | +0.0445 | 0.0010 | 42.69 |  |
| all referenced candidates (at mid) | 1325 | +0.0080 | 0.0008 | 9.68 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 10 | +0.0294 | 0.0044 | 6.77 |
| nhl | 257 | +0.0451 | 0.0011 | 42.77 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 132 | +0.0520 | 0.0018 | 29.15 |
| unquoted | 25 | +0.0378 | 0.0016 | 24.31 |
| wide | 110 | +0.0370 | 0.0007 | 53.24 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 3 | +0.0376 | 0.0022 | 16.71 |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 5 | +0.0338 | 0.0027 | 12.29 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 249 | +0.0454 | 0.0011 | 42.10 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 1325; slope 1.259 (95% CI 1.04–1.48); intercept +0.117. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
