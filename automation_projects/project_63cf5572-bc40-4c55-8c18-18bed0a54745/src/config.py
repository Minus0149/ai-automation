"""
Project Configuration for Automation Workflow
Generated for: Test case 1: Positive LogIn test
            Open page
            Type username student into Username field
            Type password Password123 into Password field
            Push Submit button
            Verify new page URL contains practicetestautomation.com/logged-in-successfully/
            Verify new page contains expected text ('Congratulations' or 'successfully logged in')
            Verify button Log out is displayed on the new page
Workflow ID: 63cf5572-bc40-4c55-8c18-18bed0a54745
"""

import os
from pathlib import Path

class Config:
    """Configuration class for automation project."""
    
    # Project info
    PROJECT_ID = "63cf5572-bc40-4c55-8c18-18bed0a54745"
    PROJECT_NAME = "automation_project"
    TASK_DESCRIPTION = """Test case 1: Positive LogIn test
            Open page
            Type username student into Username field
            Type password Password123 into Password field
            Push Submit button
            Verify new page URL contains practicetestautomation.com/logged-in-successfully/
            Verify new page contains expected text ('Congratulations' or 'successfully logged in')
            Verify button Log out is displayed on the new page"""
    
    # Directories
    BASE_DIR = Path(__file__).parent.parent
    SRC_DIR = BASE_DIR / "src"
    TESTS_DIR = BASE_DIR / "tests"
    LOGS_DIR = BASE_DIR / "logs"
    SCREENSHOTS_DIR = BASE_DIR / "screenshots"
    RESULTS_DIR = BASE_DIR / "results"
    
    # Browser settings
    BROWSER_TYPE = "chrome"  # chrome or edge
    HEADLESS = False  # Set to True for headless mode
    WINDOW_SIZE = (1920, 1080)
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 30
    
    # Execution settings
    MAX_RETRIES = 5
    RETRY_DELAY = 2
    SCREENSHOT_ON_ERROR = True
    SAVE_EXECUTION_LOGS = True
    
    # Output settings
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories."""
        for directory in [cls.LOGS_DIR, cls.SCREENSHOTS_DIR, cls.RESULTS_DIR]:
            directory.mkdir(exist_ok=True)
    
    @classmethod
    def get_chrome_options(cls):
        """Get Chrome browser options."""
        from selenium.webdriver.chrome.options import Options
        options = Options()
        
        if cls.HEADLESS:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={cls.WINDOW_SIZE[0]},{cls.WINDOW_SIZE[1]}")
        options.add_argument("--start-maximized")
        
        return options
    
    @classmethod
    def get_edge_options(cls):
        """Get Edge browser options."""
        from selenium.webdriver.edge.options import Options
        options = Options()
        
        if cls.HEADLESS:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={cls.WINDOW_SIZE[0]},{cls.WINDOW_SIZE[1]}")
        options.add_argument("--start-maximized")
        
        return options
