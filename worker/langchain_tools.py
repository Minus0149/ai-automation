"""
LangChain Tools for Web Automation
Provides function calling capabilities for Selenium automation
"""

import os
import time
import json
from typing import List, Dict, Any, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from langchain.tools import BaseTool, StructuredTool
    from langchain.agents import Tool
    from langchain.schema import AgentAction, AgentFinish
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class WebAutomationTool(BaseModel):
    """Base class for web automation tools"""
    model_config = {"arbitrary_types_allowed": True}
    
    name: str
    description: str
    driver: Optional[webdriver.Chrome] = None
    wait_timeout: int = 10

class ClickElementTool(WebAutomationTool):
    """Tool for clicking web elements"""
    name: str = "click_element"
    description: str = "Click on a web element using various selectors (CSS, XPath, text content)"
    
    def _run(self, selector: str, selector_type: str = "css", timeout: int = 10) -> str:
        """Click on an element
        
        Args:
            selector: The selector string (CSS, XPath, or text)
            selector_type: Type of selector - 'css', 'xpath', 'text', 'id', 'class'
            timeout: Wait timeout in seconds
        """
        if not self.driver:
            return "Error: No driver instance available"
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            
            if selector_type == "css":
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            elif selector_type == "xpath":
                element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            elif selector_type == "id":
                element = wait.until(EC.element_to_be_clickable((By.ID, selector)))
            elif selector_type == "class":
                element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, selector)))
            elif selector_type == "text":
                element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{selector}')]")))
            else:
                return f"Error: Unsupported selector type '{selector_type}'"
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            element.click()
            return f"Successfully clicked element: {selector}"
            
        except TimeoutException:
            return f"Error: Element not found or not clickable: {selector}"
        except Exception as e:
            return f"Error clicking element: {str(e)}"

class TypeTextTool(WebAutomationTool):
    """Tool for typing text into input fields"""
    name: str = "type_text"
    description: str = "Type text into input fields, textareas, or editable elements"
    
    def _run(self, selector: str, text: str, selector_type: str = "css", clear_first: bool = True) -> str:
        """Type text into an element
        
        Args:
            selector: The selector string
            text: Text to type
            selector_type: Type of selector
            clear_first: Whether to clear the field first
        """
        if not self.driver:
            return "Error: No driver instance available"
        
        try:
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            if selector_type == "css":
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif selector_type == "xpath":
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            elif selector_type == "id":
                element = wait.until(EC.presence_of_element_located((By.ID, selector)))
            elif selector_type == "class":
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, selector)))
            else:
                return f"Error: Unsupported selector type '{selector_type}'"
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            if clear_first:
                element.clear()
            
            element.send_keys(text)
            return f"Successfully typed text into element: {selector}"
            
        except TimeoutException:
            return f"Error: Element not found: {selector}"
        except Exception as e:
            return f"Error typing text: {str(e)}"

class NavigateUrlTool(WebAutomationTool):
    """Tool for navigating to URLs"""
    name: str = "navigate_url"
    description: str = "Navigate to a specific URL"
    
    def _run(self, url: str) -> str:
        """Navigate to a URL
        
        Args:
            url: The URL to navigate to
        """
        if not self.driver:
            return "Error: No driver instance available"
        
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            
            return f"Successfully navigated to: {url}"
            
        except Exception as e:
            return f"Error navigating to URL: {str(e)}"

class WaitForElementTool(WebAutomationTool):
    """Tool for waiting for elements to appear"""
    name: str = "wait_for_element"
    description: str = "Wait for an element to appear on the page"
    
    def _run(self, selector: str, selector_type: str = "css", timeout: int = 10) -> str:
        """Wait for an element to appear
        
        Args:
            selector: The selector string
            selector_type: Type of selector
            timeout: Wait timeout in seconds
        """
        if not self.driver:
            return "Error: No driver instance available"
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            
            if selector_type == "css":
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif selector_type == "xpath":
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            elif selector_type == "id":
                element = wait.until(EC.presence_of_element_located((By.ID, selector)))
            elif selector_type == "class":
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, selector)))
            else:
                return f"Error: Unsupported selector type '{selector_type}'"
            
            return f"Element found: {selector}"
            
        except TimeoutException:
            return f"Error: Element not found within {timeout} seconds: {selector}"
        except Exception as e:
            return f"Error waiting for element: {str(e)}"

class GetElementTextTool(WebAutomationTool):
    """Tool for getting text from elements"""
    name: str = "get_element_text"
    description: str = "Get text content from a web element"
    
    def _run(self, selector: str, selector_type: str = "css") -> str:
        """Get text from an element
        
        Args:
            selector: The selector string
            selector_type: Type of selector
        """
        if not self.driver:
            return "Error: No driver instance available"
        
        try:
            wait = WebDriverWait(self.driver, self.wait_timeout)
            
            if selector_type == "css":
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif selector_type == "xpath":
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            elif selector_type == "id":
                element = wait.until(EC.presence_of_element_located((By.ID, selector)))
            elif selector_type == "class":
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, selector)))
            else:
                return f"Error: Unsupported selector type '{selector_type}'"
            
            text = element.text.strip()
            return f"Element text: {text}"
            
        except TimeoutException:
            return f"Error: Element not found: {selector}"
        except Exception as e:
            return f"Error getting element text: {str(e)}"

