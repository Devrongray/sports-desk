# Desk scorecard 2026-10-27T12:15:19+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 65 | +0.0373 | 0.0028 | 13.24 | P&L $+542.65 on 65 settled, 35 winners |
| paper posts (every flagged post, at post price, fill unknown) | 25 | +0.0374 | 0.0019 | 19.50 |  |
| live-action candidates (scanner, at post price) | 90 | +0.0486 | 0.0021 | 23.27 |  |
| all referenced candidates (at mid) | 674 | +0.0037 | 0.0012 | 3.15 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 5 | +0.0217 | 0.0073 | 2.99 |
| nhl | 85 | +0.0502 | 0.0021 | 24.46 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 74 | +0.0516 | 0.0024 | 21.67 |
| wide | 16 | +0.0350 | 0.0018 | 19.80 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 3 | +0.0319 | 0.0041 | 7.76 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 77 | +0.0519 | 0.0022 | 23.90 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 674; slope 1.000 (95% CI 0.69–1.31); intercept +0.066. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
