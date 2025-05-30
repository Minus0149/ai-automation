"""
Project Configuration for Automation Workflow
Generated for: test login functionality with username student and password Password123
Workflow ID: a88b2dac-16c3-4ce3-8bbc-09efdeba51f8
"""

import os
from pathlib import Path

class Config:
    """Configuration class for automation project."""
    
    # Project info
    PROJECT_ID = "a88b2dac-16c3-4ce3-8bbc-09efdeba51f8"
    PROJECT_NAME = "automation_project"
    TASK_DESCRIPTION = """test login functionality with username student and password Password123"""
    
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
