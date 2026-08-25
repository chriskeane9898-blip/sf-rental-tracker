"""
One entry per site you're tracking. `engine` picks which scraper module
handles it:

  - "appfolio": for any property manager whose public listings live at
    https://<subdomain>.appfolio.com/listings/listings — very common
    among small/mid SF landlords. Confirmed for Chandler Properties.
  - "generic": a configurable CSS-selector scraper for everyone else.
    You'll likely need to tweak the selectors per site — see README.

Run `python inspect_site.py <site_name>` after setup to dump each site's
rendered HTML to data/ so you can find the right selectors quickly.
"""

# What counts as a match worth a push notification (see filters.py).
# "Downtown SF" isn't a single official boundary, so this is a practical
# definition: FiDi/SOMA/Union Square/Civic Center-ish zip codes, plus a
# keyword list for sites (like Zumper) whose listing URLs/text name the
# neighborhood directly. Adjust freely if it's too wide/narrow.
FILTERS = {
    "max_price": 4000,
    "min_beds": 1,
    "downtown_sf_zips": {"94102", "94103", "94104", "94105", "94108", "94111"},
    "downtown_sf_keywords": [
        "financial district", "soma", "south beach", "union square",
        "embarcadero", "civic center", "yerba buena", "rincon hill",
        "jackson square", "downtown",
    ],
    "sausalito_keywords": ["sausalito"],
}

SITES = [
    {
    "name": "Anchor Realty",
    "engine": "appfolio",
    "url": "https://anchorrlty.appfolio.com/listings/listings",
    },
    {
        "name": "Chandler Properties",
        "engine": "appfolio",
        "url": "https://chandlerproperties.appfolio.com/listings/listings",
    },
    {
        "name": "RentSFNow",
        "engine": "generic",
        "url": "https://www.rentsfnow.com/vacancies/",  # verify path
        "listing_selector": ".vacancy-item",             # ADJUST ME
        "address_selector": ".vacancy-item__address",    # ADJUST ME
        "price_selector": ".vacancy-item__price",         # ADJUST ME
        "link_selector": "a",
        "wait_selector": ".vacancy-item",
    },
    {
        "name": "Trinity",
        "engine": "generic",
        "url": "https://www.trinitysf.com/apartments",  # verify path
        "listing_selector": ".unit-card",                # ADJUST ME
        "address_selector": ".unit-card__address",       # ADJUST ME
        "price_selector": ".unit-card__price",            # ADJUST ME
        "link_selector": "a",
        "wait_selector": ".unit-card",
    },
    {
        "name": "Brick and Timber",
        "engine": "generic",
        "url": "https://rentbt.com/",
        "listing_selector": ".unit",                      # ADJUST ME
        "address_selector": ".unit__address",             # ADJUST ME
        "price_selector": ".unit__price",                  # ADJUST ME
        "link_selector": "a",
        "wait_selector": "body",
    },
    {
        # Verified 2026-08-25: AppFolio Websites product -- the whole
        # site (including /vacancies) is hosted through AppFolio, so the
        # same detail-link-anchored scraper as Chandler/Anchor works here
        # even though the URL isn't a *.appfolio.com subdomain.
        "name": "L&L Property Management",
        "engine": "appfolio",
        "url": "https://www.llpm.com/vacancies",
    },
    {
        # Verified 2026-08-25 against live search-rentals.php. Real
        # listings, but this office's inventory skews Sacramento-area --
        # kept in rotation for whenever Sausalito units show up.
        "name": "RNB Property Management",
        "engine": "generic",
        "url": "https://www.rnbrentals.com/search-rentals.php",
        "listing_selector": ".rnb-prop",
        "address_selector": ".rnb-prop-title",   # street address
        "city_selector": ".rnb-prop-addr",       # "City, CA zip"
        "price_selector": ".rnb-prop-price",
        "link_selector": ".rnb-prop-title",
        "wait_selector": ".rnb-prop",
    },
    {
        # Large aggregator, not a small brokerage -- kept separate at the
        # user's request despite the stronger anti-bot/ToS risk than the
        # boutique sites above. Uses the "zumper" engine (anchors on
        # stable URL patterns, not CSS classes -- see scrapers/zumper.py).
        "name": "Zumper - San Francisco",
        "engine": "zumper",
        "url": "https://www.zumper.com/apartments-for-rent/san-francisco-ca?beds_min=1&price_max=4000",
    },
    {
        "name": "Zumper - Sausalito",
        "engine": "zumper",
        "url": "https://www.zumper.com/apartments-for-rent/sausalito-ca?beds_min=1&price_max=4000",
    },
]
