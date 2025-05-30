"""
Selenium Executor - Chrome WebDriver Implementation with Windows compatibility
"""
import os
import time
import json
import tempfile
import zipfile
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

# WebDriver Manager with fallback
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

import requests
import subprocess


class SeleniumExecutor:
    """Selenium automation executor with Chrome driver management."""
    
    def __init__(self):
        self.drivers = []
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.chrome_binary_path = None
        self.driver_path = None
        
    def create_chrome_driver(self, headless: bool = True) -> Optional[webdriver.Chrome]:
        """Create Chrome WebDriver with comprehensive Windows compatibility."""
        try:
            options = Options()
            
            # Essential Chrome options for automation
            if headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--window-size=1920,1080")
            
            # Force Windows x64 architecture if on Windows
            if platform.system() == "Windows":
                os.environ["WDM_ARCHITECTURE"] = "64"
                
            service = None
            driver = None
            
            # Method 1: Try webdriver-manager with architecture fix
            if WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    # Clear cache if wrong architecture was downloaded
                    cache_path = Path.home() / ".wdm" / "drivers" / "chromedriver"
                    if cache_path.exists():
                        for chrome_dir in cache_path.iterdir():
                            if chrome_dir.is_dir():
                                for version_dir in chrome_dir.iterdir():
                                    if version_dir.is_dir():
                                        chromedriver_exe = version_dir / "chromedriver.exe"
                                        if chromedriver_exe.exists():
                                            # Test if it's the right architecture
                                            try:
                                                result = subprocess.run([str(chromedriver_exe), "--version"], 
                                                                      capture_output=True, text=True, timeout=5)
                                                if result.returncode != 0:
                                                    print("Wrong architecture detected, cleaning cache...")
                                                    import shutil
                                                    shutil.rmtree(str(chrome_dir))
                                                    break
                                            except Exception:
                                                print("Wrong architecture detected, cleaning cache...")
                                                import shutil
                                                shutil.rmtree(str(chrome_dir))
                                                break
                    
                    # Download correct driver
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    print("Chrome driver created successfully using webdriver-manager")
                    return driver
                    
                except Exception as e:
                    print(f"webdriver-manager failed: {e}")
            
            # Method 2: Try manual download with correct architecture
            try:
                driver_path = self._download_chrome_driver()
                if driver_path:
                    service = Service(driver_path)
                    driver = webdriver.Chrome(service=service, options=options)
                    print("Chrome driver created using manual download")
                    return driver
            except Exception as e:
                print(f"Manual driver download failed: {e}")
            
            # Method 3: Try to find system Chrome and use with downloaded driver
            try:
                chrome_path = self._find_chrome_binary()
                if chrome_path:
                    options.binary_location = chrome_path
                    print(f"Chrome driver created using system Chrome at: {chrome_path}")
                    
                    # Try with manual driver path
                    if self.driver_path and Path(self.driver_path).exists():
                        service = Service(self.driver_path)
                        driver = webdriver.Chrome(service=service, options=options)
                        return driver
                        
            except Exception as e:
                print(f"System Chrome method failed: {e}")
            
            # Method 4: Last resort - try without service
            try:
                driver = webdriver.Chrome(options=options)
                return driver
            except Exception as e:
                print(f"Default Chrome creation failed: {e}")
            
            return None
            
        except Exception as e:
            print(f"Chrome driver creation completely failed: {e}")
            return None
    
    def test_driver(self, driver: webdriver.Chrome) -> bool:
        """Test if the driver works correctly."""
        try:
            driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
            title = driver.title
            print("Chrome driver test successful")
            return True
        except Exception as e:
            return False
    
    def execute_automation(self, url: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute automation with Chrome driver."""
        start_time = time.time()
        driver = None
        logs = []
        screenshots = []
        
        try:
            # Create driver
            driver = self.create_chrome_driver()
            if not driver:
                error_msg = "Failed to create Chrome driver after all attempts"
                print(f"ERROR: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "logs": logs,
                    "screenshots": screenshots,
                    "execution_time": time.time() - start_time,
                    "troubleshooting": {
                        "suggestions": [
                            "Install Google Chrome browser",
                            "Check if Chrome is in PATH",
                            "Try running: pip install webdriver-manager",
                            "Check Windows architecture (32-bit vs 64-bit)",
                            "Run check_chrome.py for detailed diagnostics"
                        ]
                    }
                }
            
            self.drivers.append(driver)
            
            logs.append({
                "level": "info",
                "message": "Chrome driver created successfully",
                "timestamp": datetime.now().isoformat()
            })
            
            # Execute actions
            for i, action in enumerate(actions):
                try:
                    self._execute_action(driver, action, logs, screenshots)
                except Exception as action_error:
                    logs.append({
                        "level": "error",
                        "message": f"Action {i+1} failed: {str(action_error)}",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Take final screenshot
            screenshot_path = self._take_screenshot(driver, "final")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            execution_time = time.time() - start_time
            
            logs.append({
                "level": "info",
                "message": f"Automation completed in {execution_time:.2f}s",
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "logs": logs,
                "screenshots": screenshots,
                "execution_time": execution_time,
                "actions_completed": len(actions)
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logs.append({
                "level": "error",
                "message": f"Automation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": False,
                "error": str(e),
                "logs": logs,
                "screenshots": screenshots,
                "execution_time": execution_time
            }
            
        finally:
            if driver:
                try:
                    driver.quit()
                    if driver in self.drivers:
                        self.drivers.remove(driver)
                except Exception as e:
                    print(f"Error closing driver: {e}")
    
    def _execute_action(self, driver: webdriver.Chrome, action: Dict[str, Any], 
                       logs: List[Dict[str, Any]], screenshots: List[str]):
        """Execute a single action."""
        action_type = action.get("type", "")
        
        if action_type == "navigate":
            url = action.get("url", "")
            driver.get(url)
            logs.append({
                "level": "info",
                "message": f"Navigated to: {url}",
                "timestamp": datetime.now().isoformat()
            })
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
        elif action_type == "click":
            selector = action.get("selector", "")
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            logs.append({
                "level": "info",
                "message": f"Clicked element: {selector}",
                "timestamp": datetime.now().isoformat()
            })
            
        elif action_type == "type":
            selector = action.get("selector", "")
            text = action.get("text", "")
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            logs.append({
                "level": "info",
                "message": f"Typed text in {selector}: {text}",
                "timestamp": datetime.now().isoformat()
            })
            
        elif action_type == "wait":
            duration = action.get("duration", 1)
            time.sleep(duration)
            logs.append({
                "level": "info",
                "message": f"Waited for {duration} seconds",
                "timestamp": datetime.now().isoformat()
            })
            
        elif action_type == "screenshot":
            name = action.get("name", "action")
            screenshot_path = self._take_screenshot(driver, name)
            if screenshot_path:
                screenshots.append(screenshot_path)
                logs.append({
                    "level": "info",
                    "message": f"Screenshot saved: {screenshot_path}",
                    "timestamp": datetime.now().isoformat()
                })
    
    def _take_screenshot(self, driver: webdriver.Chrome, name: str) -> Optional[str]:
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
    
    def _download_chrome_driver(self) -> Optional[str]:
        """Download ChromeDriver manually with correct architecture."""
        try:
            # Get Chrome version
            chrome_version = self._get_chrome_version()
            if not chrome_version:
                return None
            
            # Determine architecture
            arch = "win64" if platform.machine().endswith('64') else "win32"
            
            # ChromeDriver download URL
            major_version = chrome_version.split('.')[0]
            
            # For Chrome 115+, use different API
            if int(major_version) >= 115:
                api_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
                try:
                    response = requests.get(api_url, timeout=10)
                    if response.status_code == 200:
                        driver_version = response.text.strip()
                    else:
                        # Fallback: try to find compatible version
                        driver_version = chrome_version
                except:
                    driver_version = chrome_version
            else:
                driver_version = chrome_version
            
            download_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_{arch}.zip"
            
            # Download to temp directory
            temp_dir = Path(tempfile.gettempdir()) / "chromedriver_download"
            temp_dir.mkdir(exist_ok=True)
            
            zip_path = temp_dir / "chromedriver.zip"
            
            print(f"Downloading ChromeDriver from: {download_url}")
            
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            with open(zip_path, "wb") as f:
                f.write(response.content)
            
            # Extract
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            
            driver_exe = temp_dir / "chromedriver.exe"
            if driver_exe.exists():
                self.driver_path = str(driver_exe)
                return str(driver_exe)
            
            return None
            
        except Exception as e:
            print(f"Manual ChromeDriver download failed: {e}")
            return None
    
    def _get_chrome_version(self) -> Optional[str]:
        """Get installed Chrome version."""
        try:
            if platform.system() == "Windows":
                # Try registry first
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                        r"Software\Google\Chrome\BLBeacon")
                    version, _ = winreg.QueryValueEx(key, "version")
                    winreg.CloseKey(key)
                    return version
                except:
                    pass
                
                # Try command line
                try:
                    result = subprocess.run([
                        "reg", "query", 
                        "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon",
                        "/v", "version"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'version' in line:
                                version = line.split()[-1]
                                return version
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"Failed to get Chrome version: {e}")
            return None
    
    def _find_chrome_binary(self) -> Optional[str]:
        """Find Chrome binary path."""
        try:
            if platform.system() == "Windows":
                possible_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        self.chrome_binary_path = path
                        return path
            
            return None
            
        except Exception as e:
            print(f"Failed to find Chrome binary: {e}")
            return None
    
    def scrape_page_content(self, url: str) -> Dict[str, Any]:
        """Scrape page content for analysis."""
        start_time = time.time()
        driver = None
        
        try:
            driver = self.create_chrome_driver()
            if not driver:
                return {
                    "success": False,
                    "error": "Failed to create Chrome driver"
                }
            
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract page information
            title = driver.title
            page_source = driver.page_source
            
            # Find interactive elements
            inputs = driver.find_elements(By.TAG_NAME, "input")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            links = driver.find_elements(By.TAG_NAME, "a")
            
            return {
                "success": True,
                "url": url,
                "title": title,
                "page_source": page_source[:2000],  # First 2000 chars
                "elements": {
                    "inputs": len(inputs),
                    "buttons": len(buttons),
                    "links": len(links)
                },
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "execution_time": time.time() - start_time
            }
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def execute_code(self, code: str, website_url: str) -> Dict[str, Any]:
        """Execute custom Selenium code."""
        start_time = time.time()
        driver = None
        logs = []
        screenshots = []
        
        try:
            driver = self.create_chrome_driver()
            if not driver:
                return {
                    "success": False,
                    "error": "Failed to create Chrome driver",
                    "logs": logs,
                    "screenshots": screenshots,
                    "execution_time": time.time() - start_time
                }
            
            # Create execution environment
            exec_globals = {
                "driver": driver,
                "By": By,
                "WebDriverWait": WebDriverWait,
                "EC": EC,
                "time": time,
                "website_url": website_url,
                "print": lambda x: logs.append({
                    "level": "info",
                    "message": str(x),
                    "timestamp": datetime.now().isoformat()
                })
            }
            
            # Execute the code
            exec(code, exec_globals)
            
            # Take screenshot
            screenshot_path = self._take_screenshot(driver, "execution_result")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            return {
                "success": True,
                "logs": logs,
                "screenshots": screenshots,
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            logs.append({
                "level": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": False,
                "error": str(e),
                "logs": logs,
                "screenshots": screenshots,
                "execution_time": time.time() - start_time
            }
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def close_all_drivers(self):
        """Close all active drivers."""
        for driver in self.drivers[:]:
            try:
                driver.quit()
                self.drivers.remove(driver)
            except Exception as e:
                print(f"Error closing driver: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        self.close_all_drivers() 