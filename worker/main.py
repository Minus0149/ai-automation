import os
import time
import asyncio
import traceback
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import contextlib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import all executors
from selenium_executor import SeleniumExecutor
from dynamic_ai_executor import DynamicAIExecutor
from enhanced_executor import EnhancedAutomationExecutor
from comprehensive_automation_executor import ComprehensiveAutomationExecutor, get_comprehensive_executor
from smart_automation_workflow import SmartAutomationWorkflow, get_smart_workflow
from edge_executor import EdgeExecutor

# Enhanced executor
ENHANCED_AVAILABLE = False
try:
    from enhanced_langchain_executor import EnhancedLangChainExecutor
    from simple_enhanced_executor import SimpleEnhancedExecutor
    ENHANCED_AVAILABLE = True
except ImportError:
    print("[WARNING] Enhanced automation features not available - install LangChain dependencies")

# Function calling and agent components
FUNCTION_CALLING_AVAILABLE = False
try:
    from langchain_tools import WebAutomationToolkit
    from langchain_agent import WebAutomationAgent
    from langchain_automation import LangChainAutomationIntegrator
    FUNCTION_CALLING_AVAILABLE = True
except ImportError:
    print("[WARNING] Function calling features not available - LangChain dependencies missing")

# Comprehensive automation executor
COMPREHENSIVE_AVAILABLE = False
try:
    from comprehensive_automation_executor import ComprehensiveAutomationExecutor, get_comprehensive_executor
    COMPREHENSIVE_AVAILABLE = True
except ImportError:
    print("[WARNING] Comprehensive automation not available - check dependencies")

# Smart workflow executor
SMART_WORKFLOW_AVAILABLE = False
try:
    from smart_automation_workflow import SmartAutomationWorkflow, get_smart_workflow
    SMART_WORKFLOW_AVAILABLE = True
except ImportError:
    print("[WARNING] Smart workflow not available - check dependencies")

def find_available_port(start_port: int = 8000, max_port: int = 8010) -> int:
    """Find an available port starting from start_port."""
    import socket
    
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    # If no port is available, return the start_port anyway
    return start_port

# Global executors
selenium_executor = None
dynamic_executor = None
enhanced_executor = None
comprehensive_executor = None
smart_workflow = None
edge_executor = None

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    global selenium_executor, dynamic_executor, enhanced_executor, comprehensive_executor, smart_workflow, edge_executor
    
    print("Starting Selenium Automation Worker...")
    
    # Setup directories
    setup_screenshot_directory()
    
    # Initialize executors
    try:
        selenium_executor = SeleniumExecutor()
        print("[OK] Selenium executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Selenium executor: {e}")
    
    try:
        dynamic_executor = DynamicAIExecutor()
        print("[OK] Dynamic automation executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Dynamic executor: {e}")
    
    try:
        enhanced_executor = EnhancedAutomationExecutor()
        print("[OK] Enhanced automation executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Enhanced executor: {e}")
    
    if ENHANCED_AVAILABLE:
        try:
            enhanced_executor = EnhancedLangChainExecutor()
            print("[OK] Enhanced LangChain automation executor initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize Enhanced executor: {e}")
            try:
                from simple_enhanced_executor import SimpleEnhancedExecutor
                enhanced_executor = SimpleEnhancedExecutor()
                print("[OK] Fallback to simple enhanced executor")
            except Exception as fallback_e:
                print(f"[ERROR] Failed to initialize fallback executor: {fallback_e}")
    else:
        print("[WARNING] Enhanced automation skipped - LangChain dependencies missing")
    
    if FUNCTION_CALLING_AVAILABLE:
        try:
            langchain_integrator = LangChainAutomationIntegrator()
            print("[OK] LangChain integration initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize LangChain integrator: {e}")
    else:
        print("[WARNING] Function calling features skipped - dependencies missing")
    
    try:
        comprehensive_executor = ComprehensiveAutomationExecutor()
        print("[OK] Comprehensive automation executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Comprehensive executor: {e}")
    
    if SMART_WORKFLOW_AVAILABLE:
        try:
            smart_workflow = SmartAutomationWorkflow()
            print("[OK] Smart workflow executor initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize Smart workflow executor: {e}")
    
    try:
        edge_executor = EdgeExecutor()
        print("[OK] Edge executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Edge executor: {e}")
    
    print("Worker startup complete!")
    
    yield
    
    # Shutdown
    print("Shutting down worker...")
    
    # Cleanup executors
    if selenium_executor:
        try:
            if hasattr(selenium_executor, 'cleanup'):
                selenium_executor.cleanup()
        except:
            pass
    
    if dynamic_executor:
        try:
            if hasattr(dynamic_executor, 'cleanup'):
                dynamic_executor.cleanup()
        except:
            pass
    
    if enhanced_executor:
        try:
            if hasattr(enhanced_executor, 'cleanup'):
                enhanced_executor.cleanup()
        except:
            pass
    
    if comprehensive_executor:
        try:
            if hasattr(comprehensive_executor, 'cleanup'):
                comprehensive_executor.cleanup()
        except:
            pass
    
    if smart_workflow:
        try:
            if hasattr(smart_workflow, 'cleanup'):
                smart_workflow.cleanup()
        except:
            pass
    
    if edge_executor:
        try:
            if hasattr(edge_executor, 'cleanup'):
                edge_executor.cleanup()
        except:
            pass
    
    print("Worker shutdown complete")

