"""Scrape NYT Connections puzzles into .raw_json/YYYY-MM-DD.json."""
from __future__ import annotations

import argparse
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

DEFAULT_START_DATE = date(2023, 6, 12)
DEFAULT_END_DATE = date.today()
URL_TEMPLATE = "https://www.nytimes.com/svc/connections/v2/{}.json"
DEFAULT_OUT_DIR = Path(__file__).parent / ".raw_json"
RATE_LIMIT_PER_SEC = 5
MAX_WORKERS = 5
USER_AGENT = "connections-data-scraper (github.com/CSymes/connections-data)"


class RateLimiter:
    """Simple thread-safe rate limiter: at most `rate` calls per second."""

    def __init__(self, rate: float):
        self._interval = 1.0 / rate
        self._lock = threading.Lock()
        self._next_time = 0.0

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self._next_time - now
            if wait > 0:
                time.sleep(wait)
                now += wait
            self._next_time = max(self._next_time, now) + self._interval


def daterange(start: date, end: date):
    days = (end - start).days
    for i in range(days + 1):
        yield start + timedelta(days=i)


def fetch_and_save(
    session: requests.Session,
    limiter: RateLimiter,
    d: date,
    out_path: Path,
) -> tuple[date, str]:
    limiter.acquire()
    url = URL_TEMPLATE.format(d.isoformat())
    try:
        resp = session.get(url, timeout=30)
        if resp.status_code == 200:
            out_path.write_bytes(resp.content)
            return d, "ok"
        return d, f"http {resp.status_code}"
    except requests.RequestException as e:
        return d, f"error: {e}"


def parse_date(s: str) -> date:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"invalid date {s!r}, expected YYYY-MM-DD") from e


def scrape_raw_data(start: date, end: date, out_dir: Path = DEFAULT_OUT_DIR) -> int:
    if start > end:
        raise ValueError(f"start ({start}) must be <= end ({end})")

    out_dir.mkdir(exist_ok=True)
    all_dates = list(daterange(start, end))
    total = len(all_dates)

    todo: list[tuple[date, Path]] = []
    skipped = 0
    for d in all_dates:
        out_path = out_dir / f"{d.isoformat()}.json"
        if out_path.exists():
            skipped += 1
        else:
            todo.append((d, out_path))

    print(f"{total} dates: {skipped} cached, {len(todo)} to fetch")
    if not todo:
        return 0

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    limiter = RateLimiter(RATE_LIMIT_PER_SEC)

    fetched = failed = 0
    start_time = time.monotonic()
    interrupted = False

    pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    try:
        futures = [
            pool.submit(fetch_and_save, session, limiter, d, p) for d, p in todo
        ]
        try:
            for i, fut in enumerate(as_completed(futures), 1):
                d, status = fut.result()
                if status == "ok":
                    fetched += 1
                else:
                    failed += 1
                    print(f"  {d}: {status}", file=sys.stderr)
                if i % 25 == 0 or i == len(futures):
                    elapsed = time.monotonic() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    print(f"[{i}/{len(futures)}] {rate:.1f} req/s")
        except KeyboardInterrupt:
            interrupted = True
            print("\nInterrupted, cancelling pending requests...", file=sys.stderr)
            for f in futures:
                f.cancel()
    finally:
        pool.shutdown(wait=True, cancel_futures=True)

    print(
        f"\nDone. fetched={fetched} skipped={skipped} failed={failed}"
        + (" (interrupted)" if interrupted else "")
    )
    return 130 if interrupted else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scrape NYT Connections puzzles.")
    parser.add_argument(
        "--start",
        type=parse_date,
        default=DEFAULT_START_DATE,
        help=f"start date YYYY-MM-DD (default: {DEFAULT_START_DATE})",
    )
    parser.add_argument(
        "--end",
        type=parse_date,
        default=DEFAULT_END_DATE,
        help=f"end date YYYY-MM-DD inclusive (default: today)",
    )
    args = parser.parse_args(argv)

    if args.start > args.end:
        parser.error(f"start ({args.start}) must be <= end ({args.end})")

    return scrape_raw_data(args.start, args.end, DEFAULT_OUT_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
