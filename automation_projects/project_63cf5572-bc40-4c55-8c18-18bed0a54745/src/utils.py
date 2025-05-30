"""
Utility functions for automation project
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    from logging_config import setup_project_logging
    return setup_project_logging(log_level, log_file)

def take_screenshot(driver, name: str, directory: str = "screenshots") -> Optional[str]:
    """Take and save a screenshot."""
    try:
        screenshot_dir = Path(directory)
        screenshot_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = screenshot_dir / filename
        
        driver.save_screenshot(str(filepath))
        logging.info(f"Screenshot saved: {filepath}")
        return str(filepath)
        
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")
        return None

def save_execution_result(result: Dict[str, Any], filename: str, directory: str = "results") -> Optional[str]:
    """Save execution result to JSON file."""
    try:
        results_dir = Path(directory)
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_with_timestamp = f"{filename}_{timestamp}.json"
        filepath = results_dir / filename_with_timestamp
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        logging.info(f"Result saved: {filepath}")
        return str(filepath)
        
    except Exception as e:
        logging.error(f"Failed to save result: {e}")
        return None

def wait_for_element(driver, by, value, timeout=10):
    """Wait for element to be present and return it."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except Exception as e:
        logging.error(f"Element not found: {by}={value}, error: {e}")
        return None

def wait_for_clickable(driver, by, value, timeout=10):
    """Wait for element to be clickable and return it."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except Exception as e:
        logging.error(f"Element not clickable: {by}={value}, error: {e}")
        return None

def retry_operation(func, max_retries=3, delay=1, *args, **kwargs):
    """Retry an operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            else:
                wait_time = delay * (2 ** attempt)
                logging.warning(f"Operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                logging.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

def log_execution_step(step_name: str, details: str = "", level: str = "INFO"):
    """Log an execution step with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {step_name}"
    if details:
        message += f" - {details}"
    
    if level.upper() == "INFO":
        logging.info(message)
    elif level.upper() == "ERROR":
        logging.error(message)
    elif level.upper() == "WARNING":
        logging.warning(message)
    elif level.upper() == "DEBUG":
        logging.debug(message)
    
    print(message)

def cleanup_old_files(directory: str, max_age_days: int = 7):
    """Clean up old files in a directory."""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return
        
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        for file_path in dir_path.glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                logging.info(f"Cleaned up old file: {file_path}")
                
    except Exception as e:
        logging.error(f"Failed to cleanup old files: {e}")

def get_browser_info(driver):
    """Get browser information for logging."""
    try:
        caps = driver.capabilities
        browser_name = caps.get('browserName', 'unknown')
        browser_version = caps.get('version', caps.get('browserVersion', 'unknown'))
        
        return {
            "name": browser_name,
            "version": browser_version,
            "platform": caps.get('platform', caps.get('platformName', 'unknown'))
        }
    except Exception as e:
        logging.error(f"Failed to get browser info: {e}")
        return {"name": "unknown", "version": "unknown", "platform": "unknown"}
