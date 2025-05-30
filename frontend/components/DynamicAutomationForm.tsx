"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Loader2,
  Send,
  Zap,
  Settings,
  Brain,
  GitBranch,
  CheckCircle2,
} from "lucide-react";

interface DynamicAutomationFormProps {
  onTaskCreated: (taskId: string) => void;
}

export function DynamicAutomationForm({
  onTaskCreated,
}: DynamicAutomationFormProps) {
  const [prompt, setPrompt] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [framework, setFramework] = useState("selenium");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [timeout, setTimeout] = useState(180);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!prompt.trim() || !websiteUrl.trim()) {
      alert("Please fill in both the prompt and website URL");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch("/api/tasks/dynamic", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          websiteUrl: websiteUrl.trim(),
          framework,
          options: {
            timeout,
            maxAttempts: 3,
          },
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create automation task");
      }

      const data = await response.json();

      // Clear form
      setPrompt("");
      setWebsiteUrl("");

      // Notify parent component
      onTaskCreated(data.taskId);
    } catch (error) {
      console.error("Error creating task:", error);
      alert("Failed to create automation task. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const examplePrompts = [
    "Fill out the contact form with sample data",
    "Search for 'automation testing' and click the first result",
    "Navigate through the product pages and collect pricing information",
    "Sign up for the newsletter with test email",
    "Find and click all social media links",
  ];

  const handleExampleClick = (example: string) => {
    setPrompt(example);
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-6 w-6 text-blue-600" />
          Dynamic AI Automation
          <Badge className="ml-2">
            <Zap className="h-3 w-3 mr-1" />
            Powered by AI
          </Badge>
        </CardTitle>
        <p className="text-sm text-gray-600">
          Describe what you want to automate and let AI analyze the website
          dynamically
        </p>
      </CardHeader>

      <CardContent className="space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="prompt" className="block text-sm font-medium mb-2">
              Automation Task Description
            </label>
            <Textarea
              id="prompt"
              placeholder="Describe what you want to automate on the website..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-[100px]"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Be specific about what actions you want to perform
            </p>
          </div>

          <div>
            <label
              htmlFor="websiteUrl"
              className="block text-sm font-medium mb-2"
            >
              Website URL
            </label>
            <Input
              id="websiteUrl"
              type="url"
              placeholder="https://example.com"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Automation Framework
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  framework === "selenium"
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
                onClick={() => setFramework("selenium")}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">Selenium</h3>
                    <p className="text-sm text-gray-600">
                      Standard web automation
                    </p>
                  </div>
                  {framework === "selenium" && (
                    <CheckCircle2 className="h-5 w-5 text-blue-600" />
                  )}
                </div>
              </div>

              <div
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  framework === "seleniumbase"
                    ? "border-purple-500 bg-purple-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
                onClick={() => setFramework("seleniumbase")}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">SeleniumBase</h3>
                    <p className="text-sm text-gray-600">
                      Enhanced automation with detection bypass
                    </p>
                  </div>
                  {framework === "seleniumbase" && (
                    <CheckCircle2 className="h-5 w-5 text-purple-600" />
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center gap-2"
            >
              <Settings className="h-4 w-4" />
              Advanced Settings
            </Button>

            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2"
            >
              {isSubmitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              {isSubmitting ? "Creating..." : "Start Automation"}
            </Button>
          </div>

          {showAdvanced && (
            <div className="p-4 border rounded-lg bg-gray-50 space-y-4">
              <h3 className="font-medium text-sm">Advanced Settings</h3>

              <div>
                <label
                  htmlFor="timeout"
                  className="block text-sm font-medium mb-2"
                >
                  Timeout (seconds)
                </label>
                <Input
                  id="timeout"
                  type="number"
                  min="30"
                  max="600"
                  value={timeout}
                  onChange={(e) => setTimeout(parseInt(e.target.value))}
                  className="w-32"
                />
              </div>
            </div>
          )}
        </form>

        <div>
          <h3 className="font-medium text-sm mb-3 flex items-center gap-2">
            <GitBranch className="h-4 w-4" />
            Example Prompts
          </h3>
          <div className="grid grid-cols-1 gap-2">
            {examplePrompts.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="text-left text-sm p-2 rounded border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-sm text-blue-800 mb-2">
            🚀 How Dynamic Automation Works:
          </h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• AI analyzes the website structure automatically</li>
            <li>• Dynamically adapts to page changes during navigation</li>
            <li>• Maintains context across multiple page interactions</li>
            <li>• Uses intelligent function calling for better accuracy</li>
            <li>• Supports both Selenium and SeleniumBase frameworks</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
