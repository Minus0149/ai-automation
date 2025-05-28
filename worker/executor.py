import logging
import tempfile
import os
import sys
import subprocess
import base64
import json
import traceback
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import psutil

# Resource module is Unix-specific, make it optional for Windows
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    # Windows doesn't have the resource module
    HAS_RESOURCE = False
    
from threading import Timer
import gc

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Configure logging with Windows-compatible paths
import platform

# Use Windows-compatible temp directory
TEMP_DIR = tempfile.gettempdir()
LOG_FILE = os.path.join(TEMP_DIR, 'executor.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s]: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE)
    ]
)

logger = logging.getLogger('selenium-executor')

class ExecutionLog:
    def __init__(self, timestamp: datetime, level: str, message: str, data: Optional[Dict[str, Any]] = None):
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.data = data
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "data": self.data
        }

class TaskStatus:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.status = "running"
        self.start_time = datetime.now()
        self.process = None
        self.logs: List[ExecutionLog] = []
    
    def add_log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None):
        log = ExecutionLog(datetime.now(), level, message, data)
        self.logs.append(log)
        logger.log(getattr(logging, level.upper(), logging.INFO), f"Task {self.task_id}: {message}")

class ResourceMonitor:
    def __init__(self, max_memory_mb: int = 512, max_cpu_percent: int = 80):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        self.process = psutil.Process()
        
    def check_resources(self):
        """Check if resource usage is within limits."""
        try:
            memory_usage = self.process.memory_info().rss / 1024 / 1024  # MB
            cpu_percent = self.process.cpu_percent()
            
            if memory_usage > self.max_memory_mb:
                logger.warning(f"Memory usage {memory_usage:.2f}MB exceeds limit {self.max_memory_mb}MB")
                return False, f"Memory limit exceeded: {memory_usage:.2f}MB"
                
            if cpu_percent > self.max_cpu_percent:
                logger.warning(f"CPU usage {cpu_percent:.2f}% exceeds limit {self.max_cpu_percent}%")
                return False, f"CPU limit exceeded: {cpu_percent:.2f}%"
                
            return True, f"Memory: {memory_usage:.2f}MB, CPU: {cpu_percent:.2f}%"
            
        except Exception as e:
            logger.error(f"Resource monitoring error: {e}")
            return True, "Resource monitoring failed"

def cleanup_selenium_resources(driver):
    """Comprehensive cleanup of Selenium resources."""
    try:
        if driver:
            # Close all windows
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                driver.close()
            
            # Quit the driver
            driver.quit()
            
        # Force garbage collection
        gc.collect()
        
        # Kill any remaining browser processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if any(name in proc.info['name'].lower() for name in ['chrome', 'chromium', 'firefox', 'gecko']):
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

