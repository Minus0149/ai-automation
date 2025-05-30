"use client";

import React, { useState, useEffect } from "react";
import { ChevronDown, Check, Cpu } from "lucide-react";

interface ModelInfo {
  provider: string;
  model: string;
  available: boolean;
}

interface AvailableModels {
  [provider: string]: string[];
}

interface ModelSelectorProps {
  onModelChange?: (provider: string, model: string) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ onModelChange }) => {
  const [currentModel, setCurrentModel] = useState<ModelInfo | null>(null);
  const [availableModels, setAvailableModels] = useState<AvailableModels>({});
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch available models and current model
  const fetchModels = async () => {
    try {
      const response = await fetch("/api/models");
      const data = await response.json();

      if (data.available) {
        setAvailableModels(data.models);
        setCurrentModel(data.current_model);
      } else {
        setError(data.message || "Models not available");
      }
    } catch (err) {
      setError("Failed to fetch models");
      console.error("Error fetching models:", err);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const switchModel = async (provider: string, modelName: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/models", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          provider,
          model_name: modelName,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setCurrentModel(data.current_model);
        setIsOpen(false);
        onModelChange?.(provider, modelName);
      } else {
        setError(data.error || "Failed to switch model");
      }
    } catch (err) {
      setError("Failed to switch model");
      console.error("Error switching model:", err);
    } finally {
      setLoading(false);
    }
  };

  const getProviderIcon = (provider: string) => {
    const iconClass = "w-4 h-4 mr-2";

    switch (provider.toLowerCase()) {
      case "openai":
        return <div className={`${iconClass} bg-green-500 rounded-full`} />;
      case "anthropic":
        return <div className={`${iconClass} bg-orange-500 rounded-full`} />;
      case "google":
        return <div className={`${iconClass} bg-blue-500 rounded-full`} />;
      case "ollama":
        return <div className={`${iconClass} bg-purple-500 rounded-full`} />;
      case "huggingface":
        return <div className={`${iconClass} bg-yellow-500 rounded-full`} />;
      default:
        return <Cpu className={iconClass} />;
    }
  };

  const getProviderDisplayName = (provider: string) => {
    switch (provider.toLowerCase()) {
      case "openai":
        return "OpenAI";
      case "anthropic":
        return "Anthropic";
      case "google":
        return "Google";
      case "ollama":
        return "Ollama";
      case "huggingface":
        return "Hugging Face";
      default:
        return provider.charAt(0).toUpperCase() + provider.slice(1);
    }
  };

  if (error && !currentModel) {
    return (
      <div className="text-sm text-gray-500 flex items-center">
        <Cpu className="w-4 h-4 mr-1" />
        Models unavailable
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={loading}
        className="flex items-center justify-between min-w-48 px-3 py-2 text-sm bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
      >
        <div className="flex items-center">
          {currentModel ? (
            <>
              {getProviderIcon(currentModel.provider)}
              <span className="font-medium">
                {getProviderDisplayName(currentModel.provider)}
              </span>
              <span className="ml-1 text-gray-500">{currentModel.model}</span>
            </>
          ) : (
            <>
              <Cpu className="w-4 h-4 mr-2" />
              <span>Select Model</span>
            </>
          )}
        </div>
        <ChevronDown
          className={`w-4 h-4 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <div className="absolute z-50 w-80 mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-96 overflow-y-auto">
          {Object.entries(availableModels).map(([provider, models]) => (
            <div
              key={provider}
              className="border-b border-gray-100 last:border-b-0"
            >
              <div className="px-3 py-2 bg-gray-50 text-sm font-medium text-gray-700 flex items-center">
                {getProviderIcon(provider)}
                {getProviderDisplayName(provider)}
              </div>
              {models.map((model) => (
                <button
                  key={`${provider}-${model}`}
                  onClick={() => switchModel(provider, model)}
                  disabled={loading}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-blue-50 focus:outline-none focus:bg-blue-50 disabled:opacity-50 flex items-center justify-between"
                >
                  <span>{model}</span>
                  {currentModel?.provider === provider &&
                    currentModel?.model === model && (
                      <Check className="w-4 h-4 text-blue-600" />
                    )}
                </button>
              ))}
            </div>
          ))}

          {Object.keys(availableModels).length === 0 && (
            <div className="px-4 py-3 text-sm text-gray-500 text-center">
              No models available
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="absolute z-50 w-full mt-1 px-3 py-2 bg-red-50 border border-red-200 rounded-md text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
