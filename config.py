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
]
