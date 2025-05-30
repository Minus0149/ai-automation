"use client";

import React, { useState } from "react";
import {
  ChevronRight,
  ChevronDown,
  File,
  Folder,
  FolderOpen,
} from "lucide-react";

interface FileNode {
  name: string;
  type: "file" | "folder";
  content?: string;
  children?: FileNode[];
  path: string;
  language?: string;
}

interface FileExplorerProps {
  projectStructure: any;
  onFileSelect?: (file: FileNode) => void;
  selectedFile?: string;
}

export function FileExplorer({
  projectStructure,
  onFileSelect,
  selectedFile,
}: FileExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set(["root"])
  );

  // Convert the flat file structure to a tree
  const buildFileTree = (structure: any): FileNode => {
    const root: FileNode = {
      name: "project",
      type: "folder",
      path: "root",
      children: [],
    };

    if (!structure?.files) return root;

    const folders = new Map<string, FileNode>();
    folders.set("", root);

    // Create all directories first
    structure.files.forEach((filePath: string) => {
      const parts = filePath.split("/");
      let currentPath = "";

      for (let i = 0; i < parts.length - 1; i++) {
        const parentPath = currentPath;
        currentPath = currentPath ? `${currentPath}/${parts[i]}` : parts[i];

        if (!folders.has(currentPath)) {
          const folderNode: FileNode = {
            name: parts[i],
            type: "folder",
            path: currentPath,
            children: [],
          };

          const parent = folders.get(parentPath);
          if (parent) {
            parent.children!.push(folderNode);
          }
          folders.set(currentPath, folderNode);
        }
      }
    });

    // Add files to their respective directories
    structure.files.forEach((filePath: string) => {
      const parts = filePath.split("/");
      const fileName = parts[parts.length - 1];
      const dirPath = parts.slice(0, -1).join("/");

      const fileNode: FileNode = {
        name: fileName,
        type: "file",
        path: filePath,
        language: getFileLanguage(fileName),
        content: getFileContent(filePath, structure),
      };

      const parent = folders.get(dirPath);
      if (parent) {
        parent.children!.push(fileNode);
      }
    });

    // Sort children: folders first, then files, both alphabetically
    const sortChildren = (node: FileNode) => {
      if (node.children) {
        node.children.sort((a, b) => {
          if (a.type !== b.type) {
            return a.type === "folder" ? -1 : 1;
          }
          return a.name.localeCompare(b.name);
        });
        node.children.forEach(sortChildren);
      }
    };

    sortChildren(root);
    return root;
  };

  const getFileLanguage = (fileName: string): string => {
    const ext = fileName.split(".").pop()?.toLowerCase();
    switch (ext) {
      case "py":
        return "python";
      case "js":
        return "javascript";
      case "ts":
        return "typescript";
      case "json":
        return "json";
      case "md":
        return "markdown";
      case "yml":
      case "yaml":
        return "yaml";
      case "txt":
        return "text";
      case "env":
        return "bash";
      default:
        return "text";
    }
  };

  const getFileContent = (filePath: string, structure: any): string => {
    // Check if we have actual file contents
    if (structure?.contents && structure.contents[filePath]) {
      return structure.contents[filePath];
    }

    // Fallback to placeholder content based on file type
    const fileName = filePath.split("/").pop() || "";
    const ext = fileName.split(".").pop()?.toLowerCase();

    switch (ext) {
      case "py":
        return `# ${fileName}\n# Generated Python automation file\n\nprint("Hello from ${fileName}")`;
      case "md":
        return `# ${fileName.replace(
          ".md",
          ""
        )}\n\nThis is an auto-generated file.`;
      case "json":
        return `{\n  "name": "${fileName}",\n  "generated": true\n}`;
      case "yml":
      case "yaml":
        return `# ${fileName}\ngenerated: true\nproject: automation`;
      default:
        return `# ${fileName}\n# Auto-generated file`;
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

  const getFileIcon = (file: FileNode) => {
    if (file.type === "folder") {
      return expandedFolders.has(file.path) ? (
        <FolderOpen className="w-4 h-4 text-blue-500" />
      ) : (
        <Folder className="w-4 h-4 text-blue-500" />
      );
    }

    const ext = file.name.split(".").pop()?.toLowerCase();
    let color = "text-gray-500";

    switch (ext) {
      case "py":
        color = "text-yellow-600";
        break;
      case "js":
        color = "text-yellow-500";
        break;
      case "ts":
        color = "text-blue-600";
        break;
      case "json":
        color = "text-green-600";
        break;
      case "md":
        color = "text-blue-400";
        break;
      case "yml":
      case "yaml":
        color = "text-red-500";
        break;
      case "txt":
        color = "text-gray-600";
        break;
      default:
        color = "text-gray-500";
    }

    return <File className={`w-4 h-4 ${color}`} />;
  };

  const renderNode = (node: FileNode, depth: number = 0) => {
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedFile === node.path;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center py-1 px-2 hover:bg-gray-100 cursor-pointer ${
            isSelected ? "bg-blue-100 border-r-2 border-blue-500" : ""
          }`}
          style={{ paddingLeft: `${8 + depth * 16}px` }}
          onClick={() => {
            if (node.type === "folder") {
              toggleFolder(node.path);
            } else if (onFileSelect) {
              onFileSelect(node);
            }
          }}
        >
          {node.type === "folder" && (
            <span className="mr-1">
              {isExpanded ? (
                <ChevronDown className="w-3 h-3 text-gray-500" />
              ) : (
                <ChevronRight className="w-3 h-3 text-gray-500" />
              )}
            </span>
          )}

          {node.type === "file" && <span className="w-4 mr-1" />}

          {getFileIcon(node)}

          <span
            className={`ml-2 text-sm ${
              node.type === "folder"
                ? "font-medium text-gray-800"
                : "text-gray-700"
            }`}
          >
            {node.name}
          </span>
        </div>

        {node.type === "folder" && isExpanded && node.children && (
          <div>
            {node.children.map((child) => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (!projectStructure?.files || projectStructure.files.length === 0) {
    return (
      <div className="bg-gray-50 border rounded-lg p-6 text-center">
        <Folder className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-500">No project structure generated yet</p>
        <p className="text-sm text-gray-400">
          Create an automation to see the generated files
        </p>
      </div>
    );
  }

  const fileTree = buildFileTree(projectStructure);

  return (
    <div className="bg-white border rounded-lg overflow-hidden">
      <div className="bg-gray-50 border-b px-4 py-2">
        <h3 className="font-medium text-gray-800 flex items-center">
          <Folder className="w-4 h-4 mr-2" />
          Project Structure
        </h3>
      </div>

      <div className="max-h-96 overflow-y-auto">{renderNode(fileTree)}</div>

      <div className="bg-gray-50 border-t px-4 py-2 text-xs text-gray-500">
        {projectStructure.files.length} files generated
      </div>
    </div>
  );
}
