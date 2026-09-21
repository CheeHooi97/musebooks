"""Yahoo Auctions Japan active-listing worker entrypoint.

The Go adapter routes only Yahoo Auctions Japan ``mode=active`` requests here.
Keep that contract enforced at the process boundary as well, so a bad worker
mapping cannot send another marketplace, sold work, or detail reconciliation
through this lane.
"""

from __future__ import annotations

import io
import json
import sys
from datetime import datetime, timedelta, timezone

from worker import main as worker_main


JAPAN_ACTIVE_PLATFORMS = frozenset({"yahoo-auctions-jp"})
JAPAN_TIMEZONE = timezone(timedelta(hours=9))


def _parse_utc_bound(value: object) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _current_japan_day_bounds(now: datetime | None = None) -> tuple[datetime, datetime]:
    local_now = (now or datetime.now(JAPAN_TIMEZONE)).astimezone(JAPAN_TIMEZONE)
    start_local = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = (start_local + timedelta(days=1)).astimezone(
        timezone.utc
    ) - timedelta(microseconds=1)
    return start_utc, end_utc


def _apply_current_japan_day_bounds(
    request: dict[str, object], now: datetime | None = None
) -> None:
    """Refresh bounds after a queued request acquires its browser worker.

    A request can be created just before Japan midnight and start just after it,
    especially while waiting for the single Japan browser slot. The worker is
    the last process that can define "today" without that race, so it replaces
    the already-validated full-day bounds immediately before scraping.
    """
    start_utc, end_utc = _current_japan_day_bounds(now)
    request["from"] = start_utc.isoformat().replace("+00:00", "Z")
    request["to"] = end_utc.isoformat().replace("+00:00", "Z")


def _validate_request(request: dict[str, object]) -> None:
    platform = str(request.get("platform") or "").strip().lower()
    if platform not in JAPAN_ACTIVE_PLATFORMS:
        raise ValueError(
            "japan_active_worker only supports Yahoo Auctions Japan; "
            f"got {platform or '<missing>'}"
        )
    mode = str(request.get("mode") or "").strip().lower()
    if mode != "active":
        raise ValueError("japan_active_worker only supports active mode")
    if (
        not request.get("importNewOnly")
        or not request.get("from")
        or not request.get("to")
    ):
        raise ValueError(
            "japan_active_worker requires importNewOnly with current-day from/to bounds"
        )

    from_bound = _parse_utc_bound(request["from"])
    to_bound = _parse_utc_bound(request["to"])
    start_local = from_bound.astimezone(JAPAN_TIMEZONE)
    is_japan_midnight = (
        start_local.hour == 0
        and start_local.minute == 0
        and start_local.second == 0
        and start_local.microsecond == 0
    )
    next_start_utc = (start_local + timedelta(days=1)).astimezone(timezone.utc)
    if not is_japan_midnight or not (
        next_start_utc - timedelta(microseconds=1) <= to_bound < next_start_utc
    ):
        raise ValueError("japan_active_worker requires bounds for one full Japan calendar day")


def main() -> None:
    request = json.load(sys.stdin)
    if not isinstance(request, dict):
        raise ValueError("japan_active_worker expects a JSON object request")
    _validate_request(request)
    _apply_current_japan_day_bounds(request)
    sys.stdin = io.StringIO(json.dumps(request))
    worker_main()


if __name__ == "__main__":
    main()
