# Desk scorecard 2026-10-30T12:18:13+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 74 | +0.0365 | 0.0028 | 13.16 | P&L $+556.07 on 74 settled, 40 winners |
| paper posts (every flagged post, at post price, fill unknown) | 38 | +0.0367 | 0.0015 | 23.80 |  |
| live-action candidates (scanner, at post price) | 112 | +0.0472 | 0.0019 | 24.66 |  |
| all referenced candidates (at mid) | 825 | +0.0038 | 0.0010 | 3.72 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 7 | +0.0252 | 0.0055 | 4.59 |
| nhl | 105 | +0.0487 | 0.0019 | 25.22 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 85 | +0.0511 | 0.0023 | 21.89 |
| unquoted | 2 | +0.0418 | 0.0030 | 13.93 |
| wide | 25 | +0.0345 | 0.0014 | 23.91 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 1 | +0.0347 |  |  |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 4 | +0.0322 | 0.0029 | 11.02 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 97 | +0.0499 | 0.0020 | 24.50 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 825; slope 1.049 (95% CI 0.76–1.34); intercept +0.065. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
