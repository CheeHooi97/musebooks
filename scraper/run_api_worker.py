"""Lease MuseBooks jobs and execute them with the browser-only photobook worker.

This process talks to the MuseBooks control-plane API, never to a marketplace
API. Each claimed job is handed to ``photobook_worker.py`` as JSON over stdin;
that child process performs all marketplace reads with CloakBrowser.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

from musebooks_api import MuseBooksAPIError, MuseBooksScrapeAPI


WORKER_PATH = Path(__file__).with_name("photobook_worker.py")


def log(message: str) -> None:
    print(f"[musebooks-python-worker] {message}", file=sys.stderr, flush=True)


def invoke_browser_worker(request: dict, timeout_seconds: int, heartbeat) -> tuple[dict, str]:
    process = subprocess.Popen(
        [sys.executable, str(WORKER_PATH)],
        cwd=str(WORKER_PATH.parent),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    payload = json.dumps(request, ensure_ascii=False)
    result: dict[str, str] = {}
    error: list[BaseException] = []

    def wait_for_process() -> None:
        try:
            stdout, stderr = process.communicate(input=payload)
            result["stdout"] = stdout
            result["stderr"] = stderr
        except BaseException as exc:  # propagate the child/pipe failure to the caller
            error.append(exc)

    waiter = threading.Thread(target=wait_for_process, daemon=True)
    waiter.start()
    deadline = time.monotonic() + timeout_seconds
    next_heartbeat = time.monotonic() + 45
    while waiter.is_alive():
        if time.monotonic() >= deadline:
            if process.poll() is None:
                process.kill()
            waiter.join(timeout=5)
            raise TimeoutError(f"browser worker exceeded {timeout_seconds}s")
        if time.monotonic() >= next_heartbeat:
            try:
                heartbeat()
            except MuseBooksAPIError as exc:
                # Keep the child isolated and let the lease expiry/retry path
                # decide ownership if the control plane is temporarily down.
                log(f"heartbeat failed: {exc}")
            next_heartbeat = time.monotonic() + 45
        time.sleep(0.25)
    if error:
        raise RuntimeError(str(error[0])) from error[0]
    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")
    if stderr.strip():
        log(stderr.strip()[-8_000:])
    if process.returncode != 0:
        blocked_line = next(
            (line.strip() for line in stderr.splitlines() if line.strip().startswith("BLOCKED_SOURCE:")),
            "",
        )
        if blocked_line:
            raise RuntimeError(blocked_line)
        detail = stderr.strip().splitlines()[-1].strip() if stderr.strip() else ""
        suffix = f": {detail[:1_000]}" if detail else ""
        raise RuntimeError(f"photobook worker exited with code {process.returncode}{suffix}")
    try:
        batch = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("photobook worker returned invalid JSON") from exc
    if not isinstance(batch, dict):
        raise RuntimeError("photobook worker returned a non-object batch")
    return batch, stderr


def should_requeue(job: dict) -> bool:
    try:
        return int(job.get("attemptCount", 0)) < int(job.get("maxAttempts", 0))
    except (TypeError, ValueError):
        return True


def process_claim(api: MuseBooksScrapeAPI, claimed: dict, timeout_seconds: int) -> None:
    job = claimed.get("job") or {}
    source = claimed.get("source") or {}
    job_id = str(job.get("id") or "")
    if not job_id:
        raise RuntimeError("claim response did not include a job id")
    request = dict(job.get("request") or {})
    request.update(
        {
            "jobId": job_id,
            "workerId": api.worker_id,
            "leaseToken": job.get("leaseToken") or "",
            "sourceId": job.get("sourceId") or source.get("id") or "",
            "operation": job.get("operation") or request.get("operation") or "catalog_discovery",
            "source": source,
            "pageCursor": job.get("pageCursor") or request.get("pageCursor") or "",
        }
    )
    log(f"claimed job={job_id} source={request['sourceId']} adapter={source.get('adapter', '')}")
    try:
        batch, _ = invoke_browser_worker(
            request,
            timeout_seconds,
            lambda: api.heartbeat(job_id),
        )
        batch.setdefault("jobId", job_id)
        batch.setdefault("workerId", api.worker_id)
        batch.setdefault("leaseToken", job.get("leaseToken") or "")
        batch.setdefault("sourceId", request["sourceId"])
        ingest = api.ingest_batch(batch)
        items = batch.get("items") or []
        accepted = int(ingest.get("created", 0)) + int(ingest.get("updated", 0))
        rejected = int(ingest.get("rejected", 0))
        api.complete(
            job_id,
            "succeeded",
            next_cursor=str(batch.get("nextCursor") or ""),
            requeue=bool(batch.get("hasMore")),
            items_received=len(items),
            items_accepted=accepted,
            items_rejected=rejected,
            warnings=[str(item) for item in (batch.get("warnings") or [])],
        )
        if batch.get("hasMore"):
            log(
                f"completed page for job={job_id}; queued cursor={batch.get('nextCursor', '')} "
                f"received={len(items)} accepted={accepted} rejected={rejected}"
            )
        else:
            log(f"completed job={job_id} received={len(items)} accepted={accepted} rejected={rejected}")
    except Exception as exc:
        message = str(exc)[:2_000]
        log(f"job={job_id} failed: {message}")
        try:
            api.complete(
                job_id,
                "blocked" if message.startswith("BLOCKED_SOURCE:") else "failed",
                requeue=False if message.startswith("BLOCKED_SOURCE:") else should_requeue(job),
                error=message,
            )
        except MuseBooksAPIError as complete_error:
            log(f"could not record failure for job={job_id}: {complete_error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run browser-only MuseBooks photobook jobs")
    parser.add_argument("--api-url", default=os.environ.get("MUSEBOOKS_API_URL", "http://localhost:2001"))
    parser.add_argument("--token", default=os.environ.get("SCRAPER_INGEST_TOKEN", ""))
    parser.add_argument("--worker-id", default=os.environ.get("MUSEBOOKS_WORKER_ID", "python-worker"))
    parser.add_argument("--source-id", action="append", dest="source_ids", help="restrict claims; repeat for multiple sources")
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--timeout-seconds", type=int, default=240)
    parser.add_argument("--once", action="store_true", help="claim at most one job, then exit")
    args = parser.parse_args()
    api = MuseBooksScrapeAPI(
        base_url=args.api_url,
        token=args.token,
        worker_id=args.worker_id,
        timeout=30.0,
    )
    while True:
        try:
            claimed = api.claim_job(source_ids=args.source_ids)
        except MuseBooksAPIError as exc:
            log(f"claim failed: {exc}")
            if args.once:
                raise SystemExit(1)
            time.sleep(max(1.0, args.poll_seconds))
            continue
        if not claimed:
            if args.once:
                return
            time.sleep(max(0.5, args.poll_seconds))
            continue
        process_claim(api, claimed, max(30, args.timeout_seconds))
        if args.once:
            return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("stopped")
