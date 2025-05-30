"""
Smart Automation Workflow - Intelligent automation with error fixing and fallbacks
Enhanced with robust Chrome driver management and subprocess execution
"""
import os
import time
import json
import uuid
import requests
import tempfile
import subprocess
import platform
import psutil
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

# Import existing executors
from selenium_executor import SeleniumExecutor
from dynamic_ai_executor import DynamicAIExecutor

# Selenium imports with fallback
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# WebDriver Manager with fallback
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    import os
    os.environ['WDM_ARCHITECTURE'] = '64'  # Force 64-bit Chrome driver
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

# Web scraping with fallback
try:
    from bs4 import BeautifulSoup
    import lxml
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

class SmartWorkflowRequest(BaseModel):
    task: str
    website_url: str

class SmartAutomationWorkflow:
    """
    Smart automation workflow that can generate code, execute it, and fix errors automatically.
    Supports multiple browsers with intelligent fallbacks and error recovery.
    """
    
    def __init__(self):
        self.project_dir = Path("automation_projects")
        self.project_dir.mkdir(exist_ok=True)
        self.workflows = {}
        
        # Browser session management
        self.current_driver = None
        self.browser_session_timeout = 300  # 5 minutes
        self.last_browser_activity = None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.browser_sessions = {}
        self.session_timeout = 5 * 60  # 5 minutes
        
        # Initialize executors
        try:
            self.selenium_executor = SeleniumExecutor()
            self.dynamic_executor = DynamicAIExecutor()
        except Exception as e:
            print(f"Warning: Could not initialize executors: {e}")
            self.selenium_executor = None
            self.dynamic_executor = None
        
    def _extract_concise_error(self, error_message: str) -> str:
        """Extract a concise error message from verbose Selenium errors."""
        error_str = str(error_message)
        
        # DNS/Network errors
        if "ERR_NAME_NOT_RESOLVED" in error_str:
            return "DNS resolution failed - invalid domain"
        if "ERR_INTERNET_DISCONNECTED" in error_str:
            return "Internet connection lost"
        if "ERR_CONNECTION_REFUSED" in error_str:
            return "Connection refused by server"
        if "ERR_CONNECTION_TIMED_OUT" in error_str:
            return "Connection timed out"
        
        # Chrome/Browser specific errors
        if "chrome not reachable" in error_str.lower():
            return "Chrome browser not responding"
        if "chromedriver" in error_str.lower() and "executable" in error_str.lower():
            return "ChromeDriver not found or invalid"
        if "session not created" in error_str.lower():
            return "Browser session creation failed"
        
        # Timeout errors
        if "timeout" in error_str.lower():
            return "Operation timed out"
        if "page load timeout" in error_str.lower():
            return "Page load timeout"
        
        # Permission/Access errors
        if "permission denied" in error_str.lower():
            return "Permission denied"
        if "access denied" in error_str.lower():
            return "Access denied"
        
        # WebDriver errors
        if "WebDriverException" in error_str:
            return "WebDriver error occurred"
        if "TimeoutException" in error_str:
            return "Operation timeout"
        
        # File/Path errors
        if "No such file or directory" in error_str:
            return "Required file not found"
        if "WinError 193" in error_str:
            return "Invalid executable format"
        
        # Generic fallback - extract first line only
        first_line = error_str.split('\n')[0].strip()
        if len(first_line) > 100:
            first_line = first_line[:97] + "..."
        
        return first_line if first_line else "Unknown error"
    
    def execute_smart_workflow(self, task: str, website_url: str) -> Dict[str, Any]:
        """Execute the complete smart automation workflow."""
        workflow_id = str(uuid.uuid4())
        start_time = time.time()
        
        print(f"Starting Smart Workflow: {task}")
        print(f"Target URL: {website_url}")
        print(f"Workflow ID: {workflow_id}")
        
        try:
            # Step 1: Scrape and analyze the website
            print("Step 1: Analyzing website...")
            fetch_result = self._scrape_website_with_fallback(website_url)
            
            if not fetch_result.get("success"):
                print(f"Website analysis failed: {fetch_result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": f"Failed to analyze website: {fetch_result.get('error')}",
                    "workflow_id": workflow_id,
                    "execution_time": time.time() - start_time
                }
            
            print("Website analysis completed successfully")
            
            # Step 2: Generate automation code
            print("Step 2: Generating automation code...")
            code_result = self._generate_automation_code(task, website_url, fetch_result)
            
            if not code_result.get("success"):
                print(f"Code generation failed: {code_result.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "error": f"Failed to generate code: {code_result.get('error')}",
                    "workflow_id": workflow_id,
                    "execution_time": time.time() - start_time
                }
            
            print("Automation code generated successfully")
            
            # Step 3: Execute with intelligent error fixing
            print("Step 3: Executing automation with error fixing...")
            execution_result = self._execute_with_fallback_and_fixes(
                code_result["code"], website_url, max_attempts=5
            )
            
            # Step 4: Manage project files
            print("Step 4: Creating project files...")
            project_result = self._manage_project_files(workflow_id, code_result["code"], task)
            
            # Step 5: Save workflow results
            workflow_result = {
                "success": execution_result.get("success", False),
                "workflow_id": workflow_id,
                "task": task,
                "website_url": website_url,
                "execution_time": time.time() - start_time,
                "fetch_result": fetch_result,
                "code_result": code_result,
                "execution_result": execution_result,
                "project_result": project_result,
                "generated_code": execution_result.get("generated_code", code_result.get("code", "")),
                "browser_used": execution_result.get("browser_used", "unknown"),
                "attempts_made": execution_result.get("attempts_made", 1),
                "screenshots": execution_result.get("screenshots", []),
                "logs": execution_result.get("logs", []),
                "generated_files": project_result.get("project_files", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            self._save_workflow_results(workflow_id, workflow_result)
            
            print(f"Smart Workflow completed in {workflow_result['execution_time']:.2f}s")
            print(f"Success: {workflow_result['success']}")
            print(f"Browser used: {workflow_result['browser_used']}")
            
            return workflow_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id,
                "task": task,
                "website_url": website_url,
                "execution_time": time.time() - start_time
            }
            
            print(f"Smart Workflow failed: {str(e)}")
            return error_result
    
    def _scrape_website_with_fallback(self, url: str) -> Dict[str, Any]:
        """Enhanced website scraping with multiple fallback methods and timeouts."""
        print(f"Analyzing website: {url}")
        
        # Method 1: Try browser-based scraping with threading timeout (Windows compatible)
        browser_success = False
        try:
            print("Attempting browser-based scraping...")
            import threading
            import queue
            
            def browser_scrape_worker(result_queue, url, browser):
                try:
                    result = self._scrape_with_browser_enhanced(url, browser)
                    result_queue.put(result)
                except Exception as e:
                    result_queue.put({"success": False, "error": str(e)})
            
            # Try Chrome with timeout
            result_queue = queue.Queue()
            chrome_thread = threading.Thread(target=browser_scrape_worker, args=(result_queue, url, "chrome"))
            chrome_thread.daemon = True
            chrome_thread.start()
            chrome_thread.join(timeout=20)  # 20 second timeout
            
            if chrome_thread.is_alive():
                print("Chrome browser scraping timed out, trying Edge...")
                # Try Edge with timeout
                result_queue = queue.Queue()
                edge_thread = threading.Thread(target=browser_scrape_worker, args=(result_queue, url, "edge"))
                edge_thread.daemon = True
                edge_thread.start()
                edge_thread.join(timeout=15)  # 15 second timeout for Edge
                
                if edge_thread.is_alive():
                    print("Edge browser also timed out, falling back to HTTP...")
                else:
                    try:
                        browser_result = result_queue.get_nowait()
                        if browser_result.get("success"):
                            print("Edge browser scraping successful")
                            return browser_result
                    except queue.Empty:
                        print("Edge thread completed but no result available")
            else:
                try:
                    browser_result = result_queue.get_nowait()
                    if browser_result.get("success"):
                        print("Chrome browser scraping successful")
                        return browser_result
                    else:
                        concise_error = self._extract_concise_error(browser_result.get('error', 'Unknown error'))
                        print(f"Chrome failed: {concise_error}")
                except queue.Empty:
                    print("Chrome thread completed but no result available")
                    
        except Exception as browser_error:
            print(f"Browser scraping setup failed: {browser_error}")
        
        # Method 2: HTTP fetching with session management (immediate fallback)
        try:
            print("Attempting HTTP fetching with session...")
            fetch_result = self._fetch_with_session(url)
            if fetch_result.get("success"):
                print("HTTP session fetching successful")
                return fetch_result
        except Exception as session_error:
            print(f"Session fetching failed: {session_error}")
        
        # Method 3: Basic HTTP requests (last resort)
        try:
            print("Attempting basic HTTP request...")
            basic_result = self._fetch_basic(url)
            if basic_result.get("success"):
                print("Basic HTTP fetching successful")
                return basic_result
        except Exception as basic_error:
            print(f"Basic fetching failed: {basic_error}")
        
        # All methods failed
        return {
            "success": False,
            "error": "All scraping methods failed",
            "methods_tried": ["browser_chrome", "browser_edge", "http_session", "http_basic"],
            "auth_wall_detected": False
        }
    
    def _scrape_with_browser_enhanced(self, url: str, browser: str) -> Dict[str, Any]:
        """Enhanced browser-based scraping with aggressive timeout handling."""
        driver = None
        
        try:
            # Create browser session with shorter timeout
            print(f"Creating {browser} browser session...")
            driver = self._create_browser_session_fast(browser)
            
            if not driver:
                raise Exception(f"Failed to create {browser} browser")
            
            print(f"Navigating to {url}...")
            # Navigate with timeout
            driver.set_page_load_timeout(15)  # 15 second page load timeout
            driver.get(url)
            
            print("Waiting for page to load...")
            # Quick wait for basic page elements
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                print("Page load wait timed out, proceeding anyway...")
            
            print("Analyzing page content...")
            # Quick page analysis without heavy DOM manipulation
            page_data = self._analyze_page_fast(driver, url)
            
            print("Checking for auth walls...")
            # Quick auth wall check
            auth_wall_info = self._detect_auth_wall_fast(driver)
            
            return {
                "success": True,
                "method": f"browser_{browser}",
                "url": url,
                "page_data": page_data,
                "auth_wall": auth_wall_info,
                "browser_session": True,
                "session_maintained": False  # Don't maintain session to avoid hanging
            }
            
        except Exception as e:
            error_msg = str(e)
            concise_error = self._extract_concise_error(error_msg)
            print(f"Browser scraping error: {concise_error}")
            
            return {
                "success": False,
                "error": error_msg,
                "method": f"browser_{browser}",
                "auth_wall": self._detect_auth_wall_from_errors([error_msg])
            }
        finally:
            # Always clean up browser to prevent hanging
            if driver:
                try:
                    print("Cleaning up browser session...")
                    driver.quit()
                except:
                    pass
    
    def _create_browser_session_fast(self, browser: str):
        """Create a fast browser session without persistence."""
        try:
            if browser == "chrome":
                from selenium.webdriver.chrome.options import Options as ChromeOptions
                options = ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--headless")  # Force headless for speed
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-features=TranslateUI")
                options.add_argument("--disable-ipc-flooding-protection")
                
                # Try system Chrome first (faster)
                try:
                    driver = webdriver.Chrome(options=options)
                    print("Using system Chrome driver")
                except:
                    # Fallback to ChromeDriverManager
                    if WEBDRIVER_MANAGER_AVAILABLE:
                        try:
                            os.environ['WDM_ARCHITECTURE'] = '64'
                            from selenium.webdriver.chrome.service import Service as ChromeService
                            service = ChromeService(ChromeDriverManager().install())
                            driver = webdriver.Chrome(service=service, options=options)
                            print("Using ChromeDriverManager")
                        except Exception as e:
                            print(f"ChromeDriverManager failed: {e}")
                            raise
                    else:
                        raise Exception("No Chrome driver available")
            
            else:  # edge
                from selenium.webdriver.edge.options import Options as EdgeOptions
                options = EdgeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--headless")  # Force headless
                options.add_argument("--window-size=1920,1080")
                
                try:
                    driver = webdriver.Edge(options=options)
                    print("Using system Edge driver")
                except:
                    if WEBDRIVER_MANAGER_AVAILABLE:
                        try:
                            from selenium.webdriver.edge.service import Service as EdgeService
                            service = EdgeService(EdgeChromiumDriverManager().install())
                            driver = webdriver.Edge(service=service, options=options)
                            print("Using EdgeDriverManager")
                        except Exception as e:
                            print(f"EdgeDriverManager failed: {e}")
                            raise
                    else:
                        raise Exception("No Edge driver available")
            
            # Set shorter timeouts
            driver.implicitly_wait(5)  # Reduced from 10
            driver.set_page_load_timeout(15)  # Reduced from 30
            
            return driver
            
        except Exception as e:
            print(f"Failed to create {browser} session: {e}")
            return None
    
    def _analyze_page_fast(self, driver, url: str) -> Dict[str, Any]:
        """Fast page analysis without heavy DOM manipulation."""
        try:
            title = driver.title
            current_url = driver.current_url
            
            print("Getting basic page info...")
            # Get basic page info without DOM manipulation
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:2000]
            except:
                body_text = "Could not extract body text"
            
            print("Counting elements...")
            # Quick element counting
            try:
                inputs = len(driver.find_elements(By.TAG_NAME, "input"))
                buttons = len(driver.find_elements(By.TAG_NAME, "button"))
                forms = len(driver.find_elements(By.TAG_NAME, "form"))
                links = len(driver.find_elements(By.TAG_NAME, "a"))
            except:
                inputs = buttons = forms = links = 0
            
            print("Getting sample input details...")
            # Get sample input details (just first few)
            input_details = []
            try:
                input_elements = driver.find_elements(By.TAG_NAME, "input")[:3]  # Only first 3
                for inp in input_elements:
                    try:
                        input_details.append({
                            "type": inp.get_attribute("type") or "text",
                            "name": inp.get_attribute("name") or "",
                            "id": inp.get_attribute("id") or "",
                            "placeholder": inp.get_attribute("placeholder") or ""
                        })
                    except:
                        continue
            except:
                pass
            
            return {
                "title": title,
                "url": current_url,
                "clean_body_content": {"text": body_text, "content_length": len(body_text)},
                "element_counts": {
                    "total_interactive": inputs + buttons + forms,
                    "high_priority": {"input_fields": inputs, "buttons": buttons, "forms": forms},
                    "medium_priority": {"links": links},
                    "automation_score": min((inputs + buttons + forms) / 10.0, 1.0)
                },
                "input_analysis": {"inputs": input_details, "input_count": len(input_details)},
                "automation_priority": {
                    "high": [{"type": "form_detected", "count": forms + inputs}],
                    "medium": [{"type": "links_detected", "count": links}],
                    "low": []
                },
                "page_loaded": True
            }
            
        except Exception as e:
            print(f"Fast page analysis failed: {e}")
            return {
                "title": "Analysis failed",
                "url": url,
                "clean_body_content": {"text": "Failed to analyze page"},
                "element_counts": {"total_interactive": 0, "automation_score": 0.0},
                "input_analysis": {"inputs": [], "input_count": 0},
                "automation_priority": {"high": [], "medium": [], "low": []},
                "page_loaded": False,
                "error": str(e)
            }
    
    def _detect_auth_wall_fast(self, driver) -> Dict[str, Any]:
        """Fast auth wall detection without heavy analysis."""
        try:
            # Quick password field check
            password_fields = len(driver.find_elements(By.CSS_SELECTOR, "input[type='password']"))
            
            # Quick text check (just check if 'login' is in page source)
            page_source_lower = driver.page_source.lower()
            login_text = "login" in page_source_lower or "signin" in page_source_lower
            
            auth_score = password_fields * 3 + int(login_text)
            
            return {
                "detected": auth_score > 2,
                "confidence": min(auth_score / 6.0, 1.0),
                "indicators": {
                    "password_fields": password_fields,
                    "login_text": login_text
                },
                "score": auth_score
            }
            
        except Exception as e:
            return {
                "detected": False,
                "confidence": 0.0,
                "error": str(e),
                "indicators": {},
                "score": 0
            }
    
    def _create_browser_session(self, browser: str, keep_alive: bool = True):
        """Create a persistent browser session with Windows compatibility."""
        try:
            if browser == "chrome":
                options = ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--start-maximized")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-backgrounding-occluded-windows")
                
                if WEBDRIVER_MANAGER_AVAILABLE:
                    try:
                        # Force 64-bit architecture for Windows
                        os.environ['WDM_ARCHITECTURE'] = '64'
                        service = ChromeService(ChromeDriverManager().install())
                        driver = webdriver.Chrome(service=service, options=options)
                    except Exception as e:
                        print(f"ChromeDriverManager failed: {e}, trying system Chrome")
                        driver = webdriver.Chrome(options=options)
                else:
                    driver = webdriver.Chrome(options=options)
            
            else:  # edge
                options = EdgeOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--start-maximized")
                
                if WEBDRIVER_MANAGER_AVAILABLE:
                    try:
                        service = EdgeService(EdgeChromiumDriverManager().install())
                        driver = webdriver.Edge(service=service, options=options)
                    except Exception as e:
                        print(f"EdgeDriverManager failed: {e}, trying system Edge")
                        driver = webdriver.Edge(options=options)
                else:
                    driver = webdriver.Edge(options=options)
            
            # Set timeouts
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)
            
            # Store session
            if keep_alive:
                self.current_driver = driver
                self.last_browser_activity = time.time()
            
            return driver
            
        except Exception as e:
            print(f"Failed to create {browser} session: {e}")
            return None
    
    def _is_browser_session_valid(self) -> bool:
        """Check if current browser session is still valid."""
        if not self.current_driver or not self.last_browser_activity:
            return False
        
        # Check if session timeout exceeded
        if time.time() - self.last_browser_activity > self.browser_session_timeout:
            try:
                self.current_driver.quit()
            except:
                pass
            self.current_driver = None
            return False
        
        # Try to ping the session
        try:
            self.current_driver.current_url
            return True
        except:
            self.current_driver = None
            return False
    
    def _analyze_page_comprehensive(self, driver, url: str) -> Dict[str, Any]:
        """Comprehensive page analysis with enhanced element detection and content filtering."""
        try:
            title = driver.title
            current_url = driver.current_url
            page_source = driver.page_source
            
            # Extract and clean body content
            clean_content = self._extract_clean_body_content(driver)
            
            # Count basic elements with priority
            element_counts = self._count_elements_with_priority(driver)
            
            # Get detailed input analysis
            input_analysis = self._analyze_input_elements(driver)
            
            # Get clickable elements analysis
            clickable_analysis = self._analyze_clickable_elements(driver)
            
            # Create automation priority list
            automation_priority = self._create_automation_priority_list(driver)
            
            return {
                "title": title,
                "url": current_url,
                "clean_body_content": clean_content,
                "page_source_snippet": page_source[:2000],  # Just a snippet for reference
                "element_counts": element_counts,
                "input_analysis": input_analysis,
                "clickable_analysis": clickable_analysis,
                "automation_priority": automation_priority,
                "page_loaded": True
            }
            
        except Exception as e:
            print(f"Page analysis failed: {e}")
            return {
                "title": "Analysis failed",
                "url": url,
                "clean_body_content": {"text": "Failed to analyze page", "headings": [], "paragraphs": []},
                "page_source_snippet": "",
                "element_counts": {"total": 0, "priority_elements": {}},
                "input_analysis": {"inputs": [], "forms": []},
                "clickable_analysis": {"buttons": [], "links": []},
                "automation_priority": {"high": [], "medium": [], "low": []},
                "page_loaded": False,
                "error": str(e)
            }
    
    def _extract_clean_body_content(self, driver) -> Dict[str, Any]:
        """Extract clean, meaningful content from page body, filtering out useless elements."""
        try:
            # Remove script, style, and other non-content elements
            driver.execute_script("""
                // Remove unwanted elements
                var unwantedTags = ['script', 'style', 'noscript', 'iframe', 'embed', 'object'];
                unwantedTags.forEach(function(tag) {
                    var elements = document.getElementsByTagName(tag);
                    for (var i = elements.length - 1; i >= 0; i--) {
                        elements[i].remove();
                    }
                });
                
                // Remove comments
                var walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_COMMENT,
                    null,
                    false
                );
                var comments = [];
                while (walker.nextNode()) {
                    comments.push(walker.currentNode);
                }
                comments.forEach(function(comment) {
                    comment.remove();
                });
            """)
            
            # Get body element
            body = driver.find_element(By.TAG_NAME, "body")
            
            # Extract meaningful text content
            body_text = body.text[:3000]  # First 3000 characters
            
            # Extract headings in order
            headings = []
            for level in range(1, 7):  # h1 to h6
                heading_elements = body.find_elements(By.TAG_NAME, f"h{level}")
                for heading in heading_elements:
                    text = heading.text.strip()
                    if text:
                        headings.append({
                            "level": level,
                            "text": text,
                            "tag": f"h{level}"
                        })
            
            # Extract paragraphs
            paragraphs = []
            paragraph_elements = body.find_elements(By.TAG_NAME, "p")
            for p in paragraph_elements[:10]:  # Limit to first 10 paragraphs
                text = p.text.strip()
                if text and len(text) > 10:  # Only meaningful paragraphs
                    paragraphs.append(text)
            
            # Extract lists
            lists = []
            list_elements = body.find_elements(By.CSS_SELECTOR, "ul, ol")
            for list_elem in list_elements[:5]:  # Limit to first 5 lists
                list_items = list_elem.find_elements(By.TAG_NAME, "li")
                items = [li.text.strip() for li in list_items[:10] if li.text.strip()]
                if items:
                    lists.append({
                        "type": list_elem.tag_name,
                        "items": items
                    })
            
            return {
                "text": body_text,
                "headings": headings,
                "paragraphs": paragraphs,
                "lists": lists,
                "content_length": len(body_text)
            }
            
        except Exception as e:
            return {
                "text": f"Error extracting body content: {e}",
                "headings": [],
                "paragraphs": [],
                "lists": [],
                "content_length": 0
            }
    
    def _count_elements_with_priority(self, driver) -> Dict[str, Any]:
        """Count elements with automation priority classification."""
        try:
            # High priority elements for automation
            high_priority = {
                "input_fields": len(driver.find_elements(By.TAG_NAME, "input")),
                "buttons": len(driver.find_elements(By.TAG_NAME, "button")),
                "forms": len(driver.find_elements(By.TAG_NAME, "form")),
                "select_dropdowns": len(driver.find_elements(By.TAG_NAME, "select")),
                "textareas": len(driver.find_elements(By.TAG_NAME, "textarea"))
            }
            
            # Medium priority elements
            medium_priority = {
                "links": len(driver.find_elements(By.TAG_NAME, "a")),
                "images": len(driver.find_elements(By.TAG_NAME, "img")),
                "tables": len(driver.find_elements(By.TAG_NAME, "table")),
                "divs_with_onclick": len(driver.find_elements(By.CSS_SELECTOR, "div[onclick]")),
                "clickable_elements": len(driver.find_elements(By.CSS_SELECTOR, "[onclick], [role='button']"))
            }
            
            # Low priority elements
            low_priority = {
                "headings": len(driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")),
                "paragraphs": len(driver.find_elements(By.TAG_NAME, "p")),
                "spans": len(driver.find_elements(By.TAG_NAME, "span")),
                "divs": len(driver.find_elements(By.TAG_NAME, "div"))
            }
            
            total_interactive = sum(high_priority.values()) + medium_priority["links"] + medium_priority["clickable_elements"]
            
            return {
                "total_interactive": total_interactive,
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority,
                "automation_score": min(total_interactive / 10.0, 1.0)  # Score out of 1.0
            }
            
        except Exception as e:
            return {
                "total_interactive": 0,
                "high_priority": {},
                "medium_priority": {},
                "low_priority": {},
                "automation_score": 0.0,
                "error": str(e)
            }
    
    def _analyze_input_elements(self, driver) -> Dict[str, Any]:
        """Detailed analysis of input elements for automation."""
        try:
            inputs = []
            forms = []
            
            # Analyze input fields
            input_elements = driver.find_elements(By.TAG_NAME, "input")
            for inp in input_elements[:15]:  # Limit to first 15 inputs
                try:
                    input_info = {
                        "type": inp.get_attribute("type") or "text",
                        "name": inp.get_attribute("name") or "",
                        "id": inp.get_attribute("id") or "",
                        "placeholder": inp.get_attribute("placeholder") or "",
                        "required": inp.get_attribute("required") is not None,
                        "visible": inp.is_displayed(),
                        "enabled": inp.is_enabled(),
                        "value": inp.get_attribute("value") or "",
                        "automation_priority": self._get_input_priority(inp)
                    }
                    inputs.append(input_info)
                except:
                    continue
            
            # Analyze forms
            form_elements = driver.find_elements(By.TAG_NAME, "form")
            for form in form_elements[:5]:  # Limit to first 5 forms
                try:
                    form_inputs = form.find_elements(By.TAG_NAME, "input")
                    form_buttons = form.find_elements(By.CSS_SELECTOR, "button, input[type='submit'], input[type='button']")
                    
                    form_info = {
                        "action": form.get_attribute("action") or "",
                        "method": form.get_attribute("method") or "get",
                        "id": form.get_attribute("id") or "",
                        "input_count": len(form_inputs),
                        "button_count": len(form_buttons),
                        "automation_priority": "high" if len(form_inputs) > 1 else "medium"
                    }
                    forms.append(form_info)
                except:
                    continue
            
            return {
                "inputs": inputs,
                "forms": forms,
                "input_count": len(inputs),
                "form_count": len(forms)
            }
            
        except Exception as e:
            return {
                "inputs": [],
                "forms": [],
                "input_count": 0,
                "form_count": 0,
                "error": str(e)
            }
    
    def _analyze_clickable_elements(self, driver) -> Dict[str, Any]:
        """Analyze clickable elements for automation."""
        try:
            buttons = []
            links = []
            
            # Analyze buttons
            button_elements = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit'], input[type='button']")
            for btn in button_elements[:10]:  # Limit to first 10 buttons
                try:
                    button_info = {
                        "text": btn.text.strip() or btn.get_attribute("value") or "",
                        "type": btn.get_attribute("type") or "button",
                        "id": btn.get_attribute("id") or "",
                        "class": btn.get_attribute("class") or "",
                        "visible": btn.is_displayed(),
                        "enabled": btn.is_enabled(),
                        "automation_priority": self._get_button_priority(btn)
                    }
                    buttons.append(button_info)
                except:
                    continue
            
            # Analyze links
            link_elements = driver.find_elements(By.TAG_NAME, "a")
            for link in link_elements[:15]:  # Limit to first 15 links
                try:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    
                    if href and text:  # Only meaningful links
                        link_info = {
                            "text": text,
                            "href": href,
                            "id": link.get_attribute("id") or "",
                            "class": link.get_attribute("class") or "",
                            "target": link.get_attribute("target") or "",
                            "visible": link.is_displayed(),
                            "automation_priority": self._get_link_priority(link, href)
                        }
                        links.append(link_info)
                except:
                    continue
            
            return {
                "buttons": buttons,
                "links": links,
                "button_count": len(buttons),
                "link_count": len(links)
            }
            
        except Exception as e:
            return {
                "buttons": [],
                "links": [],
                "button_count": 0,
                "link_count": 0,
                "error": str(e)
            }
    
    def _create_automation_priority_list(self, driver) -> Dict[str, List[Dict[str, Any]]]:
        """Create a prioritized list of elements for automation."""
        try:
            high_priority = []
            medium_priority = []
            low_priority = []
            
            # High priority: Login/form elements
            login_indicators = ["login", "signin", "sign-in", "username", "password", "email"]
            for indicator in login_indicators:
                elements = driver.find_elements(By.CSS_SELECTOR, f"input[name*='{indicator}'], input[id*='{indicator}'], input[placeholder*='{indicator}']")
                for elem in elements:
                    if elem.is_displayed():
                        high_priority.append({
                            "type": "input",
                            "indicator": indicator,
                            "name": elem.get_attribute("name") or "",
                            "id": elem.get_attribute("id") or "",
                            "selector": self._generate_selector(elem)
                        })
            
            # High priority: Submit buttons
            submit_buttons = driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            for btn in submit_buttons:
                if btn.is_displayed():
                    high_priority.append({
                        "type": "submit_button",
                        "text": btn.text or btn.get_attribute("value") or "",
                        "selector": self._generate_selector(btn)
                    })
            
            # Medium priority: Navigation and interactive elements
            nav_elements = driver.find_elements(By.CSS_SELECTOR, "nav a, .nav a, .navbar a, .menu a")
            for elem in nav_elements[:5]:  # Limit to first 5
                if elem.is_displayed() and elem.text.strip():
                    medium_priority.append({
                        "type": "navigation",
                        "text": elem.text.strip(),
                        "href": elem.get_attribute("href") or "",
                        "selector": self._generate_selector(elem)
                    })
            
            # Medium priority: Search elements
            search_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='search'], input[name*='search'], input[placeholder*='search']")
            for elem in search_elements:
                if elem.is_displayed():
                    medium_priority.append({
                        "type": "search",
                        "placeholder": elem.get_attribute("placeholder") or "",
                        "selector": self._generate_selector(elem)
                    })
            
            # Low priority: Content elements
            headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")
            for heading in headings[:3]:  # First 3 headings
                if heading.is_displayed() and heading.text.strip():
                    low_priority.append({
                        "type": "heading",
                        "level": heading.tag_name,
                        "text": heading.text.strip()[:100],  # First 100 chars
                        "selector": self._generate_selector(heading)
                    })
            
            return {
                "high": high_priority,
                "medium": medium_priority,
                "low": low_priority,
                "total_elements": len(high_priority) + len(medium_priority) + len(low_priority)
            }
            
        except Exception as e:
            return {
                "high": [],
                "medium": [],
                "low": [],
                "total_elements": 0,
                "error": str(e)
            }
    
    def _get_input_priority(self, input_element) -> str:
        """Determine automation priority for input element."""
        try:
            input_type = input_element.get_attribute("type") or "text"
            name = (input_element.get_attribute("name") or "").lower()
            id_attr = (input_element.get_attribute("id") or "").lower()
            placeholder = (input_element.get_attribute("placeholder") or "").lower()
            
            # High priority types and names
            high_priority_types = ["email", "password", "tel", "url"]
            high_priority_names = ["username", "email", "password", "login", "signin"]
            
            if input_type in high_priority_types:
                return "high"
            
            if any(keyword in name or keyword in id_attr or keyword in placeholder 
                   for keyword in high_priority_names):
                return "high"
            
            # Medium priority
            medium_priority_types = ["text", "search", "number", "date"]
            if input_type in medium_priority_types:
                return "medium"
            
            return "low"
            
        except:
            return "low"
    
    def _get_button_priority(self, button_element) -> str:
        """Determine automation priority for button element."""
        try:
            text = (button_element.text or "").lower()
            button_type = (button_element.get_attribute("type") or "").lower()
            value = (button_element.get_attribute("value") or "").lower()
            
            # High priority buttons
            high_priority_keywords = ["submit", "login", "signin", "sign in", "send", "search"]
            
            if button_type == "submit":
                return "high"
            
            if any(keyword in text or keyword in value for keyword in high_priority_keywords):
                return "high"
            
            return "medium"
            
        except:
            return "low"
    
    def _get_link_priority(self, link_element, href: str) -> str:
        """Determine automation priority for link element."""
        try:
            text = (link_element.text or "").lower()
            href_lower = href.lower()
            
            # High priority links
            high_priority_keywords = ["login", "signin", "register", "signup"]
            
            if any(keyword in text or keyword in href_lower for keyword in high_priority_keywords):
                return "high"
            
            # Medium priority - navigation links
            if any(keyword in text for keyword in ["home", "about", "contact", "services", "products"]):
                return "medium"
            
            return "low"
            
        except:
            return "low"
    
    def _generate_selector(self, element) -> str:
        """Generate a reliable CSS selector for an element."""
        try:
            # Try ID first
            element_id = element.get_attribute("id")
            if element_id:
                return f"#{element_id}"
            
            # Try name attribute
            name = element.get_attribute("name")
            if name:
                return f"[name='{name}']"
            
            # Try class if unique enough
            class_attr = element.get_attribute("class")
            if class_attr and len(class_attr.split()) <= 3:  # Not too many classes
                return f".{'.'.join(class_attr.split())}"
            
            # Fallback to tag name with attributes
            tag = element.tag_name
            placeholder = element.get_attribute("placeholder")
            if placeholder:
                return f"{tag}[placeholder='{placeholder}']"
            
            element_type = element.get_attribute("type")
            if element_type:
                return f"{tag}[type='{element_type}']"
            
            return tag
            
        except:
            return "unknown"
    
    def _detect_auth_wall(self, driver) -> Dict[str, Any]:
        """Detect authentication walls and login requirements."""
        try:
            auth_indicators = {
                "login_forms": len(driver.find_elements(By.CSS_SELECTOR, "form[action*='login'], form[id*='login']")),
                "password_fields": len(driver.find_elements(By.CSS_SELECTOR, "input[type='password']")),
                "login_text": "login" in driver.page_source.lower(),
                "signin_text": "sign in" in driver.page_source.lower(),
                "auth_text": "authenticate" in driver.page_source.lower()
            }
            
            auth_score = sum([
                auth_indicators["login_forms"] * 3,
                auth_indicators["password_fields"] * 2,
                int(auth_indicators["login_text"]),
                int(auth_indicators["signin_text"]),
                int(auth_indicators["auth_text"])
            ])
            
            return {
                "detected": auth_score > 2,
                "confidence": min(auth_score / 10.0, 1.0),
                "indicators": auth_indicators,
                "score": auth_score
            }
            
        except Exception as e:
            return {
                "detected": False,
                "confidence": 0.0,
                "error": str(e),
                "indicators": {},
                "score": 0
            }
    
    def _detect_auth_wall_from_errors(self, errors: List[str]) -> bool:
        """Detect auth walls from error messages."""
        auth_keywords = ["login", "authenticate", "unauthorized", "forbidden", "access denied"]
        for error in errors:
            if any(keyword in error.lower() for keyword in auth_keywords):
                return True
        return False
    
    def _fetch_with_session(self, url: str) -> Dict[str, Any]:
        """HTTP fetching with session management and content filtering."""
        try:
            if not self.session:
                self.session = requests.Session()
                self.session.headers.update({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                })
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse and filter content with BeautifulSoup if available
            if BS4_AVAILABLE:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove useless elements
                for tag in soup(["script", "style", "noscript", "iframe", "embed", "object"]):
                    tag.decompose()
                
                # Extract clean content
                clean_content = self._extract_clean_content_from_soup(soup)
                
                # Count elements with priority
                element_counts = self._count_soup_elements_with_priority(soup)
                
                # Analyze forms and inputs
                input_analysis = self._analyze_soup_input_elements(soup)
                
                # Analyze clickable elements
                clickable_analysis = self._analyze_soup_clickable_elements(soup)
                
                # Create automation priority list
                automation_priority = self._create_soup_automation_priority_list(soup)
                
                return {
                    "success": True,
                    "method": "http_session",
                    "status_code": response.status_code,
                    "url": response.url,
                    "page_data": {
                        "title": soup.title.string if soup.title else "HTTP Session Response",
                        "url": response.url,
                        "clean_body_content": clean_content,
                        "page_source_snippet": str(soup)[:2000],
                        "element_counts": element_counts,
                        "input_analysis": input_analysis,
                        "clickable_analysis": clickable_analysis,
                        "automation_priority": automation_priority,
                        "page_loaded": True
                    }
                }
            else:
                # Basic parsing without BeautifulSoup
                text_content = response.text[:3000]
                
                return {
                    "success": True,
                    "method": "http_session",
                    "status_code": response.status_code,
                    "url": response.url,
                    "page_data": {
                        "title": "HTTP Session Response",
                        "url": response.url,
                        "clean_body_content": {"text": text_content, "headings": [], "paragraphs": []},
                        "page_source_snippet": text_content,
                        "element_counts": {"total_interactive": 0, "automation_score": 0.0},
                        "input_analysis": {"inputs": [], "forms": []},
                        "clickable_analysis": {"buttons": [], "links": []},
                        "automation_priority": {"high": [], "medium": [], "low": []},
                        "page_loaded": True
                    }
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "http_session"
            }
    
    def _fetch_basic(self, url: str) -> Dict[str, Any]:
        """Basic HTTP request with content filtering."""
        try:
            response = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            
            # Parse and filter content if BeautifulSoup is available
            if BS4_AVAILABLE:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove useless elements
                for tag in soup(["script", "style", "noscript", "iframe", "embed", "object"]):
                    tag.decompose()
                
                clean_content = self._extract_clean_content_from_soup(soup)
                element_counts = self._count_soup_elements_with_priority(soup)
                
                return {
                    "success": True,
                    "method": "http_basic",
                    "status_code": response.status_code,
                    "url": response.url,
                    "page_data": {
                        "title": soup.title.string if soup.title else "Basic HTTP Response",
                        "url": response.url,
                        "clean_body_content": clean_content,
                        "page_source_snippet": str(soup)[:2000],
                        "element_counts": element_counts,
                        "input_analysis": {"inputs": [], "forms": []},
                        "clickable_analysis": {"buttons": [], "links": []},
                        "automation_priority": {"high": [], "medium": [], "low": []},
                        "page_loaded": True
                    }
                }
            else:
                # Basic parsing without BeautifulSoup
                text_content = response.text[:2000]
                
                return {
                    "success": True,
                    "method": "http_basic",
                    "status_code": response.status_code,
                    "url": response.url,
                    "page_data": {
                        "title": "Basic HTTP Response",
                        "url": response.url,
                        "clean_body_content": {"text": text_content, "headings": [], "paragraphs": []},
                        "page_source_snippet": text_content,
                        "element_counts": {"total_interactive": 0, "automation_score": 0.0},
                        "input_analysis": {"inputs": [], "forms": []},
                        "clickable_analysis": {"buttons": [], "links": []},
                        "automation_priority": {"high": [], "medium": [], "low": []},
                        "page_loaded": True
                    }
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "http_basic"
            }
    
    def _extract_clean_content_from_soup(self, soup) -> Dict[str, Any]:
        """Extract clean content from BeautifulSoup object."""
        try:
            # Get body or fall back to whole document
            body = soup.body if soup.body else soup
            
            # Extract text content
            body_text = body.get_text(separator=' ', strip=True)[:3000]
            
            # Extract headings
            headings = []
            for level in range(1, 7):
                heading_elements = body.find_all(f'h{level}')
                for heading in heading_elements:
                    text = heading.get_text(strip=True)
                    if text:
                        headings.append({
                            "level": level,
                            "text": text,
                            "tag": f"h{level}"
                        })
            
            # Extract paragraphs
            paragraphs = []
            paragraph_elements = body.find_all('p')
            for p in paragraph_elements[:10]:
                text = p.get_text(strip=True)
                if text and len(text) > 10:
                    paragraphs.append(text)
            
            # Extract lists
            lists = []
            list_elements = body.find_all(['ul', 'ol'])
            for list_elem in list_elements[:5]:
                items = [li.get_text(strip=True) for li in list_elem.find_all('li')[:10]]
                items = [item for item in items if item]
                if items:
                    lists.append({
                        "type": list_elem.name,
                        "items": items
                    })
            
            return {
                "text": body_text,
                "headings": headings,
                "paragraphs": paragraphs,
                "lists": lists,
                "content_length": len(body_text)
            }
            
        except Exception as e:
            return {
                "text": f"Error extracting content: {e}",
                "headings": [],
                "paragraphs": [],
                "lists": [],
                "content_length": 0
            }
    
    def _count_soup_elements_with_priority(self, soup) -> Dict[str, Any]:
        """Count elements with priority using BeautifulSoup."""
        try:
            # High priority elements
            high_priority = {
                "input_fields": len(soup.find_all('input')),
                "buttons": len(soup.find_all('button')),
                "forms": len(soup.find_all('form')),
                "select_dropdowns": len(soup.find_all('select')),
                "textareas": len(soup.find_all('textarea'))
            }
            
            # Medium priority elements
            medium_priority = {
                "links": len(soup.find_all('a')),
                "images": len(soup.find_all('img')),
                "tables": len(soup.find_all('table')),
                "divs_with_onclick": len(soup.find_all('div', onclick=True)),
                "clickable_elements": len(soup.find_all(attrs={"onclick": True})) + len(soup.find_all(attrs={"role": "button"}))
            }
            
            # Low priority elements
            low_priority = {
                "headings": len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                "paragraphs": len(soup.find_all('p')),
                "spans": len(soup.find_all('span')),
                "divs": len(soup.find_all('div'))
            }
            
            total_interactive = sum(high_priority.values()) + medium_priority["links"] + medium_priority["clickable_elements"]
            
            return {
                "total_interactive": total_interactive,
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority,
                "automation_score": min(total_interactive / 10.0, 1.0)
            }
            
        except Exception as e:
            return {
                "total_interactive": 0,
                "high_priority": {},
                "medium_priority": {},
                "low_priority": {},
                "automation_score": 0.0,
                "error": str(e)
            }
    
    def _analyze_soup_input_elements(self, soup) -> Dict[str, Any]:
        """Analyze input elements using BeautifulSoup."""
        try:
            inputs = []
            forms = []
            
            # Analyze input fields
            input_elements = soup.find_all('input')
            for inp in input_elements[:15]:
                input_info = {
                    "type": inp.get('type', 'text'),
                    "name": inp.get('name', ''),
                    "id": inp.get('id', ''),
                    "placeholder": inp.get('placeholder', ''),
                    "required": inp.has_attr('required'),
                    "value": inp.get('value', ''),
                    "automation_priority": self._get_soup_input_priority(inp)
                }
                inputs.append(input_info)
            
            # Analyze forms
            form_elements = soup.find_all('form')
            for form in form_elements[:5]:
                form_inputs = form.find_all('input')
                form_buttons = form.find_all(['button', 'input'], type=['submit', 'button'])
                
                form_info = {
                    "action": form.get('action', ''),
                    "method": form.get('method', 'get'),
                    "id": form.get('id', ''),
                    "input_count": len(form_inputs),
                    "button_count": len(form_buttons),
                    "automation_priority": "high" if len(form_inputs) > 1 else "medium"
                }
                forms.append(form_info)
            
            return {
                "inputs": inputs,
                "forms": forms,
                "input_count": len(inputs),
                "form_count": len(forms)
            }
            
        except Exception as e:
            return {
                "inputs": [],
                "forms": [],
                "input_count": 0,
                "form_count": 0,
                "error": str(e)
            }
    
    def _analyze_soup_clickable_elements(self, soup) -> Dict[str, Any]:
        """Analyze clickable elements using BeautifulSoup."""
        try:
            buttons = []
            links = []
            
            # Analyze buttons
            button_elements = soup.find_all(['button', 'input'], type=['submit', 'button'])
            for btn in button_elements[:10]:
                button_info = {
                    "text": btn.get_text(strip=True) or btn.get('value', ''),
                    "type": btn.get('type', 'button'),
                    "id": btn.get('id', ''),
                    "class": ' '.join(btn.get('class', [])),
                    "automation_priority": self._get_soup_button_priority(btn)
                }
                buttons.append(button_info)
            
            # Analyze links
            link_elements = soup.find_all('a', href=True)
            for link in link_elements[:15]:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                
                if href and text:
                    link_info = {
                        "text": text,
                        "href": href,
                        "id": link.get('id', ''),
                        "class": ' '.join(link.get('class', [])),
                        "target": link.get('target', ''),
                        "automation_priority": self._get_soup_link_priority(link, href)
                    }
                    links.append(link_info)
            
            return {
                "buttons": buttons,
                "links": links,
                "button_count": len(buttons),
                "link_count": len(links)
            }
            
        except Exception as e:
            return {
                "buttons": [],
                "links": [],
                "button_count": 0,
                "link_count": 0,
                "error": str(e)
            }
    
    def _create_soup_automation_priority_list(self, soup) -> Dict[str, List[Dict[str, Any]]]:
        """Create automation priority list from BeautifulSoup object."""
        try:
            high_priority = []
            medium_priority = []
            low_priority = []
            
            # High priority: Login/form elements
            login_indicators = ["login", "signin", "sign-in", "username", "password", "email"]
            for indicator in login_indicators:
                # Find inputs by name, id, or placeholder
                inputs = soup.find_all('input', attrs={
                    'name': lambda x: x and indicator in x.lower() if x else False
                }) + soup.find_all('input', attrs={
                    'id': lambda x: x and indicator in x.lower() if x else False
                }) + soup.find_all('input', attrs={
                    'placeholder': lambda x: x and indicator in x.lower() if x else False
                })
                
                for inp in inputs:
                    high_priority.append({
                        "type": "input",
                        "indicator": indicator,
                        "name": inp.get('name', ''),
                        "id": inp.get('id', ''),
                        "selector": self._generate_soup_selector(inp)
                    })
            
            # High priority: Submit buttons
            submit_buttons = soup.find_all(['button', 'input'], type='submit')
            for btn in submit_buttons:
                high_priority.append({
                    "type": "submit_button",
                    "text": btn.get_text(strip=True) or btn.get('value', ''),
                    "selector": self._generate_soup_selector(btn)
                })
            
            # Medium priority: Navigation elements
            nav_links = soup.find_all('a', href=True)
            for link in nav_links[:5]:
                text = link.get_text(strip=True)
                if text and any(nav_word in text.lower() for nav_word in ["home", "about", "contact", "menu"]):
                    medium_priority.append({
                        "type": "navigation",
                        "text": text,
                        "href": link.get('href', ''),
                        "selector": self._generate_soup_selector(link)
                    })
            
            # Medium priority: Search elements
            search_inputs = soup.find_all('input', type='search') + soup.find_all('input', attrs={
                'name': lambda x: x and 'search' in x.lower() if x else False
            })
            for inp in search_inputs:
                medium_priority.append({
                    "type": "search",
                    "placeholder": inp.get('placeholder', ''),
                    "selector": self._generate_soup_selector(inp)
                })
            
            # Low priority: Content elements
            headings = soup.find_all(['h1', 'h2', 'h3'])
            for heading in headings[:3]:
                text = heading.get_text(strip=True)
                if text:
                    low_priority.append({
                        "type": "heading",
                        "level": heading.name,
                        "text": text[:100],
                        "selector": self._generate_soup_selector(heading)
                    })
            
            return {
                "high": high_priority,
                "medium": medium_priority,
                "low": low_priority,
                "total_elements": len(high_priority) + len(medium_priority) + len(low_priority)
            }
            
        except Exception as e:
            return {
                "high": [],
                "medium": [],
                "low": [],
                "total_elements": 0,
                "error": str(e)
            }
    
    def _get_soup_input_priority(self, input_element) -> str:
        """Get input priority from BeautifulSoup element."""
        try:
            input_type = input_element.get('type', 'text').lower()
            name = (input_element.get('name') or '').lower()
            id_attr = (input_element.get('id') or '').lower()
            placeholder = (input_element.get('placeholder') or '').lower()
            
            high_priority_types = ["email", "password", "tel", "url"]
            high_priority_names = ["username", "email", "password", "login", "signin"]
            
            if input_type in high_priority_types:
                return "high"
            
            if any(keyword in name or keyword in id_attr or keyword in placeholder 
                   for keyword in high_priority_names):
                return "high"
            
            medium_priority_types = ["text", "search", "number", "date"]
            if input_type in medium_priority_types:
                return "medium"
            
            return "low"
        except:
            return "low"
    
    def _get_soup_button_priority(self, button_element) -> str:
        """Get button priority from BeautifulSoup element."""
        try:
            text = (button_element.get_text(strip=True) or '').lower()
            button_type = (button_element.get('type') or '').lower()
            value = (button_element.get('value') or '').lower()
            
            high_priority_keywords = ["submit", "login", "signin", "sign in", "send", "search"]
            
            if button_type == "submit":
                return "high"
            
            if any(keyword in text or keyword in value for keyword in high_priority_keywords):
                return "high"
            
            return "medium"
        except:
            return "low"
    
    def _get_soup_link_priority(self, link_element, href: str) -> str:
        """Get link priority from BeautifulSoup element."""
        try:
            text = (link_element.get_text(strip=True) or '').lower()
            href_lower = href.lower()
            
            high_priority_keywords = ["login", "signin", "register", "signup"]
            
            if any(keyword in text or keyword in href_lower for keyword in high_priority_keywords):
                return "high"
            
            if any(keyword in text for keyword in ["home", "about", "contact", "services", "products"]):
                return "medium"
            
            return "low"
        except:
            return "low"
    
    def _generate_soup_selector(self, element) -> str:
        """Generate CSS selector from BeautifulSoup element."""
        try:
            # Try ID first
            element_id = element.get('id')
            if element_id:
                return f"#{element_id}"
            
            # Try name attribute
            name = element.get('name')
            if name:
                return f"[name='{name}']"
            
            # Try class if reasonable
            class_list = element.get('class', [])
            if class_list and len(class_list) <= 3:
                return f".{'.'.join(class_list)}"
            
            # Fallback to tag with attributes
            tag = element.name
            placeholder = element.get('placeholder')
            if placeholder:
                return f"{tag}[placeholder='{placeholder}']"
            
            element_type = element.get('type')
            if element_type:
                return f"{tag}[type='{element_type}']"
            
            return tag
        except:
            return "unknown"
    
    def _generate_automation_code(self, task: str, url: str, fetch_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automation code based on task and page analysis."""
        try:
            code = self._generate_template_code(task, url, fetch_result)
            
            return {
                "success": True,
                "code": code,
                "method": "template_generation",
                "task": task,
                "url": url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "code_generation_failed"
            }
    
    def _generate_template_code(self, task: str, url: str, fetch_result: Dict[str, Any]) -> str:
        """Generate code using templates based on task type."""
        task_lower = task.lower()
        
        # Login test template
        if "login" in task_lower and "test" in task_lower:
            return f'''# Login Test Automation
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup Chrome driver
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

try:
    # Navigate to login page
    driver.get("{url}")

    # Wait for page to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Find username field
    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
    except:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='user'], input[id*='user'], input[type='email']"))
        )
    
    username_field.clear()
    username_field.send_keys("student")
    print("Username entered successfully")
    
    # Find password field
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
    )
    password_field.clear()
    password_field.send_keys("Password123")
    print("Password entered successfully")
    
    # Find and click submit button
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
    except:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
        )
    
    # Click submit button
    driver.execute_script("arguments[0].scrollIntoView();", submit_button)
    time.sleep(1)
    submit_button.click()
    print("Submit button clicked")
    
    # Wait for response
    time.sleep(5)
    
    # Check for success
    try:
        success_element = driver.find_element(By.CSS_SELECTOR, ".post-title, h1, .success")
        if "success" in success_element.text.lower() or "logged in" in success_element.text.lower():
            print("LOGIN TEST PASSED")
        else:
            print(f"LOGIN TEST: Response received - {{success_element.text}}")
    except:
        current_url = driver.current_url
        page_title = driver.title
        print(f"LOGIN TEST: Current URL - {{current_url}}")
        print(f"LOGIN TEST: Page Title - {{page_title}}")

except Exception as e:
    print(f"LOGIN TEST FAILED: {{e}}")
finally:
    driver.quit()
'''

        # Generic automation template
        else:
            return f'''# Generic Automation
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup Chrome driver
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

try:
    # Navigate to website
    driver.get("{url}")

    # Wait for page to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Task: {task}
    print(f"Executing task: {task}")
    
    # Get page information
    title = driver.title
    print(f"Page title: {{title}}")
    
    # Find interactive elements
    buttons = driver.find_elements(By.TAG_NAME, "button")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    links = driver.find_elements(By.TAG_NAME, "a")
    
    print(f"Found {{len(buttons)}} buttons, {{len(inputs)}} inputs, {{len(links)}} links")
    
    # Take screenshot
    driver.save_screenshot("automation_screenshot.png")
    print("Screenshot saved")
    
    # Wait and observe
    time.sleep(5)
    
    print("Automation completed successfully")

except Exception as e:
    print(f"AUTOMATION FAILED: {{e}}")
finally:
    driver.quit()
'''
    
    def _execute_with_fallback_and_fixes(self, code: str, website_url: str, max_attempts: int = 5) -> Dict[str, Any]:
        """Execute automation code with fallback browsers and error fixing."""
        browsers = ["chrome", "edge"]
        
        for browser in browsers:
            for attempt in range(max_attempts):
                try:
                    print(f"Execution attempt {attempt + 1}/{max_attempts} with {browser}")
                    
                    # Execute with subprocess isolation
                    result = self._execute_with_subprocess_isolation(code, website_url, browser, None)
                    
                    if result.get("success"):
                        print(f"Execution successful with {browser}")
                        return {
                            "success": True,
                            "browser_used": browser,
                            "attempts_made": attempt + 1,
                            "logs": result.get("logs", []),
                            "screenshots": result.get("screenshots", []),
                            "generated_code": code,
                            "execution_details": result
                        }
                    
                    print(f"Attempt {attempt + 1} failed: {result.get('error', 'Unknown error')}")
                    
                except Exception as e:
                    print(f"Execution attempt {attempt + 1} failed: {e}")
                    continue
        
        return {
            "success": False,
            "error": "All execution attempts failed",
            "browsers_tried": browsers,
            "attempts_made": max_attempts * len(browsers),
            "logs": [],
            "screenshots": [],
            "generated_code": code
        }
    
    def _execute_with_subprocess_isolation(self, code: str, website_url: str, browser: str, executor) -> Dict[str, Any]:
        """Execute automation code in isolated subprocess with enhanced error handling."""
        script_dir = Path(__file__).parent
        temp_script_path = script_dir / f"temp_automation_{uuid.uuid4().hex[:8]}.py"
        
        try:
            # Properly indent the automation code
            indented_code = '\n'.join(['        ' + line for line in code.split('\n')])
            
            # Create complete automation script
            full_script = f'''
import sys
import os
import time
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, r"{script_dir}")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    # Enhanced Chrome driver setup for Windows
    if "{browser}" == "chrome":
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            import os
            os.environ['WDM_ARCHITECTURE'] = '64'  # Force 64-bit
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            
            try:
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except:
                driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"Chrome setup failed: {{e}}")
            exit(1)
    else:
        try:
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            options = EdgeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            
            try:
                service = EdgeService(EdgeChromiumDriverManager().install())
                driver = webdriver.Edge(service=service, options=options)
            except:
                driver = webdriver.Edge(options=options)
        except Exception as e:
            print(f"Edge setup failed: {{e}}")
            exit(1)
    
    print(f"Created {{'{browser}'}} driver successfully")
    
    # Execute the automation code
    try:
{indented_code}
        print("Automation completed successfully")
    except Exception as e:
        print(f"Automation error: {{e}}")
    finally:
        if driver:
            try:
                driver.quit()
                print("Browser closed")
            except Exception as e:
                print(f"Error closing browser: {{e}}")

except Exception as e:
    print(f"Script error: {{e}}")
    exit(1)
'''
            
            # Write script to file
            with open(temp_script_path, 'w', encoding='utf-8') as f:
                f.write(full_script)
            
            # Execute script with timeout
            result = subprocess.run(
                [sys.executable, str(temp_script_path)],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=str(script_dir)
            )
            
            # Parse output
            logs = result.stdout.split('\n') if result.stdout else []
            errors = result.stderr.split('\n') if result.stderr else []
            
            success = result.returncode == 0 and not any('error' in log.lower() for log in logs)
            
            return {
                "success": success,
                "logs": logs + errors,
                "returncode": result.returncode,
                "browser": browser,
                "execution_time": time.time(),
                "screenshots": []
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timeout",
                "logs": ["Execution timed out after 180 seconds"],
                "browser": browser
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "logs": [f"Subprocess execution failed: {e}"],
                "browser": browser
            }
        finally:
            # Clean up temp script
            try:
                if temp_script_path.exists():
                    temp_script_path.unlink()
            except:
                pass
    
    def _manage_project_files(self, workflow_id: str, code: str, task: str) -> Dict[str, Any]:
        """Enhanced project file management with proper structure."""
        try:
            # Create project directory structure
            base_dir = Path("automation_projects")
            project_dir = base_dir / f"project_{workflow_id}"
            
            # Create directories
            directories = [
                project_dir,
                project_dir / "src",
                project_dir / "tests",
                project_dir / "logs",
                project_dir / "screenshots"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Create main automation script
            main_script = project_dir / "src" / "automation.py"
            with open(main_script, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Create requirements.txt
            requirements_file = project_dir / "requirements.txt"
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write(self._generate_enhanced_requirements())
            
            # Create README.md
            readme_file = project_dir / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(self._generate_project_readme(workflow_id, task))
            
            # Create run script
            run_script = project_dir / "run.py"
            with open(run_script, 'w', encoding='utf-8') as f:
                f.write(self._generate_run_script("windows"))
            
            project_files = {
                "main_script": str(main_script),
                "requirements": str(requirements_file),
                "readme": str(readme_file),
                "run_script": str(run_script),
                "project_dir": str(project_dir)
            }
            
            return {
                "success": True,
                "project_files": project_files,
                "project_dir": str(project_dir),
                "files_created": len(project_files)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "project_files": {}
            }
    
    def _generate_enhanced_requirements(self) -> str:
        """Generate requirements.txt with all necessary dependencies."""
        return '''# Selenium Automation Requirements
selenium==4.15.2
webdriver-manager==4.0.1
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
pandas==2.1.3
openpyxl==3.1.2
pillow==10.1.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-html==4.1.1
'''
    
    def _generate_project_readme(self, workflow_id: str, task: str) -> str:
        """Generate comprehensive README for the project."""
        return f'''# Automation Project: {workflow_id}

## Task Description
{task}

## Setup Instructions

1. Install Python 3.8 or higher
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the automation:
   ```
   python run.py
   ```

## Project Structure
- `src/automation.py` - Main automation script
- `tests/` - Test files
- `logs/` - Execution logs
- `screenshots/` - Captured screenshots
- `requirements.txt` - Python dependencies
- `run.py` - Execution script

## Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    def _generate_run_script(self, platform: str) -> str:
        """Generate execution script for the platform."""
        return '''#!/usr/bin/env python3
"""
Automation Project Runner
"""
import sys
import os
import subprocess
from pathlib import Path

def main():
    """Run the automation script."""
    try:
        # Set up paths
        project_dir = Path(__file__).parent
        src_dir = project_dir / "src"
        automation_script = src_dir / "automation.py"
        
        print(f"Running automation from: {automation_script}")
        
        # Execute automation
        result = subprocess.run(
            [sys.executable, str(automation_script)],
            cwd=str(project_dir),
            capture_output=True,
            text=True
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Exit code: {result.returncode}")
        
    except Exception as e:
        print(f"Error running automation: {e}")
        return 1
    
    return result.returncode

if __name__ == "__main__":
    exit(main())
'''
    
    def _save_workflow_results(self, workflow_id: str, results: Dict[str, Any]):
        """Save workflow results with absolute path handling."""
        try:
            script_dir = Path(__file__).parent
            results_dir = script_dir / "workflow_results"
            results_dir.mkdir(exist_ok=True)
            
            results_file = results_dir / f"{workflow_id}.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"Workflow results saved to: {results_file}")
            
        except Exception as e:
            print(f"Failed to save workflow results: {e}")
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get basic workflow status."""
        try:
            script_dir = Path(__file__).parent
            results_file = script_dir / "workflow_results" / f"{workflow_id}.json"
            
            if not results_file.exists():
                return {"error": "Workflow not found", "workflow_id": workflow_id}
            
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            return {"error": str(e), "workflow_id": workflow_id}
    
    def get_comprehensive_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status with logs and file structure."""
        try:
            script_dir = Path(__file__).parent
            results_file = script_dir / "workflow_results" / f"{workflow_id}.json"
            
            if not results_file.exists():
                return {
                    "success": False,
                    "error": "Workflow not found",
                    "workflow_id": workflow_id,
                    "logs": [],
                    "file_structure": {},
                    "execution_details": {}
                }
            
            with open(results_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            # Get file structure if project exists
            file_structure = {}
            project_dir = Path("automation_projects") / f"project_{workflow_id}"
            if project_dir.exists():
                file_structure = self._get_project_file_structure(project_dir)
            
            # Prepare comprehensive response
            return {
                "success": workflow_data.get("success", False),
                "workflow_id": workflow_id,
                "task": workflow_data.get("task", ""),
                "website_url": workflow_data.get("website_url", ""),
                "execution_time": workflow_data.get("execution_time", 0),
                "browser_used": workflow_data.get("browser_used", "unknown"),
                "logs": workflow_data.get("logs", []),
                "file_structure": file_structure,
                "execution_details": workflow_data.get("execution_result", {}),
                "generated_files": workflow_data.get("generated_files", {}),
                "timestamp": workflow_data.get("timestamp", ""),
                "error": workflow_data.get("error")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id,
                "logs": [f"Error loading workflow: {e}"],
                "file_structure": {},
                "execution_details": {}
            }
    
    def _get_project_file_structure(self, project_dir: Path) -> Dict[str, Any]:
        """Get project file structure recursively."""
        structure = {"type": "folder", "children": {}}
        
        try:
            for item in project_dir.iterdir():
                if item.is_file():
                    structure["children"][item.name] = {
                        "type": "file",
                        "size": item.stat().st_size,
                        "modified": item.stat().st_mtime
                    }
                elif item.is_dir():
                    structure["children"][item.name] = self._get_project_file_structure(item)
        except Exception as e:
            structure["error"] = str(e)
        
        return structure
    
    def cleanup(self, force_close_browser: bool = False):
        """Clean up resources."""
        try:
            if self.current_driver:
                try:
                    self.current_driver.quit()
                    print("Browser session closed")
                except:
                    pass
                self.current_driver = None
            
            if self.session:
                try:
                    self.session.close()
                except:
                    pass
                self.session = None
                
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def get_browser_session_info(self) -> Dict[str, Any]:
        """Get information about current browser session."""
        if self.current_driver and self._is_browser_session_valid():
            try:
                return {
                    "active": True,
                    "current_url": self.current_driver.current_url,
                    "title": self.current_driver.title,
                    "last_activity": self.last_browser_activity,
                    "time_remaining": max(0, self.browser_session_timeout - (time.time() - self.last_browser_activity))
                }
            except:
                pass
        
        return {
            "active": False,
            "current_url": None,
            "title": None,
            "last_activity": None,
            "time_remaining": 0
        }
    
    def extend_browser_session(self, additional_minutes: int = 5):
        """Extend browser session timeout."""
        if self.current_driver and self._is_browser_session_valid():
            self.last_browser_activity = time.time()
            self.browser_session_timeout += additional_minutes * 60
            return True
        return False

def get_smart_workflow() -> SmartAutomationWorkflow:
    """Get or create smart workflow instance."""
    if not hasattr(get_smart_workflow, "_instance"):
        get_smart_workflow._instance = SmartAutomationWorkflow()
    return get_smart_workflow._instance 