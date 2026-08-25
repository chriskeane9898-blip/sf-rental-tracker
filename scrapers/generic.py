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

        street = addr_el.get_text(strip=True) if addr_el else None

        # Some sites split street address and city/zip (or a neighborhood
        # tag, e.g. Brick and Timber's "Downtown"/"Tenderloin" label) into
        # a separate element -- city_selector is optional and gets
        # appended if present.
        city_selector = site_config.get("city_selector")
        city = None
        if city_selector:
            city_el = card.select_one(city_selector)
            city = city_el.get_text(strip=True) if city_el else None

        address = ", ".join(p for p in [street, city] if p) or None

        # Optional: bedroom count, needed for the min_beds filter to
        # actually exclude studios on sites that show beds (without
        # this, beds stays None and the filter can't check it at all).
        beds_selector = site_config.get("beds_selector")
        beds = None
        if beds_selector:
            beds_el = card.select_one(beds_selector)
            beds = beds_el.get_text(strip=True) if beds_el else None

        price = price_el.get_text(strip=True) if price_el else None

        # Usually the link is a child of the card (link_selector), but
        # some sites make the whole card itself the <a> (e.g. Brick and
        # Timber) -- fall back to the card's own href in that case.
        link_selector = site_config.get("link_selector")
        if link_selector:
            link_el = card.select_one(link_selector)
            href = link_el.get("href") if link_el else None
        elif card.name == "a":
            href = card.get("href")
        else:
            href = None

        if href and href.startswith("/"):
            base = site_config["url"].split("/")[0] + "//" + site_config["url"].split("/")[2]
            href = base + href

        if not address:
            continue  # skip cards we couldn't parse at all

        results.append({
            # href included (not just address+price) because two
            # different units can share both -- e.g. Brick and Timber
            # listing multiple identically-priced studios in one
            # building, which otherwise collide as "the same listing"
            # and crash the DB's unique constraint.
            "listing_id": make_listing_id(address, price, href),
            "address": address,
            "unit": None,
            "price": price,
            "beds": beds,
            "baths": None,
            "sqft": None,
            "url": href,
        })

    return results
