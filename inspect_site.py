#!/usr/bin/env python3
"""
Dumps a site's fully-rendered HTML to data/debug_<site>.html so you can
open it and find the right CSS selectors for config.py.

Usage: python inspect_site.py "Trinity"
"""
import sys
from config import SITES
from scrapers.base import fetch_rendered_html, DEBUG_DIR

name = sys.argv[1] if len(sys.argv) > 1 else None
site = next((s for s in SITES if s["name"] == name), None)
if not site:
    print(f"Usage: python inspect_site.py \"<site name>\"")
    print(f"Available: {[s['name'] for s in SITES]}")
    sys.exit(1)

html = fetch_rendered_html(site["url"], wait_selector=site.get("wait_selector"))
DEBUG_DIR.mkdir(parents=True, exist_ok=True)
out = DEBUG_DIR / f"debug_{site['name'].lower().replace(' ', '_')}.html"
out.write_text(html, encoding="utf-8")
print(f"Wrote {out} ({len(html)} chars). Open it and find the repeating listing element.")
