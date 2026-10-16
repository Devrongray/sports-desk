"""sports-desk: a separate Polymarket US desk.

Reads the public data branch of Devrongray/sports-method (Polymarket US quotes,
Pinnacle odds, price histories), finds markets where a small maker can be the
price at a Pinnacle-referenced level, writes every candidate to its own ledger,
and grades posts and fills by closing-line value against Pinnacle.

Nothing here places an order. The user posts; the desk logs and grades.
"""
__version__ = "0.1.0"
