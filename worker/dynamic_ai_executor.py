"""
Dynamic AI Executor - Simple Implementation
"""

import time
import traceback
from typing import Dict, Any
from datetime import datetime
from selenium_executor import SeleniumExecutor
from edge_executor import EdgeExecutor

class DynamicAIExecutor:
    """Simple dynamic automation executor."""
    
    def __init__(self):
        self.selenium_executor = SeleniumExecutor()
        self.edge_executor = EdgeExecutor()
        
    def execute_automation(self, prompt: str, website_url: str, framework: str = "selenium", timeout: int = 180) -> Dict[str, Any]:
        """Execute automation based on prompt."""
        start_time = time.time()
        
        try:
            # Generate simple automation code based on prompt
            code = self._generate_simple_code(prompt, website_url)
            
            # Try Chrome first, then Edge
            try:
                result = self.selenium_executor.execute_code(code, website_url, timeout)
                result["browser_used"] = "chrome"
            except Exception as e:
                print(f"Chrome failed, trying Edge: {e}")
                # Adapt code for Edge
                edge_code = code.replace("webdriver.Chrome", "webdriver.Edge")
                result = self.edge_executor.execute_code(edge_code, website_url, timeout)
                result["browser_used"] = "edge"
            
            result.update({
                "framework": framework,
                "generated_code": code,
                "context_chain": [{"prompt": prompt, "timestamp": datetime.now().isoformat()}],
                "function_calls": [],
                "automation_flow": {"steps": ["navigate", "execute", "capture"]}
            })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "logs": [{
                    "level": "error",
                    "message": f"Dynamic execution failed: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }],
                "screenshots": [],
                "execution_time": time.time() - start_time,
                "framework": framework,
                "generated_code": "",
                "context_chain": [],
                "function_calls": [],
                "automation_flow": None
            }
    
    def _generate_simple_code(self, prompt: str, url: str) -> str:
        """Generate simple automation code based on prompt."""
        prompt_lower = prompt.lower()
        
        # Simple keyword-based code generation
        if "click" in prompt_lower and "button" in prompt_lower:
            return f'''
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Navigate to website
driver.get("{url}")
time.sleep(3)

# Find and click button
try:
    # Try different button selectors
    button = None
    for selector in ["button", "input[type='submit']", "input[type='button']", "a.btn", ".button"]:
        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            break
        except:
            continue
    
    if button:
        button.click()
        print("Button clicked successfully")
        time.sleep(2)
    else:
        print("No clickable button found")
        
except Exception as e:
    print(f"Error clicking button: {{e}}")
'''
        
        elif "fill" in prompt_lower or "form" in prompt_lower:
            return f'''
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Navigate to website
driver.get("{url}")
time.sleep(3)

# Find and fill form fields
try:
    # Find input fields
    inputs = driver.find_elements(By.TAG_NAME, "input")
    
    for i, input_field in enumerate(inputs):
        if input_field.get_attribute("type") in ["text", "email", "password"]:
            input_field.clear()
            input_field.send_keys(f"test_value_{{i}}")
            print(f"Filled input field {{i}}")
    
    # Look for submit button
    submit_button = None
    for selector in ["input[type='submit']", "button[type='submit']", "button"]:
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, selector)
            break
        except:
            continue
    
    if submit_button:
        submit_button.click()
        print("Form submitted")
        time.sleep(2)
        
except Exception as e:
    print(f"Error filling form: {{e}}")
'''
        
        else:
            # Default: navigate and take screenshot
            return f'''
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Navigate to website
driver.get("{url}")
time.sleep(3)

# Take screenshot
driver.save_screenshot("automation_result.png")

# Get page title and basic info
title = driver.title
print(f"Page title: {{title}}")

# Count page elements
links = len(driver.find_elements(By.TAG_NAME, "a"))
buttons = len(driver.find_elements(By.TAG_NAME, "button"))
inputs = len(driver.find_elements(By.TAG_NAME, "input"))

print(f"Found {{links}} links, {{buttons}} buttons, {{inputs}} inputs")
'''
    
    def cleanup(self):
        """Cleanup resources."""
        pass 