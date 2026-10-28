# Desk scorecard 2026-10-28T12:19:09+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 70 | +0.0361 | 0.0027 | 13.54 | P&L $+550.07 on 70 settled, 38 winners |
| paper posts (every flagged post, at post price, fill unknown) | 30 | +0.0380 | 0.0018 | 21.69 |  |
| live-action candidates (scanner, at post price) | 100 | +0.0478 | 0.0019 | 24.97 |  |
| all referenced candidates (at mid) | 734 | +0.0038 | 0.0011 | 3.40 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 6 | +0.0239 | 0.0063 | 3.79 |
| nhl | 94 | +0.0493 | 0.0019 | 26.01 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 80 | +0.0507 | 0.0022 | 22.64 |
| wide | 20 | +0.0359 | 0.0016 | 22.83 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 1 | +0.0347 |  |  |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 3 | +0.0319 | 0.0041 | 7.76 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 86 | +0.0508 | 0.0020 | 25.39 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 734; slope 0.992 (95% CI 0.69–1.29); intercept +0.054. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
