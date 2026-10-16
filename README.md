# sports-desk

A separate Polymarket US desk. It does one thing: find markets where a small
maker can **be the price** at a Pinnacle-referenced level, tell you exactly what
to post, log every candidate whether you post or pass, and grade everything by
closing-line value against Pinnacle. It never places an order.

It is a separate track from the "Begin" daily picks (Daily Picks Playbook and
Tracker stay as they are) and from the sports-method research pipeline. It reads
sports-method's public data branch and never writes to it. Its trigger word in
chat is **"Desk"**.

The rules are frozen in [PREREGISTRATION.md](PREREGISTRATION.md). The reasoning
behind them is in the doc *Prediction Research Synthesis & Plan*.

## Why "be the price" and not "beat the price"

Two days of recordings (14–15 Oct 2026) show that on full-game winner, total and
spread lines Polymarket US sits within 1–2¢ of Pinnacle's de-vigged price, with
0.5–1¢ spreads and tens of thousands of contracts quoted at the touch by market
makers hedging off sportsbook feeds. A taker there had negative edge in 87–100%
of snapshots. The same recordings show NHL period totals and spreads, NFL
quarter and half totals and about two-thirds of CS2 matches quoted 3–30¢ wide,
or not at all. In those books a resting order at fair ∓ 3¢ is often the best
price on its side; fills come from retail crossing the spread.

## What runs

| Piece | What it does |
|---|---|
| `desk/live.py` | Fetches each upcoming event's **full** market list (`GET /v1/events/slug/{slug}`) and BBO for markets inside the posting window. Needed because the league events feed stopped embedding non-winner markets on 15 Oct 2026. |
| `desk/period_poll.py` | Pinnacle period / half / quarter / inning lines through The Odds API per-event endpoint, only for events inside the window, quota-guarded. Needs the `ODDS_API_KEY` secret. |
| `desk/reference.py` | Matches a Polymarket contract to its Pinnacle line and de-vigs (additive) using sports-method's code. |
| `desk/scan.py` | Quote state, taker and maker edges, the one action the rules allow, size, reason. Writes `scans/<day>/scan_<ts>.{csv,md}` and `scans/latest.md`. |
| `desk/ledger.py` | `ledger/candidates.csv`, `orders.csv`, `fills.csv`. |
| `desk/grade.py` | `ledger/grades.csv` and `ledger/summary.md`: fee-adjusted CLV against Pinnacle's last pre-game fair, would-have CLV for unfilled posts and all candidates, fill rate, P&L (reported), reference calibration. |
| `.github/workflows/scan.yml` | Every 30 minutes, 09:00–22:30 Pacific. |
| `.github/workflows/grade.yml` | Daily at 11:40 UTC. |
| `.github/workflows/log.yml` | Records an order, fill or cancel from a manual trigger (how Claude logs what you report in chat). |

sports-method's `devig`, `fees`, `metrics`, `polymarket_us` and matcher are reused
at a pinned commit (`config/desk.yaml → reference.sports_method_sha`); the
workflow clones it into `vendor/`.

## Setup (one time, ~2 minutes)

1. Create the empty public repository `Devrongray/sports-desk` on GitHub and push this folder.
2. Add the repository secret `ODDS_API_KEY` (the same The Odds API key sports-method uses). Without it the desk still scans full-game lines; period lines get no reference.
3. Run the **Desk scan** workflow once by hand (Actions → Desk scan → Run workflow) and open `scans/latest.md`.

Quota: the period poll costs (markets returned × 1) credits per event per poll.
An event is inside the 180-minute window for six half-hourly scans, so one NHL
game costs up to 3 × 6 = 18 credits a day; a 10-game NHL night ≈ 180, an
8-game NBA night ≈ 144. In full season that is ~300–350 credits a day
(~10k a month) **on top of sports-method's own ~11–15k a month on the same
key**, which does not fit a 20k plan. Three ceilings bound it
(`period_markets` in `config/desk.yaml`): 80 credits per run, 400 per UTC day,
and a stop when the key has fewer than 2,000 credits left, so sports-method's
hourly poll keeps running to the end of the cycle. `data/desk_pinnacle/latest_poll.json`
shows the quota and today's spend after every poll. Cheaper settings if
needed: poll every 60 minutes instead of 30 (halves it; references stay inside
the 60-minute rule), or drop NBA halves/quarters.

## The daily routine ("Desk")

1. You say **Desk** in chat. Claude reads `scans/latest.md`, checks the live
   actions for a reason the gap exists (lineup, goalie, injury, a Pinnacle move),
   and returns one table: contract, bid/ask, Pinnacle fair, action, price,
   size, reason.
2. You post the orders you choose on Polymarket US, as limit orders at the
   stated price and size, and tell Claude what you posted and later what filled.
3. Claude logs orders and fills (ledger), and pulls are your job: cancel resting
   orders 15 minutes before start and on any news for that game.
4. Grading runs every morning. `ledger/summary.md` is the scorecard; the gates
   and kill rules in PREREGISTRATION.md decide what happens next.

The posting window is 15–180 minutes before start, so the useful scans are the
afternoon and early-evening ones: roughly 2–3 hours before NBA tips, after NHL
morning skates, 3 hours before MLB first pitch.

## Running locally

```
pip install -r requirements.txt
export SPORTS_METHOD_PATH=/path/to/sports-method        # a checkout at the pinned commit
pytest -q                                                # arithmetic and rule checks, no network
python -m desk scan  --data /path/to/sports-method-data/data --as-of 2026-10-15T22:30:00Z --no-ledger --print
python -m desk replay --data /path/to/sports-method-data/data --from 2026-10-15T20:00Z --to 2026-10-16T03:00Z --every 30 --show-live
python -m desk grade --data /path/to/sports-method-data/data
```

`--as-of` replays the scan at a past moment using only files stamped at or
before it. Live fetches need network to `gateway.polymarket.us` (GitHub Actions
has it; Claude's workspace does not).

## Data layout

```
scans/<YYYY-MM-DD>/scan_<ts>.csv|md     every scan; scans/latest.{csv,md} the newest
ledger/candidates.csv                    live actions + ten largest referenced gaps per scan
ledger/orders.csv  ledger/fills.csv      what you did
ledger/grades.csv  ledger/summary.md     the scorecard
data/desk_pinnacle/<day>/period_<ts>.ndjson.gz   Pinnacle period lines (own poll)
data/desk_polymarket/<day>/{markets,bbo}_<ts>.ndjson.gz   the desk's own Polymarket snapshots
```

## Known issues

- **sports-method's recorder lost all non-winner markets at ~20:34 UTC on 15 Oct 2026** because the league events feed now embeds only the headline winner (`marketCounts.numMarkets` still reports 150–190 per event). The fix is one extra call per event (`/v1/events/slug/{slug}`); see `patches/sports-method-full-markets.diff`. The desk does this itself in the meantime.
- No Pinnacle esports reference: CS2 and LoL are scanned for quote state only.
- Pinnacle rarely posts NHL 2nd/3rd-period lines pregame; those markets will show "no reference".
