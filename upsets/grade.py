"""Grade upsets/ledger.csv.

Usage: python upsets/grade.py [ledger.csv]
Fills brier_mine / brier_market / clv_pp for rows that have a result (1/0) and
prints a scorecard: mean Brier (mine vs market) by tier and overall, hit rate by
probability band, and ROI at stated stakes (binary contract paying $1).
"""
import csv, sys, math, statistics
from collections import defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else 'upsets/ledger.csv'
rows = list(csv.DictReader(open(path, newline='')))
fields = rows[0].keys() if rows else []

def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

for r in rows:
    res = f(r.get('result'))
    if res is None:
        continue
    p, q = f(r.get('my_prob')), f(r.get('pm_price'))
    if p is not None:
        r['brier_mine'] = f"{(p - res) ** 2:.4f}"
    if q is not None:
        r['brier_market'] = f"{(q - res) ** 2:.4f}"
    pc = f(r.get('pin_close'))
    if pc is not None and q is not None:
        r['clv_pp'] = f"{(pc - q) * 100:.2f}"

with open(path, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(fields))
    w.writeheader(); w.writerows(rows)

graded = [r for r in rows if f(r.get('result')) is not None and f(r.get('my_prob')) is not None]
print(f"graded rows: {len(graded)} of {len(rows)}")
by_tier = defaultdict(list)
for r in graded:
    by_tier[r['tier']].append(r)
    by_tier['ALL'].append(r)
print("\ntier | n | mean Brier mine | mean Brier market | diff (neg = we beat price) | hits")
for t, rs in by_tier.items():
    bm = statistics.mean(float(r['brier_mine']) for r in rs)
    bq = statistics.mean(float(r['brier_market']) for r in rs if r.get('brier_market'))
    hits = sum(int(float(r['result'])) for r in rs)
    print(f"{t} | {len(rs)} | {bm:.4f} | {bq:.4f} | {bm - bq:+.4f} | {hits}/{len(rs)}")
bands = defaultdict(list)
for r in graded:
    q = f(r['pm_price']); bands[f"{math.floor(q*10)/10:.1f}-{math.floor(q*10)/10+0.1:.1f}"].append(float(r['result']))
print("\nprice band | n | actual win rate")
for b in sorted(bands):
    print(f"{b} | {len(bands[b])} | {statistics.mean(bands[b]):.3f}")
pnl = 0.0; staked = 0.0
for r in graded:
    s, q, res = f(r.get('stake_usd')) or 0.0, f(r['pm_price']), float(r['result'])
    if s > 0 and q:
        staked += s; pnl += s * (1 / q - 1) if res == 1 else -s
print(f"\nstaked ${staked:.2f}, P&L ${pnl:+.2f}" if staked else "\nno staked rows")
