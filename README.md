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
cp shoes.example.json shoes.json
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

Strava run descriptions override defaults when they include a line like `Shoe: Skyflow`. Shoe pair history lives in `shoes.json`; the SQLite cache is rebuildable. Keep a private backup of `shoes.json` to preserve shoe cycles.

## iMessage (macOS only)

Set `IMESSAGE_RECIPIENT` in `.env` to the intended number or Apple ID email, then:

```bash
python send_summary.py
```

The Messages app must be configured and macOS may ask for automation permission. Optionally schedule `sync.py` and `send_summary.py` with cron or launchd. The Mac needs to be awake for scheduled tasks.

## Important

- `.env`, `tokens.json`, `shoes.json`, SQLite files, logs, and virtualenv are ignored by Git.
- The repository is public. **Never commit Strava tokens or your API secret.**
- Run pagination is supported; Strava rate limits may interrupt a large backfill.
- This is a clean implementation based on our conversation, not a byte-for-byte copy of the user's existing local project.
- No interval analytics are included.
