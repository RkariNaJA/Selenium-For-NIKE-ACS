# Nike ACS Auto-Downloader — Developer Guide

> The technical guide: what each pass does, the duplicate protection, the log format, how to verify
> the counts by hand, and the known limits. For a short overview of what this does, see the
> **[README](../README.md)**.
>
> The exported JSON files are what **WISDOM** imports.

Selenium automation that logs in to the Nike ACS portal, filters CBD records, and downloads the JSON export for every record **created or modified today**. It runs two passes — one sorted by the Created column, then one sorted by the Modified column — because the website can only sort one column at a time.

## Files

| File            | Purpose                                                                                      |
| --------------- | -------------------------------------------------------------------------------------------- |
| `main.py`       | Main automation script (two-pass download + summary log)                                     |
| `test.py`       | Test version of the script (uses `.env` credentials and a `day=4` date override for testing) |
| `CodeCheck.txt` | Browser-console snippet to manually verify record counts per column                          |
| `downloads/`    | One `YYYY-MM-DD/` folder per day: JSON files + that day's export log (git-ignored)           |
| `README.md`     | GitHub landing page — what this does, for anyone                                             |
| `docs/DEVELOPER-GUIDE.md` | This file                                                                          |
| `docs/Diagram Flow.md`    | Text diagrams of the run, one pass, and the summary check                          |

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

The browser opens visibly (not headless). If Microsoft login shows a "Remind me later" / "Stay signed in" prompt, the script handles it automatically. When the run ends — or stops on an error — the browser closes by itself (`driver.quit()` in a `finally` block); the console output and the log tell you what happened.

## What the Script Does

1. **Login** — signs in to `https://acs.partner.nike-cloud.com/` with the Microsoft login flow.
2. **Set filters** — opens Search Criteria and selects CBD Status: `Q-QRMDS`, `Q-CRMDS`, `C`.
3. **Search** — clicks the CBD button and waits for results.
4. **Show 500 records** — sets rows-per-page to 500 so today's records fit on page 1.
5. **Pass 1 — Created date**
   - Sorts the table by the **Created** column (clicks the header twice for newest-first).
   - Collects the CBD IDs of rows whose text contains today's date (e.g. `Nov 25, 2026`) — these feed the "Records found on ACS website" number in the summary.
   - Opens each matching record in a new tab, clicks **eDocuments → Export to JSON**, logs the result, then closes the tab.
6. **Pass 2 — Modified date**
   - Re-sorts by the **Modified** column and repeats the same count + download.
   - Records already downloaded in Pass 1 are **skipped**, so nothing is downloaded twice.
7. **Summary log** — written after both passes finish.
8. **Close the browser** — always, even if a step above raised an error.

### Duplicate protection

Before clicking a record, the script checks the set of CBD IDs already handled during this run
(`processed_ids`, shared by both passes). If the ID is in it, the record is skipped and the console
shows `Skipped (already downloaded): <CBDID>`. Nothing on disk is checked, and the set lives only in
memory for the length of the run.

## Logs

Each day's JSON files and log go to `downloads/YYYY-MM-DD/`; the log is
`downloads/YYYY-MM-DD/export_log_YYYY-MM-DD.txt`. Each export attempt adds one line:

```
[2026-07-06 10:15:32] CBDID: 12345678 | Status: Success
[2026-07-06 10:16:05] CBDID: 12345679 | Status: Failed: <error message>
```

After both passes, one summary is appended:

```
[2026-07-06 10:20:11] === Summary ===
[2026-07-06 10:20:11] Records found on ACS website : 15
[2026-07-06 10:20:11] Files downloaded          : 15
[2026-07-06 10:20:11] Result                    : OK
```

- **Records found on ACS website** — unique CBD IDs, across both passes, of page-1 rows whose text contains today's date.
- **Files downloaded** — number of `Success` lines written this run.
- **OK / MISMATCH** — OK when the two numbers are equal; MISMATCH means a record was missed or an export failed.

## Manual Verification (CodeCheck.txt)

To double-check the counts yourself: open the ACS record list page, press `F12` → Console, paste the contents of `CodeCheck.txt`, and press Enter. Edit the `target` date on the first line if needed. It prints separate totals for the Created column, the Modified column, the overlap (both), and the unique total.

## Known Limits

- Only **page 1** is processed (up to 500 rows per sort). If more than 500 records exist, older ones can be missed.
- Date matching is text-based (e.g. `Jul 6, 2026`) and must match the format shown on the website.
- A row matches if today's date appears **anywhere** in it, not only in the sorted column.
- Running the script twice on the same day downloads every record again into the same `downloads/YYYY-MM-DD/` folder and appends a second set of lines and a second summary to the same log — the duplicate check only covers one run.
- "Success" is logged once the export menu was clicked; the script doesn't confirm the file actually finished downloading.
- Timing uses fixed `time.sleep()` waits; a slow network may need larger values.
