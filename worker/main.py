import os
import logging
import uvicorn
import socket
import tempfile
import requests
import zipfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from executor import execute_automation
import shutil
from pathlib import Path
import datetime

# Use Windows-compatible temp directory
TEMP_DIR = tempfile.gettempdir()
LOG_FILE = os.path.join(TEMP_DIR, 'worker.log')

def find_available_port(start_port: int = 8000, max_port: int = 8010) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available ports found between {start_port} and {max_port}")

# Configure logging with Windows-compatible encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s]: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)

logger = logging.getLogger('selenium-worker')

# FastAPI app
app = FastAPI(title="Selenium Automation Worker", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Screenshot management
SCREENSHOTS_DIR = Path(os.path.join(TEMP_DIR, "screenshots"))
MAX_SCREENSHOTS_PER_TASK = 5
SCREENSHOT_RETENTION_DAYS = 7

def setup_screenshot_directory():
    """Ensure screenshots directory exists and clean old files."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clean screenshots older than retention period
    cutoff_time = datetime.datetime.now() - datetime.timedelta(days=SCREENSHOT_RETENTION_DAYS)
    for screenshot in SCREENSHOTS_DIR.glob("*.png"):
        if datetime.datetime.fromtimestamp(screenshot.stat().st_mtime) < cutoff_time:
            screenshot.unlink()
            logger.info(f"Removed old screenshot: {screenshot}")

def cleanup_task_screenshots(task_id: str):
    """Clean up screenshots for a specific task."""
    try:
        for screenshot in SCREENSHOTS_DIR.glob(f"*{task_id}*.png"):
            screenshot.unlink()
            logger.debug(f"Cleaned up screenshot: {screenshot}")
    except Exception as e:
        logger.error(f"Failed to cleanup screenshots for task {task_id}: {e}")

# Initialize on startup
setup_screenshot_directory()

# Request models
class ExecutionRequest(BaseModel):
    code: str
    website_url: str
    timeout: Optional[int] = 60

class ExecutionResponse(BaseModel):
    success: bool
    logs: list
    error: Optional[str] = None
    screenshots: list
    execution_time: float

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "selenium-worker",
        "version": "1.0.0"
    }

# Execute automation endpoint
@app.post("/execute", response_model=ExecutionResponse)
async def execute_code(request: ExecutionRequest):
    """Execute Selenium automation code"""
    logger.info(f"Received execution request for: {request.website_url}")
    
    try:
        # Validate input
        if not request.code or not request.code.strip():
            logger.error("Empty code provided")
            raise HTTPException(status_code=400, detail="Code cannot be empty")
        
        if not request.website_url or not request.website_url.strip():
            logger.error("Empty website URL provided")
            raise HTTPException(status_code=400, detail="Website URL cannot be empty")
        
        # Validate URL format
        try:
            from urllib.parse import urlparse
            parsed = urlparse(request.website_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            logger.error(f"Invalid URL format: {request.website_url}")
            raise HTTPException(status_code=400, detail="Invalid website URL format")
        
        # Execute the automation
        logger.info(f"Starting automation execution with timeout: {request.timeout}s")
        
        result = execute_automation(
            code=request.code,
            website_url=request.website_url,
            timeout=request.timeout
        )
        
        logger.info(f"Automation execution completed: success={result.get('success')}")
        
        return ExecutionResponse(
            success=result.get("success", False),
            logs=result.get("logs", []),
            error=result.get("error"),
            screenshots=result.get("screenshots", []),
            execution_time=result.get("execution_time", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during execution: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Get worker status
@app.get("/status")
async def get_status():
    """Get worker status and statistics"""
    logger.info("Status check requested")
    
    try:
        import psutil
        import platform
        
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "running",
            "system": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_free": disk.free
            },
            "worker": {
                "service": "selenium-worker",
                "version": "1.0.0"
            }
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "status": "running",
            "error": str(e)
        }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Selenium Worker starting up...")
    
    try:
        # Import required modules
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        import platform
        import sys
        import shutil
        
        logger.info("Testing Chrome WebDriver setup...")
        logger.info(f"Platform: {platform.system()} {platform.architecture()}")
        
        # Setup Chrome options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        
        # Enhanced ChromeDriver path resolution - completely bypass ChromeDriverManager if needed
        driver_path = None
        
        # Method 1: Try ChromeDriverManager first
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            logger.info("Attempting ChromeDriverManager...")
            
            # Force download and get path
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
        
        # Method 4: Download directly if all else fails
        if not driver_path:
            logger.info("Attempting direct ChromeDriver download...")
            try:
                # Get latest ChromeDriver version
                version_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
                response = requests.get(version_url, timeout=10)
                latest_version = response.text.strip()
                
                # Download ChromeDriver
                download_url = f"https://chromedriver.storage.googleapis.com/{latest_version}/chromedriver_win32.zip"
                download_dir = os.path.join(tempfile.gettempdir(), "chromedriver_download")
                os.makedirs(download_dir, exist_ok=True)
                
                zip_path = os.path.join(download_dir, "chromedriver.zip")
                
                logger.info(f"Downloading ChromeDriver {latest_version}...")
                with requests.get(download_url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    with open(zip_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                
                # Extract ChromeDriver
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(download_dir)
                
                driver_path = os.path.join(download_dir, "chromedriver.exe")
                
                if os.path.exists(driver_path):
                    logger.info(f"Successfully downloaded ChromeDriver: {driver_path}")
                else:
                    raise Exception("Downloaded ChromeDriver not found")
                    
            except Exception as download_error:
                logger.error(f"Direct download failed: {download_error}")
        
        # Final validation
        if not driver_path or not os.path.exists(driver_path):
            raise Exception("No valid ChromeDriver found anywhere")
        
        if not os.access(driver_path, os.X_OK):
            raise Exception(f"ChromeDriver is not executable: {driver_path}")
        
        if os.path.getsize(driver_path) < 1000000:
            raise Exception(f"ChromeDriver file too small: {driver_path}")
        
        logger.info(f"Using verified ChromeDriver: {driver_path}")
        
        # Test the driver
        service = Service(driver_path)
        test_driver = webdriver.Chrome(service=service, options=options)
        test_driver.quit()
        
        logger.info("✅ Chrome WebDriver setup successful!")
        
    except Exception as e:
        logger.error(f"❌ Chrome WebDriver setup failed: {e}")
        logger.error("Worker may not function properly without WebDriver")
        logger.info("Continuing startup - worker will handle errors gracefully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Selenium Worker shutting down...")

if __name__ == "__main__":
    port = find_available_port()
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Selenium Worker on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    ) 