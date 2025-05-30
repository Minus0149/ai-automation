"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { FileExplorer } from "@/components/FileExplorer";
import { CodeViewer } from "@/components/CodeViewer";
import ModelSelector from "@/components/ModelSelector";
import { Loader2, CheckCircle, XCircle, Clock, File } from "lucide-react";

interface EnhancedAutomationFormProps {
  onTaskCreated: (taskId: string) => void;
}

interface ProjectConfiguration {
  projectType: string;
  features: string[];
  includeTests: boolean;
  includeDocker: boolean;
  includeCICD: boolean;
}

interface AutomationResult {
  success: boolean;
  taskId: string;
  logs: any[];
  screenshots: string[];
  execution_time: number;
  framework: string;
  generated_code: string;
  project_structure: any;
  context_chain: string[];
  function_calls: any[];
  chat_history: any[];
  error?: string;
}

export function EnhancedAutomationForm({
  onTaskCreated,
}: EnhancedAutomationFormProps) {
  const [prompt, setPrompt] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [framework, setFramework] = useState("selenium");
  const [taskId, setTaskId] = useState("");
  const [projectConfig, setProjectConfig] = useState<ProjectConfiguration>({
    projectType: "selenium_automation",
    features: [
      "Dynamic page analysis",
      "Error handling",
      "Comprehensive logging",
    ],
    includeTests: true,
    includeDocker: true,
    includeCICD: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AutomationResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [executionPhase, setExecutionPhase] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<{
    provider: string;
    model: string;
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !websiteUrl.trim()) return;

    setIsLoading(true);
    setResult(null);
    setSelectedFile(null);
    setExecutionPhase("Initializing LangChain agent...");

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        const phases = [
          "Initializing LangChain agent...",
          "Analyzing website structure...",
          "Generating project structure...",
          "Creating automation files...",
          "Configuring Docker setup...",
          "Generating documentation...",
          "Finalizing project...",
        ];
        setExecutionPhase((prev) => {
          const currentIndex = phases.indexOf(prev);
          return currentIndex < phases.length - 1
            ? phases[currentIndex + 1]
            : prev;
        });
      }, 3000);

      const response = await fetch("/api/tasks/enhanced", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          website_url: websiteUrl.trim(),
          framework,
          task_id: taskId.trim() || undefined,
          project_config: projectConfig,
        }),
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error("Failed to execute enhanced automation");
      }

      const data = await response.json();
      setResult(data);
      onTaskCreated(data.taskId);
    } catch (error) {
      console.error("Error executing enhanced automation:", error);
      setResult({
        success: false,
        taskId: taskId || `error_${Date.now()}`,
        logs: [
          {
            level: "error",
            message: error instanceof Error ? error.message : "Unknown error",
            timestamp: new Date().toISOString(),
          },
        ],
        screenshots: [],
        execution_time: 0,
        framework,
        generated_code: "",
        project_structure: {},
        context_chain: [],
        function_calls: [],
        chat_history: [],
        error: error instanceof Error ? error.message : "Unknown error",
      });
    } finally {
      setIsLoading(false);
      setExecutionPhase("");
    }
  };

  const examplePrompts = [
    {
      title: "E-commerce Product Search",
      prompt:
        "Create a complete automation project that searches for 'laptop' on an e-commerce site, filters by price range, and extracts product details",
      url: "https://example-shop.com",
    },
    {
      title: "Social Media Automation",
      prompt:
        "Build a comprehensive social media automation that logs in, posts content, and monitors engagement metrics",
      url: "https://twitter.com",
    },
    {
      title: "Data Collection Suite",
      prompt:
        "Generate a full data collection project that navigates multiple pages, extracts structured data, and saves to CSV with error handling",
      url: "https://quotes.toscrape.com",
    },
    {
      title: "Form Automation Testing",
      prompt:
        "Create a complete testing framework that fills out complex forms, validates responses, and generates comprehensive test reports",
      url: "https://httpbin.org/forms/post",
    },
  ];

  const handleExampleClick = (example: any) => {
    setPrompt(example.prompt);
    setWebsiteUrl(example.url);
  };

  const toggleFeature = (feature: string) => {
    setProjectConfig((prev) => ({
      ...prev,
      features: prev.features.includes(feature)
        ? prev.features.filter((f) => f !== feature)
        : [...prev.features, feature],
    }));
  };

  const handleFileSelect = (file: any) => {
    setSelectedFile(file);
  };

  const availableFeatures = [
    "Dynamic page analysis",
    "Error handling",
    "Comprehensive logging",
    "Multi-page navigation",
    "Data extraction",
    "Form automation",
    "Screenshot capture",
    "Report generation",
    "Parallel execution",
    "Anti-detection",
    "Proxy support",
    "Database integration",
  ];

  const handleModelChange = (provider: string, model: string) => {
    setSelectedModel({ provider, model });
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border">
        <h2 className="text-2xl font-bold mb-2 text-gray-800">
          🚀 Enhanced AI Automation
        </h2>
        <p className="text-gray-600 mb-4">
          Create complete automation projects with LangChain, project structure
          generation, incremental code modification, and persistent chat
          history.
        </p>
        <div className="flex flex-wrap gap-2">
          <Badge className="bg-green-100 text-green-800">
            Project Structure
          </Badge>
          <Badge className="bg-blue-100 text-blue-800">LangChain Agents</Badge>
          <Badge className="bg-purple-100 text-purple-800">
            Code Modification
          </Badge>
          <Badge className="bg-orange-100 text-orange-800">Chat History</Badge>
          <Badge className="bg-red-100 text-red-800">Function Calling</Badge>
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* File Explorer */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              {result.success ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <XCircle className="w-5 h-5 text-red-500" />
              )}
              <h3 className="text-lg font-semibold">
                {result.success
                  ? "Project Generated Successfully!"
                  : "Generation Failed"}
              </h3>
            </div>

            <FileExplorer
              projectStructure={result.project_structure}
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile?.path}
            />

            {/* Execution Stats */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium mb-2">Execution Summary</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Framework:</span>
                  <span className="ml-2 font-medium">{result.framework}</span>
                </div>
                <div>
                  <span className="text-gray-600">Execution Time:</span>
                  <span className="ml-2 font-medium">
                    {result.execution_time}s
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Function Calls:</span>
                  <span className="ml-2 font-medium">
                    {result.function_calls.length}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Chat Messages:</span>
                  <span className="ml-2 font-medium">
                    {result.chat_history.length}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Code Viewer */}
          <div className="h-96">
            {selectedFile ? (
              <CodeViewer
                fileName={selectedFile.name}
                content={
                  selectedFile.content || "// File content not available"
                }
                language={selectedFile.language || "text"}
              />
            ) : (
              <div className="bg-gray-50 border rounded-lg h-full flex items-center justify-center">
                <div className="text-center">
                  <File className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">
                    Select a file to view its content
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-center mb-4">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">
              Creating Enhanced Automation Project
            </h3>
            <p className="text-blue-600 mb-2">{executionPhase}</p>
            <div className="w-full bg-blue-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full animate-pulse"
                style={{ width: "60%" }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {!result && !isLoading && (
        <>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Task Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="taskId"
                  className="block text-sm font-medium mb-2"
                >
                  Task ID (Optional)
                  <span className="text-gray-500 text-xs ml-2">
                    For continuing previous conversations
                  </span>
                </label>
                <Input
                  id="taskId"
                  value={taskId}
                  onChange={(e) => setTaskId(e.target.value)}
                  placeholder="e.g., task_12345 (auto-generated if empty)"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    AI Model Selection
                  </label>
                  <ModelSelector onModelChange={handleModelChange} />
                  {selectedModel && (
                    <p className="text-xs text-gray-500 mt-1">
                      Using {selectedModel.provider}/{selectedModel.model}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Framework
                  </label>
                  <select
                    value={framework}
                    onChange={(e) => setFramework(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={isLoading}
                  >
                    <option value="selenium">Selenium</option>
                    <option value="seleniumbase">SeleniumBase</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Main Task Input */}
            <div>
              <label
                htmlFor="prompt"
                className="block text-sm font-medium mb-2"
              >
                Automation Task Description
              </label>
              <Textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe what you want to automate. Be specific about the workflow, data to extract, forms to fill, etc. The AI will create a complete project structure."
                rows={4}
                required
              />
            </div>

            <div>
              <label
                htmlFor="websiteUrl"
                className="block text-sm font-medium mb-2"
              >
                Target Website URL
              </label>
              <Input
                id="websiteUrl"
                type="url"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="https://example.com"
                required
              />
            </div>

            {/* Project Configuration */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-3">
                Project Configuration
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Project Type
                  </label>
                  <select
                    value={projectConfig.projectType}
                    onChange={(e) =>
                      setProjectConfig((prev) => ({
                        ...prev,
                        projectType: e.target.value,
                      }))
                    }
                    className="w-full p-2 border border-gray-300 rounded-md"
                  >
                    <option value="selenium_automation">
                      Selenium Automation
                    </option>
                    <option value="web_scraping">Web Scraping</option>
                    <option value="testing_framework">Testing Framework</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium">
                    Include Options
                  </label>
                  <div className="space-y-1">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={projectConfig.includeTests}
                        onChange={(e) =>
                          setProjectConfig((prev) => ({
                            ...prev,
                            includeTests: e.target.checked,
                          }))
                        }
                        className="mr-2"
                      />
                      Test Files
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={projectConfig.includeDocker}
                        onChange={(e) =>
                          setProjectConfig((prev) => ({
                            ...prev,
                            includeDocker: e.target.checked,
                          }))
                        }
                        className="mr-2"
                      />
                      Docker Configuration
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={projectConfig.includeCICD}
                        onChange={(e) =>
                          setProjectConfig((prev) => ({
                            ...prev,
                            includeCICD: e.target.checked,
                          }))
                        }
                        className="mr-2"
                      />
                      CI/CD Pipeline
                    </label>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Project Features
                </label>
                <div className="flex flex-wrap gap-2">
                  {availableFeatures.map((feature) => (
                    <Badge
                      key={feature}
                      onClick={() => toggleFeature(feature)}
                      className={`cursor-pointer transition-colors ${
                        projectConfig.features.includes(feature)
                          ? "bg-blue-500 text-white"
                          : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                      }`}
                    >
                      {feature}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <Button
              type="submit"
              disabled={isLoading || !prompt.trim() || !websiteUrl.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating Enhanced Automation...
                </>
              ) : (
                "🚀 Create Enhanced Automation Project"
              )}
            </Button>
          </form>

          {/* Example Prompts */}
          <div className="bg-white p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">
              📋 Example Automation Projects
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {examplePrompts.map((example, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 cursor-pointer transition-colors"
                  onClick={() => handleExampleClick(example)}
                >
                  <h4 className="font-medium text-blue-600 mb-2">
                    {example.title}
                  </h4>
                  <p className="text-sm text-gray-600 mb-2">{example.prompt}</p>
                  <p className="text-xs text-gray-500">Target: {example.url}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
