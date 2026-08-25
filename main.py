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

from config import SITES
from storage import upsert_listings
from notifier import notify_new_listings
from scrapers import appfolio, generic

ENGINES = {
    "appfolio": appfolio.scrape,
    "generic": generic.scrape,
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
    new_listings = upsert_listings(name, listings)
    if new_listings:
        print(f"[{name}] {len(new_listings)} NEW listing(s):")
        for l in new_listings:
            print(f"   - {l.get('address')} — {l.get('price')}")
        notify_new_listings(name, new_listings)
    else:
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
