"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Code,
  Play,
  Download,
  Copy,
  Settings,
  Zap,
  FileCode,
  Terminal,
  FolderOpen,
  File,
  ChevronRight,
  ChevronDown,
  Folder,
  Eye,
  RefreshCw,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
} from "lucide-react";

interface Message {
  id: string;
  type: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  metadata?: {
    code?: string;
    executionResult?: any;
    results?: any;
    screenshots?: string[];
    functionCalls?: any[];
    projectStructure?: any;
    workflowId?: string;
    success?: boolean;
    logs?: any[];
  };
}

interface ChatInterfaceProps {
  onExecuteAutomation?: (prompt: string, url: string) => Promise<any>;
}

// Robust ID generation to prevent duplicates
let messageCounter = 0;
const generateUniqueId = () => {
  messageCounter++;
  return `msg_${Date.now()}_${messageCounter}_${Math.random()
    .toString(36)
    .substr(2, 9)}`;
};

interface FileNode {
  name: string;
  type: "file" | "folder";
  children?: FileNode[];
  content?: string;
  path: string;
}

export default function ChatInterface({
  onExecuteAutomation,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: generateUniqueId(),
      type: "system",
      content:
        "🤖 Welcome to AI Automation Assistant! I can help you automate web tasks, generate code, and create complete automation projects. What would you like to automate today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [selectedModel, setSelectedModel] = useState(
    "google/gemini-2.5-flash-preview-05-20"
  );
  const [showSettings, setShowSettings] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileStructure, setFileStructure] = useState<FileNode[]>([]);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set()
  );
  const [showLogs, setShowLogs] = useState(false);
  const [selectedLogs, setSelectedLogs] = useState<any[]>([]);
  const [lastWorkflowId, setLastWorkflowId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: generateUniqueId(),
      type: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setInput("");

    try {
      // Execute automation with real backend using smart workflow
      if (onExecuteAutomation && websiteUrl) {
        const response = await fetch("http://localhost:8000/smart-workflow", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            task: input,
            website_url: websiteUrl,
          }),
        });

        const result = await response.json();

        const assistantMessage: Message = {
          id: generateUniqueId(),
          type: "assistant",
          content: result.success
            ? `✅ **Smart Workflow Completed Successfully!**\n\n📋 **Task:** ${
                result.task
              }\n🌐 **Website:** ${
                result.website_url
              }\n⏱️ **Execution Time:** ${result.execution_time.toFixed(
                2
              )}s\n📊 **Workflow ID:** ${result.workflow_id}\n\n${
                result.results?.success
                  ? "🎯 **Automation Result:** Success"
                  : "⚠️ **Automation Result:** Failed"
              }\n\n📁 **Generated Files:** ${
                result.generated_files
                  ? Object.keys(result.generated_files).length
                  : 0
              } files created`
            : `❌ **Smart Workflow Failed**\n\n🚫 **Error:** ${
                result.error
              }\n📋 **Task:** ${result.task}\n🌐 **Website:** ${
                result.website_url
              }\n⏱️ **Execution Time:** ${
                result.execution_time?.toFixed(2) || 0
              }s\n\n🔧 **Troubleshooting:**\n• Check if Chrome is installed\n• Verify website URL is accessible\n• Try running: python check_chrome.py`,
          timestamp: new Date(),
          metadata: {
            code: result.results?.final_code,
            executionResult: result.results,
            screenshots: result.results?.execution_result?.screenshots || [],
            functionCalls: result.results?.function_calls || [],
            projectStructure: result.generated_files,
            workflowId: result.workflow_id,
            success: result.success,
            logs: result.results?.logs || [],
            results: result.results,
          },
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // Store workflow ID for log viewing
        if (result.workflow_id) {
          setLastWorkflowId(result.workflow_id);
        }

        // Update file structure if files were generated
        if (
          result.generated_files &&
          Object.keys(result.generated_files).length > 0
        ) {
          console.log("Updating file structure with:", result.generated_files);
          updateFileStructure(result.generated_files);
        }
      } else {
        // Simulate AI response
        await simulateAIResponse(input);
      }
    } catch (error) {
      const errorMessage: Message = {
        id: generateUniqueId(),
        type: "system",
        content: `❌ Error: ${
          error instanceof Error ? error.message : "Unknown error occurred"
        }`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const simulateAIResponse = async (userInput: string) => {
    // Detect intent from user input
    const intent = detectIntent(userInput);

    let response = "";
    let metadata: any = {};

    switch (intent.type) {
      case "automation":
        if (websiteUrl) {
          response = `🔄 I'll help you automate "${userInput}" on ${websiteUrl}. Let me break this down into steps and execute them.`;

          // Generate mock automation plan
          metadata = generateMockAutomationPlan(userInput, websiteUrl);
          response += `\n\n📋 **Automation Plan:**\n${metadata.plan
            .map((step: any, i: number) => `${i + 1}. ${step.description}`)
            .join("\n")}`;
        } else {
          response = `🌐 To help you automate this task, I need to know which website you'd like to work with. Please provide the URL first.`;
        }
        break;

      case "code_generation":
        metadata = generateMockCode(userInput);
        response = `💻 I'll generate the automation code for you:\n\n\`\`\`python\n${metadata.code}\n\`\`\`\n\nThis code includes error handling, screenshots, and detailed logging. Would you like me to execute it?`;
        break;

      case "project_creation":
        metadata = generateMockProject(userInput);
        response = `🏗️ I'll create a complete automation project for you. Here's the structure:\n\n${formatProjectStructure(
          metadata.projectStructure
        )}`;
        updateFileStructure(metadata.projectStructure);
        break;

      case "question":
        response = getAutomationAdvice(userInput);
        break;

      default:
        response = `🤔 I understand you want to: "${userInput}". Could you be more specific about what automation task you'd like me to help with? For example:
        
• "Click the login button and fill in credentials"
• "Scrape product data from this e-commerce site"  
• "Create a complete testing suite for this form"
• "Generate a web scraping script"`;
    }

    const assistantMessage: Message = {
      id: generateUniqueId(),
      type: "assistant",
      content: response,
      timestamp: new Date(),
      metadata,
    };

    setMessages((prev) => [...prev, assistantMessage]);
  };

  const detectIntent = (input: string) => {
    const lower = input.toLowerCase();

    if (
      lower.includes("click") ||
      lower.includes("fill") ||
      lower.includes("navigate") ||
      lower.includes("automate")
    ) {
      return { type: "automation", confidence: 0.9 };
    }
    if (
      lower.includes("code") ||
      lower.includes("script") ||
      lower.includes("generate")
    ) {
      return { type: "code_generation", confidence: 0.8 };
    }
    if (
      lower.includes("project") ||
      lower.includes("create") ||
      lower.includes("build")
    ) {
      return { type: "project_creation", confidence: 0.7 };
    }
    if (
      lower.includes("how") ||
      lower.includes("what") ||
      lower.includes("why")
    ) {
      return { type: "question", confidence: 0.6 };
    }

    return { type: "general", confidence: 0.5 };
  };

  const generateMockAutomationPlan = (task: string, url: string) => ({
    plan: [
      { description: `Navigate to ${url}`, action: "navigate" },
      { description: "Wait for page to load", action: "wait" },
      { description: `Execute task: ${task}`, action: "execute" },
      { description: "Take screenshot for verification", action: "screenshot" },
      { description: "Return results", action: "complete" },
    ],
    estimatedTime: "30-60 seconds",
    tools: ["selenium", "langchain", "ai-analysis"],
  });

  const generateMockCode = (task: string) => ({
    code: `#!/usr/bin/env python3
"""
Automation script for: ${task}
Generated by AI Automation Assistant
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def automate_task():
    """Main automation function"""
    driver = None
    try:
        # Setup Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        
        # Navigate to website
        driver.get("${websiteUrl || "https://example.com"}")
        time.sleep(2)
        
        # AI-generated automation steps for: ${task}
        # TODO: Implement specific automation logic
        
        # Take screenshot for verification
        driver.save_screenshot("automation_result.png")
        
        print("✅ Automation completed successfully!")
        
    except Exception as e:
        print(f"❌ Automation failed: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    automate_task()`,
    language: "python",
    framework: "selenium",
  });

  const generateMockProject = (task: string) => ({
    projectStructure: {
      "main.py": "Main automation script",
      "config.py": "Configuration settings",
      "requirements.txt": "Python dependencies",
      "README.md": "Project documentation",
      "tests/": {
        "test_automation.py": "Unit tests",
        "test_integration.py": "Integration tests",
      },
      "utils/": {
        "helpers.py": "Helper functions",
        "logger.py": "Logging utilities",
      },
      "screenshots/": "Screenshot storage",
      "logs/": "Log files",
    },
  });

  const formatProjectStructure = (structure: any, indent = 0) => {
    let result = "";
    const spaces = "  ".repeat(indent);

    for (const [key, value] of Object.entries(structure)) {
      if (typeof value === "string") {
        result += `${spaces}📄 ${key} - ${value}\n`;
      } else {
        result += `${spaces}📁 ${key}\n`;
        result += formatProjectStructure(value, indent + 1);
      }
    }

    return result;
  };

  const getAutomationAdvice = (question: string) => {
    const adviceMap: Record<string, string> = {
      selenium:
        "🔧 Selenium is great for browser automation. It can click, type, navigate, and extract data from web pages.",
      langchain:
        "🧠 LangChain adds AI capabilities to automation, making it smarter and more adaptive.",
      testing:
        "🧪 Automated testing helps ensure your web applications work correctly across different scenarios.",
      scraping:
        "📊 Web scraping extracts data from websites. Always respect robots.txt and rate limits.",
      default:
        "💡 I can help with web automation, code generation, testing, and project creation. What specific area interests you?",
    };

    const lower = question.toLowerCase();
    for (const [key, advice] of Object.entries(adviceMap)) {
      if (lower.includes(key)) {
        return advice;
      }
    }

    return adviceMap.default;
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code);
  };

  const executeCode = async (message: Message) => {
    if (!message.metadata?.code) return;

    const executingMessage: Message = {
      id: generateUniqueId(),
      type: "system",
      content: "🔄 Executing automation code...",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, executingMessage]);

    // Simulate execution
    setTimeout(() => {
      const resultMessage: Message = {
        id: generateUniqueId(),
        type: "system",
        content: "✅ Code executed successfully! Check the results above.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, resultMessage]);
    }, 2000);
  };

  const updateFileStructure = (projectStructure: any) => {
    console.log("Raw project structure:", projectStructure);

    const convertToFileNodes = (
      structure: any,
      basePath: string = ""
    ): FileNode[] => {
      const nodes: FileNode[] = [];

      // Handle different structure formats
      if (typeof structure === "string") {
        // It's file content - this shouldn't happen at root level
        return nodes;
      }

      for (const [key, value] of Object.entries(structure)) {
        const path = basePath ? `${basePath}/${key}` : key;

        if (typeof value === "string") {
          // It's a file with content
          nodes.push({
            name: key,
            type: "file",
            path,
            content: value,
          });
        } else if (typeof value === "object" && value !== null) {
          // It's a folder
          nodes.push({
            name: key,
            type: "folder",
            path,
            children: convertToFileNodes(value, path),
          });
        }
      }

      // Sort nodes: folders first, then files
      nodes.sort((a, b) => {
        if (a.type === b.type) {
          return a.name.localeCompare(b.name);
        }
        return a.type === "folder" ? -1 : 1;
      });

      return nodes;
    };

    const newFileStructure = convertToFileNodes(projectStructure);
    console.log("Converted file structure:", newFileStructure);

    setFileStructure(newFileStructure);

    // Expand important folders by default
    const foldersToExpand = new Set([
      "app",
      "components",
      "utils",
      "tests",
      "src",
      "lib",
    ]);

    // Also expand any top-level folders
    newFileStructure.forEach((node) => {
      if (node.type === "folder") {
        foldersToExpand.add(node.path);
      }
    });

    setExpandedFolders(foldersToExpand);
  };

  const viewLogs = async (workflowId: string, executionLogs?: any[]) => {
    try {
      if (executionLogs && executionLogs.length > 0) {
        // Use logs from the message metadata
        setSelectedLogs(executionLogs);
      } else {
        // Fetch logs from the backend
        const response = await fetch(
          `http://localhost:8000/workflow/${workflowId}/status`
        );
        const status = await response.json();
        setSelectedLogs(status.logs || []);
      }
      setShowLogs(true);
    } catch (error) {
      console.error("Failed to fetch logs:", error);
      setSelectedLogs([
        {
          level: "error",
          message: "Failed to fetch logs from server",
          timestamp: new Date().toISOString(),
        },
      ]);
      setShowLogs(true);
    }
  };

  const refreshFileStructure = async () => {
    if (!lastWorkflowId) return;

    try {
      const response = await fetch(
        `http://localhost:8000/workflow/${lastWorkflowId}/status`
      );
      const status = await response.json();

      if (status.generated_files) {
        updateFileStructure(status.generated_files);
      }
    } catch (error) {
      console.error("Failed to refresh file structure:", error);
    }
  };

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const renderFileTree = (
    nodes: FileNode[],
    level: number = 0
  ): JSX.Element[] => {
    return nodes.map((node) => (
      <div key={node.path} className="select-none">
        <div
          className={`flex items-center px-2 py-1 hover:bg-gray-100 cursor-pointer ${
            selectedFile === node.path
              ? "bg-blue-50 border-r-2 border-blue-500"
              : ""
          }`}
          style={{ paddingLeft: `${8 + level * 16}px` }}
          onClick={() => {
            if (node.type === "folder") {
              toggleFolder(node.path);
            } else {
              setSelectedFile(node.path);
            }
          }}
        >
          {node.type === "folder" ? (
            <>
              {expandedFolders.has(node.path) ? (
                <ChevronDown className="w-4 h-4 mr-1" />
              ) : (
                <ChevronRight className="w-4 h-4 mr-1" />
              )}
              <Folder className="w-4 h-4 mr-2 text-blue-500" />
            </>
          ) : (
            <>
              <div className="w-4 mr-1" />
              <File className="w-4 h-4 mr-2 text-gray-500" />
            </>
          )}
          <span className="text-sm text-gray-700">{node.name}</span>
        </div>
        {node.type === "folder" &&
          node.children &&
          expandedFolders.has(node.path) &&
          renderFileTree(node.children, level + 1)}
      </div>
    ));
  };

  const getSelectedFileContent = (): string => {
    const findNode = (nodes: FileNode[], path: string): FileNode | null => {
      for (const node of nodes) {
        if (node.path === path) {
          return node;
        }
        if (node.children) {
          const found = findNode(node.children, path);
          if (found) return found;
        }
      }
      return null;
    };

    if (!selectedFile) return "";
    const node = findNode(fileStructure, selectedFile);
    return node?.content || "";
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Left Column - Chat Interface */}
      <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
        {/* Chat Header */}
        <div className="bg-white border-b border-gray-200 p-4 shadow-sm">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">AI Chat</h1>
              <p className="text-xs text-gray-500">
                {selectedModel.split("/")[1]}
              </p>
            </div>
            <div className="ml-auto flex items-center space-x-2 px-2 py-1 bg-green-50 border border-green-200 rounded-full">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
              <span className="text-xs font-medium text-green-700">Online</span>
            </div>
          </div>

          {/* Website URL Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🌐 Target Website
            </label>
            <input
              type="url"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400 text-sm"
            />
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[85%] rounded-xl px-4 py-3 ${
                  message.type === "user"
                    ? "bg-blue-600 text-white"
                    : message.type === "system"
                    ? "bg-amber-50 text-amber-800 border border-amber-200"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {message.type !== "user" && (
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center">
                      {message.type === "system" ? (
                        <Terminal className="w-3 h-3 text-amber-600" />
                      ) : (
                        <Bot className="w-3 h-3 text-gray-600" />
                      )}
                    </div>
                    <span className="text-xs font-medium text-gray-600">
                      {message.type === "system" ? "System" : "Assistant"}
                    </span>
                  </div>
                )}

                <div className="text-sm whitespace-pre-wrap leading-relaxed">
                  {message.content}
                </div>

                {/* Status Cards */}
                {message.metadata?.success === false && (
                  <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-red-600 text-sm">❌</span>
                      <span className="text-sm font-medium text-red-800">
                        Failed
                      </span>
                    </div>
                    {message.content.includes("Chrome driver") && (
                      <div className="text-xs text-red-700">
                        <p>
                          • Run: <code>python check_chrome.py</code>
                        </p>
                        <p>• Update drivers</p>
                      </div>
                    )}
                  </div>
                )}

                {message.metadata?.success === true && (
                  <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <span className="text-green-600 text-sm">✅</span>
                      <span className="text-sm font-medium text-green-800">
                        Success
                      </span>
                    </div>
                  </div>
                )}

                {/* Function Calls */}
                {message.metadata?.functionCalls &&
                  message.metadata.functionCalls.length > 0 && (
                    <div className="mt-3 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <Zap className="w-4 h-4 text-purple-600" />
                        <span className="text-sm font-medium text-purple-800">
                          {message.metadata.functionCalls.length} Function Calls
                        </span>
                      </div>
                    </div>
                  )}

                {/* Generated Code Display */}
                {(message.metadata?.code ||
                  message.metadata?.executionResult?.final_code ||
                  message.metadata?.results?.final_code) && (
                  <div className="mt-3">
                    <div className="bg-gray-900 rounded-lg overflow-hidden">
                      <div className="bg-gray-800 px-4 py-2 border-b border-gray-700">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <FileCode className="w-4 h-4 text-gray-300" />
                            <span className="text-sm font-medium text-gray-200">
                              Generated Automation Code
                            </span>
                          </div>
                          <button
                            onClick={() =>
                              navigator.clipboard.writeText(
                                message.metadata?.code ||
                                  message.metadata?.executionResult
                                    ?.final_code ||
                                  message.metadata?.results?.final_code ||
                                  ""
                              )
                            }
                            className="p-1 text-gray-400 hover:text-white transition-colors rounded"
                            title="Copy code"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      <div className="max-h-80 overflow-y-auto">
                        <pre className="p-4 text-sm text-gray-100 bg-gray-900 font-mono leading-relaxed">
                          <code>
                            {message.metadata?.code ||
                              message.metadata?.executionResult?.final_code ||
                              message.metadata?.results?.final_code}
                          </code>
                        </pre>
                      </div>
                    </div>
                  </div>
                )}

                {/* Enhanced Execution Results */}
                {message.metadata?.executionResult && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Terminal className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">
                          Execution Details
                        </span>
                      </div>
                      {message.metadata?.logs &&
                        message.metadata.logs.length > 0 && (
                          <button
                            onClick={() =>
                              viewLogs(
                                message.metadata?.workflowId || "",
                                message.metadata?.logs
                              )
                            }
                            className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors flex items-center space-x-1"
                          >
                            <Eye className="w-3 h-3" />
                            <span>
                              View Logs ({message.metadata.logs.length})
                            </span>
                          </button>
                        )}
                    </div>
                    <div className="text-xs text-blue-700 space-y-1">
                      {message.metadata.executionResult.success !==
                        undefined && (
                        <div className="flex items-center space-x-1">
                          {message.metadata.executionResult.success ? (
                            <CheckCircle className="w-3 h-3 text-green-600" />
                          ) : (
                            <XCircle className="w-3 h-3 text-red-600" />
                          )}
                          <span>
                            Status:{" "}
                            {message.metadata.executionResult.success
                              ? "Success"
                              : "Failed"}
                          </span>
                        </div>
                      )}
                      {message.metadata.executionResult.execution_time !==
                        undefined && (
                        <div>
                          ⏱ Time:{" "}
                          {message.metadata.executionResult.execution_time.toFixed(
                            2
                          )}
                          s
                        </div>
                      )}
                      {message.metadata.executionResult.browser_used && (
                        <div>
                          🌐 Browser:{" "}
                          {message.metadata.executionResult.browser_used}
                        </div>
                      )}
                      {message.metadata.executionResult.screenshots &&
                        message.metadata.executionResult.screenshots.length >
                          0 && (
                          <div>
                            📸 Screenshots:{" "}
                            {
                              message.metadata.executionResult.screenshots
                                .length
                            }{" "}
                            captured
                          </div>
                        )}
                      {message.metadata.executionResult.logs &&
                        message.metadata.executionResult.logs.length > 0 && (
                          <div>
                            📋 Logs:{" "}
                            {message.metadata.executionResult.logs.length}{" "}
                            entries
                          </div>
                        )}
                    </div>
                  </div>
                )}

                {/* Project Files Generated */}
                {message.metadata?.projectStructure && (
                  <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <FolderOpen className="w-4 h-4 text-green-600" />
                        <span className="text-sm font-medium text-green-800">
                          Project Generated
                        </span>
                      </div>
                      <button
                        onClick={() =>
                          updateFileStructure(
                            message.metadata?.projectStructure
                          )
                        }
                        className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors flex items-center space-x-1"
                      >
                        <RefreshCw className="w-3 h-3" />
                        <span>Refresh Files</span>
                      </button>
                    </div>
                    <div className="text-xs text-green-700">
                      <div>
                        📁 Files:{" "}
                        {Object.keys(message.metadata.projectStructure).length}{" "}
                        created
                      </div>
                      <div className="mt-1 max-h-20 overflow-y-auto space-y-1">
                        {Object.keys(message.metadata.projectStructure)
                          .slice(0, 10)
                          .map((file, idx) => (
                            <div
                              key={idx}
                              className="flex items-center space-x-1"
                            >
                              <File className="w-3 h-3" />
                              <span className="truncate">{file}</span>
                            </div>
                          ))}
                        {Object.keys(message.metadata.projectStructure).length >
                          10 && (
                          <div className="text-gray-500">
                            ... and{" "}
                            {Object.keys(message.metadata.projectStructure)
                              .length - 10}{" "}
                            more files
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <div className="mt-2 text-xs text-gray-500">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-xl px-4 py-3">
                <div className="flex items-center space-x-3">
                  <div className="w-5 h-5 bg-gray-200 rounded-full flex items-center justify-center">
                    <Bot className="w-3 h-3 animate-pulse text-blue-500" />
                  </div>
                  <div className="flex space-x-1">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                    <div
                      className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600">Processing...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="flex space-x-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Describe what you'd like to automate..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-gray-900 placeholder-gray-500 text-sm"
              rows={2}
              style={{ minHeight: "44px", maxHeight: "100px" }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading || !websiteUrl.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          {!websiteUrl.trim() && (
            <p className="mt-2 text-xs text-amber-600">
              ⚠️ Please enter a website URL above
            </p>
          )}
        </div>
      </div>

      {/* Middle Column - File Explorer/Folder Structure */}
      <div className="w-1/3 bg-gray-50 border-r border-gray-200 flex flex-col">
        <div className="bg-white border-b border-gray-200 p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FolderOpen className="w-5 h-5 text-blue-500" />
              <span className="font-semibold text-gray-800">Project Files</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="text-xs text-gray-500">
                {fileStructure.length} items
              </div>
              {lastWorkflowId && (
                <div className="flex space-x-1">
                  <button
                    onClick={() => viewLogs(lastWorkflowId)}
                    className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors rounded"
                    title="View Logs"
                  >
                    <Terminal className="w-4 h-4" />
                  </button>
                  <button
                    onClick={refreshFileStructure}
                    className="p-1.5 text-gray-400 hover:text-green-600 transition-colors rounded"
                    title="Refresh Files"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          {fileStructure.length > 0 ? (
            <div className="space-y-1">{renderFileTree(fileStructure)}</div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 p-6">
              <Folder className="w-16 h-16 text-gray-300 mb-4" />
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                No Files Yet
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed">
                Start a conversation to generate automation projects and see
                files here.
              </p>
            </div>
          )}
        </div>

        {/* Model Selection */}
        <div className="bg-white border-t border-gray-200 p-4">
          <label className="block text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">
            AI Model
          </label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="w-full px-3 py-2 text-sm bg-white border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-800"
          >
            <optgroup label="Google (Default)">
              <option value="google/gemini-2.5-flash-preview-05-20">
                Gemini 2.5 Flash Preview
              </option>
              <option value="google/gemini-2.0-flash-exp">
                Gemini 2.0 Flash Exp
              </option>
              <option value="google/gemini-1.5-pro-002">
                Gemini 1.5 Pro 002
              </option>
            </optgroup>
            <optgroup label="OpenAI">
              <option value="openai/gpt-4o">GPT-4o</option>
              <option value="openai/gpt-4-turbo">GPT-4 Turbo</option>
            </optgroup>
          </select>
        </div>
      </div>

      {/* Right Column - Code Viewer */}
      <div className="w-1/3 bg-white flex flex-col">
        {selectedFile ? (
          <>
            {/* Code Header */}
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <File className="w-4 h-4 text-gray-500" />
                  <div>
                    <div className="text-sm font-medium text-gray-700">
                      {selectedFile.split("/").pop()}
                    </div>
                    <div className="text-xs text-gray-500">{selectedFile}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() =>
                      navigator.clipboard.writeText(getSelectedFileContent())
                    }
                    className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors rounded"
                    title="Copy code"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors rounded"
                    title="Close"
                  >
                    <span className="text-lg">×</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Code Content */}
            <div className="flex-1 overflow-auto bg-gray-50">
              <div className="h-full">
                <pre className="p-6 text-sm text-gray-800 bg-gray-50 h-full font-mono leading-relaxed whitespace-pre-wrap">
                  <code className="block">{getSelectedFileContent()}</code>
                </pre>
              </div>
            </div>
          </>
        ) : (
          /* Code Placeholder */
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 p-6">
            <FileCode className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-sm font-medium text-gray-700 mb-2">
              No File Selected
            </h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Click on a file in the project explorer to view its contents here.
            </p>

            {/* Latest Message Code Preview */}
            {messages.length > 0 &&
              messages[messages.length - 1].metadata?.code && (
                <div className="mt-6 w-full">
                  <div className="bg-gray-900 rounded-lg overflow-hidden">
                    <div className="bg-gray-800 px-4 py-3 border-b border-gray-700">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <FileCode className="w-5 h-5 text-gray-300" />
                          <span className="text-sm font-medium text-gray-200">
                            💻 Latest Generated Code
                          </span>
                        </div>
                        <button
                          onClick={() =>
                            navigator.clipboard.writeText(
                              messages[messages.length - 1].metadata?.code || ""
                            )
                          }
                          className="p-1.5 text-gray-400 hover:text-white transition-colors rounded"
                          title="Copy code"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      <pre className="p-4 text-sm text-gray-100 bg-gray-900 font-mono leading-relaxed">
                        <code>
                          {messages[messages.length - 1].metadata?.code}
                        </code>
                      </pre>
                    </div>
                  </div>
                </div>
              )}

            {/* Latest Workflow Results */}
            {messages.length > 0 &&
              messages[messages.length - 1].metadata?.results?.final_code && (
                <div className="mt-6 w-full">
                  <div className="bg-gray-900 rounded-lg overflow-hidden">
                    <div className="bg-gray-800 px-4 py-3 border-b border-gray-700">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Zap className="w-5 h-5 text-blue-400" />
                          <span className="text-sm font-medium text-gray-200">
                            🚀 Workflow Generated Code
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-green-400">
                            {messages[messages.length - 1].metadata?.success
                              ? "✓ Success"
                              : "✗ Failed"}
                          </span>
                          <button
                            onClick={() =>
                              navigator.clipboard.writeText(
                                messages[messages.length - 1].metadata?.results
                                  ?.final_code || ""
                              )
                            }
                            className="p-1.5 text-gray-400 hover:text-white transition-colors rounded"
                            title="Copy code"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      <pre className="p-4 text-sm text-gray-100 bg-gray-900 font-mono leading-relaxed">
                        <code>
                          {
                            messages[messages.length - 1].metadata?.results
                              ?.final_code
                          }
                        </code>
                      </pre>
                    </div>
                  </div>
                </div>
              )}
          </div>
        )}
      </div>

      {/* Logs Modal */}
      {showLogs && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl max-h-[80vh] w-full flex flex-col">
            {/* Modal Header */}
            <div className="bg-gray-800 text-white px-6 py-4 rounded-t-lg flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Terminal className="w-5 h-5" />
                <h2 className="text-lg font-semibold">Execution Logs</h2>
                <span className="text-sm text-gray-300">
                  ({selectedLogs.length} entries)
                </span>
              </div>
              <button
                onClick={() => setShowLogs(false)}
                className="text-gray-300 hover:text-white transition-colors"
              >
                <span className="text-2xl">×</span>
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {selectedLogs.length > 0 ? (
                <div className="space-y-2">
                  {selectedLogs.map((log, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border-l-4 ${
                        log.level === "error"
                          ? "bg-red-50 border-red-400"
                          : log.level === "warning"
                          ? "bg-yellow-50 border-yellow-400"
                          : log.level === "info"
                          ? "bg-blue-50 border-blue-400"
                          : "bg-gray-50 border-gray-400"
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            {log.level === "error" && (
                              <XCircle className="w-4 h-4 text-red-600" />
                            )}
                            {log.level === "warning" && (
                              <AlertTriangle className="w-4 h-4 text-yellow-600" />
                            )}
                            {log.level === "info" && (
                              <Info className="w-4 h-4 text-blue-600" />
                            )}
                            <span
                              className={`text-xs font-medium uppercase tracking-wide ${
                                log.level === "error"
                                  ? "text-red-600"
                                  : log.level === "warning"
                                  ? "text-yellow-600"
                                  : log.level === "info"
                                  ? "text-blue-600"
                                  : "text-gray-600"
                              }`}
                            >
                              {log.level}
                            </span>
                          </div>
                          <div className="text-sm text-gray-800 whitespace-pre-wrap">
                            {log.message}
                          </div>
                        </div>
                        <div className="text-xs text-gray-500 ml-4 flex-shrink-0">
                          {log.timestamp &&
                            new Date(log.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <Terminal className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p>No logs available</p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="bg-gray-50 px-6 py-4 rounded-b-lg flex justify-between items-center">
              <div className="text-sm text-gray-600">
                Last workflow: {lastWorkflowId || "None"}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    const logText = selectedLogs
                      .map(
                        (log) =>
                          `[${log.level}] ${log.timestamp} - ${log.message}`
                      )
                      .join("\n");
                    navigator.clipboard.writeText(logText);
                  }}
                  className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors flex items-center space-x-1"
                >
                  <Copy className="w-3 h-3" />
                  <span>Copy Logs</span>
                </button>
                <button
                  onClick={() => setShowLogs(false)}
                  className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
