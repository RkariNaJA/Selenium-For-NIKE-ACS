# Diagram Flow

How the Nike ACS Auto-Downloader (`main.py`) works, drawn from the code. For the full explanation see [DEVELOPER-GUIDE.md](DEVELOPER-GUIDE.md).

## 1. Overview

What runs where: `main.py` drives a visible Chrome window through Selenium, and the files land in a folder named after today's date.

```text
┌────────────────────┐        ┌────────────────────────────────────┐
│ .env (git-ignored) │───────▶│ main.py                            │
│ ACS_USER           │  read  │ class NikeACSAutomator             │
│ ACS_PASS           │        │ run with: python main.py           │
│                    │        │                                    │
│ load_dotenv()      │        │ run(): login → filters → search    │
└────────────────────┘        │   → 500 rows → Created pass        │
                              │   → Modified pass → summary log    │
                              └─────────────────┬──────────────────┘
                                                │ Selenium WebDriver
                                                ▼
                              ┌────────────────────────────────────┐        ┌────────────────────────────┐
                              │ Google Chrome (visible window)     │───────▶│ Nike ACS portal            │
                              │ ChromeDriver via webdriver-manager │ HTTPS  │ acs.partner.nike-cloud.com │
                              │ WebDriverWait timeout 20 s         │◀───────│                            │
                              │                                    │ pages  │ Microsoft sign-in          │
                              │ download.default_directory =       │        │ CBD record list            │
                              │   downloads/YYYY-MM-DD/            │        │ CBD detail page (new tab)  │
                              └─────────────────┬──────────────────┘        └────────────────────────────┘
                                                │ Export to JSON (browser download)
                                                ▼
                              ┌────────────────────────────────────┐
                              │ downloads/YYYY-MM-DD/              │
                              │   one .json per CBD record         │
                              │   export_log_YYYY-MM-DD.txt        │
                              │                                    │
                              │ WISDOM imports the .json files     │
                              └────────────────────────────────────┘
```

## 2. Run sequence

What `NikeACSAutomator.run()` does, in order. Each box is a method in `main.py`.

```text
┌────────────────────────────────────────────────────────────┐
│ 1. login()                                                 │
│ open https://acs.partner.nike-cloud.com/                   │
│ email → Next → password → Sign in / Verify                 │
│ 'Remind me later' shown within 5 s? → click it             │
│ wait 5 s                                                   │
└─────────────────────────────┬──────────────────────────────┘
                              │ signed in
                              ▼
┌────────────────────────────────────────────────────────────┐
│ 2. set_filters()                                           │
│ open Search Criteria → CBD Status dropdown                 │
│ select option-1 Q-QRMDS, option-2 Q-CRMDS, option-3 C      │
└─────────────────────────────┬──────────────────────────────┘
                              │ statuses set
                              ▼
┌────────────────────────────────────────────────────────────┐
│ 3. set_CBD()                                               │
│ click button.split-btn-main (run the search)               │
│ wait 20 s for results                                      │
└─────────────────────────────┬──────────────────────────────┘
                              │ results shown
                              ▼
┌────────────────────────────────────────────────────────────┐
│ 4. set_records()                                           │
│ rows-per-page select → 500 (everything on page 1)          │
└─────────────────────────────┬──────────────────────────────┘
                              │ 500 rows
                              ▼
┌────────────────────────────────────────────────────────────┐
│ 5. Pass 1 · column = "Created"  (see diagram 3)            │
│ set_modified → count_today_records → click_today_records   │
└─────────────────────────────┬──────────────────────────────┘
                              │ pass 1 done
                              ▼
┌────────────────────────────────────────────────────────────┐
│ 6. Pass 2 · column = "Modified"  (see diagram 3)           │
│ same steps; CBD IDs from pass 1 are skipped                │
└─────────────────────────────┬──────────────────────────────┘
                              │ pass 2 done
                              ▼
┌────────────────────────────────────────────────────────────┐
│ 7. write_summary_log()  (see diagram 4)                    │
└─────────────────────────────┬──────────────────────────────┘
                              │ finally
                              ▼
┌────────────────────────────────────────────────────────────┐
│ 8. driver.quit()  (always runs, also after an error)       │
│ any exception in steps 1-7 → print it, jump here           │
└────────────────────────────────────────────────────────────┘
```

## 3. One pass (Created, then Modified)

Steps 5 and 6 of the run both do this, with `column` set to `"Created"` and then `"Modified"`. `processed_ids` is shared by both passes, so a record touched by both is downloaded once.

```text
┌────────────────────────────────────────────────┐
│ set_modified(column)                           │
│ click the column header twice → newest first   │
│ header click fails? → same clicks via JS       │
└───────────────────────┬────────────────────────┘
                        │ sorted
                        ▼
┌────────────────────────────────────────────────┐
│ count_today_records()                          │
│ today = e.g. "Nov 25, 2026"                    │
│ JS: rows whose text contains today             │
│ → add their CBD IDs to expected_ids            │
│ expected_count = len(expected_ids)             │
└───────────────────────┬────────────────────────┘
                        │ counted
                        ▼
┌────────────────────────────────────────────────┐        ┌────────────────────────────────────────┐
│ click_today_records()  · page 1 only           │───────▶│ export_json()                          │
│ for each row in tbody tr:                      │ step 5 │ 1. cbdId = from the URL (cbdId=...)    │
│  1. fewer than 4 cells? → next row             │        │ 2. JS: click 'eDocuments' button       │
│  2. no cell shows today? → next row            │        │    then menu item 3 (Export JSON)      │
│  3. CBD ID in processed_ids?                   │        │ 3. wait 3 s for the download           │
│     → 'Skipped', next row                      │        │ 4. write_log(cbdId, "Success")         │
│  4. add to processed_ids, click .table-link    │        │ error → write_log(cbdId,               │
│  5. switch to the new tab → export_json()      │        │           "Failed: <error>")           │
│  6. close tab, back to the list → next row     │        └───────────────────┬────────────────────┘
│ error in a row → close extra tab, next row     │                            │ append line
└────────────────────────────────────────────────┘                            ▼
                                                          ┌────────────────────────────────────────┐
                                                          │ downloads/YYYY-MM-DD/                  │
                                                          │   export_log_YYYY-MM-DD.txt            │
                                                          │ [ts] CBDID: <id> | Status: Success     │
                                                          │                                        │
                                                          │ Success → downloaded_count += 1        │
                                                          └────────────────────────────────────────┘
```

## 4. Summary check

How the summary at the end of the log decides OK or MISMATCH.

```text
┌──────────────────────────────────────┐        ┌──────────────────────────────────────┐
│ count_today_records()  · both passes │        │ write_log()  · both passes           │
│ expected_ids = unique CBD IDs        │        │ downloaded_count = number of         │
│   with today's date on page 1        │        │   'Success' log lines                │
│ expected_count = len(expected_ids)   │        │                                      │
└──────────────────┬───────────────────┘        └──────────────────┬───────────────────┘
                   └───────────────────────┬───────────────────────┘
                                           ▼
                 ┌────────────────────────────────────────────────────┐
                 │ write_summary_log()  → export_log_YYYY-MM-DD.txt   │
                 │ === Summary ===                                    │
                 │ Records found on ACS website : <expected_count>    │
                 │ Files downloaded          : <downloaded_count>     │
                 │ Result                    : OK | MISMATCH          │
                 │                                                    │
                 │ equal → OK, different → MISMATCH (check by hand    │
                 │   with CodeCheck.txt in the browser console)       │
                 └────────────────────────────────────────────────────┘
```
