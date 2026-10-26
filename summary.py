import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from auth import ROOT
from sync import connect


def build_summary():
    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    next_monday = monday + timedelta(days=7)
    begin = monday.astimezone(timezone.utc).isoformat()
    end = next_monday.astimezone(timezone.utc).isoformat()
    conn = connect()
    try:
        rows = conn.execute("""
            SELECT start_date, distance_miles, COALESCE(inferred_shoe, 'Unknown'),
                   COALESCE(shoe_cycle_id, 'unassigned')
            FROM activities
        """).fetchall()
    finally:
        conn.close()
    weekly = defaultdict(float)
    totals = defaultdict(float)
    for start, miles, shoe, cycle in rows:
        key = f"{shoe} ({cycle})"
        totals[key] += miles
        stamp = datetime.fromisoformat(start.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        if begin <= stamp.isoformat() < end:
            weekly[key] += miles
    lines = [f"Running shoe report — week of {monday:%b %d, %Y}",
             f"Weekly total: {sum(weekly.values()):.1f} mi", "",
             "This week:"]
    lines += [f"  {key}: {miles:.1f} mi" for key, miles in sorted(weekly.items())] or ["  No runs yet"]
    lines += ["", "Lifetime totals:"]
    lines += [f"  {key}: {miles:.1f} mi" for key, miles in sorted(totals.items())] or ["  No runs yet"]
    return "\n".join(lines)


if __name__ == "__main__":
    print(build_summary())