class ScrollPageTool(WebAutomationTool):
    """Tool for scrolling the page"""
    name: str = "scroll_page"
    description: str = "Scroll the page up, down, or to a specific element"
    
    def _run(self, direction: str = "down", amount: int = 500, element_selector: str = None) -> str:
        """Scroll the page
        
        Args:
            direction: 'up', 'down', 'top', 'bottom', or 'element'
            amount: Number of pixels to scroll (for up/down)
            element_selector: Selector for element to scroll to (if direction is 'element')
        """
        if not self.driver:
            return "Error: No driver instance available"
        
        try:
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{amount});")
            elif direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elif direction == "element" and element_selector:
                element = self.driver.find_element(By.CSS_SELECTOR, element_selector)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            else:
                return f"Error: Invalid scroll direction or missing element selector"
            
            time.sleep(0.5)  # Wait for scroll to complete
            return f"Successfully scrolled {direction}"
            
        except Exception as e:
            return f"Error scrolling page: {str(e)}"

class TakeScreenshotTool(WebAutomationTool):
    """Tool for taking screenshots"""
    name: str = "take_screenshot"
    description: str = "Take a screenshot of the current page"
    
    def _run(self, filename: str = None) -> str:
        """Take a screenshot
        
        Args:
            filename: Optional filename for the screenshot
        """
        if not self.driver:
            return "Error: No driver instance available"
        
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure screenshots directory exists
            screenshots_dir = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            
            filepath = os.path.join(screenshots_dir, filename)
            self.driver.save_screenshot(filepath)
            
            return f"Screenshot saved: {filepath}"
            
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"

class WebAutomationToolkit:
    """Collection of web automation tools for LangChain agents"""
    
    def __init__(self, driver: webdriver.Chrome = None):
        self.driver = driver
        self.tools = self._create_tools()
    
    def _create_tools(self) -> List[Tool]:
        """Create LangChain tools from automation classes"""
        tools = []
        
        if not LANGCHAIN_AVAILABLE:
            return tools
        
        # Click tool
        click_tool = Tool(
            name="click_element",
            description="Click on a web element using CSS selector, XPath, ID, class, or text content",
            func=lambda selector, selector_type="css", timeout=10: self._execute_tool(
                ClickElementTool(driver=self.driver), selector, selector_type, timeout
            )
        )
        tools.append(click_tool)
        
        # Type text tool
        type_tool = Tool(
            name="type_text",
            description="Type text into input fields or editable elements",
            func=lambda selector, text, selector_type="css", clear_first=True: self._execute_type_tool(
                selector, text, selector_type, clear_first
            )
        )
        tools.append(type_tool)
        
        # Navigate tool
        navigate_tool = Tool(
            name="navigate_url",
            description="Navigate to a specific URL",
            func=lambda url: self._execute_navigate_tool(url)
        )
        tools.append(navigate_tool)
        
        # Wait tool
        wait_tool = Tool(
            name="wait_for_element",
            description="Wait for an element to appear on the page",
            func=lambda selector, selector_type="css", timeout=10: self._execute_wait_tool(
                selector, selector_type, timeout
            )
        )
        tools.append(wait_tool)
        
        # Get text tool
        text_tool = Tool(
            name="get_element_text",
            description="Get text content from a web element",
            func=lambda selector, selector_type="css": self._execute_text_tool(selector, selector_type)
        )
        tools.append(text_tool)
        
        # Scroll tool
        scroll_tool = Tool(
            name="scroll_page",
            description="Scroll the page in different directions",
            func=lambda direction="down", amount=500, element_selector=None: self._execute_scroll_tool(
                direction, amount, element_selector
            )
        )
        tools.append(scroll_tool)
        
        # Screenshot tool
        screenshot_tool = Tool(
            name="take_screenshot",
            description="Take a screenshot of the current page",
            func=lambda filename=None: self._execute_screenshot_tool(filename)
        )
        tools.append(screenshot_tool)
        
        return tools
    
    def _execute_tool(self, tool_instance, *args, **kwargs):
        """Execute a tool instance"""
        return tool_instance._run(*args, **kwargs)
    
    def _execute_type_tool(self, selector, text, selector_type="css", clear_first=True):
        """Execute type text tool"""
        tool = TypeTextTool(driver=self.driver)
        return tool._run(selector, text, selector_type, clear_first)
    
    def _execute_navigate_tool(self, url):
        """Execute navigate tool"""
        tool = NavigateUrlTool(driver=self.driver)
        return tool._run(url)
    
    def _execute_wait_tool(self, selector, selector_type="css", timeout=10):
        """Execute wait tool"""
        tool = WaitForElementTool(driver=self.driver)
        return tool._run(selector, selector_type, timeout)
    
    def _execute_text_tool(self, selector, selector_type="css"):
        """Execute get text tool"""
        tool = GetElementTextTool(driver=self.driver)
        return tool._run(selector, selector_type)
    
    def _execute_scroll_tool(self, direction="down", amount=500, element_selector=None):
        """Execute scroll tool"""
        tool = ScrollPageTool(driver=self.driver)
        return tool._run(direction, amount, element_selector)
    
    def _execute_screenshot_tool(self, filename=None):
        """Execute screenshot tool"""
        tool = TakeScreenshotTool(driver=self.driver)
        return tool._run(filename)
    
    def update_driver(self, driver: webdriver.Chrome):
        """Update the driver instance for all tools"""
        self.driver = driver
    
    def get_tools(self) -> List[Tool]:
        """Get the list of tools"""
        return self.tools
    
    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all tools"""
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions) 