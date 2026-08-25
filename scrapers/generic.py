"""
Configurable scraper for sites that aren't AppFolio. Selectors come from
each site's entry in config.py. These are BEST-GUESS selectors — I
could not test them against the live sites from this environment
(network access here is restricted to package registries, not arbitrary
websites), and a couple are JS-heavy pages I only saw partial renders of.

To fix a site that isn't finding listings:
  1. Run: SCRAPER_DEBUG=1 python main.py --only "Site Name"
  2. Open data/debug_<site>.html in a browser or editor
  3. Find the repeating element that wraps one listing, and update
     listing_selector / address_selector / price_selector / link_selector
     in config.py to match
"""
from scrapers.base import soup_for, make_listing_id


def scrape(site_config: dict) -> list[dict]:
    soup = soup_for(
        site_config["url"],
        site_name=site_config["name"].lower().replace(" ", "_"),
        wait_selector=site_config.get("wait_selector"),
    )

    cards = soup.select(site_config["listing_selector"])
    results = []

    for card in cards:
        addr_el = card.select_one(site_config["address_selector"])
        price_el = card.select_one(site_config["price_selector"])
        link_el = card.select_one(site_config["link_selector"])

        address = addr_el.get_text(strip=True) if addr_el else None
        price = price_el.get_text(strip=True) if price_el else None
        href = link_el.get("href") if link_el else None

        if href and href.startswith("/"):
            base = site_config["url"].split("/")[0] + "//" + site_config["url"].split("/")[2]
            href = base + href

        if not address:
            continue  # skip cards we couldn't parse at all

        results.append({
            "listing_id": make_listing_id(address, price),
            "address": address,
            "unit": None,
            "price": price,
            "beds": None,
            "baths": None,
            "sqft": None,
            "url": href,
        })

    return results
