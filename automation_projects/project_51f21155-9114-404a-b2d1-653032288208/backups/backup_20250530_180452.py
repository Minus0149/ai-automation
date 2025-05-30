# Generic Automation
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Navigate to website
driver.get("https://practicetestautomation.com/practice-test-login/")

# Wait for page to load
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)

try:
    # Task: Test case 2: Negative username test
            Open page
            Type username incorrectUser into Username field
            Type password Password123 into Password field
            Push Submit button
            Verify error message is displayed
            Verify error message text is Your username is invalid!
    print(f"Executing task: Test case 2: Negative username test
            Open page
            Type username incorrectUser into Username field
            Type password Password123 into Password field
            Push Submit button
            Verify error message is displayed
            Verify error message text is Your username is invalid!")
    
    # Get page information
    title = driver.title
    print(f"Page title: {title}")
    
    # Find interactive elements
    buttons = driver.find_elements(By.TAG_NAME, "button")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    links = driver.find_elements(By.TAG_NAME, "a")
    
    print(f"Found {len(buttons)} buttons, {len(inputs)} inputs, {len(links)} links")
    
    # Take screenshot
    driver.save_screenshot("automation_screenshot.png")
    print("Screenshot saved")
    
    # Wait and observe
    time.sleep(5)
    
    print("Automation completed successfully")

except Exception as e:
    print(f"AUTOMATION FAILED: {e}")
