"""
Shared helpers for all site scrapers.

Uses Playwright (a real headless browser) rather than plain requests,
because several of these property-management sites render their listings
with JavaScript — a plain HTTP GET would return an empty shell.

Each site module exposes one function: scrape() -> list[dict], where each
dict has keys: listing_id, address, unit, price, beds, baths, sqft, url.

IMPORTANT: I was not able to test these selectors against the live sites
(this environment can't reach arbitrary external domains). Treat each
scraper as a first draft — run it once with SCRAPER_DEBUG=1 to dump the
page HTML to data/debug_<site>.html, inspect it, and adjust the CSS
selectors marked "ADJUST ME" in each file.
"""
import os
import time
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

DEBUG = os.environ.get("SCRAPER_DEBUG") == "1"
DEBUG_DIR = Path(__file__).parent.parent / "data"


def fetch_rendered_html(url: str, wait_selector: str | None = None, wait_ms: int = 2500) -> str:
    """Load a page in headless Chromium and return the fully rendered HTML."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        )
        page.goto(url, timeout=30000)
        if wait_selector:
            try:
                page.wait_for_selector(wait_selector, timeout=8000)
            except Exception:
                pass  # fall through and grab whatever loaded
        page.wait_for_timeout(wait_ms)
        html = page.content()
        browser.close()
    return html


def soup_for(url: str, site_name: str, wait_selector: str | None = None) -> BeautifulSoup:
    html = fetch_rendered_html(url, wait_selector=wait_selector)
    if DEBUG:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        out = DEBUG_DIR / f"debug_{site_name}.html"
        out.write_text(html, encoding="utf-8")
        print(f"[{site_name}] wrote rendered HTML to {out}")
    return BeautifulSoup(html, "html.parser")


def make_listing_id(*parts: str) -> str:
    """Stable id built from whatever fields uniquely identify a unit on a site."""
    return " | ".join(str(p).strip() for p in parts if p)
