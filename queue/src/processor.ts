import express, { Request, Response, RequestHandler } from "express";
import cors from "cors";
import * as dotenv from "dotenv";
import * as path from "path";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import OpenAI from "openai";

// Database and utilities
import { db } from "./database.js";
import { createGeminiService, GeminiService } from "./gemini-service.js";

// Load environment variables
dotenv.config({ path: path.join(__dirname, "..", ".env") });
dotenv.config({ path: path.join(process.cwd(), ".env") });

// Environment validation and loading
const ENV_PATHS = [
  path.join(__dirname, "..", ".env"),
  path.join(process.cwd(), ".env"),
  path.join(__dirname, "..", "queue-env.example"),
];

console.log("🔍 Looking for environment files...");
for (const envPath of ENV_PATHS) {
  try {
    dotenv.config({ path: envPath });
    console.log(`✅ Loading env from: ${envPath}`);
  } catch (error) {
    console.log(`❌ Failed to load env from: ${envPath}`);
  }
}

// Enhanced environment configuration
interface Config {
  hasGemini: boolean;
  hasOpenAI: boolean;
  geminiKeyLength: number;
  openaiKeyLength: number;
  gemini20Model: string;
  gemini25Model: string;
  openaiModel: string;
  gemini20ContextCaching: boolean;
  gemini25ContextCaching: boolean;
  defaultModel: string;
  workerUrl: string;
  redisHost: string;
  dbHost: string;
  workingDir: string;
  port: number;
}

const config: Config = {
  hasGemini: !!process.env.GEMINI_API_KEY,
  hasOpenAI: !!process.env.OPENAI_API_KEY,
  geminiKeyLength: process.env.GEMINI_API_KEY?.length || 0,
  openaiKeyLength: process.env.OPENAI_API_KEY?.length || 0,
  gemini20Model: process.env.GEMINI_2_0_MODEL || "gemini-2.0-flash-exp",
  gemini25Model: process.env.GEMINI_2_5_MODEL || "gemini-2.5-flash-exp",
  openaiModel: process.env.OPENAI_MODEL || "gpt-4o-mini",
  gemini20ContextCaching: process.env.GEMINI_2_0_USE_CONTEXT_CACHING === "true",
  gemini25ContextCaching: process.env.GEMINI_2_5_USE_CONTEXT_CACHING === "true",
  defaultModel: process.env.DEFAULT_MODEL || "gpt-4o-mini",
  workerUrl: process.env.WORKER_URL || "http://localhost:8000",
  redisHost: process.env.REDIS_HOST || "localhost",
  dbHost: process.env.DB_HOST || "localhost",
  workingDir: __dirname,
  port: parseInt(process.env.QUEUE_PORT || "3002"),
};

console.log("🔧 Environment loaded:", {
  hasGemini: config.hasGemini,
  hasOpenAI: config.hasOpenAI,
  geminiKeyLength: config.geminiKeyLength,
  openaiKeyLength: config.openaiKeyLength,
  models: {
    gemini20: config.gemini20Model,
    gemini25: config.gemini25Model,
    openai: config.openaiModel,
  },
  defaultModel: config.defaultModel,
  port: config.port,
});

// Initialize AI services
let geminiService: GeminiService | null = null;
let openaiClient: OpenAI | null = null;

if (config.hasGemini) {
  try {
    geminiService = createGeminiService();
    console.log("✅ Gemini AI service initialized successfully");
  } catch (error) {
    console.error("❌ Failed to initialize Gemini AI service:", error);
  }
}

if (config.hasOpenAI) {
  try {
    openaiClient = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
    console.log("✅ OpenAI service initialized successfully");
  } catch (error) {
    console.error("❌ Failed to initialize OpenAI service:", error);
  }
}

if (!config.hasGemini && !config.hasOpenAI) {
  console.error(
    "❌ No AI service available. Please set GEMINI_API_KEY or OPENAI_API_KEY environment variable."
  );
}

// Simple in-memory job queue (Redis replacement)
interface Job {
  id: string;
  type: string;
  data: any;
  status: "pending" | "processing" | "completed" | "failed" | "awaiting_chat";
  createdAt: Date;
  completedAt?: Date;
  error?: string;
  result?: any;
}

class SimpleJobQueue {
  private jobs = new Map<string, Job>();
  private processing = false;
  private maxConcurrent = 2;
  private currentlyProcessing = 0;

