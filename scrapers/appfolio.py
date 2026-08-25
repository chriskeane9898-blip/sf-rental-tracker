"""
Scraper for AppFolio-hosted public listing pages
(https://<company>.appfolio.com/listings/listings).

Verified against Chandler Properties' real page on 2026-08-22. AppFolio
listing pages don't have stable, documented CSS class names across
skins, so instead of relying on classes, this scraper anchors on the
one thing that IS stable: every listing links to
    /listings/detail/<uuid>
That uuid is a perfect unique listing_id — it doesn't change even if
AppFolio restyles the page.

If a site using this engine stops matching, run with SCRAPER_DEBUG=1 and
check data/debug_<site>.html for what actually changed.
"""
import re
from scrapers.base import fetch_rendered_html, make_listing_id

DETAIL_RE = re.compile(r"/listings/detail/([0-9a-fA-F-]{36})")
PRICE_RE = re.compile(r"\$[\d,]+")
BEDBATH_RE = re.compile(r"(Studio|\d+\s*bd)\s*/\s*[\d.]+\s*ba", re.IGNORECASE)
SQFT_RE = re.compile(r"([\d,]+)\s*(?:sq ?ft|square feet)", re.IGNORECASE)
# AppFolio cards duplicate their price/bed/bath text (visible + a11y
# copy) ahead of the actual address, all on one line if joined with a
# plain space -- which made this greedily swallow that whole prefix.
# Joining the card with "\n" and anchoring per-line (MULTILINE, and "."
# not crossing lines) confines the match to just the address's own line.
ADDRESS_RE = re.compile(r"^(\d.*?,\s*CA\s*\d{5})", re.MULTILINE)


def scrape(site_config: dict) -> list[dict]:
    url = site_config["url"]
    html = fetch_rendered_html(url, wait_selector="a[href*='/listings/detail/']")

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    seen_uids = set()
    results = []

    for a in soup.select("a[href*='/listings/detail/']"):
        href = a.get("href", "")
        m = DETAIL_RE.search(href)
        if not m:
            continue
        uid = m.group(1)
        if uid in seen_uids:
            continue
        seen_uids.add(uid)

        # Walk up to a container with enough text to hold price/address/beds
        container = a
        text = ""
        for _ in range(6):
            if container.parent is None:
                break
            container = container.parent
            text = container.get_text("\n", strip=True)
            if "$" in text and len(text) > 60:
                break

        price_match = PRICE_RE.search(text)
        bedbath_match = BEDBATH_RE.search(text)
        sqft_match = SQFT_RE.search(text)
        addr_match = ADDRESS_RE.search(text)

        beds = baths = None
        if bedbath_match:
            parts = bedbath_match.group(0).split("/")
            beds = parts[0].strip()
            baths = parts[1].replace("ba", "").strip() if len(parts) > 1 else None

        full_url = href if href.startswith("http") else f"https://{url.split('/')[2]}{href}"

        results.append({
            "listing_id": make_listing_id(uid),
            "address": addr_match.group(1) if addr_match else text[:80],
            "unit": None,  # usually embedded in the address string (e.g. "#304")
            "price": price_match.group(0) if price_match else None,
            "beds": beds,
            "baths": baths,
            "sqft": sqft_match.group(1) if sqft_match else None,
            "url": full_url,
        })

    return results
