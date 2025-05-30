"""
LangChain Automation Integration
Connects LangChain agents with automation frameworks
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from selenium import webdriver

try:
    from langchain_agent import WebAutomationAgent, SimpleWebAutomationAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

from selenium_executor import SeleniumExecutor
from dynamic_automation import DynamicAutomationExecutor

class LangChainAutomationIntegrator:
    """Integrates LangChain agents with automation frameworks"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.selenium_executor = SeleniumExecutor()
        self.dynamic_executor = DynamicAutomationExecutor()
        self.agent = None
        self.current_driver = None
        
        # Initialize agent if available
        if AGENT_AVAILABLE and llm:
            self.agent = WebAutomationAgent(llm=llm)
        elif llm:
            self.agent = SimpleWebAutomationAgent(llm=llm)
    
    def create_automation_session(self, url: str = "", headless: bool = True) -> Dict[str, Any]:
        """Create a new automation session with WebDriver"""
        try:
            # Create new driver through selenium executor
            driver_result = self.selenium_executor.create_driver(headless=headless)
            
            if driver_result.get("success"):
                self.current_driver = driver_result.get("driver")
                
                # Update agent with driver
                if self.agent:
                    self.agent.update_driver(self.current_driver)
                
                # Navigate to URL if provided
                if url:
                    self.current_driver.get(url)
                    time.sleep(2)
                
                return {
                    "success": True,
                    "message": "Automation session created",
                    "session_id": id(self.current_driver),
                    "url": url,
                    "agent_available": self.agent is not None
                }
            else:
                return {
                    "success": False,
                    "error": driver_result.get("error", "Failed to create driver")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create automation session: {str(e)}"
            }
    
    def execute_langchain_automation(self, task: str, url: str = "", framework: str = "selenium") -> Dict[str, Any]:
        """Execute automation task using LangChain agent"""
        if not self.agent:
            return {
                "success": False,
                "error": "LangChain agent not available"
            }
        
        try:
            # Create session if needed
            if not self.current_driver:
                session_result = self.create_automation_session(url=url)
                if not session_result.get("success"):
                    return session_result
            elif url:
                # Navigate to new URL
                self.current_driver.get(url)
                time.sleep(2)
            
            # Execute task through agent
            result = self.agent.execute_task(task, url)
            
            # Add framework info
            result["framework"] = framework
            result["integration"] = "langchain"
            result["session_id"] = id(self.current_driver) if self.current_driver else None
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"LangChain automation failed: {str(e)}",
                "task": task,
                "url": url,
                "framework": framework
            }
    
    def execute_hybrid_automation(self, task: str, url: str = "", use_langchain: bool = True) -> Dict[str, Any]:
        """Execute automation using hybrid approach (LangChain + traditional)"""
        try:
            if use_langchain and self.agent:
                # Try LangChain first
                langchain_result = self.execute_langchain_automation(task, url)
                
                if langchain_result.get("success"):
                    return {
                        **langchain_result,
                        "approach": "langchain_primary"
                    }
                else:
                    # Fallback to traditional automation
                    print("LangChain approach failed, falling back to traditional automation")
                    traditional_result = self.execute_traditional_automation(task, url)
                    return {
                        **traditional_result,
                        "approach": "traditional_fallback",
                        "langchain_error": langchain_result.get("error")
                    }
            else:
                # Use traditional automation directly
                return self.execute_traditional_automation(task, url)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Hybrid automation failed: {str(e)}",
                "task": task,
                "url": url
            }
    
    def execute_traditional_automation(self, task: str, url: str = "") -> Dict[str, Any]:
        """Execute automation using traditional Selenium approach"""
        try:
            # Use dynamic executor for traditional automation
            result = self.dynamic_executor.execute_automation(
                url=url,
                task_description=task,
                framework="selenium"
            )
            
            return {
                **result,
                "approach": "traditional",
                "integration": "dynamic_executor"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Traditional automation failed: {str(e)}",
                "task": task,
                "url": url,
                "approach": "traditional"
            }
    
    def chat_with_agent(self, message: str) -> str:
        """Interactive chat with LangChain agent"""
        if not self.agent:
            return "Error: LangChain agent not available"
        
        try:
            return self.agent.chat(message)
        except Exception as e:
            return f"Error in chat: {str(e)}"
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of LangChain agent and tools"""
        if not self.agent:
            return {
                "agent_available": False,
                "tools": [],
                "memory": "Not available"
            }
        
        try:
            return {
                "agent_available": True,
                "tools": self.agent.get_available_tools(),
                "memory": self.agent.get_memory_summary() if hasattr(self.agent, 'get_memory_summary') else "Simple agent",
                "execution_history": len(self.agent.get_execution_history()) if hasattr(self.agent, 'get_execution_history') else 0,
                "session_id": id(self.current_driver) if self.current_driver else None
            }
        except Exception as e:
            return {
                "agent_available": False,
                "error": str(e)
            }
    
    def create_automation_plan(self, task: str, url: str = "") -> Dict[str, Any]:
        """Create automation plan using LangChain agent"""
        if not self.agent or not hasattr(self.agent, 'create_automation_plan'):
            return {
                "success": False,
                "error": "Advanced planning not available"
            }
        
        try:
            plan = self.agent.create_automation_plan(task, url)
            return {
                "success": True,
                "plan": plan,
                "task": task,
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Planning failed: {str(e)}",
                "task": task,
                "url": url
            }
    
    def execute_plan_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step from automation plan"""
        if not self.agent or not hasattr(self.agent, 'execute_plan_step'):
            return {
                "success": False,
                "error": "Step execution not available"
            }
        
        try:
            return self.agent.execute_plan_step(step)
        except Exception as e:
            return {
                "success": False,
                "error": f"Step execution failed: {str(e)}",
                "step": step
            }
    
    def take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Take screenshot of current page"""
        if not self.current_driver:
            return {
                "success": False,
                "error": "No active driver session"
            }
        
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"langchain_screenshot_{timestamp}.png"
            
            # Ensure screenshots directory exists
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
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get information about current page"""
        if not self.current_driver:
            return {
                "success": False,
                "error": "No active driver session"
            }
        
        try:
            return {
                "success": True,
                "url": self.current_driver.current_url,
                "title": self.current_driver.title,
                "page_source_length": len(self.current_driver.page_source),
                "window_size": self.current_driver.get_window_size()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get page info: {str(e)}"
            }
    
    def close_session(self) -> Dict[str, Any]:
        """Close current automation session"""
        try:
            if self.current_driver:
                self.current_driver.quit()
                self.current_driver = None
                
                # Clear agent memory if available
                if self.agent and hasattr(self.agent, 'clear_memory'):
                    self.agent.clear_memory()
            
            return {
                "success": True,
                "message": "Automation session closed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to close session: {str(e)}"
            }
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export current session data"""
        try:
            session_data = {
                "agent_status": self.get_agent_status(),
                "page_info": self.get_page_info(),
                "timestamp": time.time()
            }
            
            # Add agent-specific data if available
            if self.agent and hasattr(self.agent, 'export_session'):
                session_data["agent_data"] = self.agent.export_session()
            
            return {
                "success": True,
                "session_data": session_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to export session data: {str(e)}"
            }

# Factory function to create integrator
def create_langchain_integrator(llm=None) -> LangChainAutomationIntegrator:
    """Factory function to create LangChain automation integrator"""
    return LangChainAutomationIntegrator(llm=llm) 