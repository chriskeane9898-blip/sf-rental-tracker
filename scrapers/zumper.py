"""
Scraper for Zumper search-results pages.

Zumper is a Next.js app with CSS-module class names that get rehashed on
every deploy (e.g. "ListingCardContentSection_listingInfo__pKfPE"), so
this deliberately does NOT select on CSS classes -- same strategy as
appfolio.py. It anchors on the one thing that's stable: every listing
card links to /apartment-buildings/<id>/<slug> or /address/<slug>.

Zumper often shows a price *range* across unit types (e.g.
"$4,034-$6,757") -- parse_price() in filters.py takes the low end.

Verified against a live San Francisco search on 2026-08-25. As a large
platform (unlike the small AppFolio-hosted sites), Zumper is more likely
to rate-limit or bot-block a headless scraper over time -- if this starts
returning 0 listings, check data/debug_zumper*.html for a CAPTCHA/block
page before assuming the markup changed.
"""
import re
from scrapers.base import fetch_rendered_html, make_listing_id

CARD_LINK_RE = re.compile(r"/(?:apartment-buildings|address)/([^/?#]+)")
PRICE_RE = re.compile(r"\$[\d,]+")
BEDS_RE = re.compile(r"(Studio|\d+(?:[–-]\d+)?)\s*beds?", re.IGNORECASE)
ADDRESS_RE = re.compile(r"\d+[^,\n]*,\s*[A-Za-z .]+,\s*CA\s*\d{5}")


def scrape(site_config: dict) -> list[dict]:
    url = site_config["url"]
    html = fetch_rendered_html(
        url,
        wait_selector="a[href*='/apartment-buildings/'], a[href*='/address/']",
        wait_ms=4000,
    )

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    seen_ids = set()
    results = []

    for a in soup.select("a[href*='/apartment-buildings/'], a[href*='/address/']"):
        href = a.get("href", "")
        m = CARD_LINK_RE.search(href)
        if not m:
            continue
        slug_id = m.group(1)
        if slug_id in seen_ids:
            continue
        seen_ids.add(slug_id)

        container = a
        text = ""
        for _ in range(6):
            if container.parent is None:
                break
            container = container.parent
            text = container.get_text("\n", strip=True)
            if "$" in text and len(text) > 40:
                break

        price_match = PRICE_RE.search(text)
        beds_match = BEDS_RE.search(text)
        addr_match = ADDRESS_RE.search(text)

        full_url = href if href.startswith("http") else f"https://www.zumper.com{href}"

        results.append({
            "listing_id": make_listing_id(slug_id),
            "address": addr_match.group(0) if addr_match else text.split("\n")[0][:100],
            "unit": None,
            "price": price_match.group(0) if price_match else None,
            "beds": beds_match.group(1) if beds_match else None,
            "baths": None,
            "sqft": None,
            "url": full_url,
        })

    return results
