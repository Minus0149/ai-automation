"""
Edge WebDriver Executor - Windows Compatible Alternative
Uses Microsoft Edge which is built into Windows 10/11
"""

import os
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

class EdgeExecutor:
    """Executor using Microsoft Edge WebDriver for Windows compatibility."""
    
    def __init__(self):
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def create_driver(self) -> webdriver.Edge:
        """Create and return an Edge WebDriver instance."""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")
            
            # Disable logging
            options.add_argument("--log-level=3")
            options.add_argument("--silent")
            
            try:
                # Try using webdriver-manager for Edge
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                service = Service(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
                print("✅ Edge driver created successfully using webdriver-manager")
                
            except Exception as e:
                print(f"webdriver-manager failed: {e}")
                
                # Try using system Edge (usually available on Windows 10/11)
                try:
                    driver = webdriver.Edge(options=options)
                    print("✅ Edge driver created using system Edge")
                except Exception as e2:
                    print(f"System Edge failed: {e2}")
                    raise Exception(f"All Edge driver methods failed. Last error: {e2}")
            
            # Set timeouts
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            # Test the driver
            try:
                driver.get("data:text/html,<html><body><h1>Test Page</h1></body></html>")
                print("✅ Edge driver test successful")
            except Exception as test_error:
                print(f"Driver test failed: {test_error}")
                driver.quit()
                raise Exception(f"Edge driver test failed: {test_error}")
            
            return driver
            
        except Exception as e:
            error_msg = f"Failed to create Edge driver: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def execute_code(self, code: str, website_url: str, timeout: int = 180) -> Dict[str, Any]:
        """Execute Selenium code using Edge driver."""
        start_time = time.time()
        logs = []
        screenshots = []
        driver = None
        
        try:
            driver = self.create_driver()
            
            logs.append({
                "level": "info",
                "message": "Edge driver initialized successfully",
                "timestamp": datetime.now().isoformat(),
                "source": "edge_executor"
            })
            
            # Navigate to website
            logs.append({
                "level": "info",
                "message": f"Navigating to: {website_url}",
                "timestamp": datetime.now().isoformat(),
                "source": "edge_executor"
            })
            
            driver.get(website_url)
            
            # Take initial screenshot
            screenshot_path = self._take_screenshot(driver, "initial_page")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            # Execute the user code
            logs.append({
                "level": "info",
                "message": "Executing user code",
                "timestamp": datetime.now().isoformat(),
                "source": "edge_executor"
            })
            
            # Create execution environment
            exec_globals = {
                'driver': driver,
                'By': webdriver.common.by.By,
                'WebDriverWait': webdriver.support.ui.WebDriverWait,
                'expected_conditions': webdriver.support.expected_conditions,
                'time': time,
                'print': self._custom_print_function(logs)
            }
            
            # Execute the code
            exec(code, exec_globals)
            
            # Take final screenshot
            screenshot_path = self._take_screenshot(driver, "final_result")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            logs.append({
                "level": "info",
                "message": "Code execution completed successfully",
                "timestamp": datetime.now().isoformat(),
                "source": "edge_executor"
            })
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "logs": logs,
                "screenshots": screenshots,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Take error screenshot
            if driver:
                screenshot_path = self._take_screenshot(driver, "error")
                if screenshot_path:
                    screenshots.append(screenshot_path)
            
            logs.append({
                "level": "error",
                "message": f"Execution error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "source": "edge_executor",
                "traceback": traceback.format_exc()
            })
            
            return {
                "success": False,
                "logs": logs,
                "screenshots": screenshots,
                "execution_time": execution_time,
                "error": str(e)
            }
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def scrape_page_content(self, url: str) -> Dict[str, Any]:
        """Scrape page content using Edge driver."""
        driver = None
        try:
            driver = self.create_driver()
            driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Get page content
            page_source = driver.page_source
            page_title = driver.title
            current_url = driver.current_url
            
            # Take screenshot
            screenshot_path = self._take_screenshot(driver, f"scrape_{int(time.time())}")
            
            # Get basic page elements for analysis
            elements_info = {
                'links': len(driver.find_elements('tag name', 'a')),
                'forms': len(driver.find_elements('tag name', 'form')),
                'inputs': len(driver.find_elements('tag name', 'input')),
                'buttons': len(driver.find_elements('tag name', 'button')),
            }
            
            return {
                "success": True,
                "url": current_url,
                "title": page_title,
                "content_length": len(page_source),
                "elements": elements_info,
                "screenshot": screenshot_path,
                "page_source": page_source[:5000] if page_source else ""
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
        finally:
            if driver:
                driver.quit()
    
    def _take_screenshot(self, driver, name: str) -> Optional[str]:
        """Take and save a screenshot."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            driver.save_screenshot(str(filepath))
            return str(filepath)
            
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None
    
    def _custom_print_function(self, logs: list):
        """Create a custom print function that logs to our logs list."""
        def custom_print(*args, **kwargs):
            message = " ".join(str(arg) for arg in args)
            logs.append({
                "level": "info",
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "source": "user_code"
            })
            # Also print to console
            print(*args, **kwargs)
        
        return custom_print
    
    def cleanup(self):
        """Clean up resources."""
        pass