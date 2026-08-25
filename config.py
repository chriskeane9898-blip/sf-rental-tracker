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
    "min_price": 3000,
    "max_price": 4000,
    "min_beds": 1,
    # Excludes whole-building listings quoting a price/bed range across
    # floor plans (currently only Zumper does this) -- only individual
    # single-unit listings should trigger a notification.
    "exclude_building_ranges": True,
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
        # Verified 2026-08-25 against live /browse-apartments/ page (100
        # units at time of check). Their neighborhood tag (e.g.
        # "Downtown", "Tenderloin", or "Berkeley" for out-of-SF units)
        # goes through city_selector so it lands in `address` and the
        # existing "downtown" keyword in FILTERS catches it directly --
        # this site doesn't expose a zip code to match on instead.
        "name": "Brick and Timber",
        "engine": "generic",
        "url": "https://rentbt.com/browse-apartments/",
        "listing_selector": "a.resi-bt-unit-card__link",
        "address_selector": ".resi-bt-unit-card__subtitle-address",
        "city_selector": ".resi-bt-unit-card__title-link",   # neighborhood tag
        "beds_selector": ".spec-item",  # first match = beds (bed icon comes before bath)
        "price_selector": ".uk-label-danger",
        "wait_selector": "a.resi-bt-unit-card__link",
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
        # Verified 2026-08-25: same AppFolio Websites setup as L&L. 0
        # live listings at check time, but real infrastructure -- also
        # covers Tiburon (near Sausalito) per their own site title.
        "name": "Progressive Property Group",
        "engine": "appfolio",
        "url": "https://www.progressivesf.com/availability",
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
    {
        # Verified 2026-08-25. Craigslist's search UI redirects the old
        # sfbay.craigslist.org URLs to this unified www.craigslist.org
        # interface -- max_price/min_bedrooms filter server-side, postal
        # + radius scope the geographic search (still double-checked
        # locally via FILTERS since radius is approximate). Craigslist's
        # ToS prohibits scraping -- included anyway at the user's
        # explicit request for personal, non-commercial use.
        #
        # No dedicated scraper needed -- "generic" engine works directly
        # since CL's listing cards use plain (non-hashed) class names
        # and expose a real per-posting unique href.
        "name": "Craigslist - Downtown SF",
        "engine": "generic",
        "url": "https://www.craigslist.org/search/city/san-francisco-ca?cat=apa&max_price=4000&min_bedrooms=1&postal=94102&radius=1.5",
        "listing_selector": ".cl-search-result",
        "address_selector": ".posting-title .label",   # CL doesn't expose a real street address publicly; title is the closest thing
        "city_selector": ".result-location",            # neighborhood tag, e.g. "downtown / civic / van ness"
        "beds_selector": ".post-bedrooms",
        "price_selector": ".priceinfo",
        "link_selector": ".posting-title",
        "wait_selector": ".cl-search-result",
    },
    {
        "name": "Craigslist - Sausalito",
        "engine": "generic",
        "url": "https://www.craigslist.org/search/city/sausalito-ca?cat=apa&max_price=4000&min_bedrooms=1&postal=94965&radius=3",
        "listing_selector": ".cl-search-result",
        "address_selector": ".posting-title .label",
        "city_selector": ".result-location",
        "beds_selector": ".post-bedrooms",
        "price_selector": ".priceinfo",
        "link_selector": ".posting-title",
        "wait_selector": ".cl-search-result",
    },
    {
        # Verified 2026-08-25: 10 live listings at check time (real
        # inventory, not just working-but-empty infra like a couple of
        # the AppFolio sites). Boutique SF leasing firm, individual
        # units only (no floor-plan ranges seen).
        "name": "ReLISTO",
        "engine": "relisto",
        "url": "https://www.relisto.com/rentals/",
    },
]
