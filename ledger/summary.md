# Desk scorecard 2026-10-23T12:05:37+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 32 | +0.0333 | 0.0033 | 10.04 | P&L $+541.17 on 32 settled, 20 winners |
| paper posts (every flagged post, at post price, fill unknown) | 20 | +0.0374 | 0.0023 | 15.95 |  |
| live-action candidates (scanner, at post price) | 52 | +0.0452 | 0.0022 | 20.79 |  |
| all referenced candidates (at mid) | 406 | +0.0024 | 0.0014 | 1.70 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 1 | +0.0365 |  |  |
| nhl | 51 | +0.0454 | 0.0022 | 20.53 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 38 | +0.0491 | 0.0026 | 18.61 |
| wide | 14 | +0.0349 | 0.0020 | 17.46 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_PERIOD | 2 | +0.0308 | 0.0029 | 10.46 |
| FIRST_QUARTER | 1 | +0.0365 |  |  |
| REGULATION | 49 | +0.0460 | 0.0023 | 20.35 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 406; slope 0.827 (95% CI 0.43–1.22); intercept +0.036. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
