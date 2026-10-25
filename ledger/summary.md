# Desk scorecard 2026-10-25T12:02:05+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 58 | +0.0392 | 0.0029 | 13.73 | P&L $+512.63 on 58 settled, 31 winners |
| paper posts (every flagged post, at post price, fill unknown) | 22 | +0.0371 | 0.0021 | 17.39 |  |
| live-action candidates (scanner, at post price) | 80 | +0.0501 | 0.0022 | 22.88 |  |
| all referenced candidates (at mid) | 561 | +0.0044 | 0.0013 | 3.29 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 3 | +0.0319 | 0.0041 | 7.76 |
| nhl | 77 | +0.0508 | 0.0022 | 22.75 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 66 | +0.0533 | 0.0024 | 21.81 |
| wide | 14 | +0.0349 | 0.0020 | 17.46 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 3 | +0.0319 | 0.0041 | 7.76 |
| REGULATION | 69 | +0.0528 | 0.0024 | 22.22 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 561; slope 0.998 (95% CI 0.65–1.34); intercept +0.070. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
