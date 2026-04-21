# Connections Data Dump

This project fetches NYT Connections puzzle data and generates basic normalised JSONL files for downstream use by my [heatmaps](https://github.com/CSymes/connections-heatmaps) visualiser.

This is specifically formatted for my needs, and may include or omit fields useful for other purposes.

## What this application does

The pipeline has two stages:

1. Scrape raw puzzle JSONs from the NYT Connections API by date
2. Build normalised JSONL outputs from the raw files

A separate script exists for each step, but `main.py` runs both stages in sequence.

## How to run it

### Prerequisites

- Python 3 (I used 3.14)
- Dependencies from `requirements.txt`

```bash
python -m pip install -r requirements.txt
```

### Run full dump/format

```bash
python main.py
```

Flags for `main.py`:

- `--start YYYY-MM-DD`: scrape start date (inclusive). Defaults to the first date Connections ran (2023-06-12)
- `--end YYYY-MM-DD`: scrape end date (inclusive). Defaults to today (even though several days' worth of puzzles are technically available ahead of time, we do not grab these in case of changes. Also because I didn't want spoilers.)
- `--raw-dir PATH`: raw JSON directory used by the build step
- `--data-dir PATH`: output directory for generated JSONL files

Example:

```bash
python main.py --start 2024-01-01 --end 2024-12-31
```

### Run stages independently

Scrape only:

```bash
python scrape_raw_data.py --start 2023-06-12 --end 2026-04-09
```

Build JSONL only:

```bash
python build_jsonl.py --raw-dir .raw_json --data-dir data
```

## How data is stored

### Raw source data

`scrape_raw_data.py` grabs the raw API response for all targetted puzzle dates and dumps the raw response into `.raw_json/<yyyy-mm-dd>json`

It skips pre-existing dates as they have already been fetched, and are not going to be retroactively updated once published.

### Processed data

`build_jsonl.py` then takse the raw source data and converts it into a handful of JSONL files (i.e. one line per day).  
- `data/all_puzzles.jsonl` (contains all puzzles)
- `data/<year>.jsonl` (yearly split, e.g. `data/2026.jsonl`)

Each normalised puzzle row contains:

- `date`
- `categories[]`
  - `title`
  - `cards[]`
    - `content`
    - `x`, `y` (grid coordinates derived from card position)
    - `type: "image"` iff source card is image-based, absent otherwise


## Missing Puzzles

There are at least 79 puzzles that are 'missing', based on the detectable dataset presented here.

These are:
 - 207
 - 211
 - 232
 - 237
 - 246
 - 306
 - 315
 - 322
 - 331
 - 336–339
 - 342–346
 - 351
 - 384–385
 - 424
 - 454
 - 463–466
 - 490
 - 597
 - 622
 - 637
 - 657
 - 721–724
 - 729
 - 732
 - 798
 - 931–932
 - 940
 - 955
 - 963
 - 978–987
 - 1013
 - 1041–1063
 - 1091

Presumably these are some sort of secret puzzles not accessed via a specific date, or drafts that never made it to publication.

Some puzzles (e.g. IDs 1027-1029, 1090) were created significantly out of order compared to their publication date. This happens frequently enough (about one third of puzzles are 'out of order') not to comment, other than that some of them were clearly scheduled for a specific day, or planned ahead. E.G. #1027 doesn't seem date-related, but does include a meta-reference to Connections itself.


## Replicated Groups

Several groups have been recycled, either verbatim, or in majority. Below are the 20 groups that have been reused word-for-word, but there are 75 groups have a 3+/4 word match, and in total **264** group titles that have been reused (with any number of reused constituent words).

 - ADVOCATE FOR — 2024-05-25, 2024-07-26  
 (BACK, CHAMPION, ENDORSE, SUPPORT)
 - BREADTH — 2024-04-09, 2024-08-15  
 (EXTENT, RANGE, REACH, SCOPE)
 - DECLINE — 2023-09-23, 2024-01-20  
 (DIP, DROP, FALL, SINK)
 - HOMOPHONES — 2023-09-03, 2024-12-23  
 (EWE, U, YEW, YOU)
 - ICE CREAM TREATS — 2023-12-09, 2025-06-29  
 (FLOAT, SHAKE, SPLIT, SUNDAE)
 - IMPOSE, AS A PENALTY — 2024-01-25, 2025-03-14  
 (ASSESS, CHARGE, FINE, LEVY)
 - INFLUENCE — 2023-08-30, 2024-05-30  
 (CLOUT, PULL, SWAY, WEIGHT)
 - MATTRESS SIZES — 2023-06-19, 2024-08-12  
 (FULL, KING, QUEEN, TWIN)
 - OBJECTS IN 0-, 1-, 2- AND 3-DIMENSIONAL SPACE — 2024-05-01, 2025-06-24  
 (LINE, PLANE, POINT, SOLID)
 - PARTS OF A BOOK — 2023-07-08, 2024-07-28  
 (COVER, JACKET, PAGE, SPINE)
 - PARTS OF A RIVER — 2023-12-10, 2024-12-12  
 (BANK, BED, DELTA, MOUTH)
 - POULTRY CUTS — 2024-07-24, 2025-08-15  
 (BREAST, TENDER, THIGH, WING)
 - SLANG FOR TOILET — 2023-06-18, 2024-08-12  
 (CAN, HEAD, JOHN, THRONE)
 - SOMEBODY — 2024-09-20, 2025-02-09  
 (CHARACTER, INDIVIDUAL, PARTY, PERSON)
 - STATES OF MATTER — 2023-07-25, 2023-08-15, 2024-01-11  
 (GAS, LIQUID, PLASMA, SOLID)
 - STEER — 2024-12-04, 2025-11-19  
 (DIRECT, GUIDE, LEAD, SHEPHERD)
 - THINGS A DOG CAN FETCH — 2024-03-10, 2025-06-28  
 (BALL, BONE, FRISBEE, STICK)
 - WAYS TO UNLOCK A DEVICE — 2024-11-19, 2025-11-06  
 (FACE, FINGERPRINT, PASSWORD, PIN)
 - WEAPONS IN THE GAME CLUE — 2023-11-04, 2025-11-05  
 (CANDLESTICK, KNIFE, ROPE, WRENCH)
 - WEB BROWSERS — 2023-07-02, 2025-01-17  
 (CHROME, EDGE, OPERA, SAFARI)