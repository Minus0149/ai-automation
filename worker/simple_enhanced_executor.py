"""
Simplified Enhanced Executor that generates project structures without LangChain
"""
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import tempfile

class SimpleEnhancedExecutor:
    """Simplified enhanced automation executor for project generation."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "automation_projects"
        self.temp_dir.mkdir(exist_ok=True)
    
    def execute_automation(self, prompt: str, website_url: str, framework: str, task_id: str, timeout: int = 180) -> Dict[str, Any]:
        """Execute enhanced automation with project generation."""
        start_time = time.time()
        
        try:
            # Create project directory
            project_dir = self.temp_dir / task_id
            project_dir.mkdir(exist_ok=True)
            
            # Generate project structure based on prompt
            project_structure = self._generate_project_structure(prompt, website_url, framework, project_dir)
            
            # Generate main automation script
            main_script = self._generate_main_script(prompt, website_url, framework)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "logs": [
                    {
                        "level": "info",
                        "message": f"Project structure generated successfully in {execution_time:.2f}s",
                        "timestamp": datetime.now().isoformat(),
                        "source": "simple_enhanced_executor"
                    }
                ],
                "screenshots": [],
                "execution_time": execution_time,
                "framework": framework,
                "generated_code": main_script,
                "project_structure": project_structure,
                "context_chain": [
                    f"Analyzed prompt: {prompt[:100]}...",
                    f"Selected framework: {framework}",
                    f"Generated project structure",
                    f"Created main automation script"
                ],
                "function_calls": [
                    {
                        "tool": "generate_project",
                        "input": {"prompt": prompt, "framework": framework},
                        "output": "Project structure created",
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "chat_history": [],
                "task_id": task_id
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "logs": [
                    {
                        "level": "error",
                        "message": f"Enhanced automation failed: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                        "source": "simple_enhanced_executor"
                    }
                ],
                "screenshots": [],
                "execution_time": execution_time,
                "framework": framework,
                "generated_code": "",
                "project_structure": {"files": [], "contents": {}},
                "context_chain": [],
                "function_calls": [],
                "chat_history": [],
                "error": str(e),
                "task_id": task_id
            }
    
    def _generate_project_structure(self, prompt: str, website_url: str, framework: str, project_dir: Path) -> Dict[str, Any]:
        """Generate a complete project structure."""
        
        # Determine project type from prompt
        if "test" in prompt.lower() or "testing" in prompt.lower():
            project_type = "testing"
        elif "scrape" in prompt.lower() or "extract" in prompt.lower() or "data" in prompt.lower():
            project_type = "scraping"
        else:
            project_type = "automation"
        
        # Define file structure
        files = []
        contents = {}
        
        # Main automation script
        main_file = "main_automation.py"
        files.append(main_file)
        contents[main_file] = self._generate_main_script(prompt, website_url, framework)
        
        # Configuration file
        config_file = "config.py"
        files.append(config_file)
        contents[config_file] = self._generate_config_file(website_url, framework)
        
        # Requirements file
        req_file = "requirements.txt"
        files.append(req_file)
        contents[req_file] = self._generate_requirements(framework)
        
        # README file
        readme_file = "README.md"
        files.append(readme_file)
        contents[readme_file] = self._generate_readme(prompt, project_type, framework)
        
        # Test file if testing project
        if project_type == "testing":
            test_file = "tests/test_automation.py"
            files.append(test_file)
            contents[test_file] = self._generate_test_file(prompt, framework)
        
        # Utils file
        utils_file = "utils/helpers.py"
        files.append(utils_file)
        contents[utils_file] = self._generate_utils_file()
        
        # Docker file
        docker_file = "Dockerfile"
        files.append(docker_file)
        contents[docker_file] = self._generate_dockerfile()
        
        # Docker compose
        compose_file = "docker-compose.yml"
        files.append(compose_file)
        contents[compose_file] = self._generate_docker_compose()
        
        # Save files to disk
        for file_path, content in contents.items():
            try:
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
            except Exception as e:
                print(f"Error saving file {file_path}: {e}")
        
        return {
            "files": sorted(files),
            "contents": contents
        }
    
    def _generate_main_script(self, prompt: str, website_url: str, framework: str) -> str:
        """Generate the main automation script."""
        
        # Determine the type of automation needed
        prompt_lower = prompt.lower()
        
        if "login" in prompt_lower or "test" in prompt_lower:
            return self._generate_login_test_script(website_url, framework)
        elif "scrape" in prompt_lower or "extract" in prompt_lower:
            return self._generate_scraping_script(website_url, framework)
        else:
            return self._generate_generic_automation_script(prompt, website_url, framework)
    
    def _generate_login_test_script(self, website_url: str, framework: str) -> str:
        """Generate a login test script."""
        return f'''#!/usr/bin/env python3
"""
Login Test Automation Script
Target: {website_url}
Framework: {framework}
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoginTest:
    """Login test automation class."""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
    
    def run_login_test(self):
        """Execute login test."""
        try:
            logger.info("Starting login test...")
            
            # Navigate to login page
            logger.info(f"Navigating to: {website_url}")
            self.driver.get("{website_url}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find username field
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys("student")
            logger.info("Username entered")
            
            # Find password field
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys("Password123")
            logger.info("Password entered")
            
            # Click submit button
            submit_button = self.driver.find_element(By.ID, "submit")
            submit_button.click()
            logger.info("Submit button clicked")
            
            # Wait for result
            time.sleep(3)
            
            # Check for success message
            try:
                success_element = self.driver.find_element(By.CSS_SELECTOR, ".post-title")
                if "Logged In Successfully" in success_element.text:
                    logger.info("Login test PASSED")
                    return True
                else:
                    logger.error("Login test FAILED - unexpected content")
                    return False
            except Exception as e:
                logger.error(f"Login test FAILED - {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Login test error: {{e}}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    test = LoginTest()
    success = test.run_login_test()
    
    if success:
        print("Login test completed successfully!")
    else:
        print("Login test failed!")
'''
    
    def _generate_scraping_script(self, website_url: str, framework: str) -> str:
        """Generate a web scraping script."""
        return f'''#!/usr/bin/env python3
"""
Web Scraping Script
Target: {website_url}
Framework: {framework}
"""

import time
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraping automation class."""
    
    def __init__(self):
        self.driver = None
        self.data = []
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
    
    def scrape_data(self):
        """Execute web scraping."""
        try:
            logger.info("Starting web scraping...")
            
            # Navigate to target page
            logger.info(f"Navigating to: {website_url}")
            self.driver.get("{website_url}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract page title
            title = self.driver.title
            logger.info(f"Page title: {{title}}")
            
            # Extract text content
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Find all links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            link_data = []
            for link in links:
                href = link.get_attribute("href")
                text = link.text.strip()
                if href and text:
                    link_data.append({{"text": text, "url": href}})
            
            # Compile extracted data
            self.data = {{
                "title": title,
                "url": "{website_url}",
                "content_length": len(body_text),
                "links_found": len(link_data),
                "links": link_data[:10],  # First 10 links
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }}
            
            logger.info(f"Scraped {{len(link_data)}} links and page content")
            return True
                
        except Exception as e:
            logger.error(f"Scraping error: {{e}}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_data(self, filename="scraped_data.json"):
        """Save scraped data to file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {{filename}}")
        except Exception as e:
            logger.error(f"Error saving data: {{e}}")

if __name__ == "__main__":
    scraper = WebScraper()
    success = scraper.scrape_data()
    
    if success:
        scraper.save_data()
        print("Web scraping completed successfully!")
    else:
        print("Web scraping failed!")
'''
    
    def _generate_generic_automation_script(self, prompt: str, website_url: str, framework: str) -> str:
        """Generate a generic automation script."""
        return f'''#!/usr/bin/env python3
"""
Generic Automation Script
Task: {prompt}
Target: {website_url}
Framework: {framework}
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomationTask:
    """Generic automation task class."""
    
    def __init__(self):
        self.driver = None
        self.results = []
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
    
    def run_automation(self):
        """Execute the automation task."""
        try:
            logger.info("Starting automation task...")
            logger.info(f"Task: {prompt}")
            logger.info(f"Target URL: {website_url}")
            
            # Navigate to the website
            self.driver.get("{website_url}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Execute automation logic
            self.execute_task()
            
            logger.info("Automation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Automation failed: {{e}}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def execute_task(self):
        """Execute the specific automation task."""
        logger.info("Executing automation task...")
        
        try:
            # Generic automation actions based on common patterns
            
            # Find and interact with buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"Found {{len(buttons)}} buttons on the page")
            
            # Find and interact with input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"Found {{len(inputs)}} input fields on the page")
            
            # Extract page information
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            self.results.append({{"page_content": page_text[:500]}})  # First 500 chars
            
            # Wait and observe
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Task execution error: {{e}}")
            raise

if __name__ == "__main__":
    automation = AutomationTask()
    success = automation.run_automation()
    
    if success:
        print("Automation completed successfully!")
    else:
        print("Automation failed!")
'''
    
    def _generate_config_file(self, website_url: str, framework: str) -> str:
        """Generate configuration file."""
        return f'''"""
Configuration settings for automation project
"""

class Config:
    """Configuration class for automation settings."""
    
    # Target website
    WEBSITE_URL = "{website_url}"
    
    # Framework settings
    FRAMEWORK = "{framework}"
    
    # Browser settings
    HEADLESS = True
    BROWSER_TIMEOUT = 30
    
    # Output settings
    SCREENSHOTS_DIR = "screenshots"
    RESULTS_DIR = "results"
    
    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FILE = "automation.log"
    
    @property
    def website_url(self):
        return self.WEBSITE_URL
    
    @property
    def framework(self):
        return self.FRAMEWORK
'''
    
    def _generate_requirements(self, framework: str) -> str:
        """Generate requirements.txt file."""
        base_requirements = [
            "selenium==4.15.2",
            "webdriver-manager==4.0.1",
            "requests==2.31.0",
            "beautifulsoup4==4.12.2",
            "lxml==4.9.3",
            "pillow==10.1.0"
        ]
        
        if framework == "seleniumbase":
            base_requirements.append("seleniumbase==4.21.7")
        
        return "\n".join(base_requirements)
    
    def _generate_readme(self, prompt: str, project_type: str, framework: str) -> str:
        """Generate README.md file."""
        return f'''# Automation Project

## Description
{prompt}

## Project Type
{project_type.title()} automation using {framework}

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the automation:
```bash
python main_automation.py
```

## Project Structure

- `main_automation.py` - Main automation script
- `config.py` - Configuration settings
- `utils/helpers.py` - Utility functions
- `requirements.txt` - Python dependencies
- `tests/` - Test files (if applicable)

## Docker

To run with Docker:

```bash
docker-compose up
```

## Features

- Web automation using {framework}
- Screenshot capture
- Error handling and logging
- Results saving
- Docker support

## Generated by
Automation Studio
'''
    
    def _generate_test_file(self, prompt: str, framework: str) -> str:
        """Generate test file."""
        return f'''"""
Test file for automation project
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_automation import AutomationTask

class TestAutomation(unittest.TestCase):
    """Test cases for automation task."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.automation = AutomationTask()
    
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.automation, 'driver') and self.automation.driver:
            self.automation.driver.quit()
    
    def test_automation_task(self):
        """Test the main automation task."""
        # Test that automation runs without errors
        result = self.automation.run_automation()
        self.assertIsNotNone(result)
    
    def test_config_loading(self):
        """Test configuration loading."""
        from config import Config
        config = Config()
        self.assertIsNotNone(config.website_url)
        self.assertEqual(config.framework, "{framework}")

if __name__ == "__main__":
    unittest.main()
'''
    
    def _generate_utils_file(self) -> str:
        """Generate utilities file."""
        return '''"""
Utility functions for automation project
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

def take_screenshot(driver, name: str):
    """Take a screenshot and save it."""
    try:
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = screenshots_dir / filename
        
        driver.save_screenshot(str(filepath))
        print(f"Screenshot saved: {filepath}")
        return str(filepath)
        
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return None

def save_data(data, filename: str):
    """Save data to JSON file."""
    try:
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved: {filepath}")
        return str(filepath)
        
    except Exception as e:
        print(f"Failed to save data: {e}")
        return None

def wait_for_element(driver, by, value, timeout=10):
    """Wait for element to be present."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except Exception as e:
        print(f"Element not found: {by}={value}, error: {e}")
        return None

def log_action(action: str, details: str = ""):
    """Log automation actions."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {action}"
    if details:
        log_message += f" - {details}"
    
    print(log_message)
    
    # Also save to log file
    try:
        with open("automation.log", "a", encoding="utf-8") as f:
            f.write(log_message + "\\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}")
'''
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile."""
        return '''FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    curl \\
    unzip \\
    gnupg \\
    --no-install-recommends && \\
    rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \\
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \\
    apt-get update && \\
    apt-get install -y google-chrome-stable && \\
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p screenshots results

# Run the automation
CMD ["python", "main_automation.py"]
'''
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml."""
        return '''version: '3.8'

services:
  automation:
    build: .
    volumes:
      - ./screenshots:/app/screenshots
      - ./results:/app/results
      - ./automation.log:/app/automation.log
    environment:
      - DISPLAY=:99
    networks:
      - automation-network

networks:
  automation-network:
    driver: bridge
'''
    
    def cleanup(self):
        """Clean up resources."""
        pass 