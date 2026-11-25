# Nike ACS Auto-Downloader

**Exports the JSON for every Nike ACS cost record created or modified today — both, without downloading anything twice.**

<p>
  <img alt="Python 3" src="https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white">
  <img alt="Selenium" src="https://img.shields.io/badge/Selenium-Chrome%20automation-43B02A?logo=selenium&logoColor=white">
  <img alt="Google Chrome" src="https://img.shields.io/badge/Chrome-webdriver--manager-4285F4?logo=googlechrome&logoColor=white">
  <img alt="JSON export" src="https://img.shields.io/badge/output-JSON%20per%20record-000000?logo=json&logoColor=white">
  <img alt="Feeds WISDOM" src="https://img.shields.io/badge/feeds-WISDOM%20import-6E4C13">
  <img alt="Status: internal deployment" src="https://img.shields.io/badge/status-internal%20deployment-success">
</p>

Used at **Hi-Tech Apparel**. It signs in to the Nike ACS portal, filters the CBD records down to the
three statuses that matter, and exports one JSON file per record touched today. Those files are what
**WISDOM** imports.

```
ACS portal  →  filter 3 statuses  →  two sorted passes (Created, Modified)  →  one JSON per record
```

---

## The problem it solves

"Everything that changed today" sounds like one query, but the ACS record list can only be sorted by
**one** column at a time — and a record counts as touched if either its *Modified* date or its
*Created* date is today. Sorting by one column hides part of the answer.

So the script runs **two passes** over the same filtered result set:

| Pass | Sorted by | Picks up |
|------|-----------|----------|
| 1 | **Created** column | records created today |
| 2 | **Modified** column | records edited today |

A record that appears in both is downloaded **once** — pass 2 skips anything pass 1 already took.

**Duplicate protection** is the list of CBD IDs already pulled in this run: a record whose ID is on
it is skipped and reported in the console (`Skipped (already downloaded): <CBDID>`), never silently
dropped. Each day's files go to their own folder, `downloads/YYYY-MM-DD/`.

---

## It tells you if it missed something

Every run writes `downloads/YYYY-MM-DD/export_log_YYYY-MM-DD.txt`, and the run as a whole is checked
against what the website itself showed:

```
=== Summary ===
Records found on ACS website : 15
Files downloaded          : 15
Result                    : OK
```

*Records found* is the number of unique CBD IDs with today's date seen across both passes; *Files
downloaded* is the number of successful exports. They must be equal, or the result reads
**MISMATCH** — the signal that a record was missed rather than a silent partial export.
`CodeCheck.txt` is a browser-console snippet for checking the counts by hand.

---

## Running it

```bash
pip install selenium webdriver-manager python-dotenv
# create .env with ACS_USER and ACS_PASS
python main.py
```

Chrome opens visibly and drives itself: log in (the Microsoft "Stay signed in" prompt is handled),
set the CBD statuses `Q-QRMDS` / `Q-CRMDS` / `C`, search, switch to 500 rows per page, then run both
passes. The browser closes by itself when the run ends (also after an error) — check the log for
the result.

> ⚠️ **Only page 1 is processed** (up to 500 rows per sort). If more than 500 records match, the
> oldest can be missed — see the guide's *Known Limits*.

---

## Under the hood

| | |
|---|---|
| **The script** | [`main.py`](main.py) — `NikeACSAutomator`: login → filters → search → 500 rows → Created pass → Modified pass → summary log |
| **Test variant** | [`test.py`](test.py) — same flow with a date override for trying it out |
| **Manual check** | [`CodeCheck.txt`](CodeCheck.txt) — paste into the browser console to count Created / Modified / both / unique yourself |
| **Archived** | `Code Version/` — earlier snapshots, kept for reference, not run |

Credentials come from `.env` (`ACS_USER`, `ACS_PASS`); nothing is hardcoded.

---

## Documentation

**[docs/DEVELOPER-GUIDE.md](docs/DEVELOPER-GUIDE.md)** — the full guide: each pass step by step, how
duplicate protection decides, the log format field by field, the manual verification recipe, and the
known limits (page-1 cap, text-based date matching, re-runs on the same day, fixed waits).

**[docs/Diagram Flow.md](docs/Diagram%20Flow.md)** — text diagrams of the same flow.

---

<sub>Internal tool for HI-TECH APPAREL · `.env`, the `downloads/` folder, every exported file and
`output.txt` are excluded by `.gitignore` — no credentials or business data are in this repo.</sub>
