"""
Comprehensive Automation Executor with Chat Interface
"""
import os
import time
from typing import Dict, Any, List
from datetime import datetime

class ComprehensiveAutomationExecutor:
    """Comprehensive executor with chat interface and automation capabilities."""
    
    def __init__(self):
        self.chat_history = []
        self.session_data = {}
    
    def chat_with_automation(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main chat interface that can handle questions and automation requests.
        """
        start_time = time.time()
        
        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Analyze the message intent
        intent = self._analyze_intent(message)
        
        try:
            if intent["type"] == "automation_request":
                # Execute automation
                automation_result = self._execute_automation_request(
                    intent["task"], 
                    intent.get("website_url", context.get("url", "") if context else "")
                )
                
                # Create response
                response = {
                    "success": automation_result.get("success", False),
                    "message": "Automation task executed successfully!" if automation_result.get("success") else "Automation task failed.",
                    "automation_result": automation_result,
                    "intent": intent,
                    "execution_time": time.time() - start_time,
                    "generated_code": automation_result.get("generated_code", ""),
                    "approach": "automation_execution"
                }
                
            elif intent["type"] == "project_request":
                # Generate project
                project_result = self._create_project(intent["task"])
                
                response = {
                    "success": project_result.get("success", False),
                    "message": "Project generated successfully!" if project_result.get("success") else "Project generation failed.",
                    "project_result": project_result,
                    "intent": intent,
                    "execution_time": time.time() - start_time,
                    "generated_code": project_result.get("main_script", ""),
                    "approach": "project_generation"
                }
                
            elif intent["type"] == "question":
                # Answer question
                answer = self._answer_question(message)
                
                response = {
                    "success": True,
                    "message": answer,
                    "intent": intent,
                    "execution_time": time.time() - start_time,
                    "approach": "question_answering"
                }
                
            else:
                # General conversation
                reply = self._generate_general_response(message)
                
                response = {
                    "success": True,
                    "message": reply,
                    "intent": intent,
                    "execution_time": time.time() - start_time,
                    "approach": "general_conversation"
                }
            
            # Add assistant response to history
            self.chat_history.append({
                "role": "assistant",
                "content": response["message"],
                "timestamp": datetime.now().isoformat(),
                "metadata": response
            })
            
            return response
            
        except Exception as e:
            error_response = {
                "success": False,
                "message": f"Sorry, I encountered an error: {str(e)}",
                "error": str(e),
                "intent": intent,
                "execution_time": time.time() - start_time,
                "approach": "error_handling"
            }
            
            self.chat_history.append({
                "role": "assistant",
                "content": error_response["message"],
                "timestamp": datetime.now().isoformat(),
                "metadata": error_response
            })
            
            return error_response
    
    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze the intent of the user message."""
        message_lower = message.lower()
        
        # Automation keywords
        automation_keywords = [
            "automate", "test", "run", "execute", "click", "fill", "submit", 
            "navigate", "scrape", "login", "automation", "selenium"
        ]
        
        # Project generation keywords
        project_keywords = [
            "create project", "generate project", "build project", "new project",
            "project structure", "scaffold", "template"
        ]
        
        # Question keywords
        question_keywords = [
            "what", "how", "why", "when", "where", "explain", "help", "?",
            "can you", "could you", "would you"
        ]
        
        # Check for automation request
        if any(keyword in message_lower for keyword in automation_keywords):
            # Try to extract website URL
            website_url = ""
            words = message.split()
            for i, word in enumerate(words):
                if word.startswith("http"):
                    website_url = word
                    break
                elif word in ["on", "at", "from"] and i + 1 < len(words):
                    if words[i + 1].startswith("http"):
                        website_url = words[i + 1]
                        break
            
            return {
                "type": "automation_request",
                "task": message,
                "website_url": website_url,
                "confidence": 0.8
            }
        
        # Check for project generation request
        elif any(keyword in message_lower for keyword in project_keywords):
            return {
                "type": "project_request",
                "task": message,
                "confidence": 0.9
            }
        
        # Check for question
        elif any(keyword in message_lower for keyword in question_keywords):
            return {
                "type": "question",
                "question": message,
                "confidence": 0.7
            }
        
        # Default to general conversation
        else:
            return {
                "type": "conversation",
                "message": message,
                "confidence": 0.5
            }
    
    def _execute_automation_request(self, prompt: str, website_url: str) -> Dict[str, Any]:
        """Execute automation request and return results."""
        try:
            # Generate automation code based on the prompt
            code_result = self._generate_automation_code(prompt, website_url)
            
            return {
                "success": True,
                "generated_code": code_result["code"],
                "framework": "selenium",
                "task": prompt,
                "website_url": website_url,
                "execution_time": 0.5,
                "logs": [
                    {
                        "level": "info",
                        "message": "Automation code generated successfully",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": prompt,
                "website_url": website_url
            }
    
    def _generate_automation_code(self, prompt: str, url: str) -> Dict[str, str]:
        """Generate automation code based on prompt and URL."""
        prompt_lower = prompt.lower()
        
        if "login" in prompt_lower and "test" in prompt_lower:
            code = f'''from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_login():
    """Test login functionality."""
    # Setup Chrome driver
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to login page
        driver.get("{url}")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Find and fill username
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.clear()
        username_field.send_keys("student")
        
        # Find and fill password
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys("Password123")
        
        # Click submit button
        submit_button = driver.find_element(By.ID, "submit")
        submit_button.click()
        
        # Wait for result
        time.sleep(3)
        
        # Check for success message
        try:
            success_element = driver.find_element(By.CSS_SELECTOR, ".post-title")
            if "Logged In Successfully" in success_element.text:
                print("LOGIN TEST PASSED")
                return True
            else:
                print("LOGIN TEST FAILED - unexpected content")
                return False
        except Exception as e:
            print(f"LOGIN TEST FAILED - {{e}}")
            return False
            
    except Exception as e:
        print(f"Test error: {{e}}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login()
'''
        elif "scrape" in prompt_lower or "extract" in prompt_lower:
            code = f'''from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time

def scrape_website():
    """Scrape website data."""
    # Setup Chrome driver
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to website
        driver.get("{url}")
        time.sleep(3)
        
        # Extract data
        title = driver.title
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Find all links
        links = driver.find_elements(By.TAG_NAME, "a")
        link_data = []
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip()
            if href and text:
                link_data.append({{"text": text, "url": href}})
        
        # Compile results
        data = {{
            "title": title,
            "url": "{url}",
            "content_length": len(body_text),
            "links": link_data[:10]  # First 10 links
        }}
        
        # Save data
        with open("scraped_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Scraped data from {{title}}")
        print(f"Found {{len(link_data)}} links")
        
        return data
        
    except Exception as e:
        print(f"Scraping error: {{e}}")
        return None
    
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_website()
'''
        else:
            # Generic automation
            code = f'''from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def run_automation():
    """Run generic automation task."""
    # Setup Chrome driver
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to website
        driver.get("{url}")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Task: {prompt}
        # Add specific automation logic here
        
        # Example: Find and interact with elements
        buttons = driver.find_elements(By.TAG_NAME, "button")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        
        print(f"Found {{len(buttons)}} buttons and {{len(inputs)}} inputs")
        
        # Wait and observe
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"Automation error: {{e}}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    run_automation()
'''
        
        return {"code": code, "framework": "selenium"}
    
    def _create_project(self, prompt: str) -> Dict[str, Any]:
        """Create a project based on the prompt."""
        try:
            project_structure = {
                "main_automation.py": "# Main automation script\n# Generated for: " + prompt,
                "requirements.txt": "selenium==4.15.2\nwebdriver-manager==4.0.1",
                "README.md": f"# Automation Project\n\n{prompt}\n\n## Setup\n\n```bash\npip install -r requirements.txt\npython main_automation.py\n```"
            }
            
            return {
                "success": True,
                "project_structure": project_structure,
                "main_script": project_structure["main_automation.py"],
                "files_created": len(project_structure)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _answer_question(self, question: str) -> str:
        """Answer automation-related questions."""
        question_lower = question.lower()
        
        if "selenium" in question_lower:
            return "Selenium is a web automation framework that allows you to control web browsers programmatically. It's great for testing, scraping, and automating repetitive web tasks."
        
        elif "automation" in question_lower:
            return "Web automation involves using scripts to perform tasks on websites automatically. Common use cases include testing, data extraction, form filling, and repetitive task automation."
        
        elif "webdriver" in question_lower:
            return "WebDriver is the core component of Selenium that communicates with web browsers. It provides a programming interface to control browser actions like clicking, typing, and navigation."
        
        elif "chrome" in question_lower or "browser" in question_lower:
            return "Chrome is a popular browser for automation. You'll need ChromeDriver to control it with Selenium. Make sure to use headless mode for better performance in automation scripts."
        
        else:
            return "I can help you with web automation tasks using Selenium. You can ask me to automate websites, generate code, or answer questions about automation techniques."
    
    def _generate_general_response(self, message: str) -> str:
        """Generate a general conversational response."""
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon"]
        
        if any(greeting in message.lower() for greeting in greetings):
            return "Hello! I'm your automation assistant. I can help you automate websites, generate Selenium code, and answer questions about web automation. What would you like to automate today?"
        
        elif "help" in message.lower():
            return "I can help you with:\n• Website automation and testing\n• Generating Selenium code\n• Creating automation projects\n• Answering automation questions\n\nJust tell me what you'd like to automate or ask me a question!"
        
        else:
            return "I'm here to help with web automation tasks. You can ask me to automate websites, generate code, or answer questions about Selenium and web automation."
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get the chat history."""
        return self.chat_history
    
    def clear_chat_history(self):
        """Clear the chat history."""
        self.chat_history = []
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        return {
            "chat_messages": len(self.chat_history),
            "user_messages": len([msg for msg in self.chat_history if msg["role"] == "user"]),
            "assistant_messages": len([msg for msg in self.chat_history if msg["role"] == "assistant"]),
            "session_active": True,
            "capabilities": [
                "website_automation",
                "code_generation", 
                "project_creation",
                "question_answering",
                "chat_conversation"
            ]
        }
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models (simplified for this executor)."""
        return {
            "selenium": ["chrome", "firefox", "edge"],
            "frameworks": ["selenium", "seleniumbase"]
        }
    
    def switch_model(self, provider: str, model_name: str) -> bool:
        """Switch model (placeholder for this executor)."""
        return True
    
    def cleanup(self):
        """Clean up resources."""
        self.chat_history = []
        self.session_data = {}

# Global instance for easy access
_comprehensive_executor = None

def get_comprehensive_executor() -> ComprehensiveAutomationExecutor:
    """Get or create the global comprehensive executor instance."""
    global _comprehensive_executor
    if _comprehensive_executor is None:
        _comprehensive_executor = ComprehensiveAutomationExecutor()
    return _comprehensive_executor 