from selenium.webdriver.chrome import remote_connection
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

class NikeACSAutomator:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # Define download directory
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
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
        
        # Enter Email
        print("Entering email...")
        email_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='text' or contains(@name, 'loginfmt')]")))
        email_input.send_keys(self.email)
        
        # Click Next (ถัดไป / Next)
        # next_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' or @value='Next' or @value='ถัดไป']")))
        # next_btn.click()

        next_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(text(), 'Next')]")))
        next_btn.click()
        
        # Enter Password
        print("Entering password...")
        password_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password' or contains(@name, 'passwd')]")))
        password_input.send_keys(self.password)
        
        # Click Verify / Sign in (ตรวจสอบ / Verify / Sign in)
        verify_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or @value='Sign in' or @value='ตรวจสอบ' or @value='Verify']")))
        verify_btn.click()
        
        # Click "Remind me later" or "เตือนฉันในภายหลัง" if it appears
        try:
            remind_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'เตือนฉันในภายหลัง') or contains(text(), 'Remind me later') or @id='KmsiCheckboxField']"))
            )
            remind_btn.click()
            print("Clicked 'Remind me later'")
        except Exception:
            print("No 'Remind me later' prompt appeared.")
            
        print("Login completed.")
        time.sleep(5) # Wait for dashboard to load

    def set_filters(self):
        print("Setting filters...")
        print("Opening search criteria...")
        search_btn = self.driver.find_element(
            By.XPATH, "//eds-icon-button[@label='Search Criteria']//button"
        )
        self.driver.execute_script("arguments[0].click();", search_btn)
        time.sleep(1)
        # Note: The precise locators depend on the actual DOM of Nike ACS.
        # These XPaths are inferred from the UiPath actions and common Angular/PrimeNG structures.
        
        # Click 'Season' dropdown
        # try:
        #     season_dropdown = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Season')]/ancestor::div[1]")))
        #     season_dropdown.click()
        #     time.sleep(1)
            
        #     # Select SU26 or FA26
        #     season_option = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//li//*[contains(text(), 'SU26') or contains(text(), 'FA26')]")))
        #     season_option.click()
        #     # Click outside to close dropdown
        #     self.driver.find_element(By.TAG_NAME, 'body').click()
        # except Exception as e:
        #     print(f"Failed to select season: {e}")

        # Click 'CBD Status' dropdown
        try:
            # Scroll to CBD Status first
            cbd_element = self.driver.find_element(
                By.XPATH, "//eds-select[@label='CBD Status']"
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cbd_element)
            time.sleep(0.3)

            # Use dispatchEvent mousedown — this is what works
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

            # Click outside to close dropdown
            self.driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(0.5)

        except Exception as e:
            print(f"Failed to select CBD statuses: {e}")

    def set_CBD(self):
        print("Click CBD Button...")
        self.driver.execute_script("""
            var el = document.querySelector("button.split-btn-main");
            el.click();
        """)
        print("Clicked CBD button")
        time.sleep(20)

    # Select 500 Record
    def set_records(self):
        print("Click Show More Record")
        
        try:
            # It's a native <select> element now — use Select class
            from selenium.webdriver.support.ui import Select
            
            rec_select = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//select[contains(@class, 'rows-per-page-select')]"
            )))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", rec_select)
            time.sleep(0.3)
            
            select = Select(rec_select)
            select.select_by_visible_text("500")  # value="4" corresponds to 500
            print("Selected: 500 records")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Could not select 500 records: {e}")
            # Fallback: select by visible text
            try:
                select.select_by_visible_text("500")
                print("Selected 500 via visible text")
            except Exception as e2:
                print(f"Fallback also failed: {e2}")

    def set_modified(self):
        print("Click Modified Date")
        try:
            mod_btn = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//div[contains(@class, 'header-content')][.//span[text()='Modified']]"
            )))

            # Click twice to sort descending (newest first)
            mod_btn.click()
            time.sleep(0.5)
            mod_btn.click()
            time.sleep(0.5)
            print("Clicked Modified twice")
        
        except Exception as e:
            print(f"Could not click Modified: {e}")
            # Fallback: JS click
            try:
                self.driver.execute_script("""
                var els = document.querySelectorAll("div.header-content");
                for (var el of els) {
                    if (el.innerText.includes("Modified")) {
                        el.click();
                        el.click();
                        break;
                    }
                }
                """)
                print("Clicked Modified via JS")
            except Exception as e2:
                print(f"JS fallback failed: {e2}")

            
    # def download_json_for_cbd(self, cbd_id):
    #     print(f"Navigating to CBD detail page for ID: {cbd_id}")
    #     url = f"https://acs.partner.nike-cloud.com/cbd-detail?cbdId={cbd_id}&dataStage=CBD"
    #     self.driver.get(url)
    #     time.sleep(3) # Wait for page to render
        
    #     try:
    #         # Click 'eDocument Button for download Json' (assuming it has an icon or text indicating download or JSON)
    #         # This XPath targets a generic download button or one containing 'JSON' text
    #         download_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'eDocument') or contains(text(), 'JSON') or contains(text(), 'Export')]")))
    #         download_btn.click()
            
    #         # Click 'Export to JSON' if it's a dropdown option
    #         try:
    #             export_json = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Export to JSON')]")))
    #             export_json.click()
    #         except:
    #             pass # Maybe clicking the first button was enough
                
    #         print(f"Initiated JSON download for {cbd_id}")
    #         time.sleep(2) # Give it time to start downloading
    #     except Exception as e:
    #         print(f"Failed to download JSON for {cbd_id}: {e}")

    def run(self):
        try:
            self.login()
            self.set_filters()
            self.set_CBD()
            self.set_records()
            self.set_modified()
            # In a real scenario, you would extract a list of CBD_IDs from the table
            # Here we provide a dummy list for demonstration.
            cbd_ids = ["12345"] 
            for cbd_id in cbd_ids:
                self.download_json_for_cbd(cbd_id)
                
        finally:
            print("Closing browser...")
            # self.driver.quit()

if __name__ == "__main__":
    email = "your.email@company.com"
    # Using the password from Main_Modified.xaml
    password = "YOUR_PASSWORD"
    
    automator = NikeACSAutomator(email, password)
    automator.run()
