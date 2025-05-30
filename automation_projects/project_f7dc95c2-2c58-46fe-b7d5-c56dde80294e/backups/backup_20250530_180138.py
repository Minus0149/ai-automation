# Login Test Automation
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Navigate to login page
driver.get("https://practicetestautomation.com/practice-test-login/")

# Wait for page to load
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)

try:
    # Find username field (try multiple selectors)
    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
    except:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='user'], input[id*='user'], input[type='email']"))
        )
    
    username_field.clear()
    username_field.send_keys("student")
    print("Username entered successfully")
    
    # Find password field
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    )
    password_field.clear()
    password_field.send_keys("Password123")
    print("Password entered successfully")
    
    # Find and click submit button
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
    except:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
        )
    
    # Scroll to button and click
    driver.execute_script("arguments[0].scrollIntoView();", submit_button)
    time.sleep(1)
    submit_button.click()
    print("Submit button clicked")
    
    # Wait for response
    time.sleep(5)
    
    # Check for success
    try:
        success_element = driver.find_element(By.CSS_SELECTOR, ".post-title, h1, .success")
        if "success" in success_element.text.lower() or "logged in" in success_element.text.lower():
            print("LOGIN TEST PASSED")
        else:
            print(f"LOGIN TEST: Response received - {success_element.text}")
    except:
        current_url = driver.current_url
        page_title = driver.title
        print(f"LOGIN TEST: Current URL - {current_url}")
        print(f"LOGIN TEST: Page Title - {page_title}")

except Exception as e:
    print(f"LOGIN TEST FAILED: {e}")
