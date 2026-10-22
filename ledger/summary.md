# Desk scorecard 2026-10-22T12:09:49+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 30 | +0.0344 | 0.0034 | 9.99 | P&L $+496.11 on 30 settled, 19 winners |
| paper posts (every flagged post, at post price, fill unknown) | 11 | +0.0365 | 0.0037 | 9.76 |  |
| live-action candidates (scanner, at post price) | 41 | +0.0479 | 0.0026 | 18.54 |  |
| all referenced candidates (at mid) | 332 | +0.0017 | 0.0016 | 1.07 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nhl | 41 | +0.0479 | 0.0026 | 18.54 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 36 | +0.0501 | 0.0027 | 18.65 |
| wide | 5 | +0.0322 | 0.0049 | 6.63 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_PERIOD | 1 | +0.0279 |  |  |
| REGULATION | 40 | +0.0484 | 0.0026 | 18.62 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 332; slope 0.802 (95% CI 0.37–1.23); intercept +0.016. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
