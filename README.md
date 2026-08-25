# SF Rental Tracker

Scrapes 10 SF/Sausalito-area rental sites, filters for what actually
matches your search (price, beds, neighborhood — see `FILTERS` in
`config.py`), tracks what's new in a local SQLite database, pushes a
phone notification via ntfy for each new *matching* listing, and shows
everything scraped (matches highlighted) in a small local dashboard.

**Sites configured:** Anchor Realty, Chandler Properties, L&L Property
Management, Progressive Property Group, RNB Property Management, Zumper
(San Francisco + Sausalito searches), RentSFNow, Trinity, Brick and
Timber (`config.py`). ("Mosser Companies" was listed here before but
was never actually configured -- corrected.)

**Default filters:** $3,000-$4,000/mo, 1+ bedroom, downtown San
Francisco or Sausalito, individual-unit listings only (excludes
whole-building listings that quote a price/bed range across floor
plans, e.g. Zumper's "$3,995-$7,495"). Adjust `FILTERS` at the top of
`config.py` — it's a plain dict (min_price, max_price, min_beds, zip
codes / neighborhood keywords for "downtown SF", keywords for
Sausalito, exclude_building_ranges).

## Status of each scraper

| Site | Status |
|---|---|
| **Anchor Realty, Chandler Properties, L&L Property Management, Progressive Property Group** | ✅ Verified live against real pages. All four run on AppFolio (L&L's and Progressive's are embedded on their own domain rather than a `*.appfolio.com` subdomain, but the same scraper handles it) and key off AppFolio's stable `/listings/detail/<uuid>` links. |
| **RNB Property Management** | ✅ Verified live — real CSS selectors (`.rnb-prop`, etc.), not guesses. Inventory currently skews Sacramento-area rather than SF/Sausalito, but kept in rotation. |
| **Brick and Timber** | ✅ Verified live against `/browse-apartments/` (real CSS selectors, not guesses). Their neighborhood tag ("Downtown", "Tenderloin", etc.) is what the downtown-SF filter matches on for this site, since it doesn't expose a zip code. |
| **Zumper - San Francisco / Zumper - Sausalito** | ✅ Verified live. A large aggregator, not a small brokerage — included at the user's request despite more anti-bot/ToS risk than the other sites. Anchors on stable URL patterns (`/apartment-buildings/...`), not CSS classes, since Zumper's class names are build-hashed and change on every deploy. Also the only site so far that shows whole-building floor-plan ranges, which `is_range` detection excludes. If it ever returns 0 listings, check `data/debug_zumper*.html` for a block/CAPTCHA page before assuming the markup changed. |
| **RentSFNow, Trinity** | ⚠️ Selectors in `config.py` are still best-guess placeholders (marked `# ADJUST ME`) from before this project had live internet access to verify against. Run the inspector and fix the CSS selectors — see below. Takes ~5 min per site. |

If any of the ⚠️ sites turn out to run on AppFolio too (worth checking
— it's common), just switch that site's `"engine"` to `"appfolio"` in
`config.py` and delete the selector lines — no new code needed.

## Setup

```bash
cd sf-rental-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Fixing the placeholder selectors

For each site still marked ⚠️ above:

```bash
python inspect_site.py "Trinity"
```

This saves the fully-rendered page to `data/debug_trinity.html`. Open
it, find the repeating block that wraps one apartment listing (view
source / inspect element in a browser works well too), and update that
site's `listing_selector`, `address_selector`, `price_selector`, and
`link_selector` in `config.py` to match. Then test just that site:

```bash
python main.py --only "Trinity"
```

Repeat for each ⚠️ site. If a site returns 0 listings even with correct
selectors, double check `url` in `config.py` is actually the page with
current vacancies (some of these sites bury it a click deep from the
homepage).

## Push notifications (free, no account)

Uses [ntfy.sh](https://ntfy.sh):
1. Install the **ntfy** app (iOS / Android).
2. Pick a random, hard-to-guess topic name, e.g. `chris-sf-rentals-9f2k`.
3. Subscribe to that topic in the app.
4. Create a `.env` file in the project root (already gitignored) with:
   ```
   NTFY_TOPIC=chris-sf-rentals-9f2k
   ```
   `main.py` loads this automatically via `python-dotenv` — no need to
   `export` it manually each run. For the GitHub Actions scheduled run,
   set `NTFY_TOPIC` as a repo secret instead (Settings → Secrets and
   variables → Actions) and pass it as an env var in the workflow file.

Anyone who knows your topic name can see your notifications, so don't
use something guessable. If you'd rather get actual SMS texts, there's
a commented-out Twilio option in `notifier.py` (requires a paid Twilio
number).

## Running it

One-off run (scrapes everything, records new listings, sends alerts):
```bash
python main.py
```

View the dashboard:
```bash
python dashboard.py
# open http://localhost:5050
```

## Running on a schedule (cron)

Edit your crontab (`crontab -e`) and add, e.g. every 30 minutes:

```
*/30 * * * * cd /path/to/sf-rental-tracker && /path/to/venv/bin/python main.py >> data/run.log 2>&1
```

The dashboard (`dashboard.py`) can just be started once and left
running (e.g. in `tmux`, or as a systemd/launchd service) — it only
reads the database, so no need to restart it on a schedule.

## How "new" is detected

`storage.py` keeps every listing ever seen per site, keyed by a stable
ID (the AppFolio listing UUID, or address+price for generic sites).
Each run:
- listings not seen before → reported as new → notification fires
- listings seen before → just timestamp updated
- listings that disappear → marked inactive (kept for history, hidden
  from the dashboard's active view)

## Project layout

```
config.py          # site list + scrape settings
storage.py          # SQLite: what's been seen, what's new
notifier.py         # ntfy.sh push notifications
scrapers/
  base.py           # Playwright rendering helper
  appfolio.py        # scraper for any AppFolio-hosted listings page
  generic.py         # configurable CSS-selector scraper for everyone else
main.py             # orchestrator — run this on a schedule
dashboard.py        # local Flask dashboard
inspect_site.py     # dumps rendered HTML for selector debugging
templates/dashboard.html
data/               # listings.db + debug HTML dumps (created on first run)
```
