# Desk scorecard 2026-10-29T12:19:47+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 72 | +0.0369 | 0.0028 | 13.07 | P&L $+508.54 on 72 settled, 38 winners |
| paper posts (every flagged post, at post price, fill unknown) | 34 | +0.0369 | 0.0017 | 22.08 |  |
| live-action candidates (scanner, at post price) | 106 | +0.0479 | 0.0020 | 23.95 |  |
| all referenced candidates (at mid) | 777 | +0.0036 | 0.0011 | 3.35 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 7 | +0.0252 | 0.0055 | 4.59 |
| nhl | 99 | +0.0495 | 0.0020 | 24.56 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 83 | +0.0514 | 0.0024 | 21.65 |
| wide | 23 | +0.0350 | 0.0015 | 23.11 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 1 | +0.0347 |  |  |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 4 | +0.0322 | 0.0029 | 11.02 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 91 | +0.0509 | 0.0021 | 23.89 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 777; slope 1.013 (95% CI 0.72–1.30); intercept +0.051. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
