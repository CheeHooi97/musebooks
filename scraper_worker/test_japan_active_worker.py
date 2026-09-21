import unittest
from datetime import datetime, timedelta, timezone

import japan_active_worker


class JapanActiveWorkerValidationTests(unittest.TestCase):
    def japan_day_request(self, now=None, **overrides):
        now = now or datetime.now(japan_active_worker.JAPAN_TIMEZONE)
        now = now.astimezone(japan_active_worker.JAPAN_TIMEZONE)
        start_local = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_utc = start_local.astimezone(timezone.utc)
        end_utc = (start_local + timedelta(days=1)).astimezone(timezone.utc) - timedelta(
            microseconds=1
        )
        request = {
            "platform": "yahoo-auctions-jp",
            "mode": "active",
            "importNewOnly": True,
            "from": start_utc.isoformat().replace("+00:00", "Z"),
            "to": end_utc.isoformat().replace("+00:00", "Z"),
        }
        request.update(overrides)
        return request

    def current_day_request(self, **overrides):
        return self.japan_day_request(**overrides)

    def test_accepts_current_day_yahoo_japan_active_request(self):
        japan_active_worker._validate_request(self.current_day_request())

    def test_rejects_other_japan_marketplaces(self):
        with self.assertRaisesRegex(ValueError, "only supports Yahoo Auctions Japan"):
            japan_active_worker._validate_request(
                self.current_day_request(platform="mercari-jp")
            )

    def test_rejects_non_active_work(self):
        with self.assertRaisesRegex(ValueError, "only supports active mode"):
            japan_active_worker._validate_request(self.current_day_request(mode="sold"))

    def test_rejects_missing_current_day_bounds(self):
        with self.assertRaisesRegex(ValueError, "requires importNewOnly"):
            japan_active_worker._validate_request(
                self.current_day_request(
                    **{"from": None, "to": None, "importNewOnly": False}
                )
            )

    def test_rejects_partial_day_bounds(self):
        request = self.current_day_request()
        request["from"] = (
            japan_active_worker._parse_utc_bound(request["from"])
            + timedelta(hours=1)
        ).isoformat()
        with self.assertRaisesRegex(ValueError, "one full Japan calendar day"):
            japan_active_worker._validate_request(request)

    def test_refreshes_queued_previous_day_request_after_japan_midnight(self):
        worker_start = datetime(
            2026, 8, 31, 0, 0, 5, tzinfo=japan_active_worker.JAPAN_TIMEZONE
        )
        request = self.japan_day_request(worker_start - timedelta(days=1))

        japan_active_worker._validate_request(request)
        japan_active_worker._apply_current_japan_day_bounds(request, worker_start)

        self.assertEqual(
            japan_active_worker._parse_utc_bound(request["from"]),
            datetime(2026, 8, 30, 15, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            japan_active_worker._parse_utc_bound(request["to"]),
            datetime(2026, 8, 31, 14, 59, 59, 999999, tzinfo=timezone.utc),
        )


if __name__ == "__main__":
    unittest.main()
