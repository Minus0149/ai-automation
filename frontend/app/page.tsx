"use client";

import React, { useState, useEffect } from "react";
import ChatInterface from "../components/ChatInterface";
import { Zap, Settings, Globe, Code, Database } from "lucide-react";

export default function Home() {
  const [workerStatus, setWorkerStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkWorkerStatus();
  }, []);

  const checkWorkerStatus = async () => {
    try {
      const response = await fetch("http://localhost:8000/status");
      const status = await response.json();
      setWorkerStatus(status);
    } catch (error) {
      console.error("Failed to check worker status:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const executeAutomation = async (prompt: string, url: string) => {
    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: prompt,
          context: { url },
        }),
      });

      const result = await response.json();
      return result;
    } catch (error) {
      console.error("Automation execution failed:", error);
      throw error;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            Connecting to automation worker...
          </p>
        </div>
      </div>
    );
  }

  if (!workerStatus) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="bg-red-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <Zap className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            Worker Offline
          </h1>
          <p className="text-gray-600 mb-4">
            The automation worker is not available. Please make sure it's
            running on port 8000.
          </p>
          <button
            onClick={checkWorkerStatus}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">
                  AI Automation Platform
                </h1>
                <p className="text-sm text-gray-600">
                  Powered by LangChain & Function Calling •{" "}
                  {workerStatus?.executors?.comprehensive ? "Full AI" : "Basic"}{" "}
                  Mode • Gemini 2.5 Flash Preview Default
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm">
                <div
                  className={`w-2 h-2 rounded-full ${
                    workerStatus?.status === "running"
                      ? "bg-green-500"
                      : "bg-red-500"
                  }`}
                ></div>
                <span className="text-gray-600">
                  {workerStatus?.status === "running" ? "Online" : "Offline"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Status Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Selenium</p>
                <p className="text-lg font-bold text-gray-800">
                  {workerStatus?.executors?.selenium ? "Ready" : "Offline"}
                </p>
              </div>
              <Globe
                className={`w-6 h-6 ${
                  workerStatus?.executors?.selenium
                    ? "text-green-500"
                    : "text-gray-400"
                }`}
              />
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Dynamic AI</p>
                <p className="text-lg font-bold text-gray-800">
                  {workerStatus?.executors?.dynamic ? "Ready" : "Offline"}
                </p>
              </div>
              <Zap
                className={`w-6 h-6 ${
                  workerStatus?.executors?.dynamic
                    ? "text-blue-500"
                    : "text-gray-400"
                }`}
              />
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">LangChain</p>
                <p className="text-lg font-bold text-gray-800">
                  {workerStatus?.executors?.enhanced ? "Ready" : "Offline"}
                </p>
              </div>
              <Code
                className={`w-6 h-6 ${
                  workerStatus?.executors?.enhanced
                    ? "text-purple-500"
                    : "text-gray-400"
                }`}
              />
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Function Calling
                </p>
                <p className="text-lg font-bold text-gray-800">
                  {workerStatus?.executors?.comprehensive ? "Ready" : "Limited"}
                </p>
              </div>
              <Database
                className={`w-6 h-6 ${
                  workerStatus?.executors?.comprehensive
                    ? "text-indigo-500"
                    : "text-gray-400"
                }`}
              />
            </div>
          </div>
        </div>

        {/* AI Model Info */}
        {workerStatus?.ai_model && (
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-800">
                  Current AI Model
                </h3>
                <p className="text-gray-600">
                  {workerStatus.ai_model.provider}/{workerStatus.ai_model.model}
                  {workerStatus.ai_model.available ? (
                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Active
                    </span>
                  ) : (
                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      Inactive
                    </span>
                  )}
                </p>
              </div>
              <Settings className="w-6 h-6 text-gray-400" />
            </div>
          </div>
        )}

        {/* Main Chat Interface */}
        <div
          className="bg-white rounded-lg border border-gray-200 overflow-hidden"
          style={{ height: "calc(100vh - 300px)" }}
        >
          <ChatInterface onExecuteAutomation={executeAutomation} />
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="text-center text-sm text-gray-500">
            AI Automation Platform with Function Calling & Multi-Model Support
          </div>
        </div>
      </footer>
    </div>
  );
}
