#!/usr/bin/env python3
"""Refresh the pitch scorecard prices embedded in site.html, then rebuild index.html.

Run manually (python3 update_prices.py) or daily via .github/workflows/prices.yml.
Pulls daily closes from Yahoo Finance's public chart endpoint (no key needed).
"""
import datetime, json, pathlib, re, subprocess, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
PITCHES = {
    # ticker: pitch date, price at pitch (from the model), price target
    "TLN":  {"pitch_date": "2026-04-21", "pitch_price": 347.74, "target": 433.61},
    "SNAP": {"pitch_date": "2026-03-16", "pitch_price": 4.54,   "target": 6.11},
}

def closes(ticker, start):
    t0 = int(datetime.datetime.fromisoformat(start).replace(tzinfo=datetime.timezone.utc).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={t0}&period2=9999999999&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, timeout=30))["chart"]["result"][0]
    out = []
    for ts, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]):
        if c is not None:
            out.append([datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).date().isoformat(), round(c, 2)])
    return out

data = {"updated": datetime.date.today().isoformat(), "tickers": {}}
for tk, meta in PITCHES.items():
    data["tickers"][tk] = {**meta, "series": closes(tk, meta["pitch_date"])}

site = ROOT / "site.html"
s = site.read_text()
block = "/*PRICES*/" + json.dumps(data, separators=(",", ":")) + "/*END_PRICES*/"
s2 = re.sub(r"/\*PRICES\*/.*?/\*END_PRICES\*/", lambda m: block, s, flags=re.S)
if s2 != s:
    site.write_text(s2)
    subprocess.run([str(ROOT / "build.sh")], check=True)
    print("Updated prices:", {k: v["series"][-1] for k, v in data["tickers"].items()})
else:
    print("No change")
