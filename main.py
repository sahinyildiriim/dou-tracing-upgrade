from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from credentials import username, password, lesson, link
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

def main():
    index = 0

    # Initialize driver options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Disable microphone and camera pop-ups and password saving
    prefs = {
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)

    # options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to a webpage
        driver.get(link)

        # Wait until web page is loaded
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Print if the page is loaded
        if element:
            print("Page is loaded")

        # Get input elements (try multiple common selectors)
        def find_login_elements():
            selector_candidates = [
                (By.ID, "Username"),
                (By.ID, "UserName"),
                (By.NAME, "Username"),
                (By.NAME, "UserName"),
                (By.NAME, "Email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[type='text']"),
            ]
            password_candidates = [
                (By.ID, "Password"),
                (By.NAME, "Password"),
                (By.CSS_SELECTOR, "input[type='password']"),
            ]
            login_button_candidates = [
                (By.ID, "btnSubmit"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(., 'Giriş') or contains(., 'Login')]")
            ]

            username_input_el = None
            password_input_el = None
            login_button_el = None

            # Some pages place form in an iframe – try default, then any iframe
            def try_in_context():
                nonlocal username_input_el, password_input_el, login_button_el
                for by, value in selector_candidates:
                    try:
                        username_input_el = driver.find_element(by, value)
                        break
                    except Exception:
                        continue
                for by, value in password_candidates:
                    try:
                        password_input_el = driver.find_element(by, value)
                        break
                    except Exception:
                        continue
                for by, value in login_button_candidates:
                    try:
                        login_button_el = driver.find_element(by, value)
                        break
                    except Exception:
                        continue

            # Try on main document
            try_in_context()
            # If not found, scan iframes
            if not (username_input_el and password_input_el and login_button_el):
                try:
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    for frame in iframes:
                        driver.switch_to.frame(frame)
                        try_in_context()
                        if username_input_el and password_input_el and login_button_el:
                            break
                        driver.switch_to.default_content()
                except Exception:
                    driver.switch_to.default_content()

            # Ensure we are back to a valid context
            try:
                driver.switch_to.default_content()
            except Exception:
                pass

            return username_input_el, password_input_el, login_button_el

        username_input, password_input, login_button = find_login_elements()
        if not (username_input and password_input and login_button):
            raise NoSuchElementException("Login elements not found. Please verify login page and selectors.")

        # Give free time to avoid detection
        time.sleep(2)

        # Fill in the credentials by JavaScript to avoid detection
        driver.execute_script(f"arguments[0].value = '{username}';", username_input)
        driver.execute_script(f"arguments[0].value = '{password}';", password_input)
        driver.execute_script("arguments[0].click();", login_button)

        # Find specific lesson element
        lesson_xpath = f"//tbody/tr/td/a/span[contains(text(), '{lesson}')]"
        lesson_element = wait.until(EC.presence_of_element_located((By.XPATH, lesson_xpath)))

        if lesson_element:
            print(f"Successfully found the lesson: '{lesson_element.text}'")
            driver.execute_script("arguments[0].click();", lesson_element)

        # Find lesson navigation button
        navigation_button_xpath = "//i[@class='fad fa-circle live-icon me-1']"
        navigation_button = wait.until(EC.presence_of_element_located((By.XPATH, navigation_button_xpath)))

        if navigation_button:
            print("Found the 'Perculus' button.")
            driver.execute_script("arguments[0].click();", navigation_button)

        # Find and click the Perculus button
        perculus_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "perculus-button-content")))

        if perculus_button:
            print("Found the 'Perculus' button.")
            driver.execute_script("arguments[0].click();", perculus_button)

        # Wait for Perculus to open in a new window/tab and switch
        try:
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) >= 2)
            driver.switch_to.window(driver.window_handles[-1])
            print("Switched to Perculus window.")
        except TimeoutException:
            # If it didn't open a new window, we stay in the same one
            print("Perculus did not open a new window; continuing in current tab.")
        time.sleep(2)

        # Find and click the cookies acceptance button (best-effort)
        try:
            cookies_button_xpath = wait.until(EC.presence_of_element_located((By.ID, "c-p-bn")))
            if cookies_button_xpath:
                print("Found the cookies acceptance button.")
                driver.execute_script("arguments[0].click();", cookies_button_xpath)
        except TimeoutException:
            pass

        # Check common error banner for unregistered participant
        try:
            error_banner = WebDriverWait(driver, 5).until(EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZÇĞİÖŞÜ', 'abcdefghijklmnopqrstuvwxyzçğiöşü'), 'katılımcı') and (contains(., 'kayıt') or contains(., 'kod'))] | "
                "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'participant') and contains(., 'registered')]"
            )))
            if error_banner:
                print("Perculus: Katılımcı kaydı bulunamadı. Lütfen dersi LMS içinden bir kez açın ve doğru şube/link kullandığınızdan emin olun.")
                driver.quit()
                return
        except TimeoutException:
            pass

        # Helpers to locate and click "Buradayım!"
        def find_buradayim_button():
            xpaths = [
                "//button[.//span[contains(normalize-space(.), 'Buradayım')]]",
                "//button[contains(normalize-space(.), 'Buradayım')]",
                "//*[self::span or self::div][contains(normalize-space(.), 'Buradayım')]/ancestor::button[1]",
                "//*[contains(normalize-space(.), 'Buradayım') and (self::button or contains(@class,'button'))]",
            ]

            # Try in default content first
            for xp in xpaths:
                try:
                    el = driver.find_element(By.XPATH, xp)
                    if el:
                        return el
                except Exception:
                    continue

            # Scan iframes for the button
            try:
                frames = driver.find_elements(By.TAG_NAME, 'iframe')
                for fr in frames:
                    try:
                        driver.switch_to.frame(fr)
                        for xp in xpaths:
                            try:
                                el = driver.find_element(By.XPATH, xp)
                                if el:
                                    return el
                            except Exception:
                                continue
                    finally:
                        driver.switch_to.default_content()
            except Exception:
                driver.switch_to.default_content()

            return None

        def click_safely(el):
            # Skip disabled buttons
            disabled = (el.get_attribute('disabled') is not None) or (el.get_attribute('aria-disabled') in ['true', '1'])
            if disabled:
                return False
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            except Exception:
                pass
            # Try normal click
            try:
                el.click()
                return True
            except Exception:
                pass
            # Try Actions click
            try:
                ActionChains(driver).move_to_element(el).pause(0.1).click().perform()
                return True
            except Exception:
                pass
            # Try JS click
            try:
                driver.execute_script("arguments[0].click();", el)
                return True
            except Exception:
                return False

        # Loop: watch and click "Buradayım!"
        while True:
            try:
                btn = find_buradayim_button()
                if btn:
                    print("Found 'Buradayım!' button, clicking it.")
                    # Cross-platform alert
                    try:
                        if os.name == 'nt':
                            import winsound
                            winsound.MessageBeep()
                        else:
                            os.system("printf '\a'")
                    except Exception:
                        pass

                    # Ensure in the context containing the element
                    try:
                        driver.switch_to.default_content()
                    except Exception:
                        pass

                    if click_safely(btn):
                        print("'Buradayım!' clicked.")
                    else:
                        print("'Buradayım!' click attempts failed; will retry.")
                else:
                    print(f"{index}: 'Buradayım!' button not found. Continuing to watch...")
                    index += 1
            except Exception:
                print(f"{index}: Error while searching/clicking 'Buradayım!'. Retrying...")
                index += 1

            time.sleep(5)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()