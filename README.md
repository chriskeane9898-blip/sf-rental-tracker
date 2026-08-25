# SF Rental Tracker

Scrapes 6 SF property-management sites, keeps track of what's new in a
local SQLite database, pushes a phone notification for each new
listing, and shows everything currently available in a small local
dashboard.

**Sites configured:** Mosser Companies, Anchor Realty, Chandler
Properties, RentSFNow, Trinity, Brick and Timber (`config.py`).

## Honest status of each scraper

I built and verified this structurally, but I could not run any of
these scrapers against the live sites from where I built this (no
general internet access in that environment) — so treat this as a
strong first draft, not finished:

| Site | Status |
|---|---|
| **Chandler Properties** | ✅ Verified against real page content — uses AppFolio, and the scraper keys off AppFolio's stable `/listings/detail/<uuid>` links, so it should work as-is. |
| **Mosser, Anchor Realty, RentSFNow, Trinity, Brick and Timber** | ⚠️ Selectors in `config.py` are best-guess placeholders (marked `# ADJUST ME`). You'll need to run the inspector once per site and fix the CSS selectors — see below. Takes ~5 min per site. |

If any of these turn out to run on AppFolio too (worth checking — it's
very common), just switch that site's `"engine"` to `"appfolio"` in
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
4. Set it as an environment variable before running:
   ```bash
   export NTFY_TOPIC="chris-sf-rentals-9f2k"
   ```
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
