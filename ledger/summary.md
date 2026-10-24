# Desk scorecard 2026-10-24T12:03:14+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 36 | +0.0339 | 0.0031 | 10.81 | P&L $+489.44 on 36 settled, 21 winners |
| paper posts (every flagged post, at post price, fill unknown) | 21 | +0.0373 | 0.0022 | 16.69 |  |
| live-action candidates (scanner, at post price) | 57 | +0.0457 | 0.0021 | 21.68 |  |
| all referenced candidates (at mid) | 459 | +0.0019 | 0.0013 | 1.47 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 2 | +0.0360 | 0.0005 | 72.00 |
| nhl | 55 | +0.0461 | 0.0022 | 21.23 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 43 | +0.0493 | 0.0025 | 19.71 |
| wide | 14 | +0.0349 | 0.0020 | 17.46 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_PERIOD | 3 | +0.0322 | 0.0022 | 14.82 |
| FIRST_QUARTER | 2 | +0.0360 | 0.0005 | 72.00 |
| REGULATION | 52 | +0.0469 | 0.0022 | 20.89 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 459; slope 0.917 (95% CI 0.53–1.30); intercept +0.077. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
