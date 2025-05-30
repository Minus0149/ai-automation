"""
Dynamic Automation Executor with AI page analysis
"""
import os
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

class DynamicAutomationExecutor:
    """Executor for dynamic automation with AI-powered page analysis."""
    
    def __init__(self):
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.driver = None
    
    def execute_automation(self, prompt: str, website_url: str, framework: str = "selenium", timeout: int = 180) -> Dict[str, Any]:
        """Execute dynamic automation based on natural language prompt."""
        start_time = time.time()
        logs = []
        screenshots = []
        context_chain = []
        function_calls = []
        
        try:
            # Initialize browser
            self.driver = self._initialize_browser()
            if not self.driver:
                raise Exception("Failed to initialize browser")
            
            logs.append({
                "level": "info",
                "message": f"Dynamic automation started with {framework}",
                "timestamp": datetime.now().isoformat(),
                "source": "dynamic_executor"
            })
            
            context_chain.append(f"Initialized {framework} browser")
            
            # Navigate to the website
            logs.append({
                "level": "info",
                "message": f"Navigating to: {website_url}",
                "timestamp": datetime.now().isoformat(),
                "source": "dynamic_executor"
            })
            
            self.driver.get(website_url)
            context_chain.append(f"Navigated to {website_url}")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take initial screenshot
            screenshot_path = self._take_screenshot("page_analysis")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            # Analyze the page and generate automation steps
            automation_steps = self._analyze_page_and_generate_steps(prompt)
            context_chain.append(f"Generated {len(automation_steps)} automation steps")
            
            logs.append({
                "level": "info",
                "message": f"Generated {len(automation_steps)} automation steps",
                "timestamp": datetime.now().isoformat(),
                "source": "dynamic_executor"
            })
            
            # Execute automation steps
            for i, step in enumerate(automation_steps):
                try:
                    logs.append({
                        "level": "info",
                        "message": f"Executing step {i+1}: {step['description']}",
                        "timestamp": datetime.now().isoformat(),
                        "source": "dynamic_executor"
                    })
                    
                    self._execute_step(step)
                    
                    function_calls.append({
                        "step": i + 1,
                        "action": step['action'],
                        "description": step['description'],
                        "success": True,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    context_chain.append(f"Completed step {i+1}: {step['description']}")
                    
                    # Take screenshot after each major step
                    if step['action'] in ['click', 'submit', 'navigate']:
                        screenshot_path = self._take_screenshot(f"step_{i+1}")
                        if screenshot_path:
                            screenshots.append(screenshot_path)
                    
                except Exception as step_error:
                    logs.append({
                        "level": "warning",
                        "message": f"Step {i+1} failed: {str(step_error)}",
                        "timestamp": datetime.now().isoformat(),
                        "source": "dynamic_executor"
                    })
                    
                    function_calls.append({
                        "step": i + 1,
                        "action": step['action'],
                        "description": step['description'],
                        "success": False,
                        "error": str(step_error),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    context_chain.append(f"Step {i+1} failed: {str(step_error)}")
            
            # Take final screenshot
            screenshot_path = self._take_screenshot("final_result")
            if screenshot_path:
                screenshots.append(screenshot_path)
            
            # Generate the equivalent code
            generated_code = self._generate_equivalent_code(automation_steps, website_url, framework)
            
            execution_time = time.time() - start_time
            
            logs.append({
                "level": "info",
                "message": f"Dynamic automation completed in {execution_time:.2f}s",
                "timestamp": datetime.now().isoformat(),
                "source": "dynamic_executor"
            })
            
            return {
                "success": True,
                "logs": logs,
                "screenshots": screenshots,
                "execution_time": execution_time,
                "framework": framework,
                "generated_code": generated_code,
                "context_chain": context_chain,
                "function_calls": function_calls,
                "automation_flow": {
                    "prompt": prompt,
                    "steps": automation_steps,
                    "total_steps": len(automation_steps)
                }
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Take error screenshot
            if self.driver:
                screenshot_path = self._take_screenshot("error")
                if screenshot_path:
                    screenshots.append(screenshot_path)
            
            logs.append({
                "level": "error",
                "message": f"Dynamic automation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "source": "dynamic_executor",
                "traceback": traceback.format_exc()
            })
            
            return {
                "success": False,
                "logs": logs,
                "screenshots": screenshots,
                "execution_time": execution_time,
                "framework": framework,
                "generated_code": "",
                "context_chain": context_chain,
                "function_calls": function_calls,
                "error": str(e)
            }
            
        finally:
            self._close_driver()
    
    def _initialize_browser(self):
        """Initialize browser with Chrome/Edge fallback."""
        # Try Chrome first
        try:
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = ChromeService(ChromeDriverManager().install())
                return webdriver.Chrome(service=service, options=options)
            else:
                return webdriver.Chrome(options=options)
                
        except Exception as chrome_error:
            concise_error = self._extract_concise_error(chrome_error)
            print(f"Chrome failed: {concise_error}")
            
            # Fallback to Edge
            try:
                options = EdgeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                
                if WEBDRIVER_MANAGER_AVAILABLE:
                    service = EdgeService(EdgeChromiumDriverManager().install())
                    return webdriver.Edge(service=service, options=options)
                else:
                    return webdriver.Edge(options=options)
                    
            except Exception as edge_error:
                concise_error = self._extract_concise_error(edge_error)
                print(f"Edge failed: {concise_error}")
                return None
    
    def _analyze_page_and_generate_steps(self, prompt: str) -> List[Dict[str, Any]]:
        """Analyze the page and generate automation steps based on the prompt."""
        steps = []
        
        if not self.driver:
            return steps
        
        try:
            # Get page elements for analysis
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            links = self.driver.find_elements(By.TAG_NAME, "a")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            
            # Simple prompt analysis for common actions
            prompt_lower = prompt.lower()
            
            # Login test specific
            if "login" in prompt_lower or "test" in prompt_lower:
                # Find username/email input
                for inp in inputs:
                    input_type = inp.get_attribute('type') or 'text'
                    name = inp.get_attribute('name') or ''
                    id_attr = inp.get_attribute('id') or ''
                    
                    if any(keyword in (name + id_attr).lower() for keyword in ['user', 'email', 'login']):
                        steps.append({
                            "action": "fill",
                            "element": "input",
                            "selector": f"input[name='{name}']" if name else f"input[id='{id_attr}']",
                            "value": "student",
                            "description": f"Fill username/email input"
                        })
                        break
                
                # Find password input
                for inp in inputs:
                    input_type = inp.get_attribute('type') or 'text'
                    if input_type == 'password':
                        name = inp.get_attribute('name') or ''
                        id_attr = inp.get_attribute('id') or ''
                        steps.append({
                            "action": "fill",
                            "element": "input",
                            "selector": f"input[type='password']",
                            "value": "Password123",
                            "description": f"Fill password input"
                        })
                        break
                
                # Find submit button
                for button in buttons:
                    text = button.text.strip().lower()
                    if any(keyword in text for keyword in ['submit', 'login', 'sign in']):
                        steps.append({
                            "action": "click",
                            "element": "button",
                            "selector": f"//button[contains(text(), '{button.text.strip()}')]",
                            "description": f"Click '{button.text.strip()}' button"
                        })
                        break
            
            # Click actions
            elif any(word in prompt_lower for word in ['click', 'press', 'tap']):
                for button in buttons[:3]:  # Limit to first 3 buttons
                    text = button.text.strip()
                    if text and len(text) < 50:
                        steps.append({
                            "action": "click",
                            "element": "button",
                            "selector": f"//button[text()='{text}']",
                            "description": f"Click button '{text}'"
                        })
            
            # Fill form actions
            elif any(word in prompt_lower for word in ['fill', 'enter', 'type', 'input']):
                for inp in inputs[:3]:  # Limit to first 3 inputs
                    input_type = inp.get_attribute('type') or 'text'
                    placeholder = inp.get_attribute('placeholder') or ''
                    name = inp.get_attribute('name') or ''
                    
                    if input_type in ['text', 'email', 'password']:
                        value = "test_value"
                        if input_type == 'email':
                            value = "test@example.com"
                        elif input_type == 'password':
                            value = "password123"
                            
                        steps.append({
                            "action": "fill",
                            "element": "input",
                            "selector": f"input[name='{name}']" if name else f"input[type='{input_type}']",
                            "value": value,
                            "description": f"Fill {input_type} input" + (f" ({placeholder})" if placeholder else "")
                        })
            
            # Submit actions
            elif any(word in prompt_lower for word in ['submit', 'send', 'search']):
                for form in forms[:1]:  # Limit to first form
                    steps.append({
                        "action": "submit",
                        "element": "form",
                        "selector": "form",
                        "description": "Submit form"
                    })
            
            # Navigation actions
            elif any(word in prompt_lower for word in ['navigate', 'go to', 'visit']):
                for link in links[:3]:  # Limit to first 3 links
                    text = link.text.strip()
                    href = link.get_attribute('href')
                    if text and href and len(text) < 50:
                        steps.append({
                            "action": "navigate",
                            "element": "link",
                            "selector": f"//a[text()='{text}']",
                            "url": href,
                            "description": f"Navigate to '{text}'"
                        })
            
            # If no specific steps generated, add a generic page analysis step
            if not steps:
                steps.append({
                    "action": "analyze",
                    "element": "page",
                    "selector": "body",
                    "description": "Analyze page content"
                })
                
        except Exception as e:
            # Fallback step if analysis fails
            steps.append({
                "action": "analyze",
                "element": "page",
                "selector": "body",
                "description": f"Basic page analysis (error: {str(e)})"
            })
        
        return steps
    
    def _execute_step(self, step: Dict[str, Any]):
        """Execute a single automation step."""
        if not self.driver:
            return
            
        action = step['action']
        selector = step['selector']
        
        try:
            if action == "click":
                if selector.startswith("//"):
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                element.click()
                
            elif action == "fill":
                if selector.startswith("//"):
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                element.clear()
                element.send_keys(step.get('value', 'test_value'))
                
            elif action == "submit":
                form = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                form.submit()
                
            elif action == "navigate":
                url = step.get('url')
                if url:
                    self.driver.get(url)
                    
            elif action == "analyze":
                # Just wait for analysis
                time.sleep(2)
                
            # Wait a bit after each action
            time.sleep(1)
            
        except Exception as e:
            print(f"Step execution failed: {e}")
            raise
    
    def _generate_equivalent_code(self, steps: List[Dict[str, Any]], website_url: str, framework: str) -> str:
        """Generate equivalent Selenium/SeleniumBase code."""
        if framework == "seleniumbase":
            return self._generate_seleniumbase_code(steps, website_url)
        else:
            return self._generate_selenium_code(steps, website_url)
    
    def _generate_selenium_code(self, steps: List[Dict[str, Any]], website_url: str) -> str:
        """Generate Selenium code."""
        code_lines = [
            "from selenium import webdriver",
            "from selenium.webdriver.common.by import By",
            "from selenium.webdriver.chrome.options import Options",
            "from selenium.webdriver.support.ui import WebDriverWait",
            "from selenium.webdriver.support import expected_conditions as EC",
            "import time",
            "",
            "# Setup Chrome driver",
            "options = Options()",
            "options.add_argument('--headless')",
            "driver = webdriver.Chrome(options=options)",
            "",
            "try:",
            f"    # Navigate to the website",
            f"    driver.get('{website_url}')",
            "    time.sleep(2)",
            ""
        ]
        
        for i, step in enumerate(steps):
            code_lines.append(f"    # Step {i+1}: {step['description']}")
            
            if step['action'] == 'click':
                if step['selector'].startswith("//"):
                    code_lines.append(f"    element = WebDriverWait(driver, 10).until(")
                    code_lines.append(f"        EC.element_to_be_clickable((By.XPATH, '{step['selector']}'))")
                    code_lines.append(f"    )")
                    code_lines.append(f"    element.click()")
                else:
                    code_lines.append(f"    element = WebDriverWait(driver, 10).until(")
                    code_lines.append(f"        EC.element_to_be_clickable((By.CSS_SELECTOR, '{step['selector']}'))")
                    code_lines.append(f"    )")
                    code_lines.append(f"    element.click()")
                    
            elif step['action'] == 'fill':
                value = step.get('value', 'test_value')
                if step['selector'].startswith("//"):
                    code_lines.append(f"    element = WebDriverWait(driver, 10).until(")
                    code_lines.append(f"        EC.presence_of_element_located((By.XPATH, '{step['selector']}'))")
                    code_lines.append(f"    )")
                else:
                    code_lines.append(f"    element = WebDriverWait(driver, 10).until(")
                    code_lines.append(f"        EC.presence_of_element_located((By.CSS_SELECTOR, '{step['selector']}'))")
                    code_lines.append(f"    )")
                code_lines.append("    element.clear()")
                code_lines.append(f"    element.send_keys('{value}')")
                
            elif step['action'] == 'submit':
                code_lines.append(f"    form = WebDriverWait(driver, 10).until(")
                code_lines.append(f"        EC.presence_of_element_located((By.CSS_SELECTOR, '{step['selector']}'))")
                code_lines.append(f"    )")
                code_lines.append(f"    form.submit()")
                
            elif step['action'] == 'navigate':
                url = step.get('url', '')
                code_lines.append(f"    driver.get('{url}')")
                
            code_lines.append("    time.sleep(1)")
            code_lines.append("")
        
        code_lines.extend([
            "finally:",
            "    # Cleanup",
            "    driver.quit()"
        ])
        
        return "\n".join(code_lines)
    
    def _generate_seleniumbase_code(self, steps: List[Dict[str, Any]], website_url: str) -> str:
        """Generate SeleniumBase code."""
        code_lines = [
            "from seleniumbase import BaseCase",
            "",
            "class AutomationTest(BaseCase):",
            "    def test_automation(self):",
            f"        # Navigate to the website",
            f"        self.open('{website_url}')",
            ""
        ]
        
        for i, step in enumerate(steps):
            code_lines.append(f"        # Step {i+1}: {step['description']}")
            
            if step['action'] == 'click':
                code_lines.append(f"        self.click('{step['selector']}')")
                
            elif step['action'] == 'fill':
                value = step.get('value', 'test_value')
                code_lines.append(f"        self.type('{step['selector']}', '{value}')")
                
            elif step['action'] == 'submit':
                code_lines.append(f"        self.submit('{step['selector']}')")
                
            elif step['action'] == 'navigate':
                url = step.get('url', '')
                code_lines.append(f"        self.open('{url}')")
                
            code_lines.append("")
        
        return "\n".join(code_lines)
    
    def _take_screenshot(self, name: str) -> Optional[str]:
        """Take and save a screenshot."""
        if not self.driver:
            return None
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            self.driver.save_screenshot(str(filepath))
            return str(filepath)
            
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None
    
    def _close_driver(self):
        """Close the webdriver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing driver: {e}")
            finally:
                self.driver = None
    
    def cleanup(self):
        """Clean up resources."""
        self._close_driver()

    def _extract_concise_error(self, error_message: str) -> str:
        """Extract a concise error message from verbose Selenium errors."""
        error_str = str(error_message)
        
        # DNS/Network errors
        if "ERR_NAME_NOT_RESOLVED" in error_str:
            return "DNS resolution failed"
        if "ERR_CONNECTION_REFUSED" in error_str:
            return "Connection refused"
        if "ERR_CONNECTION_TIMED_OUT" in error_str:
            return "Connection timeout"
        
        # Chrome/Browser specific errors
        if "chrome not reachable" in error_str.lower():
            return "Chrome not responding"
        if "chromedriver" in error_str.lower() and "executable" in error_str.lower():
            return "ChromeDriver not found"
        if "session not created" in error_str.lower():
            return "Browser session failed"
        
        # Timeout errors
        if "timeout" in error_str.lower():
            return "Operation timeout"
        
        # WebDriver errors
        if "WebDriverException" in error_str:
            return "WebDriver error"
        
        # File/Path errors  
        if "WinError 193" in error_str:
            return "Invalid executable"
        
        # Generic fallback - extract first line only
        first_line = error_str.split('\n')[0].strip()
        if len(first_line) > 80:
            first_line = first_line[:77] + "..."
        
        return first_line if first_line else "Unknown error"
        
    def create_browser_session(self) -> Dict[str, Any]:
        """Create a browser session for automation."""
        try:
            self.driver = self._setup_driver()
            if self.driver:
                return {
                    "success": True,
                    "session_id": id(self.driver),
                    "driver": self.driver
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create browser session"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _setup_driver(self):
        """Setup Chrome driver with Edge fallback."""
        try:
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = ChromeService(ChromeDriverManager().install())
                return webdriver.Chrome(service=service, options=options)
            else:
                return webdriver.Chrome(options=options)
                
        except Exception as chrome_error:
            concise_error = self._extract_concise_error(chrome_error)
            print(f"Chrome failed: {concise_error}")
            
            # Fallback to Edge
            try:
                options = EdgeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                
                if WEBDRIVER_MANAGER_AVAILABLE:
                    service = EdgeService(EdgeChromiumDriverManager().install())
                    return webdriver.Edge(service=service, options=options)
                else:
                    return webdriver.Edge(options=options)
                    
            except Exception as edge_error:
                concise_error = self._extract_concise_error(edge_error)
                print(f"Edge failed: {concise_error}")
                return None 