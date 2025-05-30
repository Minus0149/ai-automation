"""
Main Executor - Orchestrates all automation types
Coordinates between different automation frameworks and LangChain agents
"""

import os
import time
import json
from typing import Dict, Any, Optional, List, Union
from selenium import webdriver

# Core executors
from selenium_executor import SeleniumExecutor
from dynamic_executor import DynamicAutomationExecutor
from simple_enhanced_executor import SimpleEnhancedExecutor
from comprehensive_automation_executor import ComprehensiveAutomationExecutor

# LangChain integration
try:
    from enhanced_langchain_executor import EnhancedLangChainExecutor
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class AutomationExecutor:
    """Main executor that orchestrates all automation types"""
    
    def __init__(self, llm=None):
        # Initialize core executors
        self.selenium_executor = SeleniumExecutor()
        self.dynamic_executor = DynamicAutomationExecutor()
        self.simple_enhanced_executor = SimpleEnhancedExecutor()
        self.comprehensive_executor = ComprehensiveAutomationExecutor()
        
        # Initialize LangChain components if available
        self.enhanced_executor = None
        
        if LANGCHAIN_AVAILABLE:
            try:
                self.enhanced_executor = EnhancedLangChainExecutor()
                print("LangChain executor initialized successfully")
            except Exception as e:
                print(f"Warning: LangChain executor failed to initialize: {e}")
        
        self.current_session = None
        self.execution_history = []
    
    def execute_automation(self, 
                          url: str, 
                          task_description: str, 
                          framework: str = "auto", 
                          use_langchain: bool = True,
                          model_provider: str = "openai",
                          model_name: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """
        Execute automation task with intelligent framework selection
        """
        start_time = time.time()
        
        # Record execution attempt
        execution_record = {
            "url": url,
            "task": task_description,
            "framework": framework,
            "use_langchain": use_langchain,
            "model_provider": model_provider,
            "model_name": model_name,
            "start_time": start_time,
            "attempt_id": len(self.execution_history) + 1
        }
        
        try:
            # Determine best execution approach
            if framework == "auto":
                framework = self._determine_best_framework(task_description, use_langchain)
            
            # Update model if using enhanced executor
            if self.enhanced_executor and use_langchain:
                try:
                    self.enhanced_executor.switch_model(model_provider, model_name)
                except Exception as e:
                    print(f"Warning: Could not switch model: {e}")
            
            # Execute based on framework choice
            result = None
            if framework == "comprehensive":
                result = self._execute_comprehensive_automation(url, task_description)
            elif framework == "enhanced" and self.enhanced_executor and use_langchain:
                result = self._execute_enhanced_automation(url, task_description)
            elif framework == "simple_enhanced":
                result = self._execute_simple_enhanced_automation(url, task_description)
            elif framework == "dynamic":
                result = self._execute_dynamic_automation(url, task_description)
            else:  # Default to selenium
                result = self._execute_selenium_automation(url, task_description)
            
            # Add execution metadata
            if result:
                result["execution_time"] = time.time() - start_time
                result["framework_used"] = framework
                result["langchain_enabled"] = use_langchain and LANGCHAIN_AVAILABLE
                result["model_info"] = {
                    "provider": model_provider,
                    "model": model_name
                }
            
            # Record result
            execution_record.update({
                "success": result.get("success", False) if result else False,
                "execution_time": result.get("execution_time", 0) if result else 0,
                "framework_used": framework,
                "end_time": time.time()
            })
            
            self.execution_history.append(execution_record)
            
            return result or {"success": False, "error": "No result returned"}

        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "url": url,
                "task": task_description,
                "framework": framework,
                "execution_time": time.time() - start_time
            }
            
            execution_record.update({
                "success": False,
                "error": str(e),
                "execution_time": error_result["execution_time"],
                "end_time": time.time()
            })
            
            self.execution_history.append(execution_record)
            
            return error_result
    
    def _determine_best_framework(self, task_description: str, use_langchain: bool) -> str:
        """Intelligently determine the best framework for the task"""
        task_lower = task_description.lower()
        
        # Chat/conversation indicators
        chat_indicators = ["chat", "conversation", "ask", "help", "explain"]
        
        # Complex tasks that benefit from LangChain
        complex_indicators = [
            "plan", "strategy", "multiple steps", "if", "then", "complex", 
            "analyze", "understand", "intelligent", "decision", "choose"
        ]
        
        # Project generation indicators
        project_indicators = ["project", "generate", "create", "build", "structure"]
        
        # Dynamic automation indicators
        dynamic_indicators = [
            "find", "search", "locate", "detect", "smart", "adaptive"
        ]
        
        # Simple automation tasks
        simple_indicators = [
            "click", "type", "fill", "submit", "navigate", "scroll"
        ]
        
        if any(indicator in task_lower for indicator in chat_indicators):
            return "comprehensive"
        
        if any(indicator in task_lower for indicator in project_indicators):
            if use_langchain and LANGCHAIN_AVAILABLE and self.enhanced_executor:
                return "enhanced"
            else:
                return "simple_enhanced"
        
        if use_langchain and LANGCHAIN_AVAILABLE and self.enhanced_executor:
            if any(indicator in task_lower for indicator in complex_indicators):
                return "enhanced"
        
        if any(indicator in task_lower for indicator in dynamic_indicators):
            return "dynamic"
        
        return "selenium"  # Default fallback
    
    def _execute_selenium_automation(self, url: str, task_description: str) -> Dict[str, Any]:
        """Execute using basic Selenium"""
        try:
            result = self.selenium_executor.execute_automation(
                url=url,
                actions=[{"type": "navigate", "url": url}]
            )
            
            result["approach"] = "selenium_basic"
            result["task"] = task_description
            
            return result
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Selenium automation failed: {str(e)}",
                "approach": "selenium_basic"
            }
    
    def _execute_dynamic_automation(self, url: str, task_description: str) -> Dict[str, Any]:
        """Execute using dynamic automation"""
        try:
            result = self.dynamic_executor.execute_automation(
                prompt=task_description,
                website_url=url,
                framework="selenium"
            )
            
            result["approach"] = "dynamic_automation"
            
            return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Dynamic automation failed: {str(e)}",
                "approach": "dynamic_automation"
            }
    
    def _execute_simple_enhanced_automation(self, url: str, task_description: str) -> Dict[str, Any]:
        """Execute using simple enhanced automation"""
        try:
            task_id = f"task_{int(time.time())}"
            result = self.simple_enhanced_executor.execute_automation(
                prompt=task_description,
                website_url=url,
                framework="selenium",
                task_id=task_id
            )
            
            result["approach"] = "simple_enhanced"
            
            return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Simple enhanced automation failed: {str(e)}",
                "approach": "simple_enhanced"
            }
    
    def _execute_enhanced_automation(self, url: str, task_description: str) -> Dict[str, Any]:
        """Execute using enhanced LangChain executor"""
        try:
            task_id = f"task_{int(time.time())}"
            result = self.enhanced_executor.execute_automation(
                prompt=task_description,
                website_url=url,
                framework="selenium",
                task_id=task_id
            )
            
            result["approach"] = "enhanced_langchain"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Enhanced LangChain automation failed: {str(e)}",
                "approach": "enhanced_langchain"
            }
    
    def _execute_comprehensive_automation(self, url: str, task_description: str) -> Dict[str, Any]:
        """Execute using comprehensive automation executor"""
        try:
            context = {"url": url} if url else {}
            result = self.comprehensive_executor.chat_with_automation(
                message=task_description,
                context=context
            )
            
            result["approach"] = "comprehensive"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Comprehensive automation failed: {str(e)}",
                "approach": "comprehensive"
            }
    
    def execute_with_fallback(self, url: str, task_description: str, **kwargs) -> Dict[str, Any]:
        """Execute with automatic fallback to simpler methods if advanced ones fail"""
        frameworks_to_try = []
        
        use_langchain = kwargs.get("use_langchain", True)
        
        # Add frameworks in order of preference
        frameworks_to_try.append("comprehensive")
        
        if use_langchain and LANGCHAIN_AVAILABLE and self.enhanced_executor:
            frameworks_to_try.append("enhanced")
        
        frameworks_to_try.extend(["simple_enhanced", "dynamic", "selenium"])
        
        last_error = None
        
        for framework in frameworks_to_try:
            try:
                print(f"Trying framework: {framework}")
                
                result = self.execute_automation(
                    url=url,
                    task_description=task_description,
                    framework=framework,
                    **kwargs
                )
                
                if result.get("success"):
                    result["fallback_used"] = framework != frameworks_to_try[0]
                    result["frameworks_attempted"] = frameworks_to_try[:frameworks_to_try.index(framework) + 1]
                    return result
                else:
                    last_error = result.get("error", "Unknown error")
                    
            except Exception as e:
                last_error = str(e)
                continue
        
        return {
            "success": False,
            "error": f"All frameworks failed. Last error: {last_error}",
            "frameworks_attempted": frameworks_to_try,
            "url": url,
            "task": task_description
        }
    
    def create_automation_plan(self, task_description: str, url: str = "") -> Dict[str, Any]:
        """Create an automation plan using the best available planner"""
        if self.enhanced_executor:
            try:
                # Use enhanced executor for planning
                result = self.enhanced_executor._generate_automation_plan(
                    task_description, url, "selenium"
                )
                return {
                    "success": True,
                    "plan": result,
                    "planner": "enhanced_executor"
                }
            except Exception as e:
                print(f"Enhanced planning failed: {e}")
        
        # Fallback to dynamic analysis
        try:
            # Simple plan structure
            plan = {
                "task": task_description,
                "url": url,
                "steps": [
                    {"action": "navigate", "target": url},
                    {"action": "analyze", "target": "page content"},
                    {"action": "execute", "target": task_description}
                ]
            }
            return {
                "success": True,
                "plan": plan,
                "planner": "fallback_planner"
            }
        except Exception as e:
            print(f"Fallback planning failed: {e}")
        
        return {
            "success": False,
            "error": "No planning capabilities available"
        }
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available AI models"""
        if self.enhanced_executor:
            try:
                return self.enhanced_executor.get_available_models()
            except Exception as e:
                print(f"Failed to get models from enhanced executor: {e}")
        
        return {
            "available": False,
            "models": [],
            "error": "Enhanced executor not available"
        }
    
    def switch_model(self, provider: str, model_name: str) -> Dict[str, Any]:
        """Switch the AI model for LangChain operations"""
        if self.enhanced_executor:
            try:
                result = self.enhanced_executor.switch_model(provider, model_name)
                return {
                    "success": True,
                    "provider": provider,
                    "model": model_name,
                    "result": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Model switch failed: {str(e)}"
                }
        
        return {
            "success": False,
            "error": "Enhanced executor not available"
        }
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status and capabilities"""
        return {
            "selenium_available": True,
            "dynamic_automation_available": True,
            "simple_enhanced_available": True,
            "comprehensive_available": True,
            "langchain_available": LANGCHAIN_AVAILABLE,
            "enhanced_executor_available": self.enhanced_executor is not None,
            "total_executions": len(self.execution_history),
            "successful_executions": len([e for e in self.execution_history if e.get("success", False)]),
            "current_session": self.current_session is not None
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history
    
    def clear_history(self):
        """Clear execution history"""
        self.execution_history = []
    
    def close_all_sessions(self):
        """Close all active automation sessions"""
        try:
            if self.selenium_executor:
                self.selenium_executor.close_all_drivers()
        except Exception as e:
            print(f"Error closing selenium executor: {e}")
        
        try:
            if self.dynamic_executor:
                self.dynamic_executor.cleanup()
        except Exception as e:
            print(f"Error closing dynamic executor: {e}")
        
        try:
            if self.simple_enhanced_executor:
                self.simple_enhanced_executor.cleanup()
        except Exception as e:
            print(f"Error closing simple enhanced executor: {e}")
        
        try:
            if self.comprehensive_executor:
                self.comprehensive_executor.cleanup()
        except Exception as e:
            print(f"Error closing comprehensive executor: {e}")
        
        try:
            if self.enhanced_executor:
                self.enhanced_executor.cleanup()
        except Exception as e:
            print(f"Error closing enhanced executor: {e}")
        
        self.current_session = None

# Factory function
def create_automation_executor(llm=None) -> AutomationExecutor:
    """Factory function to create an automation executor"""
    return AutomationExecutor(llm=llm) 