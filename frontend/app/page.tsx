"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { MessageCircle, Sparkles, Zap, RefreshCw } from "lucide-react";

interface TaskAttempt {
  attemptNumber: number;
  status: string;
  generatedCode: string;
  executionResult: any;
  errorMessage: string;
  screenshots: string[];
  executionTime: number;
  createdAt: string;
}

interface TaskDetails {
  task: {
    id: string;
    prompt: string;
    websiteUrl: string;
    status: string;
    attempts: number;
    maxAttempts: number;
    createdAt: string;
    updatedAt: string;
    completedAt: string;
    executionTime: number;
    finalCode: string;
    finalResult: any;
    finalError: string;
  };
  attempts: TaskAttempt[];
  logs: Array<{
    level: string;
    message: string;
    source: string;
    timestamp: string;
  }>;
}

interface Model {
  provider: string;
  model: string;
  name: string;
  features: string[];
}

interface ChatMessage {
  type: "user" | "ai";
  message: string;
  timestamp: Date;
  model?: string;
}

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [selectedModel, setSelectedModel] = useState("gpt-4o-mini");
  const [availableModels, setAvailableModels] = useState<Model[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [taskDetails, setTaskDetails] = useState<TaskDetails | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isChatMode, setIsChatMode] = useState(false);

  const createTask = async () => {
    if (!prompt || !websiteUrl) return;

    setIsLoading(true);
    try {
      const response = await fetch("/api/queue/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt.trim(),
          websiteUrl: websiteUrl.trim(),
          model: selectedModel,
        }),
      });

      const data = await response.json();
      setCurrentTaskId(data.taskId);
      setTaskDetails(null);
    } catch (error) {
      console.error("Error creating task:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTaskDetails = async () => {
    if (!currentTaskId) return;

    try {
      const response = await fetch(`/api/tasks/${currentTaskId}`);

      if (!response.ok) {
        console.error(
          `Failed to fetch task details: ${response.status} ${response.statusText}`
        );
        return;
      }

      const data = await response.json();

      if (data.error) {
        console.error("API Error:", data.error, data.details);
        return;
      }

      setTaskDetails(data);
    } catch (error) {
      console.error("Error fetching task details:", error);
    }
  };

  useEffect(() => {
    if (currentTaskId) {
      const interval = setInterval(fetchTaskDetails, 2000);
      fetchTaskDetails();
      return () => clearInterval(interval);
    }
  }, [currentTaskId]);

  useEffect(() => {
    fetchAvailableModels();
  }, []);

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch("/api/queue/models");
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.models);
        if (data.defaultModel) {
          setSelectedModel(data.defaultModel);
        }
      }
    } catch (error) {
      console.error("Failed to fetch models:", error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500";
      case "failed":
        return "bg-red-500";
      case "error":
        return "bg-red-600";
      case "processing":
        return "bg-blue-500";
      case "executing":
        return "bg-yellow-500";
      case "retrying":
        return "bg-orange-500";
      case "awaiting_chat":
        return "bg-yellow-500";
      default:
        return "bg-gray-500";
    }
  };

  // Safety check for taskDetails
  const hasValidTaskDetails =
    taskDetails && taskDetails.task && taskDetails.task.status;

  // Add copy to clipboard function
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      alert("Code copied to clipboard!");
    } catch (err) {
      console.error("Failed to copy: ", err);
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand("copy");
        alert("Code copied to clipboard!");
      } catch (fallbackErr) {
        alert("Failed to copy code. Please select and copy manually.");
      }
      document.body.removeChild(textArea);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !taskDetails) return;

    const userMessage: ChatMessage = {
      type: "user",
      message: chatInput.trim(),
      timestamp: new Date(),
    };

    setChatMessages((prev) => [...prev, userMessage]);
    setChatInput("");

    try {
      const response = await fetch(
        `/api/queue/tasks/${taskDetails.task.id}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: userMessage.message,
            model: selectedModel,
          }),
        }
      );

      if (response.ok) {
        const chatData = await response.json();
        const aiMessage: ChatMessage = {
          type: "ai",
          message: chatData.response,
          timestamp: new Date(),
          model: chatData.model,
        };
        setChatMessages((prev) => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error("Error sending chat message:", error);
    }
  };

  const continueWithRefinedPrompt = async (refinedPrompt: string) => {
    if (!taskDetails) return;

    try {
      const response = await fetch(
        `/api/queue/tasks/${taskDetails.task.id}/continue`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            refinedPrompt,
            model: selectedModel,
          }),
        }
      );

      if (response.ok) {
        setIsChatMode(false);
        setChatMessages([]);
        fetchTaskDetails();
      }
    } catch (error) {
      console.error("Error continuing task:", error);
    }
  };

  const getModelIcon = (provider: string) => {
    switch (provider) {
      case "gemini-2.0-flash":
        return <Sparkles className="w-4 h-4" />;
      case "gemini-2.5-preview":
        return <Sparkles className="w-4 h-4" />;
      case "gpt-4o-mini":
        return <Zap className="w-4 h-4" />;
      default:
        return <Zap className="w-4 h-4" />;
    }
  };

  const getModelDisplayName = (provider: string) => {
    switch (provider) {
      case "gemini-2.0-flash":
        return "Gemini 2.0 Flash";
      case "gemini-2.5-preview":
        return "Gemini 2.5 Preview";
      case "gpt-4o-mini":
        return "GPT-4o Mini";
      default:
        return provider;
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6">AI Web Automation Agent</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Task Creation Panel */}
        <Card>
          <CardHeader>
            <CardTitle>Create New Automation Task</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Website URL
              </label>
              <Input
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="https://example.com"
                type="url"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">
                Task Description
              </label>
              <Textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe what you want the automation to do..."
                rows={4}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">AI Model</label>
              <Select
                value={selectedModel}
                onValueChange={(value: string) => setSelectedModel(value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent>
                  {availableModels.map((model) => (
                    <SelectItem key={model.provider} value={model.provider}>
                      <div className="flex items-center gap-2">
                        {getModelIcon(model.provider)}
                        <div className="flex flex-col">
                          <span>{getModelDisplayName(model.provider)}</span>
                          <div className="flex gap-1 mt-1">
                            {model.features.slice(0, 2).map((feature) => (
                              <Badge
                                key={feature}
                                className="text-xs bg-blue-100 text-blue-800 border-blue-200"
                              >
                                {feature.replace("_", " ")}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {/* Show selected model details */}
              {availableModels.find((m) => m.provider === selectedModel) && (
                <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                  <div className="flex items-center gap-2 font-medium">
                    {getModelIcon(selectedModel)}
                    <span>{getModelDisplayName(selectedModel)}</span>
                    {selectedModel === "gpt-4o-mini" && (
                      <Badge className="text-xs bg-green-100 text-green-800 border-green-200">
                        Default
                      </Badge>
                    )}
                  </div>
                  <p className="text-gray-600 mt-1">
                    {selectedModel === "gemini-2.0-flash" &&
                      "Enhanced website analysis with context caching for faster performance."}
                    {selectedModel === "gemini-2.5-preview" &&
                      "Latest experimental model with advanced reasoning capabilities."}
                    {selectedModel === "gpt-4o-mini" &&
                      "Reliable and fast model with consistent performance."}
                  </p>
                </div>
              )}
            </div>
            <Button
              onClick={createTask}
              disabled={isLoading || !prompt || !websiteUrl}
              className="w-full"
            >
              {isLoading ? "Creating Task..." : "Create Task"}
            </Button>
          </CardContent>
        </Card>

        {/* Task Status Overview */}
        {hasValidTaskDetails && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                Task Status
                <Badge className={getStatusColor(taskDetails.task.status)}>
                  {taskDetails.task.status.toUpperCase()}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <p>
                  <strong>Task ID:</strong> {taskDetails.task.id}
                </p>
                <p>
                  <strong>Website:</strong> {taskDetails.task.websiteUrl}
                </p>
                <p>
                  <strong>Attempts:</strong> {taskDetails.task.attempts} /{" "}
                  {taskDetails.task.maxAttempts}
                </p>
                <p>
                  <strong>Created:</strong>{" "}
                  {new Date(taskDetails.task.createdAt).toLocaleString()}
                </p>
                {taskDetails.task.executionTime && (
                  <p>
                    <strong>Execution Time:</strong>{" "}
                    {taskDetails.task.executionTime}ms
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Show loading state when task is created but details not yet loaded */}
        {currentTaskId && !hasValidTaskDetails && (
          <Card>
            <CardHeader>
              <CardTitle>Loading Task Details...</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Fetching task information for: {currentTaskId}</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Detailed Task Information */}
      {hasValidTaskDetails && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Task Details & Attempts</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="attempts" className="w-full">
              <TabsList>
                <TabsTrigger value="attempts">
                  Attempts ({taskDetails.attempts?.length || 0})
                </TabsTrigger>
                <TabsTrigger value="logs">
                  Logs ({taskDetails.logs?.length || 0})
                </TabsTrigger>
                <TabsTrigger value="final">Final Result</TabsTrigger>
              </TabsList>

              <TabsContent value="attempts" className="space-y-4">
                {taskDetails.attempts.length === 0 ? (
                  <Alert>
                    <AlertDescription>
                      No attempts recorded yet.
                    </AlertDescription>
                  </Alert>
                ) : (
                  taskDetails.attempts.map((attempt) => (
                    <Card
                      key={attempt.attemptNumber}
                      className="border-l-4 border-l-blue-500"
                    >
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-lg">
                          Attempt #{attempt.attemptNumber}
                          <Badge className={getStatusColor(attempt.status)}>
                            {attempt.status.toUpperCase()}
                          </Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {attempt.generatedCode && (
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-semibold">Generated Code:</h4>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() =>
                                  copyToClipboard(attempt.generatedCode)
                                }
                                className="text-xs"
                              >
                                📋 Copy Code
                              </Button>
                            </div>
                            <ScrollArea className="h-40 w-full border rounded p-3 bg-gray-50">
                              <pre className="text-sm">
                                <code>{attempt.generatedCode}</code>
                              </pre>
                            </ScrollArea>
                          </div>
                        )}

                        {attempt.errorMessage && (
                          <Alert className="border-red-200 bg-red-50">
                            <AlertDescription>
                              <strong>Error:</strong> {attempt.errorMessage}
                            </AlertDescription>
                          </Alert>
                        )}

                        {attempt.executionResult && (
                          <div>
                            <h4 className="font-semibold mb-2">
                              Execution Result:
                            </h4>
                            <ScrollArea className="h-32 w-full border rounded p-3 bg-gray-50">
                              <pre className="text-xs">
                                {JSON.stringify(
                                  attempt.executionResult,
                                  null,
                                  2
                                )}
                              </pre>
                            </ScrollArea>
                          </div>
                        )}

                        <div className="flex justify-between text-sm text-gray-600">
                          <span>Time: {attempt.executionTime || 0}ms</span>
                          <span>
                            Created:{" "}
                            {new Date(attempt.createdAt).toLocaleString()}
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </TabsContent>

              <TabsContent value="logs">
                <ScrollArea className="h-96 w-full border rounded p-4">
                  {taskDetails.logs.length === 0 ? (
                    <p className="text-gray-500">No logs available.</p>
                  ) : (
                    <div className="space-y-2">
                      {taskDetails.logs.map((log, index) => (
                        <div key={index} className="text-sm">
                          <span className="text-gray-500">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </span>
                          <span
                            className={`ml-2 px-2 py-1 rounded text-xs ${
                              log.level === "error"
                                ? "bg-red-100 text-red-800"
                                : log.level === "warning"
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-blue-100 text-blue-800"
                            }`}
                          >
                            {log.level.toUpperCase()}
                          </span>
                          <span className="ml-2">{log.message}</span>
                          {log.source && (
                            <span className="ml-2 text-gray-400">
                              ({log.source})
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </TabsContent>

              <TabsContent value="final">
                {taskDetails.task.finalCode && (
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">Final Generated Code:</h4>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            copyToClipboard(taskDetails.task.finalCode)
                          }
                          className="text-xs"
                        >
                          📋 Copy Final Code
                        </Button>
                      </div>
                      <ScrollArea className="h-48 w-full border rounded p-3 bg-gray-50">
                        <pre className="text-sm">
                          <code>{taskDetails.task.finalCode}</code>
                        </pre>
                      </ScrollArea>
                    </div>

                    {taskDetails.task.finalError && (
                      <Alert className="border-red-200 bg-red-50">
                        <AlertDescription>
                          <strong>Final Error:</strong>{" "}
                          {taskDetails.task.finalError}
                        </AlertDescription>
                      </Alert>
                    )}

                    {taskDetails.task.finalResult && (
                      <div>
                        <h4 className="font-semibold mb-2">Final Result:</h4>
                        <ScrollArea className="h-40 w-full border rounded p-3 bg-gray-50">
                          <pre className="text-xs">
                            {JSON.stringify(
                              taskDetails.task.finalResult,
                              null,
                              2
                            )}
                          </pre>
                        </ScrollArea>
                      </div>
                    )}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
