// Task-related types
export interface AutomationTask {
  id: string;
  prompt: string;
  websiteUrl: string;
  status: "pending" | "processing" | "completed" | "failed";
  attempts: number;
  maxAttempts: number;
  createdAt: Date;
  updatedAt: Date;
  result?: AutomationResult;
  finalCode?: string;
}

export interface AutomationResult {
  success: boolean;
  generatedCode: string;
  screenshots: string[];
  error?: string;
  executionLogs: LogEntry[];
  executionTime: number;
}

export interface LogEntry {
  level: "info" | "warning" | "error";
  message: string;
  timestamp: Date;
  metadata?: any;
}

export interface SeleniumScript {
  code: string;
  explanation: string;
  requirements: string[];
}

// API Request/Response types
export interface TaskRequest {
  prompt: string;
  websiteUrl: string;
  options?: TaskOptions;
}

export interface TaskOptions {
  maxAttempts?: number;
  timeout?: number;
  headless?: boolean;
}

export interface TaskResponse {
  taskId: string;
  status: string;
  message: string;
}

export interface TaskStatusResponse {
  task: AutomationTask;
  logs: LogEntry[];
}

// Worker types
export interface WorkerRequest {
  taskId: string;
  code: string;
  websiteUrl: string;
  timeout?: number;
  headless?: boolean;
}

export interface WorkerResponse {
  success: boolean;
  logs: LogEntry[];
  error?: string;
  screenshots?: string[];
  domSnapshot?: string;
}

// OpenAI types
export interface OpenAIRequest {
  prompt: string;
  websiteUrl: string;
  domSnapshot?: string;
  previousCode?: string;
  errorLogs?: LogEntry[];
  attempt: number;
}

export interface OpenAIResponse {
  script: SeleniumScript;
  reasoning: string;
}

// Queue Job types
export interface AutomationJob {
  taskId: string;
  prompt: string;
  websiteUrl: string;
  attempt: number;
  maxAttempts: number;
}

// Worker Execution types
export interface WorkerExecutionRequest {
  code: string;
  websiteUrl: string;
  timeout?: number;
}

export interface WorkerExecutionResponse {
  success: boolean;
  output?: string;
  error?: string;
  screenshot?: string;
  executionTime: number;
}

// Database types
export interface CreateTaskData {
  prompt: string;
  websiteUrl: string;
  status: string;
  attempts: number;
  maxAttempts: number;
}

export interface UpdateTaskData {
  status?: string;
  attempts?: number;
  result?: AutomationResult;
}
