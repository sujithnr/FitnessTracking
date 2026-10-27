"""Export a minimal, public dashboard dataset without credentials or descriptions."""
import argparse
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
ZONE = ZoneInfo('America/Los_Angeles')


def build(db, shoes, now=None):
    now = now or datetime.now(timezone.utc)
    today = now.astimezone(ZONE).date()
    cfg = json.loads(Path(shoes).read_text())
    with sqlite3.connect(f'{Path(db).resolve().as_uri()}?mode=ro', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute('SELECT start_date, distance_miles, inferred_shoe, shoe_cycle_id, updated_at FROM activities ORDER BY start_date DESC')]
    cycle_totals = defaultdict(float)
    unassigned = defaultdict(float)
    daily = defaultdict(float)
    recent = []
    dates = []
    for row in rows:
        stamp = datetime.fromisoformat(row['start_date'].replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        date = stamp.astimezone(ZONE).date().isoformat()
        dates.append(date)
        miles = row['distance_miles']
        daily[date] += miles
        if row['shoe_cycle_id']:
            cycle_totals[row['shoe_cycle_id']] += miles
        else:
            unassigned[row['inferred_shoe'] or 'Unknown'] += miles
        if len(recent) < 12:
            recent.append({'date': date, 'miles': round(miles, 2), 'shoe': row['inferred_shoe'] or 'Unknown', 'assigned': bool(row['shoe_cycle_id'])})
    cycles = []
    for cycle in cfg['cycles']:
        retired = bool(cycle.get('retired') or (cycle.get('retired_date') and cycle['retired_date'] <= today.isoformat()))
        cycles.append({'id': cycle['id'], 'name': cycle['shoe_name'], 'label': cycle.get('label', cycle['shoe_name']), 'miles': round(cycle_totals[cycle['id']], 2), 'retired': retired, 'started': cycle.get('start_date'), 'retired_date': cycle.get('retired_date')})
    # Include previous weeks, using actual Pacific calendar dates across DST.
    days = []
    for offset in range(27, -1, -1):
        date = (today - timedelta(days=offset)).isoformat()
        days.append({'date': date, 'miles': round(daily[date], 2)})
    monday = today - timedelta(days=today.weekday())
    return {'generated_at': now.isoformat(), 'last_synced': max((r['updated_at'] for r in rows if r['updated_at']), default=None), 'timezone': str(ZONE), 'since': min(dates, default=None), 'run_count': len(rows), 'total_miles': round(sum(r['distance_miles'] for r in rows), 2), 'week_miles': round(sum(value for date, value in daily.items() if monday.isoformat() <= date <= today.isoformat()), 2), 'cycles': cycles, 'unassigned': [{'name': name, 'miles': round(miles, 2)} for name, miles in sorted(unassigned.items())], 'days': days, 'recent': recent}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=Path, default=ROOT / 'shoe_tracker.db')
    parser.add_argument('--shoes', type=Path, default=ROOT / 'shoes.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/data.json')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(args.db, args.shoes), indent=2) + '\n')
    print(f'Dashboard data written to {args.output}')
