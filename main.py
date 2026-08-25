#!/usr/bin/env python3
"""
Runs every configured scraper, records what's new, and fires a push
notification for each new listing. Meant to be run on a schedule (cron).

Usage:
    python main.py                  # run all sites
    python main.py --only "Trinity" # run just one site (for debugging)
"""
import argparse
import sys
import traceback

from dotenv import load_dotenv
load_dotenv()

from config import SITES, FILTERS
from storage import upsert_listings
from notifier import notify_new_listings
from filters import matches_filters
from scrapers import appfolio, generic, zumper

ENGINES = {
    "appfolio": appfolio.scrape,
    "generic": generic.scrape,
    "zumper": zumper.scrape,
}


def run_site(site_config: dict):
    engine = ENGINES[site_config["engine"]]
    name = site_config["name"]
    print(f"[{name}] scraping...")
    try:
        listings = engine(site_config)
    except Exception:
        print(f"[{name}] FAILED:")
        traceback.print_exc()
        return

    print(f"[{name}] found {len(listings)} active listing(s)")

    for l in listings:
        l["matches_filters"] = matches_filters(l, FILTERS)

    new_listings = upsert_listings(name, listings)
    matching_new = [l for l in new_listings if l["matches_filters"]]

    if matching_new:
        print(f"[{name}] {len(matching_new)} NEW listing(s) matching your filters:")
        for l in matching_new:
            print(f"   - {l.get('address')} — {l.get('price')}")
        notify_new_listings(name, matching_new)

    skipped = len(new_listings) - len(matching_new)
    if skipped:
        print(f"[{name}] {skipped} other new listing(s) didn't match your filters (no alert sent)")
    if not new_listings:
        print(f"[{name}] nothing new")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Only run the site with this exact name")
    args = parser.parse_args()

    sites = SITES
    if args.only:
        sites = [s for s in SITES if s["name"] == args.only]
        if not sites:
            print(f"No site named {args.only!r}. Options: {[s['name'] for s in SITES]}")
            sys.exit(1)

    for site_config in sites:
        run_site(site_config)


if __name__ == "__main__":
    main()