app = FastAPI(
    title="Selenium Automation Worker",
    description="AI-powered Selenium automation with project generation and multi-model support",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def setup_screenshot_directory():
    """Create screenshot directory if it doesn't exist."""
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    return str(screenshots_dir.absolute())

def cleanup_task_screenshots(task_id: str):
    """Clean up screenshots for a specific task to save disk space."""
    screenshots_dir = Path("screenshots")
    if screenshots_dir.exists():
        for screenshot_file in screenshots_dir.glob(f"{task_id}_*.png"):
            try:
                screenshot_file.unlink()
            except Exception as e:
                print(f"Failed to delete screenshot {screenshot_file}: {e}")

# Request/Response Models
class ExecutionRequest(BaseModel):
    code: str
    website_url: str
    timeout: Optional[int] = 180

class DynamicExecutionRequest(BaseModel):
    prompt: str
    website_url: str
    framework: Optional[str] = "selenium"  # "selenium" or "seleniumbase"
    timeout: Optional[int] = 180

class ExecutionResponse(BaseModel):
    success: bool
    logs: list
    error: Optional[str] = None
    screenshots: list
    execution_time: float

class DynamicExecutionResponse(BaseModel):
    success: bool
    logs: list
    error: Optional[str] = None
    screenshots: list
    execution_time: float
    framework: str
    generated_code: str
    context_chain: list
    function_calls: list
    automation_flow: Optional[dict] = None

class EnhancedExecutionRequest(BaseModel):
    prompt: str
    website_url: str
    framework: Optional[str] = "selenium"
    timeout: Optional[int] = 180
    task_id: Optional[str] = None

class EnhancedExecutionResponse(BaseModel):
    success: bool
    logs: list
    error: Optional[str] = None
    screenshots: list
    execution_time: float
    framework: str
    generated_code: str
    project_structure: Optional[dict] = None
    context_chain: list
    function_calls: list
    chat_history: list
    task_id: str

class ModelSwitchRequest(BaseModel):
    provider: str
    model_name: str

# New chat interface models
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    intent: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    chat_history: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None

class ProjectListResponse(BaseModel):
    projects: list
    total: int

class SessionStatusResponse(BaseModel):
    session_id: str
    current_url: str
    current_task: str
    chat_messages: int
    generated_projects: list
    capabilities: dict
    current_model: Optional[dict] = None

class SmartWorkflowRequest(BaseModel):
    task: str
    website_url: str
    
class SmartWorkflowResponse(BaseModel):
    success: bool
    workflow_id: str
    execution_time: float
    task: str
    website_url: str
    results: Dict[str, Any]
    generated_files: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "enhanced_available": ENHANCED_AVAILABLE
    }

