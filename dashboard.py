#!/usr/bin/env python3
"""
Tiny local dashboard. Run with `python dashboard.py`, then open
http://localhost:5050 in a browser. Reads whatever main.py has already
collected in data/listings.db — it doesn't scrape anything itself.
"""
from collections import defaultdict
from flask import Flask, render_template

from storage import all_active_listings

app = Flask(__name__)


@app.route("/")
def index():
    listings = all_active_listings()
    by_site = defaultdict(list)
    for row in listings:
        by_site[row["site"]].append(row)
    # newest first within each site
    for site in by_site:
        by_site[site].sort(key=lambda r: r["first_seen"], reverse=True)
    return render_template("dashboard.html", by_site=dict(by_site))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