  async add(type: string, data: any): Promise<string> {
    const jobId = uuidv4();
    const job: Job = {
      id: jobId,
      type,
      data,
      status: "pending",
      createdAt: new Date(),
    };

    this.jobs.set(jobId, job);
    console.log(`📝 Job ${jobId} added to queue`);

    // Start processing if not already running
    if (!this.processing) {
      this.startProcessing();
    }

    return jobId;
  }

  private async startProcessing() {
    this.processing = true;
    console.log("🔄 Starting job processing...");

    while (
      this.jobs.size > 0 &&
      this.currentlyProcessing < this.maxConcurrent
    ) {
      const pendingJobs = Array.from(this.jobs.values()).filter(
        (job) => job.status === "pending"
      );

      if (pendingJobs.length === 0) {
        break;
      }

      const job = pendingJobs[0];
      this.currentlyProcessing++;

      // Process job asynchronously
      this.processJob(job).finally(() => {
        this.currentlyProcessing--;
      });

      // Small delay to prevent overwhelming
      await new Promise((resolve) => setTimeout(resolve, 100));
    }

    this.processing = false;
  }

  private async processJob(job: Job) {
    try {
      console.log(`⚡ Processing job ${job.id} (${job.type})`);
      job.status = "processing";

      if (job.type === "automation") {
        await this.processAutomationJob(job);
      }

      job.status = "completed";
      job.completedAt = new Date();
      console.log(`✅ Job ${job.id} completed successfully`);
    } catch (error) {
      console.error(`❌ Job ${job.id} failed:`, error);
      job.status = "failed";
      job.error = error instanceof Error ? error.message : String(error);
      job.completedAt = new Date();
    }

    // Clean up old jobs after 1 hour
    setTimeout(() => {
      this.jobs.delete(job.id);
    }, 60 * 60 * 1000);
  }

  // Enhanced automation job processing with retry logic and chat
  private async processAutomationJob(job: Job) {
    const {
      taskId,
      prompt,
      websiteUrl,
      maxAttempts = 3,
      model = "gemini",
    } = job.data;
    let lastError: Error | null = null;
    let lastCode: string = "";

    console.log(
      `🚀 Starting automation task ${taskId} for ${websiteUrl} using ${model}`
    );

    try {
      // Update task status
      await db.updateTaskStatus(taskId, "processing");

      for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
          console.log(
            `⚡ Executing code for task ${taskId} (attempt ${attempt}) with ${model}`
          );

          // Store attempt details
          await db.createAttempt({
            taskId,
            attemptNumber: attempt,
            status: "processing",
          });

          // Generate code using selected model
          const generatedCode = await generateSeleniumCode(
            prompt,
            websiteUrl,
            model as "gemini-2.0-flash" | "gemini-2.5-preview" | "gpt-4o-mini"
          );
          lastCode = generatedCode;

          // Update attempt with generated code
          await db.createAttempt({
            taskId,
            attemptNumber: attempt,
            status: "executing",
            generatedCode,
          });

          // Execute the code
          const executionResult = await executeCode(generatedCode, websiteUrl);

          // Update attempt with execution result
          await db.createAttempt({
            taskId,
            attemptNumber: attempt,
            status: executionResult.success ? "completed" : "failed",
            generatedCode,
            executionResult,
            errorMessage: executionResult.error,
            screenshots: executionResult.screenshots,
            executionTime: executionResult.execution_time,
          });

          if (executionResult.success) {
            // Task completed successfully
            await db.updateTaskStatus(taskId, "completed", {
              generatedCode,
              executionResult,
              attemptCount: attempt,
              executionTime: executionResult.execution_time,
            });

            console.log(
              `✅ Task ${taskId} completed successfully on attempt ${attempt}`
            );
            return;
          } else {
            lastError = new Error(
              executionResult.error || "Unknown execution error"
            );
            console.log(
              `❌ Task ${taskId} failed on attempt ${attempt}: ${lastError.message}`
            );

            // Add delay before retry
            if (attempt < maxAttempts) {
              const retryDelay = Math.min(
                1000 * Math.pow(2, attempt - 1),
                10000
              );
              console.log(`⏳ Retrying task ${taskId} in ${retryDelay}ms...`);
              await new Promise((resolve) => setTimeout(resolve, retryDelay));
            }
          }
        } catch (error) {
          lastError = error instanceof Error ? error : new Error(String(error));
          console.error(`❌ Error in attempt ${attempt}:`, lastError);

          // Store failed attempt
          await db.createAttempt({
            taskId,
            attemptNumber: attempt,
            status: "failed",
            errorMessage: lastError.message,
          });

          if (attempt < maxAttempts) {
            const retryDelay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
            console.log(`⏳ Retrying task ${taskId} in ${retryDelay}ms...`);
            await new Promise((resolve) => setTimeout(resolve, retryDelay));
          }
        }
      }

