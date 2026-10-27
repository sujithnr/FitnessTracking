import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from build_dashboard import build


class DashboardExportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'history.db'
        self.shoes = Path(self.temp.name) / 'shoes.json'
        self.shoes.write_text(json.dumps({'cycles': [
            {'id': 'pair', 'shoe_name': 'Shoe', 'retired_date': '2026-10-01'}
        ]}))
        with sqlite3.connect(self.db) as conn:
            conn.execute('CREATE TABLE activities(start_date TEXT, distance_miles REAL, inferred_shoe TEXT, shoe_cycle_id TEXT, updated_at TEXT)')

    def test_empty_history(self):
        data = build(self.db, self.shoes)
        self.assertEqual(data['run_count'], 0)
        self.assertIsNone(data['last_synced'])
        self.assertEqual(data['cycles'][0]['miles'], 0)
        self.assertEqual(data['recent'], [])
        self.assertEqual(len(data['days']), 28)

    def test_totals_pair_status_and_pacific_dst_boundary(self):
        with sqlite3.connect(self.db) as conn:
            conn.executemany('INSERT INTO activities VALUES(?,?,?,?,?)', [
                ('2026-11-01T06:59:59Z', 2, 'Shoe', 'pair', '2026-11-02T08:00:00Z'),
                ('2026-11-01T07:00:00Z', 3, 'Other', None, '2026-11-02T08:00:00Z'),
            ])
        data = build(self.db, self.shoes, datetime(2026, 11, 2, 8, tzinfo=timezone.utc))
        self.assertEqual(data['total_miles'], 5)
        self.assertEqual(data['cycles'][0]['miles'], 2)
        self.assertTrue(data['cycles'][0]['retired'])
        self.assertEqual(data['unassigned'], [{'name': 'Other', 'miles': 3}])
        self.assertEqual(data['days'][-2], {'date': '2026-11-01', 'miles': 3})
        self.assertEqual(data['days'][-3], {'date': '2026-10-31', 'miles': 2})
        self.assertEqual(data['week_miles'], 0)
        self.assertEqual(set(data['recent'][0]), {'date', 'miles', 'shoe', 'assigned'})
        self.assertEqual(data['last_synced'], '2026-11-02T08:00:00Z')

    def test_missing_database_is_not_created(self):
        missing = Path(self.temp.name) / 'missing.db'
        with self.assertRaises(sqlite3.OperationalError):
            build(missing, self.shoes)
        self.assertFalse(missing.exists())


if __name__ == '__main__':
    unittest.main()
