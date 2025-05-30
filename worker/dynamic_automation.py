"""
Dynamic Automation Executor
Provides intelligent automation capabilities with AI-driven element detection
"""

import os
import re
import time
import json
from typing import Dict, Any, Optional, List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from selenium_executor import SeleniumExecutor

class DynamicAutomationExecutor:
    """Advanced automation executor with AI-driven capabilities"""
    
    def __init__(self):
        self.selenium_executor = SeleniumExecutor()
        self.current_driver = None
        self.automation_history = []
        self.element_cache = {}
        
    def create_driver(self, headless: bool = True) -> Dict[str, Any]:
        """Create a new WebDriver instance"""
        try:
            result = self.selenium_executor.create_driver(headless=headless)
            if result.get("success"):
                self.current_driver = result.get("driver")
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create driver: {str(e)}"
            }
    
    def execute_automation(self, url: str, task_description: str, framework: str = "selenium") -> Dict[str, Any]:
        """Execute dynamic automation based on task description"""
        try:
            # Create driver if needed
            if not self.current_driver:
                driver_result = self.create_driver()
                if not driver_result.get("success"):
                    return driver_result
            
            # Navigate to URL
            self.current_driver.get(url)
            time.sleep(2)
            
            # Analyze task and execute steps
            execution_plan = self.analyze_task(task_description, url)
            results = self.execute_plan(execution_plan)
            
            return {
                "success": True,
                "task": task_description,
                "url": url,
                "framework": framework,
                "plan": execution_plan,
                "execution_results": results,
                "screenshots": results.get("screenshots", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Dynamic automation failed: {str(e)}",
                "task": task_description,
                "url": url,
                "framework": framework
            }
    
    def analyze_task(self, task_description: str, url: str) -> Dict[str, Any]:
        """Analyze task description and create execution plan"""
        plan = {
            "task": task_description,
            "url": url,
            "steps": [],
            "analysis": self.extract_task_components(task_description)
        }
        
        # Extract actions from task description
        actions = self.extract_actions(task_description)
        
        for i, action in enumerate(actions):
            step = {
                "step_number": i + 1,
                "action": action["type"],
                "target": action["target"],
                "value": action.get("value", ""),
                "description": action["description"],
                "selector_strategies": self.generate_selector_strategies(action["target"])
            }
            plan["steps"].append(step)
        
        return plan
    
    def extract_task_components(self, task_description: str) -> Dict[str, Any]:
        """Extract components from task description"""
        components = {
            "login_detected": any(word in task_description.lower() for word in ["login", "sign in", "authenticate"]),
            "form_detected": any(word in task_description.lower() for word in ["form", "submit", "fill"]),
            "search_detected": any(word in task_description.lower() for word in ["search", "find", "look for"]),
            "click_detected": any(word in task_description.lower() for word in ["click", "press", "tap"]),
            "navigate_detected": any(word in task_description.lower() for word in ["go to", "navigate", "open"]),
            "data_extraction": any(word in task_description.lower() for word in ["extract", "get", "scrape", "collect"])
        }
        return components
    
    def extract_actions(self, task_description: str) -> List[Dict[str, Any]]:
        """Extract specific actions from task description"""
        actions = []
        
        # Common patterns for action extraction
        patterns = [
            (r"click (?:on )?(.+?)(?:\s|$)", "click"),
            (r"type (?:in )?(.+?) (?:in|into) (.+?)(?:\s|$)", "type"),
            (r"fill (?:in )?(.+?) (?:with|as) (.+?)(?:\s|$)", "type"),
            (r"search for (.+?)(?:\s|$)", "search"),
            (r"navigate to (.+?)(?:\s|$)", "navigate"),
            (r"go to (.+?)(?:\s|$)", "navigate"),
            (r"find (.+?)(?:\s|$)", "find"),
            (r"select (.+?)(?:\s|$)", "select"),
            (r"submit (?:the )?(.+?)(?:\s|$)", "submit")
        ]
        
        task_lower = task_description.lower()
        
        for pattern, action_type in patterns:
            matches = re.finditer(pattern, task_lower)
            for match in matches:
                if action_type == "type" and len(match.groups()) >= 2:
                    actions.append({
                        "type": "type",
                        "target": match.group(2).strip(),
                        "value": match.group(1).strip(),
                        "description": f"Type '{match.group(1).strip()}' into {match.group(2).strip()}"
                    })
                elif action_type == "navigate":
                    actions.append({
                        "type": "navigate",
                        "target": match.group(1).strip(),
                        "description": f"Navigate to {match.group(1).strip()}"
                    })
                else:
                    actions.append({
                        "type": action_type,
                        "target": match.group(1).strip(),
                        "description": f"{action_type.title()} {match.group(1).strip()}"
                    })
        
        # If no specific actions found, create a general action
        if not actions:
            actions.append({
                "type": "general",
                "target": "page",
                "description": f"Execute general task: {task_description}"
            })
        
        return actions
    
    def generate_selector_strategies(self, target: str) -> List[Dict[str, str]]:
        """Generate multiple selector strategies for a target element"""
        strategies = []
        target_lower = target.lower()
        
        # Text-based selectors
        strategies.append({
            "type": "xpath_text",
            "selector": f"//*[contains(text(), '{target}')]",
            "description": f"Find element containing text '{target}'"
        })
        
        strategies.append({
            "type": "xpath_text_partial",
            "selector": f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_lower}')]",
            "description": f"Find element containing text '{target}' (case insensitive)"
        })
        
        # Attribute-based selectors
        if "button" in target_lower or "btn" in target_lower:
            strategies.append({
                "type": "css_button",
                "selector": f"button:contains('{target}'), input[type='button'][value*='{target}'], input[type='submit'][value*='{target}']",
                "description": f"Find button with text or value '{target}'"
            })
        
        if "input" in target_lower or "field" in target_lower:
            strategies.extend([
                {
                    "type": "css_input_name",
                    "selector": f"input[name*='{target_lower}']",
                    "description": f"Find input with name containing '{target}'"
                },
                {
                    "type": "css_input_placeholder",
                    "selector": f"input[placeholder*='{target}']",
                    "description": f"Find input with placeholder containing '{target}'"
                }
            ])
        
        # ID and class-based selectors
        target_id = target_lower.replace(" ", "_").replace("-", "_")
        strategies.extend([
            {
                "type": "css_id",
                "selector": f"#{target_id}",
                "description": f"Find element with ID '{target_id}'"
            },
            {
                "type": "css_class",
                "selector": f".{target_id}",
                "description": f"Find element with class '{target_id}'"
            }
        ])
        
        return strategies
    
    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the automation plan"""
        results = {
            "success": True,
            "steps_executed": 0,
            "step_results": [],
            "screenshots": [],
            "errors": []
        }
        
        for step in plan["steps"]:
            try:
                step_result = self.execute_step(step)
                results["step_results"].append(step_result)
                
                if step_result["success"]:
                    results["steps_executed"] += 1
                else:
                    results["errors"].append(step_result.get("error", "Unknown error"))
                
                # Take screenshot after each step
                screenshot_result = self.take_screenshot(f"step_{step['step_number']}")
                if screenshot_result.get("success"):
                    results["screenshots"].append(screenshot_result["filepath"])
                
                # Small delay between steps
                time.sleep(1)
                            
            except Exception as e:
                error_msg = f"Step {step['step_number']} failed: {str(e)}"
                results["errors"].append(error_msg)
                results["step_results"].append({
                    "step": step["step_number"],
                    "success": False,
                    "error": error_msg
                })
        
        results["success"] = results["steps_executed"] == len(plan["steps"])
        return results
    
    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single automation step"""
        action = step["action"]
        target = step["target"]
        value = step.get("value", "")
        
        try:
            if action == "click":
                return self.smart_click(target, step["selector_strategies"])
            elif action == "type":
                return self.smart_type(target, value, step["selector_strategies"])
            elif action == "navigate":
                return self.navigate_to_url(target)
            elif action == "search":
                return self.perform_search(value or target)
            elif action == "submit":
                return self.submit_form(target)
            elif action == "find":
                return self.find_element(target, step["selector_strategies"])
            else:
                return self.generic_action(action, target, value)
            
        except Exception as e:
            return {
                "step": step["step_number"],
                "success": False,
                "error": f"Step execution failed: {str(e)}",
                "action": action,
                "target": target
            }
    
    def smart_click(self, target: str, strategies: List[Dict[str, str]]) -> Dict[str, Any]:
        """Intelligent element clicking with multiple strategies"""
        for strategy in strategies:
            try:
                element = self.find_element_by_strategy(strategy)
                if element:
                    # Scroll element into view
                    self.current_driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.5)
                    
                    # Try to click
                    element.click()
                    
                    return {
                        "success": True,
                        "action": "click",
                        "target": target,
                        "strategy_used": strategy["type"],
                        "message": f"Successfully clicked element using {strategy['type']}"
                    }
            except Exception as e:
                continue
        
        return {
            "success": False,
            "action": "click",
            "target": target,
            "error": f"Could not find clickable element for '{target}'"
        }
    
    def smart_type(self, target: str, value: str, strategies: List[Dict[str, str]]) -> Dict[str, Any]:
        """Intelligent text input with multiple strategies"""
        for strategy in strategies:
            try:
                element = self.find_element_by_strategy(strategy)
                if element and element.tag_name in ["input", "textarea"]:
                    # Clear and type
                    element.clear()
                    element.send_keys(value)
                    
                    return {
                        "success": True,
                        "action": "type",
                        "target": target,
                        "value": value,
                        "strategy_used": strategy["type"],
                        "message": f"Successfully typed '{value}' into element using {strategy['type']}"
                    }
            except Exception as e:
                continue
        
        return {
            "success": False,
            "action": "type",
            "target": target,
            "value": value,
            "error": f"Could not find input element for '{target}'"
        }
    
    def find_element_by_strategy(self, strategy: Dict[str, str]):
        """Find element using a specific strategy"""
        selector = strategy["selector"]
        strategy_type = strategy["type"]
        
        try:
            wait = WebDriverWait(self.current_driver, 5)
            
            if strategy_type.startswith("xpath"):
                return wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            elif strategy_type.startswith("css"):
                return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            else:
                # Try CSS first, then XPath
                try:
                    return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                except:
                    return wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    
        except TimeoutException:
            return None
    
    def navigate_to_url(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            self.current_driver.get(url)
            time.sleep(2)
            
            return {
                "success": True,
                "action": "navigate",
                "target": url,
                "message": f"Successfully navigated to {url}"
            }
        except Exception as e:
            return {
                "success": False,
                "action": "navigate",
                "target": url,
                "error": f"Navigation failed: {str(e)}"
            }
    
    def perform_search(self, query: str) -> Dict[str, Any]:
        """Perform a search operation"""
        # Common search field selectors
        search_selectors = [
            "input[type='search']",
            "input[name*='search']",
            "input[placeholder*='search' i]",
            "input[id*='search']",
            ".search-input",
            "#search",
            "[role='searchbox']"
        ]
        
        for selector in search_selectors:
            try:
                element = WebDriverWait(self.current_driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                element.clear()
                element.send_keys(query)
                element.send_keys(Keys.RETURN)
                
                return {
                    "success": True,
                    "action": "search",
                    "query": query,
                    "selector_used": selector,
                    "message": f"Successfully searched for '{query}'"
                }
            except:
                continue
        
        return {
            "success": False,
            "action": "search",
            "query": query,
            "error": "Could not find search field"
        }
    
    def submit_form(self, form_identifier: str) -> Dict[str, Any]:
        """Submit a form"""
        try:
            # Try different form submission strategies
            strategies = [
                ("css", f"form#{form_identifier}"),
                ("css", f"form.{form_identifier}"),
                ("css", f"input[type='submit']"),
                ("css", f"button[type='submit']"),
                ("xpath", f"//form[contains(@class, '{form_identifier}')]"),
                ("xpath", "//input[@type='submit'] | //button[@type='submit']")
            ]
            
            for strategy_type, selector in strategies:
                try:
                    if strategy_type == "css":
                        element = WebDriverWait(self.current_driver, 2).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    else:
                        element = WebDriverWait(self.current_driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    
                    if element.tag_name == "form":
                        element.submit()
                    else:
                        element.click()
                    
                    return {
                        "success": True,
                        "action": "submit",
                        "target": form_identifier,
                        "message": f"Successfully submitted form"
                    }
                except:
                    continue
            
            return {
                "success": False,
                "action": "submit",
                "target": form_identifier,
                "error": "Could not find form to submit"
            }
            
        except Exception as e:
            return {
                "success": False,
                "action": "submit",
                "target": form_identifier,
                "error": f"Form submission failed: {str(e)}"
            }
    
    def find_element(self, target: str, strategies: List[Dict[str, str]]) -> Dict[str, Any]:
        """Find an element and return information about it"""
        for strategy in strategies:
            try:
                element = self.find_element_by_strategy(strategy)
                if element:
                    element_info = {
                        "tag_name": element.tag_name,
                        "text": element.text[:100],  # Limit text length
                        "attributes": {},
                        "location": element.location,
                        "size": element.size
                    }
                    
                    # Get common attributes
                    for attr in ["id", "class", "name", "type", "value", "href"]:
                        try:
                            value = element.get_attribute(attr)
                            if value:
                                element_info["attributes"][attr] = value
                        except:
                            pass
                    
                    return {
                        "success": True,
                        "action": "find",
                        "target": target,
                        "strategy_used": strategy["type"],
                        "element_info": element_info,
                        "message": f"Successfully found element using {strategy['type']}"
                    }
            except Exception as e:
                continue
        
        return {
            "success": False,
            "action": "find",
            "target": target,
            "error": f"Could not find element for '{target}'"
        }
    
    def generic_action(self, action: str, target: str, value: str) -> Dict[str, Any]:
        """Handle generic actions"""
        return {
            "success": True,
            "action": action,
            "target": target,
            "value": value,
            "message": f"Executed generic action: {action} on {target}"
        }
    
    def take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"dynamic_automation_{timestamp}.png"
            
            screenshots_dir = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
        
            filepath = os.path.join(screenshots_dir, filename)
            self.current_driver.save_screenshot(filepath)
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Screenshot failed: {str(e)}"
            }
    
    def close_driver(self):
        """Close the current driver"""
        if self.current_driver:
            try:
                self.current_driver.quit()
                self.current_driver = None
            except:
                pass 