# Desk scorecard 2026-11-04T12:23:33+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 104 | +0.0376 | 0.0022 | 16.71 | P&L $+473.47 on 104 settled, 51 winners |
| paper posts (every flagged post, at post price, fill unknown) | 106 | +0.0373 | 0.0007 | 51.84 |  |
| live-action candidates (scanner, at post price) | 210 | +0.0449 | 0.0012 | 36.36 |  |
| all referenced candidates (at mid) | 1151 | +0.0072 | 0.0009 | 8.06 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 9 | +0.0283 | 0.0047 | 6.03 |
| nhl | 201 | +0.0457 | 0.0013 | 36.54 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 115 | +0.0520 | 0.0020 | 26.36 |
| unquoted | 23 | +0.0379 | 0.0017 | 22.40 |
| wide | 72 | +0.0359 | 0.0006 | 57.73 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 3 | +0.0376 | 0.0022 | 16.71 |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 4 | +0.0322 | 0.0029 | 11.02 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 193 | +0.0462 | 0.0013 | 35.82 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 1151; slope 1.183 (95% CI 0.94–1.42); intercept +0.105. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
