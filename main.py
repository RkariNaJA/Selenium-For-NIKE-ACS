from selenium.webdriver.chrome import remote_connection
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ACS_EMAIL = os.getenv("ACS_USER")
ACS_PASSWORD = os.getenv("ACS_PASS")

class NikeACSAutomator:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.downloaded_count = 0
        self.expected_count = 0
        self.processed_ids = set()
        self.expected_ids = set()
        
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        base_download_dir = os.path.join(os.getcwd(), "downloads")
        # date_stamp = datetime.now().replace(day=4).strftime("%Y-%m-%d")
        date_stamp = datetime.now().strftime("%Y-%m-%d")
        self.download_dir = os.path.join(base_download_dir, date_stamp)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        print(f"Download folder: {self.download_dir}")

        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "directory_upgrade": True
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self):
        print("Navigating to Nike ACS...")
        self.driver.get("https://acs.partner.nike-cloud.com/")
        
        print("Entering email...")
        email_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='text' or contains(@name, 'loginfmt')]")))
        email_input.send_keys(self.email)

        next_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(text(), 'Next')]")))
        next_btn.click()
        
        print("Entering password...")
        password_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password' or contains(@name, 'passwd')]")))
        password_input.send_keys(self.password)
        
        verify_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or @value='Sign in' or @value='ตรวจสอบ' or @value='Verify']")))
        verify_btn.click()
        
        try:
            remind_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'เตือนฉันในภายหลัง') or contains(text(), 'Remind me later') or @id='KmsiCheckboxField']"))
            )
            remind_btn.click()
            print("Clicked 'Remind me later'")
        except Exception:
            print("No 'Remind me later' prompt appeared.")
            
        print("Login completed.")
        time.sleep(5)

    # Open Filter Tab
    def set_filters(self):
        print("Setting filters...")
        print("Opening search criteria...")
        search_btn = self.driver.find_element(
            By.XPATH, "//eds-icon-button[@label='Search Criteria']//button"
        )
        self.driver.execute_script("arguments[0].click();", search_btn)
        time.sleep(1)

        # Click 'CBD Status' dropdown
        try:
            cbd_element = self.driver.find_element(
                By.XPATH, "//eds-select[@label='CBD Status']"
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cbd_element)
            time.sleep(0.3)

            self.driver.execute_script("""
                var el = document.querySelector("eds-select[label='CBD Status'] .eds-select__control");
                el.dispatchEvent(new MouseEvent("mousedown", {bubbles: true}));
            """)
            print("Clicked CBD Status dropdown")
            time.sleep(1)

            # Select options by index: 0=Q-ERMDS, 1=Q-QRMDS, 2=Q-CRMDS, 3=C
            for option_index in [1, 2, 3]:  # Q-QRMDS, Q-CRMDS, C
                try:
                    option = self.wait.until(EC.element_to_be_clickable((
                        By.XPATH, f"//div[contains(@id, 'option-{option_index}')]"
                    )))
                    self.driver.execute_script("arguments[0].click();", option)
                    print(f"Selected option-{option_index}")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Could not select option-{option_index}: {e}")

            self.driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(0.5)

        except Exception as e:
            print(f"Failed to select CBD statuses: {e}")

    # Click CBD button
    def set_CBD(self):
        print("Click CBD Button...")
        self.driver.execute_script("""
            var el = document.querySelector("button.split-btn-main");
            el.click();
        """)
        print("Clicked CBD button")
        time.sleep(20)

    # Select 500 Records
    def set_records(self):
        print("Click Show More Record")
        try:
            from selenium.webdriver.support.ui import Select
            
            rec_select = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//select[contains(@class, 'rows-per-page-select')]"
            )))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", rec_select)
            time.sleep(0.3)
            
            select = Select(rec_select)
            select.select_by_visible_text("500")
            print("Selected: 500 records")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Could not select 500 records: {e}")

    # Filter Latest Data
    def set_modified(self, column="Created"):
        print(f"Click {column} Date")
        try:
            mod_btn = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, f"//div[contains(@class, 'header-content')][.//span[text()='{column}']]"
            )))
            mod_btn.click()
            time.sleep(0.5)
            mod_btn.click()
            time.sleep(0.5)
            print(f"Clicked {column} twice")

        except Exception as e:
            print(f"Could not click {column}: {e}")
            try:
                self.driver.execute_script("""
                    var column = arguments[0];
                    var els = document.querySelectorAll("div.header-content");
                    for (var el of els) {
                        if (el.innerText.includes(column)) {
                            el.click();
                            el.click();
                            break;
                        }
                    }
                """, column)
                print(f"Clicked {column} via JS")
            except Exception as e2:
                print(f"JS fallback failed: {e2}")

    # FIX: Removed while True loop — now processes only 1 page
    def click_today_records(self):
        print("Clicking records modified today...")
        from datetime import datetime
        now = datetime.now()
        today = now.strftime("%b") + " " + str(now.day) + ", " + now.strftime("%Y")
        print(f"Looking for records modified on: {today}")
        clicked = 0

        print(f"Processing page 1...")
        time.sleep(2)
        rows = self.driver.find_elements(By.XPATH, "//tbody//tr")
        i = 0

        while i < len(rows):
            try:
                rows = self.driver.find_elements(By.XPATH, "//tbody//tr")
                row = rows[i]
                cells = row.find_elements(By.TAG_NAME, "td")

                if len(cells) < 4:
                    i += 1
                    continue

                # Check if any cell contains today's date
                has_today = any(
                    today in (cell.get_attribute("innerText") or "")
                    for cell in cells
                )

                if not has_today:
                    i += 1
                    continue

                # Click the table-link in first cell
                try:
                    link = cells[0].find_element(By.CLASS_NAME, "table-link")
                    cbdid = link.text.strip()

                    # Skip records already downloaded in a previous pass
                    if cbdid in self.processed_ids:
                        print(f"Skipped (already downloaded): {cbdid}")
                        i += 1
                        continue
                    self.processed_ids.add(cbdid)

                    self.driver.execute_script("arguments[0].click();", link)
                    print(f"Clicked: {cbdid}")
                    clicked += 1
                    time.sleep(3)

                    # Switch to new tab that opened
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(2)

                    # Export JSON on the detail page
                    self.export_json()

                    # Close detail tab and switch back to list tab
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(2)

                except Exception as e:
                    print(f"Could not click link in row {i}: {e}")
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])

                i += 1

            except Exception as e:
                print(f"Row {i} error: {e}")
                i += 1

        print(f"Total clicked: {clicked}")

    def export_json(self):
        try:
            time.sleep(2)

            # Get CBDID from current URL
            try:
                cbdid = self.driver.current_url.split("cbdId=")[-1].split("&")[0]
            except:
                cbdid = "Unknown"

            # Click eDocuments then Export to JSON in one JS call — original working code
            self.driver.execute_script("""
                var buttons = document.querySelectorAll("button.eds-button--secondary");
                for (var btn of buttons) {
                    if (btn.innerText.includes("eDocuments")) {
                        btn.click();
                        break;
                    }
                }
                setTimeout(function() {
                    var items = document.querySelectorAll("ul.menu-dropdown li");
                    if (items.length > 2) {
                        items[2].click();
                    }
                }, 500);
            """)
            print("Clicked eDocuments and Export to JSON")
            time.sleep(3)

            # Write log
            self.write_log(cbdid, "Success")

        except Exception as e:
            print(f"Failed to export JSON: {e}")
            try:
                cbdid = self.driver.current_url.split("cbdId=")[-1].split("&")[0]
            except:
                cbdid = "Unknown"
            self.write_log(cbdid, f"Failed: {e}")

    #Write Log
    def write_log(self, cbdid, status):
        today_str = datetime.now().strftime("%Y-%m-%d")
        log_filename = os.path.join(self.download_dir, f"export_log_{today_str}.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] CBDID: {cbdid} | Status: {status}\n"
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(log_line)
        print(f"Log saved: {log_line.strip()}")
        if status == "Success":
            self.downloaded_count += 1

    #Count Today Records On WebPage
    def count_today_records(self):
        """Count rows matching today's date on the current list page and log it."""
        today = datetime.now().strftime("%b") + " " + str(datetime.now().day) + ", " + datetime.now().strftime("%Y")
        print(f"Counting records on page for: {today}")
        try:
            ids = self.driver.execute_script("""
                var today = arguments[0];
                var rows = document.querySelectorAll("tbody tr");
                var ids = [];
                for (var row of rows) {
                    if (row.innerText.includes(today)) {
                        var link = row.querySelector(".table-link");
                        ids.push(link ? link.innerText.trim() : row.innerText.substring(0, 40));
                    }
                }
                return ids;
            """, today)
            self.expected_ids.update(ids)
            self.expected_count = len(self.expected_ids)
            print(f"Unique records found so far for today: {self.expected_count}")
        except Exception as e:
            print(f"Could not count today's records: {e}")
            self.expected_count = -1

    #Compare Count & Write Summary Log
    def write_summary_log(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        log_filename = os.path.join(self.download_dir, f"export_log_{today_str}.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        match_label = "OK" if self.downloaded_count == self.expected_count else "MISMATCH"
        summary_line = (
            f"\n[{timestamp}] === Summary ===\n"
            f"[{timestamp}] Records found on ACS website : {self.expected_count}\n"
            f"[{timestamp}] Files downloaded          : {self.downloaded_count}\n"
            f"[{timestamp}] Result                    : {match_label}\n"
        )
        with open(log_filename, "a", encoding="utf-8") as f:
            f.write(summary_line)
        print(summary_line.strip())

    #Run The Code
    def run(self):
        try:
            self.login()
            self.set_filters()
            self.set_CBD()
            self.set_records()
            # Pass 1: iterate records sorted by Created date
            self.set_modified(column="Created")
            self.count_today_records()
            self.click_today_records()

            # Pass 2: iterate records sorted by Modified date
            self.set_modified(column="Modified")
            self.count_today_records()
            self.click_today_records()

            self.write_summary_log()
            
            # print("All steps completed. Browser staying open...")
            # input("Press Enter to close the browser...")
            
        except Exception as e:
            print(f"Error occurred: {e}")
            # input("Error occurred. Press Enter to close the browser...")
            
        finally:
            print("Closing browser...")
            self.driver.quit()

if __name__ == "__main__":
    email = ACS_EMAIL
    password = ACS_PASSWORD
    
    automator = NikeACSAutomator(email, password)
    automator.run()