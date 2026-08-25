"""
Scraper for ReLISTO (relisto.com) listing pages.

Each listing card is an <a class="listing-box"> with the key fields as
data-attributes (data-price, data-beds, data-baths) rather than text
buried in nested spans -- much more reliable than the text-walking
approach appfolio.py/zumper.py need. The full street address is in the
URL slug itself (e.g.
".../71243103-1170-sacramento-16a-san-francisco-ca-94108/"), which
combines with the visible <h4 class="location"> text for the address.

Verified against a live /rentals/ page (10 listings) on 2026-08-25.
"""
import re
from scrapers.base import fetch_rendered_html, make_listing_id

# Just the zip -- trying to also capture the city name greedily off the
# slug (e.g. ".../784-clementina-st-san-francisco-ca-94103/") pulled in
# extra street-name fragments since there's no clean delimiter between
# the two. A small known-cities lookup handles the city name instead.
ZIP_RE = re.compile(r"-ca-(\d{5})/?$")
KNOWN_CITIES = ["san-francisco", "sausalito", "oakland", "berkeley", "richmond", "tiburon"]


def scrape(site_config: dict) -> list[dict]:
    url = site_config["url"]
    html = fetch_rendered_html(url, wait_selector="a.listing-box", wait_ms=3000)

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    results = []
    for card in soup.select("a.listing-box"):
        href = card.get("href", "")
        zip_match = ZIP_RE.search(href)
        zip_code = zip_match.group(1) if zip_match else None
        city = next((c.replace("-", " ").title() for c in KNOWN_CITIES if f"-{c}-ca-" in href), None)

        street_el = card.select_one(".location")
        street = street_el.get_text(strip=True) if street_el else None
        city_state_zip = f"{city}, CA {zip_code}" if city and zip_code else (f"CA {zip_code}" if zip_code else None)
        address = ", ".join(p for p in [street, city_state_zip] if p) or None

        if not address:
            continue

        results.append({
            "listing_id": make_listing_id(href),
            "address": address,
            "unit": None,
            "price": card.get("data-price"),
            "beds": card.get("data-beds"),
            "baths": card.get("data-baths"),
            "sqft": None,
            "url": href,
        })

    return results
