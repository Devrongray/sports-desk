# Desk scorecard 2026-11-01T12:11:28+00:00

Closing-line value in probability points per $1 contract against Pinnacle's last pre-game fair price; fee-adjusted on fills. Decisions use the t statistic on fills once n is in the hundreds; everything else is context.

| set | n | mean CLV | se | t | note |
|---|---|---|---|---|---|
| fills (what you actually hold) | 0 |  |  |  |  |
| unfilled posts (would-have, at post price) | 0 |  |  |  |  |
| paper takes (every flagged take, filled at the touch, fee charged) | 77 | +0.0363 | 0.0027 | 13.52 | P&L $+493.73 on 77 settled, 40 winners |
| paper posts (every flagged post, at post price, fill unknown) | 73 | +0.0373 | 0.0009 | 40.32 |  |
| live-action candidates (scanner, at post price) | 150 | +0.0449 | 0.0015 | 30.02 |  |
| all referenced candidates (at mid) | 960 | +0.0057 | 0.0010 | 5.73 |  |

## By sport (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| nba | 9 | +0.0283 | 0.0047 | 6.03 |
| nhl | 141 | +0.0459 | 0.0015 | 30.18 |

## By quote state (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| tight | 88 | +0.0510 | 0.0023 | 22.45 |
| unquoted | 17 | +0.0384 | 0.0018 | 21.57 |
| wide | 45 | +0.0353 | 0.0009 | 40.92 |

## By segment (live-action candidates)

| group | n | mean CLV | se | t |
|---|---|---|---|---|
| FIRST_HALF | 3 | +0.0376 | 0.0022 | 16.71 |
| FIRST_PERIOD | 8 | +0.0336 | 0.0009 | 36.57 |
| FIRST_QUARTER | 4 | +0.0322 | 0.0029 | 11.02 |
| FULL_GAME | 2 | +0.0065 | 0.0094 | 0.69 |
| REGULATION | 133 | +0.0467 | 0.0016 | 29.35 |

## Is Pinnacle's close calibrated on Polymarket US settlements?

n = 960; slope 1.151 (95% CI 0.88–1.42); intercept +0.088. Slope near 1 and intercept near 0 means the reference is sound on this venue. Read it from 200+.

Kill rules and thresholds: PREREGISTRATION.md.
