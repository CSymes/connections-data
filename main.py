"""Run the full Connections data pipeline: scrape raw data, then build JSONL files."""
from __future__ import annotations

import argparse
import sys

from build_jsonl import main as build_main
from scrape_raw_data import main as scrape_main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run scrape + build pipeline for Connections data",
    )
    parser.add_argument("--start", help="scrape start date YYYY-MM-DD")
    parser.add_argument("--end", help="scrape end date YYYY-MM-DD")
    parser.add_argument("--raw-dir", help="path to raw JSON directory for build step")
    parser.add_argument("--data-dir", help="path to output data directory for build step")
    args = parser.parse_args(argv)

    print("\n== Scrape raw data ==", flush=True)
    scrape_args: list[str] = []
    if args.start:
        scrape_args.extend(["--start", args.start])
    if args.end:
        scrape_args.extend(["--end", args.end])
    code = scrape_main(scrape_args)
    if code != 0:
        print(f"\nPipeline failed with exit code {code}", file=sys.stderr)
        return code

    print("\n== Build JSONL outputs ==", flush=True)
    build_args: list[str] = []
    if args.raw_dir:
        build_args.extend(["--raw-dir", args.raw_dir])
    if args.data_dir:
        build_args.extend(["--data-dir", args.data_dir])
    code = build_main(build_args)
    if code != 0:
        print(f"\nPipeline failed with exit code {code}", file=sys.stderr)
        return code

    print("\nPipeline complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
