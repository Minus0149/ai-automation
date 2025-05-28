"""
Sandbox environment for isolated script execution.

This module provides utilities for safe execution of Selenium automation scripts
in an isolated environment with proper resource management and security controls.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# Configure sandbox-specific logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [SANDBOX] [%(levelname)s]: %(message)s'
)

logger = logging.getLogger('sandbox')

# Sandbox configuration
SANDBOX_DIR = Path("/tmp/selenium_sandbox")
SCREENSHOTS_DIR = Path("/tmp/screenshots")
MAX_EXECUTION_TIME = 120  # seconds
MAX_MEMORY_MB = 512
MAX_FILE_SIZE_MB = 10

def ensure_sandbox_directories():
    """Ensure sandbox directories exist with proper permissions."""
    try:
        SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Set restrictive permissions (owner read/write/execute only)
        os.chmod(SANDBOX_DIR, 0o700)
        os.chmod(SCREENSHOTS_DIR, 0o700)
        
        logger.info(f"Sandbox directories initialized: {SANDBOX_DIR}, {SCREENSHOTS_DIR}")
        
    except Exception as e:
        logger.error(f"Failed to initialize sandbox directories: {e}")
        raise

def cleanup_sandbox():
    """Clean up temporary files and reset sandbox state."""
    try:
        import shutil
        
        # Clean up old script files
        if SANDBOX_DIR.exists():
            for file in SANDBOX_DIR.glob("script_*.py"):
                if file.is_file():
                    file.unlink()
                    logger.debug(f"Removed script file: {file}")
        
        # Clean up old screenshots (keep last 10)
        if SCREENSHOTS_DIR.exists():
            screenshots = sorted(SCREENSHOTS_DIR.glob("*.png"), key=os.path.getctime)
            if len(screenshots) > 10:
                for screenshot in screenshots[:-10]:
                    screenshot.unlink()
                    logger.debug(f"Removed old screenshot: {screenshot}")
        
        logger.info("Sandbox cleanup completed")
        
    except Exception as e:
        logger.error(f"Sandbox cleanup failed: {e}")

def get_sandbox_stats():
    """Get current sandbox usage statistics."""
    try:
        stats = {
            "script_files": len(list(SANDBOX_DIR.glob("script_*.py"))) if SANDBOX_DIR.exists() else 0,
            "screenshots": len(list(SCREENSHOTS_DIR.glob("*.png"))) if SCREENSHOTS_DIR.exists() else 0,
            "sandbox_size_mb": sum(f.stat().st_size for f in SANDBOX_DIR.rglob('*') if f.is_file()) / (1024*1024) if SANDBOX_DIR.exists() else 0,
            "screenshots_size_mb": sum(f.stat().st_size for f in SCREENSHOTS_DIR.rglob('*') if f.is_file()) / (1024*1024) if SCREENSHOTS_DIR.exists() else 0
        }
        return stats
    except Exception as e:
        logger.error(f"Failed to get sandbox stats: {e}")
        return {}

# Initialize sandbox on import
ensure_sandbox_directories()

# Cleanup on module exit
import atexit
atexit.register(cleanup_sandbox) 