@app.post("/execute", response_model=ExecutionResponse)
async def execute_code(request: ExecutionRequest):
    """Execute Selenium code directly."""
    start_time = time.time()
    
    try:
        result = selenium_executor.execute_code(
            request.code,
            request.website_url,
            request.timeout
        )
        
        execution_time = time.time() - start_time
        
        return ExecutionResponse(
            success=result.get("success", False),
            logs=result.get("logs", []),
            error=result.get("error"),
            screenshots=result.get("screenshots", []),
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return ExecutionResponse(
            success=False,
            logs=[{
                "level": "error",
                "message": f"Execution failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }],
            error=str(e),
            screenshots=[],
            execution_time=execution_time
        )

@app.post("/execute-dynamic", response_model=DynamicExecutionResponse)
async def execute_dynamic_code(request: DynamicExecutionRequest):
    """Execute dynamic automation with AI page analysis."""
    start_time = time.time()
    
    try:
        result = dynamic_executor.execute_automation(
            request.prompt,
            request.website_url,
            request.framework,
            request.timeout
        )
        
        execution_time = time.time() - start_time
        
        return DynamicExecutionResponse(
            success=result.get("success", False),
            logs=result.get("logs", []),
            error=result.get("error"),
            screenshots=result.get("screenshots", []),
            execution_time=execution_time,
            framework=result.get("framework", request.framework),
            generated_code=result.get("generated_code", ""),
            context_chain=result.get("context_chain", []),
            function_calls=result.get("function_calls", []),
            automation_flow=result.get("automation_flow")
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return DynamicExecutionResponse(
            success=False,
            logs=[{
                "level": "error",
                "message": f"Dynamic execution failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }],
            error=str(e),
            screenshots=[],
            execution_time=execution_time,
            framework=request.framework,
            generated_code="",
            context_chain=[],
            function_calls=[],
            automation_flow=None
        )

@app.post("/execute-enhanced", response_model=EnhancedExecutionResponse)
async def execute_enhanced_code(request: EnhancedExecutionRequest):
    """Execute enhanced automation with project generation."""
    start_time = time.time()
    task_id = request.task_id or f"enhanced_{int(time.time())}"
    
    if not ENHANCED_AVAILABLE:
        return EnhancedExecutionResponse(
            success=False,
            logs=[{
                "level": "error",
                "message": "Enhanced automation not available - LangChain dependencies missing",
                "timestamp": datetime.now().isoformat()
            }],
            error="Enhanced automation not available",
            screenshots=[],
            execution_time=time.time() - start_time,
            framework=request.framework,
            generated_code="",
            project_structure={"files": [], "contents": {}},
            context_chain=[],
            function_calls=[],
            chat_history=[],
            task_id=task_id
        )
    
    try:
        result = enhanced_executor.execute_automation(
            request.prompt,
            request.website_url,
            request.framework,
            task_id,
            request.timeout
        )
        
        execution_time = time.time() - start_time
        
        return EnhancedExecutionResponse(
            success=result.get("success", False),
            logs=result.get("logs", []),
            error=result.get("error"),
            screenshots=result.get("screenshots", []),
            execution_time=execution_time,
            framework=result.get("framework", request.framework),
            generated_code=result.get("generated_code", ""),
            project_structure=result.get("project_structure", {"files": [], "contents": {}}),
            context_chain=result.get("context_chain", []),
            function_calls=result.get("function_calls", []),
            chat_history=result.get("chat_history", []),
            task_id=task_id
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return EnhancedExecutionResponse(
            success=False,
            logs=[{
                "level": "error",
                "message": f"Enhanced execution failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }],
            error=str(e),
            screenshots=[],
            execution_time=execution_time,
            framework=request.framework,
            generated_code="",
            project_structure={"files": [], "contents": {}},
            context_chain=[],
            function_calls=[],
            chat_history=[],
            task_id=task_id
        )

@app.get("/models/available")
import os
import time
import asyncio
import traceback
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import contextlib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import all executors
from worker.selenium_executor import SeleniumExecutor
from worker.dynamic_ai_executor import DynamicAIExecutor
from worker.enhanced_executor import EnhancedAutomationExecutor
from worker.comprehensive_automation_executor import ComprehensiveAutomationExecutor, get_comprehensive_executor
from worker.smart_automation_workflow import SmartAutomationWorkflow, get_smart_workflow
from worker.edge_executor import EdgeExecutor

# Enhanced executor
ENHANCED_AVAILABLE = False
try:
    from worker.enhanced_langchain_executor import EnhancedLangChainExecutor
    from worker.simple_enhanced_executor import SimpleEnhancedExecutor
    ENHANCED_AVAILABLE = True
except ImportError:
    print("[WARNING] Enhanced automation features not available - install LangChain dependencies")

# Function calling and agent components
FUNCTION_CALLING_AVAILABLE = False
try:
    from worker.langchain_tools import WebAutomationToolkit
    from worker.langchain_agent import WebAutomationAgent
    from worker.langchain_automation import LangChainAutomationIntegrator
    FUNCTION_CALLING_AVAILABLE = True
except ImportError:
    print("[WARNING] Function calling features not available - LangChain dependencies missing")

# Comprehensive automation executor
COMPREHENSIVE_AVAILABLE = False
try:
    from worker.comprehensive_automation_executor import ComprehensiveAutomationExecutor, get_comprehensive_executor
    COMPREHENSIVE_AVAILABLE = True
except ImportError:
    print("[WARNING] Comprehensive automation not available - check dependencies")

# Smart workflow executor
SMART_WORKFLOW_AVAILABLE = False
try:
    from worker.smart_automation_workflow import SmartAutomationWorkflow, get_smart_workflow
    SMART_WORKFLOW_AVAILABLE = True
except ImportError:
    print("[WARNING] Smart workflow not available - check dependencies")

def find_available_port(start_port: int = 8000, max_port: int = 8010) -> int:
    """Find an available port starting from start_port."""
    import socket
    
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    # If no port is available, return the start_port anyway
    return start_port

# Global executors
selenium_executor = None
dynamic_executor = None
enhanced_executor = None
comprehensive_executor = None
smart_workflow = None
edge_executor = None

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    global selenium_executor, dynamic_executor, enhanced_executor, comprehensive_executor, smart_workflow, edge_executor
    
    print("Starting Selenium Automation Worker...")
    
    # Setup directories
    setup_screenshot_directory()
    
    # Initialize executors
    try:
        selenium_executor = SeleniumExecutor()
        print("[OK] Selenium executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Selenium executor: {e}")
    
    try:
        dynamic_executor = DynamicAIExecutor()
        print("[OK] Dynamic automation executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Dynamic executor: {e}")
    
    try:
        enhanced_executor = EnhancedAutomationExecutor()
        print("[OK] Enhanced automation executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Enhanced executor: {e}")
    
    if ENHANCED_AVAILABLE:
        try:
            enhanced_executor = EnhancedLangChainExecutor()
            print("[OK] Enhanced LangChain automation executor initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize Enhanced executor: {e}")
            try:
                from worker.simple_enhanced_executor import SimpleEnhancedExecutor
                enhanced_executor = SimpleEnhancedExecutor()
                print("[OK] Fallback to simple enhanced executor")
            except Exception as fallback_e:
                print(f"[ERROR] Failed to initialize fallback executor: {fallback_e}")
    else:
        print("[WARNING] Enhanced automation skipped - LangChain dependencies missing")
    
    if FUNCTION_CALLING_AVAILABLE:
        try:
            langchain_integrator = LangChainAutomationIntegrator()
            print("[OK] LangChain integration initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize LangChain integrator: {e}")
    else:
        print("[WARNING] Function calling features skipped - dependencies missing")
    
    try:
        comprehensive_executor = ComprehensiveAutomationExecutor()
        print("[OK] Comprehensive automation executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Comprehensive executor: {e}")
    
    if SMART_WORKFLOW_AVAILABLE:
        try:
            smart_workflow = SmartAutomationWorkflow()
            print("[OK] Smart workflow executor initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize Smart workflow executor: {e}")
    
    try:
        edge_executor = EdgeExecutor()
        print("[OK] Edge executor initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Edge executor: {e}")
    
    print("Worker startup complete!")
    
    yield
    
    # Shutdown
    print("Shutting down worker...")
    
    # Cleanup executors
    if selenium_executor:
        try:
            if hasattr(selenium_executor, 'cleanup'):
                selenium_executor.cleanup()
        except:
            pass
    
    if dynamic_executor:
        try:
            if hasattr(dynamic_executor, 'cleanup'):
                dynamic_executor.cleanup()
        except:
            pass
    
    if enhanced_executor:
        try:
            if hasattr(enhanced_executor, 'cleanup'):
                enhanced_executor.cleanup()
        except:
            pass
    
    if comprehensive_executor:
        try:
            if hasattr(comprehensive_executor, 'cleanup'):
                comprehensive_executor.cleanup()
        except:
            pass
    
    if smart_workflow:
        try:
            if hasattr(smart_workflow, 'cleanup'):
                smart_workflow.cleanup()
        except:
            pass
    
    if edge_executor:
        try:
            if hasattr(edge_executor, 'cleanup'):
                edge_executor.cleanup()
        except:
            pass
    
    print("Worker shutdown complete")

app = FastAPI(
    title="Selenium Automation Worker",
    description="AI-powered Selenium automation with project generation and multi-model support",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def setup_screenshot_directory():
    """Create screenshot directory if it doesn't exist."""
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    return str(screenshots_dir.absolute())

def cleanup_task_screenshots(task_id: str):
    """Clean up screenshots for a specific task to save disk space."""
    screenshots_dir = Path("screenshots")
    if screenshots_dir.exists():
        for screenshot_file in screenshots_dir.glob(f"{task_id}_*.png"):
            try:
                screenshot_file.unlink()
            except Exception as e:
                print(f"Failed to delete screenshot {screenshot_file}: {e}")

# Request/Response Models
class ExecutionRequest(BaseModel):
    code: str
    website_url: str
    timeout: Optional[int] = 180

class DynamicExecutionRequest(BaseModel):
    prompt: str
    website_url: str
    framework: Optional[str] = "selenium"  # "selenium" or "seleniumbase"
    timeout: Optional[int] = 180

class ExecutionResponse(BaseModel):
    success: bool
    logs: list
    error: Optional[str] = None
    screenshots: list
    execution_time: float

class DynamicExecutionResponse(BaseModel):
    success: bool
    logs: list
    error: Optional[str] = None
    screenshots: list
    execution_time: float
    framework: str
    generated_code: str
    context_chain: list
    function_calls: list
    automation_flow: Optional[dict] = None

class EnhancedExecutionRequest(BaseModel):
    prompt: str
    website_url: str
    framework: Optional[str] = "selenium"
    timeout: Optional[int] = 180
    task_id: Optional[str] = None

class EnhancedExecutionResponse(BaseModel):
    success: bool
    logs: list
    error: Optional[str] = None
    screenshots: list
    execution_time: float
    framework: str
    generated_code: str
    project_structure: Optional[dict] = None
    context_chain: list
    function_calls: list
    chat_history: list
    task_id: str

class ModelSwitchRequest(BaseModel):
    provider: str
    model_name: str

# New chat interface models
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    intent: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    chat_history: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None

class ProjectListResponse(BaseModel):
    projects: list
    total: int

class SessionStatusResponse(BaseModel):
    session_id: str
    current_url: str
    current_task: str
    chat_messages: int
    generated_projects: list
    capabilities: dict
    current_model: Optional[dict] = None

class SmartWorkflowRequest(BaseModel):
    task: str
    website_url: str
    
class SmartWorkflowResponse(BaseModel):
    success: bool
    workflow_id: str
    execution_time: float
    task: str
    website_url: str
    results: Dict[str, Any]
    generated_files: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "enhanced_available": ENHANCED_AVAILABLE
    }

@app.post("/execute", response_model=ExecutionResponse)
async def execute_code(request: ExecutionRequest):
    """Execute Selenium code directly."""
    start_time = time.time()
    
    try:
        result = selenium_executor.execute_code(
            request.code,
            request.website_url,
            request.timeout
        )
        
        execution_time = time.time() - start_time
        
        return ExecutionResponse(
            success=result.get("success", False),
            logs=result.get("logs", []),
            error=result.get("error"),
            screenshots=result.get("screenshots", []),
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return ExecutionResponse(
            success=False,
            logs=[{
                "level": "error",
                "message": f"Execution failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }],
            error=str(e),
            screenshots=[],
            execution_time=execution_time
        )

@app.post("/execute-dynamic", response_model=DynamicExecutionResponse)
async def execute_dynamic_code(request: DynamicExecutionRequest):
    """Execute dynamic automation with AI page analysis."""
    start_time = time.time()
    
    try:
        result = dynamic_executor.execute_automation(
            request.prompt,
            request.website_url,
            request.framework,
            request.timeout
        )
        
        execution_time = time.time() - start_time
        
        return DynamicExecutionResponse(
            success=result.get("success", False),
            logs=result.get("logs", []),
            error=result.get("error"),
            screenshots=result.get("screenshots", []),
            execution_time=execution_time,
            framework=result.get("framework", request.framework),
            generated_code=result.get("generated_code", ""),
            context_chain=result.get("context_chain", []),
            function_calls=result.get("function_calls", []),
            automation_flow=result.get("automation_flow")
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return DynamicExecutionResponse(
            success=False,
            logs=[{
                "level": "error",
                "message": f"Dynamic execution failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }],
            error=str(e),
            screenshots=[],
            execution_time=execution_time,
            framework=request.framework,
            generated_code="",
            context_chain=[],
            function_calls=[],
            automation_flow=None
        )

@app.post("/execute-enhanced", response_model=EnhancedExecutionResponse)
async def execute_enhanced_code(request: EnhancedExecutionRequest):
    """Execute enhanced automation with project generation."""
    start_time = time.time()
    task_id = request.task_id or f"enhanced_{int(time.time())}"
    
    if not ENHANCED_AVAILABLE:
        return EnhancedExecutionResponse(
            success=False,
            logs=[{
                "level": "error",
                "message": "Enhanced automation not available - LangChain dependencies missing",
                "timestamp": datetime.now().isoformat()
            }],
            error="Enhanced automation not available",
            screenshots=[],
            execution_time=time.time() - start_time,
            framework=request.framework,
            generated_code="",
            project_structure={"files": [], "contents": {}},
            context_chain=[],
            function_calls=[],
            chat_history=[],
            task_id=task_id
        )
    
    try:
        result = enhanced_executor.execute_automation(
            request.prompt,
            request.website_url,
            request.framework,
            task_id,
            request.timeout
        )
        
        execution_time = time.time() - start_time
        
        return EnhancedExecutionResponse(
            success=result.get("success", False),
            logs=result.get("logs", []),
            error=result.get("error"),
            screenshots=result.get("screenshots", []),
            execution_time=execution_time,
            framework=result.get("framework", request.framework),
            generated_code=result.get("generated_code", ""),
            project_structure=result.get("project_structure", {"files": [], "contents": {}}),
            context_chain=result.get("context_chain", []),
            function_calls=result.get("function_calls", []),
            chat_history=result.get("chat_history", []),
            task_id=task_id
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return EnhancedExecutionResponse(
            success=False,
            logs=[{
                "level": "error",
                "message": f"Enhanced execution failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }],
            error=str(e),
            screenshots=[],
            execution_time=execution_time,
            framework=request.framework,
            generated_code="",
            project_structure={"files": [], "contents": {}},
            context_chain=[],
            function_calls=[],
            chat_history=[],
            task_id=task_id
        )

@app.get("/models/available")
async def get_available_models():
    """Get list of available AI models."""
    if not enhanced_executor or not hasattr(enhanced_executor, 'get_available_models'):
        return {
            "available": False,
            "message": "Enhanced LangChain executor not available",
            "models": {}
        }
    
    try:
        models = enhanced_executor.get_available_models()
        current_model = {
            "provider": getattr(enhanced_executor, 'model_provider', 'unknown'),
            "model": getattr(enhanced_executor, 'model_name', 'unknown')
        }
        
        return {
            "available": True,
            "current_model": current_model,
            "models": models
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "models": {}
        }

@app.post("/models/switch")
async def switch_model(request: ModelSwitchRequest):
    """Switch to a different AI model."""
    if not enhanced_executor or not hasattr(enhanced_executor, 'switch_model'):
        raise HTTPException(
            status_code=400,
            detail="Enhanced LangChain executor not available"
        )
    
    try:
        success = enhanced_executor.switch_model(request.provider, request.model_name)
        if success:
            return {
                "success": True,
                "message": f"Successfully switched to {request.provider}/{request.model_name}",
                "current_model": {
                    "provider": enhanced_executor.model_provider,
                    "model": enhanced_executor.model_name
                }
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to switch to {request.provider}/{request.model_name}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error switching models: {str(e)}"
        )

@app.get("/status")
async def get_status():
    """Get worker status."""
    model_info = {}
    if enhanced_executor and hasattr(enhanced_executor, 'model_provider'):
        model_info = {
            "provider": enhanced_executor.model_provider,
            "model": enhanced_executor.model_name,
            "available": enhanced_executor.model is not None
        }
    
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "executors": {
            "selenium": selenium_executor is not None,
            "dynamic": dynamic_executor is not None,
            "enhanced": enhanced_executor is not None and ENHANCED_AVAILABLE,
            "comprehensive": COMPREHENSIVE_AVAILABLE
        },
        "ai_model": model_info
    }

# New Chat Interface Endpoints

@app.post("/chat", response_model=ChatResponse)
async def chat_with_automation(request: ChatRequest):
    """Main chat interface for automation - similar to bolt.new"""
    if not COMPREHENSIVE_AVAILABLE:
        return ChatResponse(
            response="❌ Comprehensive automation not available - check dependencies",
            execution_result=None,
            metadata=None,
            chat_history=None,
            session_id="error",
            error="Comprehensive automation not available"
        )
    
    try:
        executor = get_comprehensive_executor()
        result = executor.chat_with_automation(request.message, request.context)
        
        return ChatResponse(
            response=result.get("response", ""),
            intent=result.get("intent"),
            execution_result=result.get("execution_result"),
            metadata=result.get("metadata"),
            chat_history=result.get("chat_history", []),
            session_id=result.get("session_id", ""),
            error=result.get("error")
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"❌ Chat processing failed: {str(e)}",
            execution_result=None,
            metadata=None,
            chat_history=None,
            session_id="error",
            error=str(e)
        )

@app.get("/chat/history")
async def get_chat_history():
    """Get chat history for the current session"""
    if not COMPREHENSIVE_AVAILABLE:
        return {"error": "Comprehensive automation not available"}
    
    try:
        executor = get_comprehensive_executor()
        return {
            "success": True,
            "history": executor.get_chat_history(),
            "total_messages": len(executor.get_chat_history())
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.delete("/chat/history")
async def clear_chat_history():
    """Clear chat history"""
    if not COMPREHENSIVE_AVAILABLE:
        return {"error": "Comprehensive automation not available"}
    
    try:
        executor = get_comprehensive_executor()
        executor.clear_chat_history()
        return {
            "success": True,
            "message": "Chat history cleared"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/session/status", response_model=SessionStatusResponse)
async def get_session_status():
    """Get current session status"""
    if not COMPREHENSIVE_AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail="Comprehensive automation not available"
        )
    
    try:
        executor = get_comprehensive_executor()
        status = executor.get_session_status()
        
        return SessionStatusResponse(
            session_id=status["session_id"],
            current_url=status["current_url"],
            current_task=status["current_task"],
            chat_messages=status["chat_messages"],
            generated_projects=status["generated_projects"],
            capabilities=status["capabilities"],
            current_model=status["current_model"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting session status: {str(e)}"
        )

@app.get("/projects", response_model=ProjectListResponse)
async def get_generated_projects():
    """Get list of generated projects"""
    if not COMPREHENSIVE_AVAILABLE:
        return ProjectListResponse(projects=[], total=0)
    
    try:
        executor = get_comprehensive_executor()
        projects = []
        
        for project_id, project_info in executor.generated_projects.items():
            projects.append({
                "id": project_id,
                "name": project_info["name"],
                "created_at": project_info["created_at"],
                "path": project_info["path"],
                "structure": project_info["structure"]
            })
        
        return ProjectListResponse(
            projects=projects,
            total=len(projects)
        )
        
    except Exception as e:
        return ProjectListResponse(projects=[], total=0)

@app.get("/models/comprehensive")
async def get_comprehensive_models():
    """Get available models for comprehensive automation"""
    if not COMPREHENSIVE_AVAILABLE:
        return {
            "available": False,
            "message": "Comprehensive automation not available",
            "models": {}
        }
    
    try:
        executor = get_comprehensive_executor()
        models = executor.get_available_models()
        
        return {
            "available": True,
            "models": models,
            "total_providers": len(models),
            "total_models": sum(len(provider_models) for provider_models in models.values())
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "models": {}
        }

@app.post("/models/comprehensive/switch")
async def switch_comprehensive_model(request: ModelSwitchRequest):
    """Switch AI model for comprehensive automation"""
    if not COMPREHENSIVE_AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail="Comprehensive automation not available"
        )
    
    try:
        executor = get_comprehensive_executor()
        success = executor.switch_model(request.provider, request.model_name)
        
        if success:
            return {
                "success": True,
                "message": f"Successfully switched to {request.provider}/{request.model_name}",
                "current_model": {
                    "provider": request.provider,
                    "model": request.model_name
                }
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to switch to {request.provider}/{request.model_name}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error switching models: {str(e)}"
        )

@app.post("/smart-workflow", response_model=SmartWorkflowResponse)
async def execute_smart_workflow(request: SmartWorkflowRequest):
    """Execute a smart workflow."""
    if not SMART_WORKFLOW_AVAILABLE:
        return SmartWorkflowResponse(
            success=False,
            workflow_id="",
            execution_time=0.0,
            task="",
            website_url="",
            results={},
            generated_files=None,
            error="Smart workflow not available"
        )
    
    try:
        start_time = time.time()
        smart_workflow = get_smart_workflow()
        result = smart_workflow.execute_smart_workflow(request.task, request.website_url)
        execution_time = time.time() - start_time
        
        return SmartWorkflowResponse(
            success=result.get("success", False),
            workflow_id=result.get("workflow_id", ""),
            execution_time=execution_time,
            task=request.task,
            website_url=request.website_url,
            results=result.get("results", {}),
            generated_files=result.get("generated_files"),
            error=result.get("error")
        )
    except Exception as e:
        execution_time = time.time() - start_time
        return SmartWorkflowResponse(
            success=False,
            workflow_id="",
            execution_time=execution_time,
            task=request.task,
            website_url=request.website_url,
            results={},
            generated_files=None,
            error=str(e)
        )

@app.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get comprehensive workflow status including logs and files"""
    try:
        smart_workflow = get_smart_workflow()
        workflow_status = smart_workflow.get_comprehensive_workflow_status(workflow_id)
        
        # Only return 404 if the workflow truly doesn't exist (specific error message)
        if workflow_status.get("error") == "Workflow not found":
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return workflow_status
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving workflow status: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to retrieve workflow status: {str(e)}")

if __name__ == "__main__":
    port = find_available_port()
    print(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 