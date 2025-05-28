"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { TaskRequest, TaskResponse } from "@/lib/shared/types";
import { Loader2, Play } from "lucide-react";

interface AutomationFormProps {
  onTaskCreated: (taskId: string) => void;
}

export function AutomationForm({ onTaskCreated }: AutomationFormProps) {
  const [prompt, setPrompt] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!prompt.trim() || !websiteUrl.trim()) {
      setError("Please fill in both prompt and website URL");
      return;
    }

    try {
      setIsLoading(true);
      setError("");

      const request: TaskRequest = {
        prompt: prompt.trim(),
        websiteUrl: websiteUrl.trim(),
        options: {
          maxAttempts: 3,
          timeout: 60,
          headless: true,
        },
      };

      const response = await fetch("/api/tasks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to create task");
      }

      const result: TaskResponse = await response.json();
      onTaskCreated(result.taskId);

      // Reset form
      setPrompt("");
      setWebsiteUrl("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold mb-2">Create Automation Task</h2>
          <p className="text-gray-600 text-sm">
            Enter a website URL and describe what you want to automate
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="websiteUrl"
              className="text-sm font-medium text-gray-700"
            >
              Website URL
            </label>
            <Input
              id="websiteUrl"
              type="url"
              placeholder="https://example.com"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              disabled={isLoading}
              required
            />
          </div>

          <div className="space-y-2">
            <label
              htmlFor="prompt"
              className="text-sm font-medium text-gray-700"
            >
              Automation Prompt
            </label>
            <Textarea
              id="prompt"
              placeholder="Describe what you want to automate on this website..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={isLoading}
              rows={4}
              required
            />
            <p className="text-xs text-gray-500">
              Example: "Click the login button, fill in email with
              test@example.com, fill password with password123, and submit the
              form"
            </p>
          </div>

          {error && (
            <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
              {error}
            </div>
          )}

          <Button
            type="submit"
            disabled={isLoading || !prompt.trim() || !websiteUrl.trim()}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating Automation...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Generate Automation Script
              </>
            )}
          </Button>
        </form>

        <div className="text-sm text-gray-500 space-y-2">
          <h3 className="font-medium text-gray-700">How it works:</h3>
          <ol className="list-decimal list-inside space-y-1 pl-4">
            <li>AI analyzes your prompt and target website</li>
            <li>Generates Selenium automation code</li>
            <li>Tests the code via trial-and-error</li>
            <li>Returns working Python script</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
