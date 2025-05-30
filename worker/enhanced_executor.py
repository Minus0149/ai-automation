"""
Enhanced Automation Executor - Simple Implementation
"""

import time
import json
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from selenium_executor import SeleniumExecutor
from edge_executor import EdgeExecutor

class EnhancedAutomationExecutor:
    """Enhanced automation executor with project generation."""
    
    def __init__(self):
        self.selenium_executor = SeleniumExecutor()
        self.edge_executor = EdgeExecutor()
        self.projects_dir = Path("generated_projects")
        self.projects_dir.mkdir(exist_ok=True)
        
    def execute_automation(self, prompt: str, website_url: str, framework: str = "selenium", task_id: str = None, timeout: int = 180) -> Dict[str, Any]:
        """Execute enhanced automation with project generation."""
        start_time = time.time()
        task_id = task_id or f"enhanced_{int(time.time())}"
        
        try:
            # Generate automation code
            code = self._generate_enhanced_code(prompt, website_url)
            
            # Execute with fallback
            try:
                result = self.selenium_executor.execute_code(code, website_url, timeout)
                result["browser_used"] = "chrome"
            except Exception as e:
                print(f"Chrome failed, trying Edge: {e}")
                edge_code = code.replace("webdriver.Chrome", "webdriver.Edge")
                result = self.edge_executor.execute_code(edge_code, website_url, timeout)
                result["browser_used"] = "edge"
            
            # Create project structure
            project_structure = self._create_project_structure(task_id, code, prompt)
            
            result.update({
                "framework": framework,
                "generated_code": code,
                "project_structure": project_structure,
                "context_chain": [{"prompt": prompt, "timestamp": datetime.now().isoformat()}],
                "function_calls": [],
                "chat_history": [{"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()}],
                "task_id": task_id
            })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "logs": [{
                    "level": "error",
                    "message": f"Enhanced execution failed: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }],
                "screenshots": [],
                "execution_time": time.time() - start_time,
                "framework": framework,
                "generated_code": "",
                "project_structure": {"files": [], "contents": {}},
                "context_chain": [],
                "function_calls": [],
                "chat_history": [],
                "task_id": task_id
            }
    
    def _generate_enhanced_code(self, prompt: str, url: str) -> str:
        """Generate enhanced automation code."""
        return f'''#!/usr/bin/env python3
"""
Enhanced Automation Script
Task: {prompt}
Generated: {datetime.now().isoformat()}
"""

import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def setup_driver():
    """Setup Chrome driver with options."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except:
        return webdriver.Chrome(options=options)

def main():
    """Main automation function."""
    driver = setup_driver()
    
    try:
        print(f"Starting automation: {prompt}")
        
        # Navigate to website
        driver.get("{url}")
        time.sleep(3)
        
        # Take initial screenshot
        os.makedirs("screenshots", exist_ok=True)
        driver.save_screenshot("screenshots/initial.png")
        
        # Automation logic based on prompt
        {self._get_automation_logic(prompt)}
        
        # Take final screenshot
        driver.save_screenshot("screenshots/final.png")
        print("Automation completed successfully!")
        
    except Exception as e:
        print(f"Automation failed: {{e}}")
        driver.save_screenshot("screenshots/error.png")
        raise
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
'''
    
    def _get_automation_logic(self, prompt: str) -> str:
        """Generate automation logic based on prompt."""
        prompt_lower = prompt.lower()
        
        if "login" in prompt_lower:
            return '''
        # Login automation
        try:
            # Find username field
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[type='text'], input[name*='user'], input[name*='email']"))
            )
            username_field.clear()
            username_field.send_keys("test@example.com")
            
            # Find password field
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_field.clear()
            password_field.send_keys("testpassword")
            
            # Find and click login button
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button:contains('Login'), button:contains('Sign In')")
            login_button.click()
            
            time.sleep(3)
            print("Login attempted")
            
        except Exception as e:
            print(f"Login failed: {e}")
            '''
        
        elif "search" in prompt_lower:
            return '''
        # Search automation
        try:
            # Find search box
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search'], input[name*='search'], input[name*='q']"))
            )
            search_box.clear()
            search_box.send_keys("automation test")
            
            # Submit search
            search_box.submit()
            
            time.sleep(3)
            print("Search completed")
            
        except Exception as e:
            print(f"Search failed: {e}")
            '''
        
        else:
            return '''
        # Generic page interaction
        try:
            # Get page information
            title = driver.title
            print(f"Page title: {title}")
            
            # Count elements
            links = len(driver.find_elements(By.TAG_NAME, "a"))
            buttons = len(driver.find_elements(By.TAG_NAME, "button"))
            inputs = len(driver.find_elements(By.TAG_NAME, "input"))
            
            print(f"Found {links} links, {buttons} buttons, {inputs} inputs")
            
            # Click first available button if any
            if buttons > 0:
                first_button = driver.find_element(By.TAG_NAME, "button")
                if first_button.is_enabled():
                    first_button.click()
                    time.sleep(2)
                    print("Clicked first button")
            
        except Exception as e:
            print(f"Generic automation failed: {e}")
            '''
    
    def _create_project_structure(self, task_id: str, code: str, prompt: str) -> Dict[str, Any]:
        """Create project structure."""
        project_dir = self.projects_dir / task_id
        project_dir.mkdir(exist_ok=True)
        
        # Create files
        files = {
            "main.py": code,
            "requirements.txt": "selenium\nwebdriver-manager",
            "README.md": f"""# Automation Project: {task_id}

## Description
{prompt}

## Generated: {datetime.now().isoformat()}

## Usage
```bash
pip install -r requirements.txt
python main.py
```
""",
            "config.py": """# Configuration settings
HEADLESS = True
TIMEOUT = 30
SCREENSHOTS_DIR = "screenshots"
""",
        }
        
        # Save files to disk
        for filename, content in files.items():
            file_path = project_dir / filename
            file_path.write_text(content)
        
        return {
            "files": list(files.keys()),
            "contents": files,
            "project_path": str(project_dir)
        }
    
    def cleanup(self):
        """Cleanup resources."""
        pass 