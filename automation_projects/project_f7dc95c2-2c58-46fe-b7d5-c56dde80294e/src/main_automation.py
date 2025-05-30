#!/usr/bin/env python3
"""
Automation Script
Task: Test login functionality with student/Password123
Generated: 2025-05-30 18:01:38
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

# WebDriver Manager imports with fallback
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

def setup_chrome_driver():
    """Setup Chrome driver with fallback."""
    try:
        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        
        if WEBDRIVER_MANAGER_AVAILABLE:
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        else:
            return webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Chrome setup failed: {e}")
        return None

def setup_edge_driver():
    """Setup Edge driver with fallback."""
    try:
        options = EdgeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        if WEBDRIVER_MANAGER_AVAILABLE:
            from selenium.webdriver.edge.service import Service
            service = Service(EdgeChromiumDriverManager().install())
            return webdriver.Edge(service=service, options=options)
        else:
            return webdriver.Edge(options=options)
    except Exception as e:
        print(f"Edge setup failed: {e}")
        return None

def main():
    """Main automation function."""
    driver = None
    
    try:
        # Try Chrome first, fallback to Edge
        print("Attempting to start Chrome...")
        driver = setup_chrome_driver()
        
        if not driver:
            print("Chrome failed, trying Edge...")
            driver = setup_edge_driver()
        
        if not driver:
            print("ERROR: Could not initialize any browser driver")
            return False
        
        print("Browser started successfully")
        
        # Create screenshots directory
        os.makedirs("screenshots", exist_ok=True)
        
        # Execute the automation code
        try:
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
            
            return True
            
        except Exception as automation_error:
            print(f"Automation error: {{automation_error}}")
            return False
    
    except Exception as e:
        print(f"Script error: {{e}}")
        return False
    
    finally:
        if driver:
            try:
                driver.quit()
                print("Browser closed")
            except Exception as e:
                print(f"Error closing browser: {{e}}")

if __name__ == "__main__":
    success = main()
    if success:
        print("Automation completed successfully!")
    else:
        print("Automation failed!")
