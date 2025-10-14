from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from credentials import username, password, lesson, link
import time

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

        # Get input elements
        username_input = driver.find_element(By.ID, "Username")
        password_input = driver.find_element(By.ID, "Password")
        login_button = driver.find_element(By.ID, "btnSubmit")

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

        # Find and click the cookies acceptance button
        cookies_button_xpath = wait.until(EC.presence_of_element_located((By.ID, "c-p-bn")))
        if cookies_button_xpath:
            print("Found the cookies acceptance button.")
            driver.execute_script("arguments[0].click();", cookies_button_xpath)

        # Loop to find and click the "Buradayım!" button
        while True:
            try:
                # Wait for the button to be clickable
                buradayim_button_xpath = "//span[contains(text(), 'Buradayım!')]"
                buradayim_button = wait.until(EC.element_to_be_clickable((By.XPATH, buradayim_button_xpath)))
                
                # Click the button if found
                print("Found 'Buradayım!' button, clicking it.")
                driver.execute_script("arguments[0].click();", buradayim_button)
                
            except Exception:
                # Button not found, continue checking
                print(f"{index}: 'Buradayım!' button not found. Continuing to watch...")
                index += 1

            # Wait for a moment before checking again
            time.sleep(5)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()