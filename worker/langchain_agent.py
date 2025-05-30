"""
LangChain Agent for Web Automation
Advanced agent workflows with memory and planning capabilities
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from selenium import webdriver

try:
    from langchain.agents import AgentExecutor, AgentType, initialize_agent
    from langchain.agents.agent import Agent
    from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
    from langchain.prompts import PromptTemplate
    from langchain.schema import AgentAction, AgentFinish, BaseMessage, HumanMessage, SystemMessage
    from langchain.callbacks.manager import CallbackManagerForToolRun
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.tools import BaseTool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from langchain_tools import WebAutomationToolkit

class WebAutomationAgent:
    """Advanced web automation agent with planning and memory"""
    
    def __init__(self, llm: BaseLanguageModel, driver: webdriver.Chrome = None):
        self.llm = llm
        self.driver = driver
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Initialize automation toolkit
        self.toolkit = WebAutomationToolkit(driver=driver) if driver else None
        self.tools = self.toolkit.get_tools() if self.toolkit else []
        
        # Initialize agent
        self.agent = self._create_agent()
        
        # Task planning and execution state
        self.current_plan = []
        self.executed_steps = []
        self.current_url = ""
        self.page_state = {}
    
    def _create_agent(self) -> Optional[AgentExecutor]:
        """Create the LangChain agent executor"""
        if not LANGCHAIN_AVAILABLE or not self.tools:
            return None
        
        # Custom prompt for web automation
        prefix = """You are an expert web automation assistant. You can interact with web pages using the following tools:

{tools}

Your goal is to help users automate web interactions step by step. Always think through the task carefully:

1. Understand what the user wants to accomplish
2. Break down complex tasks into smaller steps
3. Use the appropriate tools for each step
4. Verify actions were successful before proceeding
5. Take screenshots when helpful for debugging
6. Provide clear feedback about what you're doing

Current conversation:
{chat_history}

User input: {input}
{agent_scratchpad}"""

        prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "chat_history", "input", "agent_scratchpad"],
            template=prefix
        )
        
        try:
            agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=10,
                agent_kwargs={
                    "prefix": prefix,
                    "format_instructions": """Use the following format:

