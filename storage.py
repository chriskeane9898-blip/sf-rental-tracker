"""
SQLite storage for scraped listings.

A listing is uniquely identified by (site, listing_id). Every scraper run:
  1. Fetches current listings from a site
  2. Calls upsert_listings() which figures out which are brand new
  3. Returns the list of *new* listings so main.py can send alerts for them
Listings that disappear from a site are marked inactive but not deleted,
so you keep history.
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "listings.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    site TEXT NOT NULL,
    listing_id TEXT NOT NULL,
    address TEXT,
    unit TEXT,
    price TEXT,
    beds TEXT,
    baths TEXT,
    sqft TEXT,
    url TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (site, listing_id)
);
"""


@contextmanager
def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_listings(site: str, listings: list[dict]) -> list[dict]:
    """
    listings: list of dicts with keys listing_id, address, unit, price,
    beds, baths, sqft, url.

    Returns the subset that are new (never seen before for this site).
    """
    now = datetime.now(timezone.utc).isoformat()
    new_listings = []

    with get_conn() as conn:
        seen_ids = {row["listing_id"] for row in conn.execute(
            "SELECT listing_id FROM listings WHERE site = ?", (site,)
        )}

        current_ids = set()
        for item in listings:
            lid = item["listing_id"]
            current_ids.add(lid)
            if lid not in seen_ids:
                new_listings.append(item)
                conn.execute(
                    """INSERT INTO listings
                       (site, listing_id, address, unit, price, beds, baths, sqft, url,
                        first_seen, last_seen, active)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                    (site, lid, item.get("address"), item.get("unit"), item.get("price"),
                     item.get("beds"), item.get("baths"), item.get("sqft"), item.get("url"),
                     now, now),
                )
            else:
                conn.execute(
                    """UPDATE listings SET last_seen = ?, active = 1,
                       price = ?, address = ?, unit = ?, beds = ?, baths = ?, sqft = ?, url = ?
                       WHERE site = ? AND listing_id = ?""",
                    (now, item.get("price"), item.get("address"), item.get("unit"),
                     item.get("beds"), item.get("baths"), item.get("sqft"), item.get("url"),
                     site, lid),
                )

        # anything previously seen but not in this run -> mark inactive
        gone = seen_ids - current_ids
        for lid in gone:
            conn.execute(
                "UPDATE listings SET active = 0, last_seen = ? WHERE site = ? AND listing_id = ?",
                (now, site, lid),
            )

    return new_listings


def all_active_listings() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM listings WHERE active = 1 ORDER BY first_seen DESC"
        ).fetchall()


def recent_new_listings(limit: int = 50) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM listings ORDER BY first_seen DESC LIMIT ?", (limit,)
        ).fetchall()
