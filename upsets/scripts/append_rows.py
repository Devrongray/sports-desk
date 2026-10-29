"""Append candidate rows to upsets/ledger.csv from a JSON file of row dicts.

Usage: python upsets/scripts/append_rows.py rows.json [ledger.csv]
Rows may omit columns; missing columns are written empty. edge_pp is computed
from my_prob and pm_price when absent. Refuses to add a row whose
(date_pt, league, event, market, selection) already exists.
"""
import csv, json, sys

rows_path = sys.argv[1]
ledger = sys.argv[2] if len(sys.argv) > 2 else 'upsets/ledger.csv'
with open(ledger, newline='') as fh:
    reader = csv.DictReader(fh)
    fields = reader.fieldnames
    existing = {(r['date_pt'], r['league'], r['event'], r['market'], r['selection']) for r in reader}
new = json.load(open(rows_path))
added = 0
with open(ledger, 'a', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    for r in new:
        key = (r.get('date_pt', ''), r.get('league', ''), r.get('event', ''), r.get('market', ''), r.get('selection', ''))
        if key in existing:
            print('skip duplicate:', key); continue
        if 'edge_pp' not in r and r.get('my_prob') not in (None, '') and r.get('pm_price') not in (None, ''):
            r['edge_pp'] = f"{(float(r['my_prob']) - float(r['pm_price'])) * 100:+.1f}"
        w.writerow({k: r.get(k, '') for k in fields}); added += 1; existing.add(key)
print(f'added {added} rows to {ledger}')