class SeleniumExecutor:
    """Executes Selenium automation scripts in a sandboxed environment."""
    
    def __init__(self):
        self.active_tasks: Dict[str, TaskStatus] = {}
        self.sandbox_dir = os.path.join(TEMP_DIR, "selenium_sandbox")
        self.screenshots_dir = os.path.join(TEMP_DIR, "screenshots")
        self.max_execution_time = 120  # 2 minutes
        self.setup_directories()
        self.driver = None
        self.setup_chrome_options()
        logger.info("SeleniumExecutor initialized")
        
    def setup_directories(self):
        """Setup sandbox and screenshots directories."""
        try:
            os.makedirs(self.sandbox_dir, exist_ok=True)
            os.makedirs(self.screenshots_dir, exist_ok=True)
            logger.info(f"Directories created: {self.sandbox_dir}, {self.screenshots_dir}")
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            raise
    
    def setup_chrome_options(self):
        """Setup Chrome options for headless execution"""
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-plugins")
        self.chrome_options.add_argument("--disable-images")
        self.chrome_options.add_argument("--disable-javascript")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    def get_driver(self):
        """Get or create a Chrome WebDriver instance"""
        if self.driver is None:
            try:
                # Set up Chrome options
                options = self.get_chrome_options()
                
                # Enhanced ChromeDriver path resolution
                driver_path = None
                
                # Method 1: Try ChromeDriverManager first
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    logger.info("Attempting ChromeDriverManager...")
                    
                    manager_path = ChromeDriverManager().install()
                    logger.info(f"ChromeDriverManager returned: {manager_path}")
                    
                    # Validate the path on Windows
                    if sys.platform.startswith('win'):
                        if manager_path and not manager_path.endswith('chromedriver.exe'):
                            logger.info("ChromeDriverManager returned invalid path, searching for correct file...")
                            
                            # Get the base directory
                            base_dir = os.path.dirname(manager_path)
                            if not os.path.exists(base_dir):
                                base_dir = manager_path
                            
                            # Search directories
                            search_dirs = [
                                base_dir,
                                os.path.dirname(base_dir),
                                os.path.join(base_dir, "chromedriver-win32"),
                                os.path.join(os.path.dirname(base_dir), "chromedriver-win32"),
                            ]
                            
                            found = False
                            for search_dir in search_dirs:
                                if not os.path.exists(search_dir):
                                    continue
                                    
                                logger.info(f"Searching in: {search_dir}")
                                
                                # Walk through directory tree
                                for root, dirs, files in os.walk(search_dir):
                                    for file in files:
                                        if file == 'chromedriver.exe':
                                            test_path = os.path.join(root, file)
                                            
                                            # Validate the executable
                                            if (os.path.exists(test_path) and 
                                                os.access(test_path, os.X_OK) and 
                                                os.path.getsize(test_path) > 1000000):  # > 1MB
                                                
                                                driver_path = test_path
                                                logger.info(f"Found valid chromedriver.exe: {driver_path}")
                                                found = True
                                                break
                                    if found:
                                        break
                                if found:
                                    break
                        else:
                            # Path looks good, validate it
                            if (os.path.exists(manager_path) and 
                                os.access(manager_path, os.X_OK) and 
                                os.path.getsize(manager_path) > 1000000):
                                driver_path = manager_path
                                logger.info(f"ChromeDriverManager path validated: {driver_path}")
                                
                except Exception as manager_error:
                    logger.error(f"ChromeDriverManager failed: {manager_error}")
                
                # Method 2: If ChromeDriverManager failed, try system PATH
                if not driver_path:
                    logger.info("Trying system PATH for chromedriver...")
                    import shutil
                    system_driver = shutil.which('chromedriver')
                    if system_driver and os.path.exists(system_driver):
                        driver_path = system_driver
                        logger.info(f"Found chromedriver in system PATH: {driver_path}")
                
                # Method 3: Manual search in common locations
                if not driver_path:
                    logger.info("Searching common ChromeDriver locations...")
                    
                    common_paths = [
                        os.path.expanduser("~/.wdm/drivers/chromedriver"),
                        "C:\\chromedriver\\chromedriver.exe",
                        "C:\\Program Files\\chromedriver\\chromedriver.exe",
                        "C:\\Program Files (x86)\\chromedriver\\chromedriver.exe",
                        os.path.join(os.getcwd(), "chromedriver.exe"),
                    ]
                    
                    for path in common_paths:
                        if os.path.exists(path):
                            if path.endswith('.exe'):
                                test_path = path
                            else:
                                # Search in directory
                                for root, dirs, files in os.walk(path):
                                    for file in files:
                                        if file == 'chromedriver.exe':
                                            test_path = os.path.join(root, file)
                                            break
                            
                            if (os.path.exists(test_path) and 
                                os.access(test_path, os.X_OK) and 
                                os.path.getsize(test_path) > 1000000):
                                driver_path = test_path
                                logger.info(f"Found chromedriver in common location: {driver_path}")
                                break
                
                # Final validation
                if not driver_path or not os.path.exists(driver_path):
                    raise Exception("No valid ChromeDriver found anywhere")
                
                if not os.access(driver_path, os.X_OK):
                    raise Exception(f"ChromeDriver is not executable: {driver_path}")
                
                if os.path.getsize(driver_path) < 1000000:
                    raise Exception(f"ChromeDriver file too small: {driver_path}")
                
                logger.info(f"Using verified ChromeDriver: {driver_path}")
                
                # Create service with verified driver path
                from selenium.webdriver.chrome.service import Service
                service = Service(driver_path)
                
                self.driver = webdriver.Chrome(service=service, options=options)
                logger.info("✅ Chrome WebDriver created successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to create Chrome WebDriver: {str(e)}")
                raise

        return self.driver

    def close_driver(self):
        """Close the WebDriver instance"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    async def initialize(self):
        """Initialize the executor"""
        # Ensure Chrome driver is available
        try:
            self.chrome_driver_path = ChromeDriverManager().install()
            logger.info(f"Chrome driver available at: {self.chrome_driver_path}")
        except Exception as e:
            logger.error(f"Failed to install Chrome driver: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources"""
        # Cancel all active tasks
        for task_id in list(self.active_tasks.keys()):
            self.cancel_task(task_id)
        
        # Clean up sandbox directory
        if self.sandbox_dir and self.sandbox_dir.exists():
            import shutil
            shutil.rmtree(self.sandbox_dir)
            logger.info("Cleaned up sandbox directory")
        
        # Close the WebDriver
        self.close_driver()
    
    def create_selenium_script(self, user_code: str, website_url: str) -> str:
        """Creates a complete Selenium script with proper setup and teardown."""
        logger.info(f"Creating Selenium script for website: {website_url}")
        
        # Use Windows-compatible temp directory
        windows_temp = TEMP_DIR.replace('\\', '/')
        
        # Properly indent user code to fit in the try block
        indented_user_code = self._indent_code(user_code, 4)
        
        script_template = f'''
import sys
import os
import time
import json
import logging
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging for the script
logging.basicConfig(level=logging.INFO)
script_logger = logging.getLogger('selenium_script')

# Results dictionary
execution_result = {{
    "success": False,
    "logs": [],
    "screenshots": [],
    "error": None,
    "execution_time": 0,
    "start_time": datetime.now().isoformat()
}}

def log_info(message):
    script_logger.info(message)
    execution_result["logs"].append({{
        "level": "info",
        "message": str(message),
        "timestamp": datetime.now().isoformat()
    }})

def log_error(message):
    script_logger.error(message)
    execution_result["logs"].append({{
        "level": "error", 
        "message": str(message),
        "timestamp": datetime.now().isoformat()
    }})

def log_warning(message):
    script_logger.warning(message)
    execution_result["logs"].append({{
        "level": "warning",
        "message": str(message),
        "timestamp": datetime.now().isoformat()
    }})

def take_screenshot(driver, name="screenshot"):
    try:
        screenshot_path = r"{windows_temp}\\screenshots\\{{name}}_{{int(time.time())}}.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        driver.save_screenshot(screenshot_path)
        execution_result["screenshots"].append(screenshot_path)
        log_info(f"Screenshot saved: {{screenshot_path}}")
        return screenshot_path
    except Exception as e:
        log_error(f"Failed to take screenshot: {{e}}")
        return None

start_time = time.time()

try:
    log_info("Starting Selenium automation script")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Initialize WebDriver
    log_info("Initializing Chrome WebDriver")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    
    # Navigate to website
    log_info(f"Navigating to: {website_url}")
    driver.get("{website_url}")
    
    # Take initial screenshot
    take_screenshot(driver, "initial")
    log_info(f"Successfully loaded: {{driver.title}}")
    
    # Execute user code
    log_info("Executing user automation code")
{indented_user_code}
    
    # Take final screenshot
    take_screenshot(driver, "final")
    
    execution_result["success"] = True
    execution_result["execution_time"] = time.time() - start_time
    log_info(f"Script executed successfully in {{execution_result['execution_time']:.2f}} seconds")

except TimeoutException as e:
    execution_result["error"] = f"Timeout error: {{str(e)}}"
    log_error(execution_result["error"])
    if 'driver' in locals():
        take_screenshot(driver, "timeout_error")

except NoSuchElementException as e:
    execution_result["error"] = f"Element not found: {{str(e)}}"
    log_error(execution_result["error"])
    if 'driver' in locals():
        take_screenshot(driver, "element_not_found")

except WebDriverException as e:
    execution_result["error"] = f"WebDriver error: {{str(e)}}"
    log_error(execution_result["error"])

except Exception as e:
    execution_result["error"] = f"Unexpected error: {{str(e)}}"
    log_error(execution_result["error"])
    log_error(f"Traceback: {{traceback.format_exc()}}")
    if 'driver' in locals():
        take_screenshot(driver, "error")

finally:
    try:
        if 'driver' in locals():
            log_info("Closing WebDriver")
            driver.quit()
    except Exception as e:
        log_error(f"Error closing driver: {{e}}")
    
    execution_result["execution_time"] = time.time() - start_time
    
    # Save results to file
    result_file = r"{windows_temp}\\execution_result.json"
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, "w") as f:
        json.dump(execution_result, f, indent=2)
    
    log_info("Script execution completed")
'''
        
        logger.info("Selenium script template created successfully")
        return script_template
    
    def execute_script(self, code: str, website_url: str, timeout: int = 60) -> Dict[str, Any]:
        """Execute Selenium code in a sandboxed environment."""
        logger.info(f"Starting script execution for {website_url}")
        execution_start = time.time()
        
        try:
            # Create the complete script
            full_script = self.create_selenium_script(code, website_url)
            
            # Create temporary script file
            script_path = os.path.join(self.sandbox_dir, f"script_{int(time.time())}.py")
            
            with open(script_path, 'w') as f:
                f.write(full_script)
            
            logger.info(f"Script written to: {script_path}")
            
            # Execute script in subprocess
            result = self._run_script_subprocess(script_path, timeout)
            
            # Clean up script file
            try:
                os.remove(script_path)
                logger.info(f"Cleaned up script file: {script_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up script file: {e}")
            
            execution_time = time.time() - execution_start
            result["total_execution_time"] = execution_time
            
            logger.info(f"Script execution completed in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in execute_script: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "logs": [
                    {
                        "level": "error",
                        "message": f"Execution failed: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "screenshots": [],
                "execution_time": time.time() - execution_start
            }
    
    def _run_script_subprocess(self, script_path: str, timeout: int) -> Dict[str, Any]:
        """Run the script in a subprocess with timeout."""
        logger.info(f"Running script subprocess with timeout: {timeout}s")
        
        try:
            # Run the script
            process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=self.sandbox_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=dict(os.environ, PYTHONPATH="")
            )
            
            logger.info(f"Started subprocess with PID: {process.pid}")
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
                logger.info(f"Subprocess completed with return code: {return_code}")
                
                if stderr:
                    logger.warning(f"Subprocess stderr: {stderr}")
                
                # Try to read execution results
                try:
                    result_file = os.path.join(TEMP_DIR, "execution_result.json")
                    with open(result_file, "r") as f:
                        result = json.load(f)
                    
                    # Add subprocess output to logs
                    if stdout:
                        result["logs"].append({
                            "level": "info",
                            "message": f"Script output: {stdout}",
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    if stderr:
                        result["logs"].append({
                            "level": "error", 
                            "message": f"Script stderr: {stderr}",
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    # Read screenshots
                    result["screenshots"] = self._collect_screenshots()
                    
                    logger.info(f"Execution result: success={result.get('success')}")
                    return result
                    
                except Exception as e:
                    logger.error(f"Failed to read execution result: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to read execution result: {str(e)}",
                        "logs": [
                            {
                                "level": "error",
                                "message": f"Stdout: {stdout}",
                                "timestamp": datetime.now().isoformat()
                            },
                            {
                                "level": "error",
                                "message": f"Stderr: {stderr}",
                                "timestamp": datetime.now().isoformat()
                            }
                        ],
                        "screenshots": [],
                        "execution_time": 0
                    }
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Script execution timed out after {timeout} seconds")
                process.kill()
                process.communicate()
                
                return {
                    "success": False,
                    "error": f"Script execution timed out after {timeout} seconds",
                    "logs": [
                        {
                            "level": "error",
                            "message": f"Execution timed out after {timeout} seconds",
                            "timestamp": datetime.now().isoformat()
                        }
                    ],
                    "screenshots": self._collect_screenshots(),
                    "execution_time": timeout
                }
                
        except Exception as e:
            logger.error(f"Error running subprocess: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return {
                "success": False,
                "error": f"Subprocess error: {str(e)}",
                "logs": [
                    {
                        "level": "error",
                        "message": f"Subprocess error: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "screenshots": [],
                "execution_time": 0
            }
    
    def _collect_screenshots(self) -> List[str]:
        """Collect all screenshots from the screenshots directory."""
        screenshots = []
        try:
            if os.path.exists(self.screenshots_dir):
                for file in os.listdir(self.screenshots_dir):
                    if file.endswith('.png'):
                        full_path = os.path.join(self.screenshots_dir, file)
                        screenshots.append(full_path)
                        
            logger.info(f"Collected {len(screenshots)} screenshots")
            return screenshots
            
        except Exception as e:
            logger.error(f"Error collecting screenshots: {e}")
            return []
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a running task"""
        task_status = self.active_tasks.get(task_id)
        if not task_status:
            return None
        
        return {
            "task_id": task_id,
            "status": task_status.status,
            "start_time": task_status.start_time.isoformat(),
            "logs": [log.to_dict() for log in task_status.logs]
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        task_status = self.active_tasks.get(task_id)
        if not task_status:
            return False
        
        if task_status.process:
            try:
                # Kill the process and its children
                parent = psutil.Process(task_status.process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
                task_status.add_log("info", "Task cancelled by user")
            except (psutil.NoSuchProcess, ProcessLookupError):
                pass  # Process already terminated
        
        task_status.status = "cancelled"
        return True
    
    def list_active_tasks(self) -> List[Dict[str, Any]]:
        """List all active tasks"""
        return [
            {
                "task_id": task_id,
                "status": task_status.status,
                "start_time": task_status.start_time.isoformat()
            }
            for task_id, task_status in self.active_tasks.items()
        ]

    def is_ready(self) -> bool:
        """Check if the executor is ready"""
        try:
            # Try to create a driver instance
            test_driver = self.get_driver()
            if test_driver:
                self.close_driver()
                return True
            return False
        except Exception:
            return False

    def check_chrome(self) -> bool:
        """Check if Chrome is available"""
        try:
            ChromeDriverManager().install()
            return True
        except Exception:
            return False

    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code by the specified number of spaces"""
        lines = code.split('\n')
        indented_lines = [' ' * spaces + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines) 

# Global executor instance
executor = SeleniumExecutor()

def execute_automation(code: str, website_url: str, timeout: int = 60) -> Dict[str, Any]:
    """Main function to execute automation code."""
    logger.info(f"Executing automation for {website_url}")
    
    try:
        result = executor.execute_script(code, website_url, timeout)
        
        # Perform cleanup
        executor.cleanup()
        
        return result
        
    except Exception as e:
        logger.error(f"Error in execute_automation: {e}")
        return {
            "success": False,
            "error": f"Automation execution failed: {str(e)}",
            "logs": [
                {
                    "level": "error",
                    "message": f"Automation execution failed: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "screenshots": [],
            "execution_time": 0
        } 