      // All attempts failed - set status to awaiting_chat for manual intervention
      await db.updateTaskStatus(taskId, "awaiting_chat", {
        errorMessage: lastError?.message || "All attempts failed",
        attemptCount: maxAttempts,
        lastCode,
        chatEnabled: true,
      });

      console.log(
        `❌ Task ${taskId} failed after ${maxAttempts} attempts - chat enabled for debugging`
      );
    } catch (error) {
      console.error(`❌ Critical error processing task ${taskId}:`, error);
      await db.updateTaskStatus(taskId, "failed", {
        errorMessage: error instanceof Error ? error.message : String(error),
      });
    }
  }

  getJob(jobId: string): Job | undefined {
    return this.jobs.get(jobId);
  }

  getAllJobs(): Job[] {
    return Array.from(this.jobs.values());
  }
}

// Global queue instance
const jobQueue = new SimpleJobQueue();

// Enhanced website content fetching with caching
async function fetchWebsiteContent(url: string): Promise<string> {
  if (geminiService) {
    return await geminiService.fetchWebsiteContent(url);
  }

  // Fallback: simple fetch for OpenAI
  try {
    console.log(`🌐 Fetching content from: ${url}`);
    const response = await axios.get(url, {
      timeout: 15000,
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      },
    });
    return response.data.substring(0, 5000); // Limit content for OpenAI
  } catch (error) {
    console.error(`❌ Failed to fetch website content:`, error);
    return `Failed to fetch website content from ${url}`;
  }
}

// Enhanced code generation with multi-model support
async function generateSeleniumCode(
  prompt: string,
  websiteUrl: string,
  model:
    | "gemini-2.0-flash"
    | "gemini-2.5-preview"
    | "gpt-4o-mini" = "gpt-4o-mini"
): Promise<string> {
  const websiteContent = await fetchWebsiteContent(websiteUrl);

  if (
    (model === "gemini-2.0-flash" || model === "gemini-2.5-preview") &&
    geminiService
  ) {
    try {
      console.log(`🤖 Generating code with ${model} for: ${websiteUrl}`);

      // Use appropriate Gemini model configuration
      const modelName =
        model === "gemini-2.0-flash"
          ? config.gemini20Model
          : config.gemini25Model;
      const useContextCaching =
        model === "gemini-2.0-flash"
          ? config.gemini20ContextCaching
          : config.gemini25ContextCaching;

      // Generate with specific Gemini model
      return await geminiService.generateSeleniumCodeWithModel(
        prompt,
        websiteUrl,
        modelName,
        useContextCaching
      );
    } catch (error) {
      console.error(`❌ ${model} generation failed:`, error);
      if (openaiClient) {
        console.log("🔄 Falling back to OpenAI...");
        return await generateWithOpenAI(prompt, websiteContent);
      }
      throw error;
    }
  } else if (model === "gpt-4o-mini" && openaiClient) {
    console.log(`🤖 Generating code with ${model} for: ${websiteUrl}`);
    return await generateWithOpenAI(prompt, websiteContent);
  } else {
    // Auto-fallback to default model
    if (config.defaultModel === "gpt-4o-mini" && openaiClient) {
      console.log(
        `🤖 Using ${config.defaultModel} (auto-selected) for: ${websiteUrl}`
      );
      return await generateWithOpenAI(prompt, websiteContent);
    } else if (geminiService) {
      const fallbackModel =
        config.defaultModel === "gemini-2.5-preview"
          ? config.gemini25Model
          : config.gemini20Model;
      console.log(
        `🤖 Using ${config.defaultModel} (auto-selected) for: ${websiteUrl}`
      );
      return await geminiService.generateSeleniumCodeWithModel(
        prompt,
        websiteUrl,
        fallbackModel,
        config.gemini20ContextCaching
      );
    }
  }

  throw new Error("No AI service available for code generation");
}

