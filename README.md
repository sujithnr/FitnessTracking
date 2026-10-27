# FitnessTracking — Strava shoe tracker

Python app for tracking running shoe mileage from Strava, including workout-specific defaults, `Shoe: ...` overrides, physical shoe pair cycles, and optional macOS iMessage summaries.

## Setup

Requires Python 3.10+, a Strava developer application, and callback domain `localhost`.

```bash
git clone https://github.com/sujithnr/FitnessTracking.git
cd FitnessTracking
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# shoes.json is already tracked; use the example only if it is missing:
cp -n shoes.example.json shoes.json
```

Edit `.env` with your Strava client ID and secret. Edit `shoes.json` with your defaults and shoe cycles. Sample shoe dates are illustrative rather than confirmed personal history.

```bash
python init_auth.py
python sync.py
python summary.py
```

For a full rebuild (activity history from May 11, 2026):

```bash
rm -f shoe_tracker.db
python sync.py --full
```

You can override the date with `python sync.py --since 2026-01-01`. The default sync window is the most recent 30 days, bounded below by May 11, 2026. Past data stays in SQLite but is only updated when fetched again.

For an interrupted initial import, rerun the same date range with `--resume`.
Each completed run is saved immediately, and cached runs are skipped to conserve
Strava requests. Omit `--resume` for regular syncs so edits to existing runs are
refreshed. On a Strava 429 response, the importer waits for the next 15-minute
window and retries. Daily quota exhaustion stops the import; rerun with
`--resume` after the daily quota resets. An interrupted run does not mean all
history has been imported.

Strava run descriptions override defaults when they include a line like `Shoe: Skyflow`. Shoe pair history lives in the tracked `shoes.json`; the SQLite cache is rebuildable. The committed database contains runs from May 11, 2026 onward.

Easy runs default to Black Evo SL. The older Evo SL and Skyflow are marked
`retired: true` as inventory status; historical runs can still use those pairs.
An unknown `start_date` may be null. Set `retired_date` only when its actual date
is known. Retirement status does not change workout defaults: long runs and
unclassified runs still default to Skyflow unless you edit those entries.

## iMessage (macOS only)

Set `IMESSAGE_RECIPIENT` in `.env` to the intended number or Apple ID email, then:

```bash
python send_summary.py
```

The Messages app must be configured and macOS may ask for automation permission. Optionally schedule `sync.py` and `send_summary.py` with cron or launchd. The Mac needs to be awake for scheduled tasks.

## Important

- `.env`, `tokens.json`, SQLite sidecar files, logs, and virtualenv are ignored by Git. `shoes.json` and `shoe_tracker.db` are intentionally tracked; the database contains activity names, descriptions, dates, mileage, and gear IDs visible to repository readers.
- The repository is public. **Never commit Strava tokens or your API secret.**
- Run pagination is supported; Strava rate limits may interrupt a large backfill.
- This is a clean implementation based on our conversation, not a byte-for-byte copy of the user's existing local project.
- No interval analytics are included.
