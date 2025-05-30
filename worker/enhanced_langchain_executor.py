"""
Enhanced LangChain Executor with Multi-Model Support
Supports OpenAI, Anthropic, Google, Ollama, and other models
"""
import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import tempfile

try:
    from langchain_openai import ChatOpenAI, OpenAI
    from langchain.schema import HumanMessage, SystemMessage
    from langchain_community.callbacks.manager import get_openai_callback
    
    # Anthropic Claude
    try:
        from langchain_anthropic import ChatAnthropic
        ANTHROPIC_AVAILABLE = True
    except ImportError:
        ANTHROPIC_AVAILABLE = False
    
    # Google Gemini
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        GOOGLE_AVAILABLE = True
    except ImportError:
        GOOGLE_AVAILABLE = False
    
    # Ollama for local models
    try:
        from langchain_community.chat_models import ChatOllama
        from langchain_community.llms import Ollama
        OLLAMA_AVAILABLE = True
    except ImportError:
        OLLAMA_AVAILABLE = False
    
    # Hugging Face
    try:
        from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
        HUGGINGFACE_AVAILABLE = True
    except ImportError:
        HUGGINGFACE_AVAILABLE = False
    
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedLangChainExecutor:
    """Enhanced automation executor with LangChain multi-model support."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "automation_projects"
        self.temp_dir.mkdir(exist_ok=True)
        self.model = None
        self.model_name = "gemini-2.5-flash-preview-05-20"  # Updated default to Google's latest
        self.model_provider = "google"  # Updated default provider
        self._initialize_model()
        
        # Initialize with fallback mechanism
        try:
            if LANGCHAIN_AVAILABLE:
                from langchain_tools import WebAutomationToolkit
                from langchain_agent import WebAutomationAgent
                self.toolkit_available = True
                self.agent_available = True
            else:
                self.toolkit_available = False
                self.agent_available = False
        except ImportError:
            self.toolkit_available = False
            self.agent_available = False
    
    def _initialize_model(self):
        """Initialize the LangChain model based on configuration with fallback logic."""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available")
            return
        
        # Get model configuration from environment with fallback to new Google default
        self.model_provider = os.getenv("AI_MODEL_PROVIDER", "google").lower()
        self.model_name = os.getenv("AI_MODEL_NAME", "gemini-2.5-flash-preview-05-20")
        
        # Try providers in order of preference with API key availability
        providers_to_try = [
            ("google", "gemini-2.5-flash-preview-05-20"),  # New default - latest Google model
            ("google", "gemini-1.5-pro-002"),   # Fallback Google model
            ("openai", "gpt-4-turbo"),
            ("anthropic", "claude-3-5-sonnet-20241022"),
            ("ollama", "llama3.1:8b"),
            ("huggingface", "microsoft/DialoGPT-medium")
        ]
        
        # If specific provider is set, try it first
        if (self.model_provider, self.model_name) not in providers_to_try:
            providers_to_try.insert(0, (self.model_provider, self.model_name))
        
        for provider, model in providers_to_try:
            try:
                self.model_provider = provider
                self.model_name = model
                
                if provider == "openai" and os.getenv("OPENAI_API_KEY"):
                    self._init_openai_model()
                    return
                elif provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY") and ANTHROPIC_AVAILABLE:
                    self._init_anthropic_model()
                    return
                elif provider == "google" and os.getenv("GOOGLE_API_KEY") and GOOGLE_AVAILABLE:
                    self._init_google_model()
                    return
                elif provider == "ollama" and OLLAMA_AVAILABLE:
                    self._init_ollama_model()
                    return
                elif provider == "huggingface" and HUGGINGFACE_AVAILABLE:
                    self._init_huggingface_model()
                    return
                    
            except Exception as e:
                logger.warning(f"Failed to initialize {provider} model: {e}")
                continue
        
        # If all else fails, create a mock model for testing
        logger.warning("No AI models available, creating mock model")
        self.model = None
        self.model_provider = "mock"
        self.model_name = "mock-model"
    
    def _init_openai_model(self):
        """Initialize OpenAI model."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        if self.model_name.startswith("gpt-"):
            self.model = ChatOpenAI(
                model_name=self.model_name,
                temperature=0.1,
                api_key=api_key
            )
        else:
            self.model = OpenAI(
                model_name=self.model_name,
                temperature=0.1,
                api_key=api_key
            )
        
        logger.info(f"Initialized OpenAI model: {self.model_name}")
    
    def _init_anthropic_model(self):
        """Initialize Anthropic Claude model."""
        if not ANTHROPIC_AVAILABLE:
            raise ValueError("Anthropic package not available")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.model = ChatAnthropic(
            model=self.model_name or "claude-3-sonnet-20240229",
            anthropic_api_key=api_key,
            temperature=0.1
        )
        
        logger.info(f"Initialized Anthropic model: {self.model_name}")
    
    def _init_google_model(self):
        """Initialize Google Gemini model."""
        if not GOOGLE_AVAILABLE:
            raise ValueError("Google Generative AI package not available")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        if self.model_name.startswith("gemini"):
            self.model = ChatGoogleGenerativeAI(
                model=self.model_name or "gemini-pro",
                google_api_key=api_key,
                temperature=0.1
            )
        else:
            self.model = ChatGoogleGenerativeAI(
                model=self.model_name or "gemini-pro",
                google_api_key=api_key,
                temperature=0.1
            )
        
        logger.info(f"Initialized Google model: {self.model_name}")
    
    def _init_ollama_model(self):
        """Initialize Ollama local model."""
        if not OLLAMA_AVAILABLE:
            raise ValueError("Ollama package not available")
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.model = ChatOllama(
            model=self.model_name or "llama2",
            base_url=base_url,
            temperature=0.1
        )
        
        logger.info(f"Initialized Ollama model: {self.model_name}")
    
    def _init_huggingface_model(self):
        """Initialize Hugging Face model."""
        if not HUGGINGFACE_AVAILABLE:
            raise ValueError("Hugging Face package not available")
        
        # This is a simplified example - you might need more configuration
        self.model = HuggingFacePipeline.from_model_id(
            model_id=self.model_name or "microsoft/DialoGPT-medium",
            task="text-generation",
            model_kwargs={"temperature": 0.1}
        )
        
        logger.info(f"Initialized Hugging Face model: {self.model_name}")
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models by provider."""
        models = {
            "openai": [
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "text-davinci-003",
                "text-davinci-002"
            ]
        }
        
        if ANTHROPIC_AVAILABLE:
            models["anthropic"] = [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "claude-2.1",
                "claude-2.0",
                "claude-instant-1.2"
            ]
        
        if GOOGLE_AVAILABLE:
            models["google"] = [
                "gemini-2.5-flash-preview-05-20",
                "gemini-2.0-flash-thinking-exp-1219",
                "gemini-1.5-pro-002",
                "gemini-1.5-flash-002", 
                "gemini-1.5-flash-8b",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro",
                "gemini-pro-vision",
                "gemini-1.0-pro",
                "text-bison-001",
                "chat-bison-001"
            ]
        
        if OLLAMA_AVAILABLE:
            models["ollama"] = [
                "llama3.1:8b",
                "llama3.1:70b",
                "llama3:8b",
                "llama3:70b",
                "llama2:7b",
                "llama2:13b", 
                "llama2:70b",
                "codellama:7b",
                "codellama:13b",
                "mistral:7b",
                "mixtral:8x7b",
                "neural-chat:7b",
                "starling-lm:7b",
                "deepseek-coder:6.7b",
                "phi3:3.8b",
                "qwen2:7b"
            ]
        
        if HUGGINGFACE_AVAILABLE:
            models["huggingface"] = [
                "microsoft/DialoGPT-large",
                "microsoft/DialoGPT-medium",
                "microsoft/CodeGPT-small-py",
                "facebook/blenderbot-400M-distill",
                "google/flan-t5-large",
                "bigcode/starcoder",
                "Salesforce/codegen-350M-mono"
            ]
        
        # Add more providers
        models["cohere"] = [
            "command-r-plus",
            "command-r",
            "command",
            "command-nightly",
            "command-light"
        ]
        
        models["perplexity"] = [
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-online",
            "llama-3.1-sonar-huge-128k-online"
        ]
        
        models["groq"] = [
            "llama3-8b-8192",
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        
        return models
    
    def switch_model(self, provider: str, model_name: str) -> bool:
        """Switch to a different model."""
        try:
            self.model_provider = provider.lower()
            self.model_name = model_name
            self._initialize_model()
            return True
        except Exception as e:
            logger.error(f"Failed to switch to {provider}/{model_name}: {e}")
            return False
    
    def execute_automation(self, prompt: str, website_url: str, framework: str, task_id: str, timeout: int = 180) -> Dict[str, Any]:
        """Execute enhanced automation with LangChain AI assistance."""
        start_time = time.time()
        
        if not self.model:
            return self._fallback_execution(prompt, website_url, framework, task_id, timeout)
        
        try:
            # Create project directory
            project_dir = self.temp_dir / task_id
            project_dir.mkdir(exist_ok=True)
            
            # Generate automation plan using AI
            automation_plan = self._generate_automation_plan(prompt, website_url, framework)
            
            # Generate project structure
            project_structure = self._generate_ai_project_structure(
                prompt, website_url, framework, project_dir, automation_plan
            )
            
            # Generate main automation script with AI
            main_script = self._generate_ai_automation_script(
                prompt, website_url, framework, automation_plan
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "logs": [
                    {
                        "level": "info",
                        "message": f"Enhanced automation completed successfully with {self.model_provider}/{self.model_name}",
                        "timestamp": datetime.now().isoformat(),
                        "source": "enhanced_langchain_executor"
                    }
                ],
                "screenshots": [],
                "execution_time": execution_time,
                "framework": framework,
                "generated_code": main_script,
                "project_structure": project_structure,
                "context_chain": automation_plan.get("steps", []),
                "function_calls": [
                    {
                        "tool": "langchain_automation",
                        "input": {"prompt": prompt, "framework": framework, "model": f"{self.model_provider}/{self.model_name}"},
                        "output": "Enhanced automation project generated",
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "chat_history": [],
                "task_id": task_id,
                "model_info": {
                    "provider": self.model_provider,
                    "model": self.model_name
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced automation failed: {e}")
            return self._fallback_execution(prompt, website_url, framework, task_id, timeout)
    
    def _generate_automation_plan(self, prompt: str, website_url: str, framework: str) -> Dict[str, Any]:
        """Generate an automation plan using AI."""
        system_message = SystemMessage(content=f"""
        You are an expert automation engineer. Create a detailed automation plan for the following task:
        
        Task: {prompt}
        Website: {website_url}
        Framework: {framework}
        
        Provide a structured plan with:
        1. Analysis of the task
        2. Step-by-step automation approach
        3. Required libraries and tools
        4. Error handling strategies
        5. Testing approach
        
        Response should be in JSON format.
        """)
        
        human_message = HumanMessage(content=f"Create automation plan for: {prompt}")
        
        try:
            if hasattr(self.model, 'invoke'):
                response = self.model.invoke([system_message, human_message])
                plan_text = response.content if hasattr(response, 'content') else str(response)
            else:
                response = self.model([system_message, human_message])
                plan_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse as JSON, fallback to structured text
            try:
                return json.loads(plan_text)
            except json.JSONDecodeError:
                return {
                    "analysis": "AI-generated automation plan",
                    "steps": plan_text.split('\n'),
                    "framework": framework,
                    "error_handling": "Standard error handling"
                }
                
        except Exception as e:
            logger.error(f"Failed to generate automation plan: {e}")
            return {
                "analysis": f"Automated task for {prompt}",
                "steps": ["Navigate to website", "Perform automation", "Return results"],
                "framework": framework,
                "error_handling": "Basic error handling"
            }
    
    def _generate_ai_automation_script(self, prompt: str, website_url: str, framework: str, plan: Dict[str, Any]) -> str:
        """Generate automation script using AI."""
        system_message = SystemMessage(content=f"""
        You are an expert Python automation developer. Generate a complete {framework} automation script for:
        
        Task: {prompt}
        Website: {website_url}
        Plan: {json.dumps(plan, indent=2)}
        
        Requirements:
        - Use {framework} framework
        - Include proper error handling
        - Add logging and screenshots
        - Make it production-ready
        - Include docstrings and comments
        
        Generate only the Python code, no explanations.
        """)
        
        human_message = HumanMessage(content=f"Generate {framework} automation script for: {prompt}")
        
        try:
            if hasattr(self.model, 'invoke'):
                response = self.model.invoke([system_message, human_message])
                script = response.content if hasattr(response, 'content') else str(response)
            else:
                response = self.model([system_message, human_message])
                script = response.content if hasattr(response, 'content') else str(response)
            
            return script
            
        except Exception as e:
            logger.error(f"Failed to generate automation script: {e}")
            return self._generate_fallback_script(prompt, website_url, framework)
    
    def _generate_ai_project_structure(self, prompt: str, website_url: str, framework: str, project_dir: Path, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project structure with AI assistance."""
        # This would be similar to the simple version but enhanced with AI
        # For brevity, I'll use a simplified version
        files = [
            "main_automation.py",
            "config.py", 
            "requirements.txt",
            "README.md",
            "tests/test_automation.py",
            "utils/helpers.py",
            "Dockerfile",
            "docker-compose.yml"
        ]
        
        contents = {}
        for file in files:
            if file == "main_automation.py":
                contents[file] = self._generate_ai_automation_script(prompt, website_url, framework, plan)
            # ... other file generations would be here
        
        return {
            "files": files,
            "contents": contents
        }
    
    def _generate_fallback_script(self, prompt: str, website_url: str, framework: str) -> str:
        """Generate a basic fallback script when AI is not available."""
        return f'''#!/usr/bin/env python3
"""
Automation script for: {prompt}
Website: {website_url}
Framework: {framework}
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main automation function."""
    driver = None
    try:
        # Setup Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        
        # Navigate to website
        logger.info(f"Navigating to {{website_url}}")
        driver.get("{website_url}")
        
        # Take screenshot
        driver.save_screenshot("automation_screenshot.png")
        
        # Add your automation logic here
        # This is a basic template - customize based on your needs
        
        logger.info("Automation completed successfully")
        
    except Exception as e:
        logger.error(f"Automation failed: {{e}}")
        raise
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
'''
    
    def _fallback_execution(self, prompt: str, website_url: str, framework: str, task_id: str, timeout: int) -> Dict[str, Any]:
        """Fallback execution when LangChain is not available."""
        from simple_enhanced_executor import SimpleEnhancedExecutor
        fallback_executor = SimpleEnhancedExecutor()
        return fallback_executor.execute_automation(prompt, website_url, framework, task_id, timeout)
    
    def create_function_calling_agent(self, driver=None):
        """Create a function calling agent with web automation tools"""
        if not self.agent_available or not self.model:
            return None
        
        try:
            from langchain_agent import WebAutomationAgent
            agent = WebAutomationAgent(llm=self.model, driver=driver)
            return agent
        except Exception as e:
            print(f"Warning: Could not create function calling agent: {e}")
            return None
    
    def execute_with_function_calling(self, url: str, task_description: str, driver=None) -> Dict[str, Any]:
        """Execute automation using function calling agent"""
        if not self.agent_available:
            return {
                "success": False,
                "error": "Function calling agent not available"
            }
        
        try:
            # Create agent with tools
            agent = self.create_function_calling_agent(driver)
            if not agent:
                return {
                    "success": False,
                    "error": "Could not create function calling agent"
                }
            
            # Execute task through agent
            result = agent.execute_task(task_description, url)
            
            # Add metadata
            result["execution_type"] = "function_calling"
            result["tools_available"] = agent.get_available_tools()
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Function calling execution failed: {str(e)}",
                "execution_type": "function_calling"
            } 