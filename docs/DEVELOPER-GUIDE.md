# Nike ACS Auto-Downloader — Developer Guide

> The technical guide: what each pass does, the duplicate protection, the log format, how to verify
> the counts by hand, and the known limits. For a short overview of what this does, see the
> **[README](../README.md)**.
>
> The exported JSON files are what **WISDOM** imports.

Selenium automation that logs in to the Nike ACS portal, filters CBD records, and downloads the JSON export for every record **created or modified today**. It runs two passes — one sorted by the Modified column, one sorted by the Created column — because the website can only sort one column at a time.

## Files

| File            | Purpose                                                                                      |
| --------------- | -------------------------------------------------------------------------------------------- |
| `main.py`       | Main automation script (two-pass download + summary log)                                     |
| `test.py`       | Test version of the script (uses `.env` credentials and a `day=4` date override for testing) |
| `CodeCheck.txt` | Browser-console snippet to manually verify record counts per column                          |
| `downloads/`    | Downloaded JSON files and the daily export log (created automatically, git-ignored)          |
| `README.md`     | GitHub landing page — what this does, for anyone                                             |
| `docs/DEVELOPER-GUIDE.md` | This file                                                                          |

## Requirements

- Python 3.x
- Google Chrome
- Packages:

```bash
pip install selenium webdriver-manager python-dotenv
```

ChromeDriver is downloaded automatically by `webdriver-manager` — no manual setup needed.

## Configuration

Both `main.py` and `test.py` read the login from a `.env` file in this folder — nothing is
hardcoded any more:

```
ACS_USER=your.email@company.com
ACS_PASS=yourpassword
```

`main.py` loads them at the top (`load_dotenv()` → `os.getenv("ACS_USER")` / `ACS_PASS`) and uses
them in the `__main__` block. `test.py` is the same script with a `day=4` date override for testing.

> `.env` is listed in `.gitignore` — never commit it. The archived scripts under `Code Version/`
> still carry a `password = "YOUR_PASSWORD"` placeholder; they are kept for reference and are not
> run.

## How to Run

```bash
python main.py
```

The browser opens visibly (not headless). If Microsoft login shows a "Remind me later" / "Stay signed in" prompt, the script handles it automatically. At the end it waits for you to press Enter before closing the browser.

## What the Script Does

1. **Login** — signs in to `https://acs.partner.nike-cloud.com/` with the Microsoft login flow.
2. **Set filters** — opens Search Criteria and selects CBD Status: `Q-QRMDS`, `Q-CRMDS`, `C`.
3. **Search** — clicks the CBD button and waits for results.
4. **Show 500 records** — sets rows-per-page to 500 so today's records fit on page 1.
5. **Pass 1 — Modified date**
   - Sorts the table by the **Modified** column (clicks the header twice for newest-first).
   - Counts rows whose _Modified column_ shows today's date (this is the "website" number in the log).
   - Opens each matching record in a new tab, clicks **eDocuments → Export to JSON**, then closes the tab.
6. **Pass 2 — Created date**
   - Re-sorts by the **Created** column and repeats the same count + download for rows whose _Created column_ shows today's date.
   - Records already downloaded in Pass 1 are **skipped**, so nothing is downloaded twice.
7. **Summary log** — written after both passes finish.

### Duplicate protection

Before clicking a record, the script checks:

1. The list of CBD IDs already downloaded during this run, and
2. The file names in the `downloads/` folder — if an existing file name contains the CBDID, the record is skipped.

Skipped records show `Skipped (already downloaded): <CBDID>` in the console and count as "skipped" in the summary.

## Logs

A daily log file is written to `downloads/export_log_YYYY-MM-DD.txt`. Each download is tagged with its pass:

```
[2026-07-06 10:15:32] [Modified pass] CBDID: 12345678 | Status: Success
```

After both passes, a summary compares each pass against the website count:

```
=== Summary ===
Modified pass : website 12 | downloaded 12 | skipped (duplicate) 0 | OK
Created pass  : website 5  | downloaded 3  | skipped (duplicate) 2 | OK
Total files downloaded (unique): 15
```

- **website** — rows on the page whose date column equals today.
- **downloaded** — JSON files exported during that pass.
- **skipped (duplicate)** — records that matched but were already downloaded.
- **OK / MISMATCH** — `downloaded + skipped` is compared with `website`; MISMATCH means something was missed.

## Manual Verification (CodeCheck.txt)

To double-check the counts yourself: open the ACS record list page, press `F12` → Console, paste the contents of `CodeCheck.txt`, and press Enter. Edit the `target` date on the first line if needed. It prints separate totals for the Created column, the Modified column, the overlap (both), and the unique total.

## Known Limits

- Only **page 1** is processed (up to 500 rows per sort). If more than 500 records exist, older ones can be missed.
- Date matching is text-based (e.g. `Jul 6, 2026`) and must match the format shown on the website.
- The `downloads/` folder is shared across days — a file from a previous day whose name contains the same CBDID will cause that record to be skipped today.
- Timing uses fixed `time.sleep()` waits; a slow network may need larger values.
