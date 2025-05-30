"""
Logging configuration for automation project
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def setup_project_logging(log_level: str = "INFO", log_file: str = None):
    """Setup comprehensive logging for the project."""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure log file
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"automation_{timestamp}.log"
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            ),
            # Console handler
            logging.StreamHandler()
        ]
    )
    
    # Configure specific loggers
    selenium_logger = logging.getLogger('selenium')
    selenium_logger.setLevel(logging.WARNING)
    
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.WARNING)
    
    # Create automation logger
    automation_logger = logging.getLogger('automation')
    automation_logger.setLevel(getattr(logging, log_level.upper()))
    
    logging.info("Logging configuration completed")
    logging.info(f"Log file: {log_file}")
    logging.info(f"Log level: {log_level}")
    
    return automation_logger

class AutomationLogger:
    """Custom logger for automation operations."""
    
    def __init__(self, name: str = "automation"):
        self.logger = logging.getLogger(name)
    
    def step(self, message: str):
        """Log an automation step."""
        self.logger.info(f"STEP: {message}")
        print(f"🔹 {message}")
    
    def success(self, message: str):
        """Log a success message."""
        self.logger.info(f"SUCCESS: {message}")
        print(f"✅ {message}")
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(f"ERROR: {message}")
        print(f"❌ {message}")
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(f"WARNING: {message}")
        print(f"⚠️ {message}")
    
    def retry(self, message: str, attempt: int, max_attempts: int):
        """Log a retry attempt."""
        self.logger.warning(f"RETRY {attempt}/{max_attempts}: {message}")
        print(f"🔄 Retry {attempt}/{max_attempts}: {message}")
    
    def browser_action(self, action: str, element: str = ""):
        """Log a browser action."""
        message = f"BROWSER: {action}"
        if element:
            message += f" on {element}"
        self.logger.info(message)
        print(f"🌐 {message}")
