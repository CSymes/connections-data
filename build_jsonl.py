"""Normalise raw Connections JSON into minified JSONL outputs.

Reads puzzles from .raw_json/*.json and writes:
- data/all_puzzles.jsonl
- data/<year>.jsonl
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_RAW_DIR = Path(__file__).parent / ".raw_json"
DEFAULT_DATA_DIR = Path(__file__).parent / "data"


def normalise_card(card: dict[str, Any]) -> dict[str, Any]:
    position = int(card["position"])
    normalised: dict[str, Any] = {
        "content": card.get("content", ""),
        "x": position % 4,
        "y": position // 4,
    }

    if "image_alt_text" in card:
        normalised["content"] = card["image_alt_text"]
        normalised["type"] = "image"

    return normalised


def normalise_puzzle(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "date": raw["print_date"],
        "categories": [
            {
                "title": category["title"],
                "cards": [normalise_card(card) for card in category.get("cards", [])],
            }
            for category in raw.get("categories", [])
        ],
    }


def read_puzzles(raw_dir: Path) -> list[dict[str, Any]]:
    puzzles: list[dict[str, Any]] = []
    for path in sorted(raw_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        puzzles.append(normalise_puzzle(raw))
    return puzzles


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [json.dumps(row, separators=(",", ":"), ensure_ascii=False) for row in rows]
    content = "\n".join(lines)
    if lines:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def build_jsonl(raw_dir: Path = DEFAULT_RAW_DIR, data_dir: Path = DEFAULT_DATA_DIR) -> tuple[int, int]:
    if not raw_dir.exists():
        raise FileNotFoundError(f"raw dir not found: {raw_dir}")

    data_dir.mkdir(parents=True, exist_ok=True)

    puzzles = read_puzzles(raw_dir)
    write_jsonl(data_dir / "all_puzzles.jsonl", puzzles)

    by_year: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for puzzle in puzzles:
        year = puzzle["date"][:4]
        by_year[year].append(puzzle)

    for year, rows in sorted(by_year.items()):
        write_jsonl(data_dir / f"{year}.jsonl", rows)

    return len(puzzles), len(by_year)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build normalised Connections JSONL files")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    args = parser.parse_args(argv)

    puzzle_count, year_count = build_jsonl(args.raw_dir, args.data_dir)

    print(f"Wrote {puzzle_count} puzzles to {args.data_dir / 'all_puzzles.jsonl'}")
    print(f"Wrote {year_count} yearly files to {args.data_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
