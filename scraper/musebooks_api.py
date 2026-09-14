"""Small standard-library client for the MuseBooks scrape control plane.

Regional workers keep marketplace logic in their adapters. This module only
handles job leasing, heartbeats, idempotent batch submission, and completion.
It intentionally has no marketplace-specific dependencies.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class MuseBooksAPIError(RuntimeError):
    """Raised when the scrape API rejects a worker request."""


class MuseBooksScrapeAPI:
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        worker_id: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (base_url or os.environ.get("MUSEBOOKS_API_URL", "http://localhost:2001")).rstrip("/")
        self.token = token if token is not None else os.environ.get("SCRAPER_INGEST_TOKEN", "")
        self.worker_id = worker_id or os.environ.get("MUSEBOOKS_WORKER_ID", "python-worker")
        self.timeout = timeout
        self._lease_tokens: dict[str, str] = {}

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any] | None:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["X-Scraper-Token"] = self.token
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=body, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                if response.status == 204:
                    return None
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise MuseBooksAPIError(f"{method} {path} returned {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise MuseBooksAPIError(f"{method} {path} failed: {exc.reason}") from exc
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MuseBooksAPIError(f"{method} {path} returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise MuseBooksAPIError(f"{method} {path} returned a non-object response")
        return value

    def create_job(self, source_id: str, operation: str, request: dict[str, Any], **extra: Any) -> dict[str, Any]:
        payload = {"sourceId": source_id, "operation": operation, "request": request, **extra}
        result = self._request("POST", "/v1/internal/scrape/jobs", payload)
        assert result is not None
        return result

    def claim_job(self, source_ids: list[str] | None = None, lease_seconds: int = 300) -> dict[str, Any] | None:
        payload: dict[str, Any] = {"workerId": self.worker_id, "leaseSeconds": lease_seconds}
        if source_ids:
            payload["sourceIds"] = source_ids
        result = self._request("POST", "/v1/internal/scrape/jobs/claim", payload)
        if result:
            job = result.get("job", {})
            job_id = job.get("id")
            lease_token = job.get("leaseToken")
            if job_id and lease_token:
                self._lease_tokens[job_id] = lease_token
        return result

    def heartbeat(self, job_id: str, lease_seconds: int = 300) -> dict[str, Any]:
        result = self._request(
            "POST",
            f"/v1/internal/scrape/jobs/{job_id}/heartbeat",
            {
                "workerId": self.worker_id,
                "leaseToken": self._lease_tokens.get(job_id, ""),
                "leaseSeconds": lease_seconds,
            },
        )
        assert result is not None
        return result

    def ingest_batch(self, batch: dict[str, Any]) -> dict[str, Any]:
        payload = dict(batch)
        payload.setdefault("workerId", self.worker_id)
        job_id = str(payload.get("jobId", ""))
        payload.setdefault("leaseToken", self._lease_tokens.get(job_id, ""))
        result = self._request("POST", "/v1/internal/scrape/batches", payload)
        assert result is not None
        return result

    def complete(
        self,
        job_id: str,
        status: str,
        *,
        next_cursor: str = "",
        requeue: bool = False,
        items_received: int = 0,
        items_accepted: int = 0,
        items_rejected: int = 0,
        warnings: list[str] | None = None,
        error: str = "",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "workerId": self.worker_id,
            "leaseToken": self._lease_tokens.get(job_id, ""),
            "status": status,
            "nextCursor": next_cursor,
            "requeue": requeue,
            "itemsReceived": items_received,
            "itemsAccepted": items_accepted,
            "itemsRejected": items_rejected,
        }
        if warnings:
            payload["warnings"] = warnings
        if error:
            payload["error"] = error
        result = self._request("POST", f"/v1/internal/scrape/jobs/{job_id}/complete", payload)
        assert result is not None
        # Completion clears the lease in the Go API even when the same job is
        # requeued for its next page. Claiming the next page receives a fresh
        # token; retaining the old token would make a transient retry look like
        # a lease-ownership conflict.
        self._lease_tokens.pop(job_id, None)
        return result