// OpenAI code generation function
async function generateWithOpenAI(
  prompt: string,
  websiteContent: string
): Promise<string> {
  if (!openaiClient) {
    throw new Error("OpenAI client not initialized");
  }

  const enhancedPrompt = `You are an expert Selenium WebDriver automation engineer. Generate ONLY clean, executable Python code.

CRITICAL REQUIREMENTS:
1. Generate ONLY Python code - NO markdown, explanations, or comments
2. Use explicit waits (WebDriverWait) instead of time.sleep()
3. Use reliable selectors from the website analysis
4. Handle exceptions with try-catch blocks
5. Verify elements exist before interaction
6. Take screenshots on errors for debugging
7. Return meaningful results

TASK TO AUTOMATE: ${prompt}

WEBSITE CONTEXT: ${websiteContent.substring(0, 3000)}

Generate precise Selenium Python code:`;

  try {
    const response = await openaiClient.chat.completions.create({
      model: config.openaiModel,
      messages: [{ role: "user", content: enhancedPrompt }],
      temperature: 0.1,
      max_tokens: 4000,
    });

    const generatedCode = response.choices[0]?.message?.content || "";

    if (!generatedCode || generatedCode.trim().length === 0) {
      throw new Error("OpenAI returned empty response");
    }

    // Clean up any remaining markdown formatting
    const cleanCode = generatedCode
      .replace(/```python\n?/g, "")
      .replace(/```\n?/g, "")
      .replace(/^#+.*$/gm, "")
      .trim();

    console.log(`✅ Generated ${cleanCode.length} characters with OpenAI`);
    return cleanCode;
  } catch (error) {
    console.error("❌ OpenAI generation failed:", error);
    throw error;
  }
}

// Chat functionality for fine-tuning
async function generateChatResponse(
  message: string,
  taskContext: any,
  model:
    | "gemini-2.0-flash"
    | "gemini-2.5-preview"
    | "gpt-4o-mini" = "gpt-4o-mini"
): Promise<string> {
  const contextPrompt = `You are helping debug and improve a failed web automation task.

TASK CONTEXT:
- Original Prompt: ${taskContext.prompt}
- Website: ${taskContext.websiteUrl}
- Attempts: ${taskContext.attempts}
- Last Error: ${taskContext.lastError}
- Generated Code: ${taskContext.lastCode?.substring(0, 1000)}...

USER MESSAGE: ${message}

Provide helpful suggestions to fix the automation. Be specific and actionable.`;

  if (
    (model === "gemini-2.0-flash" || model === "gemini-2.5-preview") &&
    geminiService
  ) {
    try {
      // Create a simple chat method in GeminiService or use direct generation
      const { GoogleGenerativeAI } = require("@google/generative-ai");
      const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
      const modelName =
        model === "gemini-2.0-flash"
          ? config.gemini20Model
          : config.gemini25Model;
      const geminiModel = genAI.getGenerativeModel({
        model: modelName,
      });
      const result = await geminiModel.generateContent(contextPrompt);
      return result.response.text();
    } catch (error) {
      console.error(`❌ ${model} chat failed:`, error);
      if (openaiClient) {
        return await generateChatWithOpenAI(contextPrompt);
      }
      throw error;
    }
  } else if (model === "gpt-4o-mini" && openaiClient) {
    return await generateChatWithOpenAI(contextPrompt);
  }

  throw new Error("No AI service available for chat");
}

async function generateChatWithOpenAI(prompt: string): Promise<string> {
  if (!openaiClient) {
    throw new Error("OpenAI client not initialized");
  }

  const response = await openaiClient.chat.completions.create({
    model: config.openaiModel,
    messages: [{ role: "user", content: prompt }],
    temperature: 0.7,
    max_tokens: 1000,
  });

  return (
    response.choices[0]?.message?.content ||
    "Sorry, I couldn't generate a response."
  );
}

// Execute code using worker
async function executeCode(code: string, websiteUrl: string): Promise<any> {
  try {
    console.log(`🔧 Executing code for ${websiteUrl}`);

    const response = await axios.post(
      `${config.workerUrl}/execute`,
      {
        code,
        website_url: websiteUrl,
        timeout: 60,
      },
      {
        timeout: 70000,
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error("❌ Code execution failed:", error);

    if (axios.isAxiosError(error)) {
      return {
        success: false,
        error: `Worker error: ${error.message}`,
        logs: [
          {
            level: "error",
            message: `Worker request failed: ${error.message}`,
            timestamp: new Date().toISOString(),
          },
        ],
        screenshots: [],
        execution_time: 0,
      };
    }

    return {
      success: false,
      error: `Execution error: ${
        error instanceof Error ? error.message : String(error)
      }`,
      logs: [
        {
          level: "error",
          message: `Execution failed: ${
            error instanceof Error ? error.message : String(error)
          }`,
          timestamp: new Date().toISOString(),
        },
      ],
      screenshots: [],
      execution_time: 0,
    };
  }
}

// Initialize database connection
async function initializeQueue() {
  try {
    console.log("🔗 Connecting to database...");
    await db.connect();
    console.log("✅ Database connection established");

    // Initialize Express server for API endpoints
    const app = express();
    app.use(cors());
    app.use(express.json());

    // Health check endpoint
    app.get("/health", (req, res) => {
      res.json({
        status: "healthy",
        gemini: config.hasGemini,
        openai: config.hasOpenAI,
        contextCaching: config.gemini20ContextCaching,
        database: "connected",
        timestamp: new Date().toISOString(),
        availableModels: {
          gemini20: config.gemini20Model,
          gemini25: config.gemini25Model,
          openai: config.openaiModel,
        },
      });
    });

    // Get available models
    app.get("/models", (req, res) => {
      const models = [];
      if (config.hasGemini) {
        models.push({
          provider: "gemini-2.0-flash",
          model: config.gemini20Model,
          name: "Gemini 2.0 Flash",
          features: ["context_caching", "enhanced_analysis"],
        });
        models.push({
          provider: "gemini-2.5-preview",
          model: config.gemini25Model,
          name: "Gemini 2.5 Preview",
          features: ["latest_model", "enhanced_reasoning"],
        });
      }
      if (config.hasOpenAI) {
        models.push({
          provider: "gpt-4o-mini",
          model: config.openaiModel,
          name: "GPT-4o Mini",
          features: ["reliable", "fast"],
        });
      }
      res.json({
        models,
        defaultModel: config.defaultModel,
      });
    });

    // Create task endpoint with model selection
    app.post("/tasks", (async (req, res) => {
      try {
        const { prompt, websiteUrl, model = config.defaultModel } = req.body;

        if (!prompt || !websiteUrl) {
          return res.status(400).json({
            error: "Missing required fields: prompt and websiteUrl",
          });
        }

        // Validate model selection
        if (
          (model === "gemini-2.0-flash" || model === "gemini-2.5-preview") &&
          !config.hasGemini
        ) {
          return res.status(400).json({
            error:
              "Gemini models not available. Please configure GEMINI_API_KEY.",
          });
        }
        if (model === "gpt-4o-mini" && !config.hasOpenAI) {
          return res.status(400).json({
            error:
              "OpenAI model not available. Please configure OPENAI_API_KEY.",
          });
        }

        const taskId = uuidv4();

        // Create task in database
        await db.createTask({
          taskId,
          prompt,
          websiteUrl,
          maxAttempts: 3,
          // model will be stored in task metadata/result field if not directly supported
        });

        // Add job to queue
        const jobId = await jobQueue.add("automation", {
          taskId,
          prompt,
          websiteUrl,
          maxAttempts: 3,
          model,
        });

        res.json({
          taskId,
          jobId,
          status: "queued",
          model,
          message: `Task created and queued for processing with ${model}`,
        });
      } catch (error) {
        console.error("Error creating task:", error);
        res.status(500).json({
          error: "Failed to create task",
          details: error instanceof Error ? error.message : String(error),
        });
      }
    }) as RequestHandler);

    // Get task status endpoint
    app.get("/tasks/:taskId", (async (req, res) => {
      try {
        const { taskId } = req.params;
        const task = await db.getTask(taskId);

        if (!task) {
          return res.status(404).json({ error: "Task not found" });
        }

        res.json(task);
      } catch (error) {
        console.error("Error fetching task:", error);
        res.status(500).json({
          error: "Failed to fetch task",
          details: error instanceof Error ? error.message : String(error),
        });
      }
    }) as RequestHandler);

    // Queue status endpoint
    app.get("/queue/status", (req, res) => {
      const jobs = jobQueue.getAllJobs();
      res.json({
        totalJobs: jobs.length,
        pending: jobs.filter((j) => j.status === "pending").length,
        processing: jobs.filter((j) => j.status === "processing").length,
        completed: jobs.filter((j) => j.status === "completed").length,
        failed: jobs.filter((j) => j.status === "failed").length,
        jobs: jobs.slice(-10), // Return last 10 jobs
      });
    });

    // Chat endpoint for task debugging
    app.post("/tasks/:taskId/chat", (async (req, res) => {
      try {
        const { taskId } = req.params;
        const { message, model = "gemini" } = req.body;

        if (!message) {
          return res.status(400).json({ error: "Message is required" });
        }

        // Get task details
        const task = await db.getTask(taskId);
        if (!task) {
          return res.status(404).json({ error: "Task not found" });
        }

        // Get task context for chat
        const taskContext = {
          prompt: task.prompt,
          websiteUrl: task.websiteUrl,
          attempts: task.attempts || 0,
          lastError: task.result?.errorMessage || "Unknown error",
          lastCode: task.result?.lastCode || "",
        };

        // Generate chat response
        const chatResponse = await generateChatResponse(
          message,
          taskContext,
          model as "gemini-2.0-flash" | "gemini-2.5-preview" | "gpt-4o-mini"
        );

        // Store chat interaction
        await db.createAttempt({
          taskId,
          attemptNumber: (task.attempts || 0) + 1,
          status: "chat_interaction",
          generatedCode: `Chat: ${message}`,
          executionResult: { chatResponse },
        });

        res.json({
          response: chatResponse,
          model,
          timestamp: new Date().toISOString(),
        });
      } catch (error) {
        console.error("Error in chat:", error);
        res.status(500).json({
          error: "Failed to generate chat response",
          details: error instanceof Error ? error.message : String(error),
        });
      }
    }) as RequestHandler);

    // Continue task with refined prompt
    app.post("/tasks/:taskId/continue", (async (req, res) => {
      try {
        const { taskId } = req.params;
        const { refinedPrompt, model } = req.body;

        if (!refinedPrompt) {
          return res.status(400).json({ error: "Refined prompt is required" });
        }

        const task = await db.getTask(taskId);
        if (!task) {
          return res.status(404).json({ error: "Task not found" });
        }

        // Update task status and continue with refined prompt
        await db.updateTaskStatus(taskId, "processing");

        const jobId = await jobQueue.add("automation", {
          taskId,
          prompt: refinedPrompt,
          websiteUrl: task.websiteUrl,
          maxAttempts: 3,
          model: model || task.model || "gemini",
          isRefinedAttempt: true,
        });

        res.json({
          message: "Task continued with refined prompt",
          jobId,
          taskId,
          model: model || task.model,
        });
      } catch (error) {
        console.error("Error continuing task:", error);
        res.status(500).json({
          error: "Failed to continue task",
          details: error instanceof Error ? error.message : String(error),
        });
      }
    }) as RequestHandler);

    // Try different ports to avoid conflicts
    let PORT = config.port;
    const maxPortAttempts = 10;
    let portAttempts = 0;

    const startServer = () => {
      const server = app.listen(PORT, () => {
        console.log(`🚀 Queue processor API listening on port ${PORT}`);
      });

      server.on("error", (error: any) => {
        if (error.code === "EADDRINUSE" && portAttempts < maxPortAttempts) {
          portAttempts++;
          PORT = config.port + portAttempts;
          console.log(`⚠️  Port ${PORT - 1} in use, trying port ${PORT}...`);
          setTimeout(startServer, 1000);
        } else {
          console.error(`❌ Failed to start server on port ${PORT}:`, error);
          process.exit(1);
        }
      });
    };

    startServer();

    console.log("📝 Queue processor ready - listening for jobs...");
    console.log("🔄 Starting simple queue processing...");
    console.log("🔄 Simple queue processor started");
    console.log("🚀 Queue processor started");
  } catch (error) {
    console.error("❌ Failed to initialize queue processor:", error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on("SIGTERM", async () => {
  console.log("Shutting down queue processor...");
  await db.disconnect();
  process.exit(0);
});

process.on("SIGINT", async () => {
  console.log("Shutting down queue processor...");
  await db.disconnect();
  process.exit(0);
});

// Start the queue processor
initializeQueue().catch((error) => {
  console.error("❌ Failed to start queue processor:", error);
  process.exit(1);
});
