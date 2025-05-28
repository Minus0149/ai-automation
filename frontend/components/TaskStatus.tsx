"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AutomationTask, TaskStatusResponse } from "@/lib/shared/types";
import {
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  Copy,
  Download,
  Play,
  Edit,
} from "lucide-react";
import dynamic from "next/dynamic";

// Dynamically import Monaco Editor to avoid SSR issues
const Editor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => <div className="h-96 bg-gray-900 rounded-lg animate-pulse" />,
});

interface TaskStatusProps {
  taskId: string;
}

export function TaskStatus({ taskId }: TaskStatusProps) {
  const [task, setTask] = useState<AutomationTask | null>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [editedCode, setEditedCode] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);

  useEffect(() => {
    const fetchTaskStatus = async () => {
      try {
        const response = await fetch(`/api/tasks/${taskId}`);

        if (!response.ok) {
          throw new Error("Failed to fetch task status");
        }

        const data: TaskStatusResponse = await response.json();
        setTask(data.task);
        setLogs(data.logs);
        setError("");

        // Set initial code for editing
        if (data.task.result?.generatedCode && !editedCode) {
          setEditedCode(data.task.result.generatedCode);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setIsLoading(false);
      }
    };

    fetchTaskStatus();

    // Poll for updates if task is still processing
    const interval = setInterval(() => {
      if (task?.status === "processing" || task?.status === "pending") {
        fetchTaskStatus();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId, task?.status, editedCode]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "processing":
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "completed":
        return "Completed Successfully";
      case "failed":
        return "Failed";
      case "processing":
        return "Processing...";
      default:
        return "Pending";
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error("Failed to copy to clipboard:", err);
    }
  };

  const downloadCode = (code: string) => {
    const blob = new Blob([code], { type: "text/python" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `automation_script_${taskId}.py`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const executeEditedCode = async () => {
    if (!editedCode || !task) return;

    setIsExecuting(true);
    try {
      const response = await fetch("/api/execute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code: editedCode,
          websiteUrl: task.websiteUrl,
          timeout: 60,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to execute code");
      }

      const result = await response.json();

      // Update logs with execution result
      const newLog = {
        level: result.success ? "info" : "error",
        message: result.success
          ? "Manual execution completed"
          : `Manual execution failed: ${result.error}`,
        timestamp: new Date().toISOString(),
      };

      setLogs((prev) => [...prev, newLog]);
    } catch (err) {
      const errorLog = {
        level: "error",
        message: `Execution error: ${
          err instanceof Error ? err.message : "Unknown error"
        }`,
        timestamp: new Date().toISOString(),
      };
      setLogs((prev) => [...prev, errorLog]);
    } finally {
      setIsExecuting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="flex items-center justify-center min-h-[200px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Loading task status...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="text-center space-y-4">
          <div className="text-red-600">{error}</div>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="text-center space-y-4">
          <div>Task not found</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Task Status</h2>
        <div className="flex items-center space-x-2">
          {getStatusIcon(task.status)}
          <span className="font-medium">{getStatusText(task.status)}</span>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="font-medium mb-2">Task Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm bg-gray-50 p-3 rounded">
            <div>
              <span className="font-medium">Task ID:</span> {task.id}
            </div>
            <div>
              <span className="font-medium">Status:</span> {task.status}
            </div>
            <div className="col-span-2">
              <span className="font-medium">Website:</span>
              <a
                href={task.websiteUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline ml-1"
              >
                {task.websiteUrl}
              </a>
            </div>
            <div>
              <span className="font-medium">Attempts:</span> {task.attempts}/
              {task.maxAttempts}
            </div>
          </div>
        </div>

        <div>
          <h3 className="font-medium mb-2">Prompt:</h3>
          <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
            {task.prompt}
          </p>
        </div>
      </div>

      {task.result?.generatedCode && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Generated Code</h3>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                <Edit className="h-4 w-4 mr-1" />
                {isEditing ? "View" : "Edit"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  copyToClipboard(
                    isEditing ? editedCode : task.result!.generatedCode
                  )
                }
              >
                <Copy className="h-4 w-4 mr-1" />
                Copy
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  downloadCode(
                    isEditing ? editedCode : task.result!.generatedCode
                  )
                }
              >
                <Download className="h-4 w-4 mr-1" />
                Download
              </Button>
              {isEditing && (
                <Button
                  variant="default"
                  size="sm"
                  onClick={executeEditedCode}
                  disabled={isExecuting}
                >
                  {isExecuting ? (
                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4 mr-1" />
                  )}
                  Execute
                </Button>
              )}
            </div>
          </div>

          {isEditing ? (
            <div className="border rounded-lg overflow-hidden">
              <Editor
                height="400px"
                defaultLanguage="python"
                value={editedCode}
                onChange={(value) => setEditedCode(value || "")}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: "on",
                  roundedSelection: false,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 4,
                  wordWrap: "on",
                }}
              />
            </div>
          ) : (
            <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm max-h-96 overflow-auto">
              <pre>{task.result.generatedCode}</pre>
            </div>
          )}
        </div>
      )}

      {logs.length > 0 && (
        <div className="space-y-4">
          <h3 className="font-semibold">Execution Logs</h3>
          <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-auto">
            {logs.map((log, index) => (
              <div key={index} className="text-sm mb-1">
                <span className="text-gray-400">
                  [{new Date(log.timestamp).toLocaleTimeString()}]
                </span>
                <span
                  className={`ml-2 ${
                    log.level === "error"
                      ? "text-red-400"
                      : log.level === "warning"
                      ? "text-yellow-400"
                      : "text-green-400"
                  }`}
                >
                  {log.level.toUpperCase()}:
                </span>
                <span className="text-white ml-2">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {task.result?.error && (
        <div className="space-y-2">
          <h3 className="font-semibold text-red-600">Error</h3>
          <div className="bg-red-50 border border-red-200 rounded p-3 text-red-700 text-sm">
            {task.result.error}
          </div>
        </div>
      )}

      {task.result?.screenshots && task.result.screenshots.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-semibold">Screenshots</h3>
          <div className="grid grid-cols-2 gap-4">
            {task.result.screenshots.map((screenshot, index) => (
              <div key={index} className="border rounded p-2">
                <img
                  src={screenshot}
                  alt={`Screenshot ${index + 1}`}
                  className="w-full h-auto rounded"
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
