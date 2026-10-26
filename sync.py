import argparse
import sqlite3
from datetime import datetime, timedelta, timezone
import requests

from auth import API, ROOT, access_token
from shoes import attribution, config

DB = ROOT / "shoe_tracker.db"


def connect():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            strava_id INTEGER PRIMARY KEY,
            start_date TEXT NOT NULL,
            start_date_local TEXT,
            distance_miles REAL NOT NULL,
            activity_name TEXT,
            workout_type TEXT,
            inferred_shoe TEXT,
            shoe_source TEXT,
            description TEXT,
            gear_id TEXT,
            shoe_cycle_id TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    return conn


def fetch(session, path, **params):
    response = session.get(API + path, params=params, timeout=45)
    response.raise_for_status()
    return response.json()


def sync(full=False, since=None):
    cfg = config()
    session = requests.Session()
    session.headers["Authorization"] = "Bearer " + access_token()
    after = (
        datetime.fromisoformat(since).replace(tzinfo=timezone.utc)
        if since else (
            datetime(2026, 5, 11, tzinfo=timezone.utc) if full
            else max(datetime.now(timezone.utc) - timedelta(days=30),
                     datetime(2026, 5, 11, tzinfo=timezone.utc))
        )
    )
    conn = connect()
    count = 0
    try:
        page = 1
        while True:
            entries = fetch(session, "/athlete/activities", after=int(after.timestamp()),
                            per_page=100, page=page)
            if not entries:
                break
            for item in entries:
                if item.get("type") != "Run" and item.get("sport_type") not in ("Run", "TrailRun", "VirtualRun"):
                    continue
                activity = fetch(session, "/activities/" + str(item["id"]))
                workout, shoe, source, cycle = attribution(activity, cfg)
                conn.execute("""
                    INSERT INTO activities
                    (strava_id, start_date, start_date_local, distance_miles,
                     activity_name, workout_type, inferred_shoe, shoe_source,
                     description, gear_id, shoe_cycle_id, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(strava_id) DO UPDATE SET
                        start_date=excluded.start_date,
                        start_date_local=excluded.start_date_local,
                        distance_miles=excluded.distance_miles,
                        activity_name=excluded.activity_name,
                        workout_type=excluded.workout_type,
                        inferred_shoe=excluded.inferred_shoe,
                        shoe_source=excluded.shoe_source,
                        description=excluded.description,
                        gear_id=excluded.gear_id,
                        shoe_cycle_id=excluded.shoe_cycle_id,
                        updated_at=excluded.updated_at
                """, (
                    activity["id"], activity["start_date"],
                    activity.get("start_date_local"), activity.get("distance", 0) / 1609.344,
                    activity.get("name"), workout, shoe, source,
                    activity.get("description"), activity.get("gear_id"), cycle,
                    datetime.now(timezone.utc).isoformat()
                ))
                count += 1
            conn.commit()
            if len(entries) < 100:
                break
            page += 1
    finally:
        conn.close()
        session.close()
    print(f"Synced {count} runs from {after.date()} onward")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Resync all runs since May 11, 2026")
    parser.add_argument("--since", help="Earliest UTC day, YYYY-MM-DD")
    args = parser.parse_args()
    sync(full=args.full, since=args.since)
