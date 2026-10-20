# Desk scorecard 2026-10-20T12:07:00+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 24 | +0.0350 | 0.0041 | 8.54 | P&L $+413.75 on 24 settled, 14 winners |
| paper posts (every flagged post, at post price, fill unknown) | 7 | +0.0366 | 0.0041 | 8.91 |  |
| live-action candidates (scanner, at post price) | 31 | +0.0487 | 0.0031 | 15.85 |  |
| all referenced candidates (at mid) | 219 | +0.0046 | 0.0020 | 2.30 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nhl | 31 | +0.0487 | 0.0031 | 15.85 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 29 | +0.0497 | 0.0032 | 15.48 |
| wide | 2 | +0.0355 | 0.0060 | 5.92 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_PERIOD | 1 | +0.0279 |  |  |
| REGULATION | 30 | +0.0494 | 0.0031 | 15.96 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 219; slope 0.787 (95% CI 0.27–1.31); intercept -0.030. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