Thought: I need to understand what the user wants and plan my approach
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""
                }
            )
            return agent
        except Exception as e:
            print(f"Error creating agent: {e}")
            return None
    
    def update_driver(self, driver: webdriver.Chrome):
        """Update the WebDriver instance"""
        self.driver = driver
        if self.toolkit:
            self.toolkit.update_driver(driver)
        # Recreate agent with new driver
        self.agent = self._create_agent()
    
    def create_automation_plan(self, task_description: str, url: str = "") -> Dict[str, Any]:
        """Create a step-by-step automation plan"""
        planning_prompt = f"""
        Create a detailed step-by-step plan for the following web automation task:
        
        Task: {task_description}
        Target URL: {url}
        
        Break this down into specific, actionable steps that can be executed with web automation tools.
        Consider elements like navigation, waiting for page loads, finding elements, clicking, typing, etc.
        
        Return your plan as a JSON structure with numbered steps, each containing:
        - action: the type of action (navigate, click, type, wait, etc.)
        - target: the element selector or URL
        - value: any text to type or other parameters
        - description: human-readable description of the step
        
        Example format:
        {{
            "plan": [
                {{
                    "step": 1,
                    "action": "navigate",
                    "target": "https://example.com",
                    "value": "",
                    "description": "Navigate to the website"
                }},
                {{
                    "step": 2,
                    "action": "wait",
                    "target": "#login-button",
                    "value": "",
                    "description": "Wait for login button to appear"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm.invoke(planning_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                plan_json = response_text[json_start:json_end]
                plan = json.loads(plan_json)
                self.current_plan = plan.get('plan', [])
                return plan
            else:
                # Fallback: create simple plan from description
                return {
                    "plan": [
                        {
                            "step": 1,
                            "action": "navigate" if url else "analyze",
                            "target": url or "current page",
                            "value": "",
                            "description": f"Start automation task: {task_description}"
                        }
                    ]
                }
                
        except Exception as e:
            print(f"Error creating plan: {e}")
            return {
                "plan": [
                    {
                        "step": 1,
                        "action": "manual",
                        "target": "",
                        "value": "",
                        "description": f"Execute task manually: {task_description}"
                    }
                ]
            }
    
    def execute_plan_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step from the automation plan"""
        if not self.agent:
            return {
                "success": False,
                "error": "Agent not available",
                "step": step
            }
        
        try:
            action = step.get('action', '')
            target = step.get('target', '')
            value = step.get('value', '')
            description = step.get('description', '')
            
            # Create execution prompt
            execution_prompt = f"""
            Execute this automation step:
            
            Action: {action}
            Target: {target}
            Value: {value}
            Description: {description}
            
            Use the appropriate tools to complete this step. Be specific about selectors and wait for elements as needed.
            """
            
            # Execute through agent
            result = self.agent.invoke({"input": execution_prompt})
            
            # Track execution
            executed_step = {
                **step,
                "executed_at": time.time(),
                "result": result.get("output", ""),
                "success": True
            }
            self.executed_steps.append(executed_step)
            
            return {
                "success": True,
                "result": result.get("output", ""),
                "step": executed_step
            }
            
        except Exception as e:
            error_step = {
                **step,
                "executed_at": time.time(),
                "error": str(e),
                "success": False
            }
            self.executed_steps.append(error_step)
            
            return {
                "success": False,
                "error": str(e),
                "step": error_step
            }
    
    def execute_full_plan(self) -> Dict[str, Any]:
        """Execute all steps in the current plan"""
        if not self.current_plan:
            return {
                "success": False,
                "error": "No plan available",
                "results": []
            }
        
        results = []
        for step in self.current_plan:
            result = self.execute_plan_step(step)
            results.append(result)
            
            # Stop execution if a step fails
            if not result.get("success", False):
                break
                
            # Add delay between steps
            time.sleep(1)
        
        return {
            "success": all(r.get("success", False) for r in results),
            "results": results,
            "total_steps": len(self.current_plan),
            "completed_steps": len([r for r in results if r.get("success", False)])
        }
    
    def execute_task(self, task_description: str, url: str = "") -> Dict[str, Any]:
        """Execute a complete automation task"""
        if not self.agent:
            return {
                "success": False,
                "error": "Agent not available"
            }
        
        try:
            # Create and execute plan
            plan = self.create_automation_plan(task_description, url)
            execution_result = self.execute_full_plan()
            
            return {
                "success": execution_result.get("success", False),
                "plan": plan,
                "execution": execution_result,
                "task": task_description,
                "url": url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": task_description,
                "url": url
            }
    
    def chat(self, message: str) -> str:
        """Chat with the agent for interactive automation"""
        if not self.agent:
            return "Error: Agent not available"
        
        try:
            response = self.agent.invoke({"input": message})
            return response.get("output", "No response generated")
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return [tool.name for tool in self.tools] if self.tools else []
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of executed steps"""
        return self.executed_steps
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        self.current_plan = []
        self.executed_steps = []
    
    def get_memory_summary(self) -> str:
        """Get summary of conversation memory"""
        if hasattr(self.memory, 'chat_memory'):
            messages = self.memory.chat_memory.messages
            if messages:
                return f"Memory contains {len(messages)} messages"
        return "Memory is empty"
    
    def export_session(self) -> Dict[str, Any]:
        """Export current session data"""
        return {
            "plan": self.current_plan,
            "executed_steps": self.executed_steps,
            "memory_summary": self.get_memory_summary(),
            "available_tools": self.get_available_tools(),
            "current_url": self.current_url,
            "page_state": self.page_state
        }

class SimpleWebAutomationAgent:
    """Simplified agent for cases where full LangChain is not available"""
    
    def __init__(self, llm=None, driver: webdriver.Chrome = None):
        self.llm = llm
        self.driver = driver
        self.toolkit = WebAutomationToolkit(driver=driver) if driver else None
        self.history = []
    
    def execute_task(self, task_description: str, url: str = "") -> Dict[str, Any]:
        """Simple task execution without full agent framework"""
        try:
            # Basic automation without complex planning
            if url and self.driver:
                self.driver.get(url)
                time.sleep(2)
            
            return {
                "success": True,
                "message": f"Task received: {task_description}",
                "simple_mode": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "simple_mode": True
            }
    
    def chat(self, message: str) -> str:
        """Simple chat without agent framework"""
        self.history.append({"user": message, "timestamp": time.time()})
        return f"Received: {message} (Simple mode - full agent features unavailable)" 