"""
Applies config.FILTERS (price range, min beds, target areas) to a scraped
listing dict. Kept separate from scraping/storage so "what counts as a
match" can change without touching how listings get collected.

Only excludes a listing on price/beds when that field parsed successfully
and failed the check -- a listing with an unparseable price isn't assumed
to be too expensive, it just can't be confirmed on that criterion. Location
is required and excludes on no match, since "somewhere in the Bay Area" is
not useful on its own.
"""
import re

PRICE_RE = re.compile(r"\$?([\d,]+)")
BEDS_NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def parse_price(price: str | None) -> int | None:
    """'$4,034-$6,757/mo' -> 4034 (low end of a range, or the only number)."""
    if not price:
        return None
    m = PRICE_RE.search(price)
    return int(m.group(1).replace(",", "")) if m else None


def parse_beds(beds: str | None) -> float | None:
    """'Studio' -> 0, '1 bd' -> 1, '1-2 beds' -> 1 (low end)."""
    if not beds:
        return None
    if "studio" in beds.lower():
        return 0.0
    m = BEDS_NUM_RE.search(beds)
    return float(m.group(0)) if m else None


def matches_location(address: str | None, filters: dict) -> bool:
    if not address:
        return False
    addr_lower = address.lower()

    if any(kw.lower() in addr_lower for kw in filters.get("sausalito_keywords", [])):
        return True
    if any(kw.lower() in addr_lower for kw in filters.get("downtown_sf_keywords", [])):
        return True

    zip_match = re.search(r"\b(\d{5})\b", address)
    if zip_match and zip_match.group(1) in filters.get("downtown_sf_zips", set()):
        return True

    return False


def matches_filters(listing: dict, filters: dict) -> bool:
    # Whole-building listings quote a price/bed range across floor plans
    # (e.g. Zumper's "Studio-2 beds, $3,960-$6,690") rather than one
    # specific unit -- excluded outright when a scraper flags one, since
    # the user only wants individual-property listings.
    if filters.get("exclude_building_ranges", True) and listing.get("is_range"):
        return False

    price = parse_price(listing.get("price"))
    max_price = filters.get("max_price")
    if max_price is not None and price is not None and price > max_price:
        return False
    min_price = filters.get("min_price")
    if min_price is not None and price is not None and price < min_price:
        return False

    min_beds = filters.get("min_beds")
    beds = parse_beds(listing.get("beds"))
    if min_beds is not None and beds is not None and beds < min_beds:
        return False

    return matches_location(listing.get("address"), filters)
