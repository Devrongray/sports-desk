# Desk scorecard 2026-10-31T12:13:29+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 75 | +0.0367 | 0.0027 | 13.38 | P&L $+535.22 on 75 settled, 40 winners |
| paper posts (every flagged post, at post price, fill unknown) | 38 | +0.0367 | 0.0015 | 23.80 |  |
| live-action candidates (scanner, at post price) | 113 | +0.0474 | 0.0019 | 24.86 |  |
| all referenced candidates (at mid) | 862 | +0.0038 | 0.0010 | 3.82 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 7 | +0.0252 | 0.0055 | 4.59 |
| nhl | 106 | +0.0489 | 0.0019 | 25.44 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 86 | +0.0513 | 0.0023 | 22.15 |
| unquoted | 2 | +0.0418 | 0.0030 | 13.93 |
| wide | 25 | +0.0345 | 0.0014 | 23.91 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 1 | +0.0347 |  |  |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 4 | +0.0322 | 0.0029 | 11.02 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 98 | +0.0501 | 0.0020 | 24.73 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 862; slope 1.063 (95% CI 0.78–1.34); intercept +0.062. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
