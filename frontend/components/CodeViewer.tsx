"use client";

import React from "react";
import { Copy, Download, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CodeViewerProps {
  fileName: string;
  content: string;
  language: string;
}

export function CodeViewer({ fileName, content, language }: CodeViewerProps) {
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
    } catch (err) {
      console.error("Failed to copy: ", err);
    }
  };

  const downloadFile = () => {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getLanguageColor = (lang: string) => {
    switch (lang) {
      case "python":
        return "text-yellow-600";
      case "javascript":
        return "text-yellow-500";
      case "typescript":
        return "text-blue-600";
      case "json":
        return "text-green-600";
      case "markdown":
        return "text-blue-400";
      case "yaml":
        return "text-red-500";
      default:
        return "text-gray-600";
    }
  };

  const formatContent = (content: string) => {
    // Basic syntax highlighting for common patterns
    let formatted = content;

    if (language === "python") {
      // Highlight Python keywords, strings, comments
      formatted = formatted
        .replace(
          /(def|class|import|from|if|else|elif|for|while|try|except|finally|with|as|return|yield|lambda|and|or|not|in|is|None|True|False)\b/g,
          '<span class="text-purple-600 font-semibold">$1</span>'
        )
        .replace(/(#.*$)/gm, '<span class="text-gray-500 italic">$1</span>')
        .replace(/(".*?"|\'.*?\')/g, '<span class="text-green-600">$1</span>');
    } else if (language === "json") {
      // Highlight JSON
      formatted = formatted
        .replace(/(".*?")\s*:/g, '<span class="text-blue-600">$1</span>:')
        .replace(/:\s*(".*?")/g, ': <span class="text-green-600">$1</span>')
        .replace(
          /:\s*(true|false|null)/g,
          ': <span class="text-purple-600">$1</span>'
        )
        .replace(/:\s*(\d+)/g, ': <span class="text-orange-600">$1</span>');
    } else if (language === "markdown") {
      // Highlight Markdown
      formatted = formatted
        .replace(
          /^(#{1,6})\s+(.*)$/gm,
          '<span class="text-blue-600 font-bold">$1</span> <span class="font-semibold">$2</span>'
        )
        .replace(/\*\*(.*?)\*\*/g, '<span class="font-bold">$1</span>')
        .replace(/\*(.*?)\*/g, '<span class="italic">$1</span>')
        .replace(
          /`(.*?)`/g,
          '<span class="bg-gray-100 px-1 rounded text-red-600 font-mono">$1</span>'
        );
    }

    return formatted;
  };

  return (
    <div className="bg-white border rounded-lg overflow-hidden h-full flex flex-col">
      {/* Header */}
      <div className="bg-gray-50 border-b px-4 py-2 flex items-center justify-between">
        <div className="flex items-center">
          <FileText className="w-4 h-4 mr-2 text-gray-600" />
          <span className="font-medium text-gray-800">{fileName}</span>
          <span
            className={`ml-2 text-xs px-2 py-1 rounded-full bg-gray-100 ${getLanguageColor(
              language
            )}`}
          >
            {language}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => copyToClipboard(content)}
            className="h-8 px-2"
          >
            <Copy className="w-3 h-3" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={downloadFile}
            className="h-8 px-2"
          >
            <Download className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-4">
          <pre className="text-sm font-mono leading-relaxed whitespace-pre-wrap">
            <code
              dangerouslySetInnerHTML={{ __html: formatContent(content) }}
            />
          </pre>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-50 border-t px-4 py-2 text-xs text-gray-500">
        {content.split("\n").length} lines • {content.length} characters
      </div>
    </div>
  );
}
