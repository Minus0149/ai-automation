import express, {
  Request,
  Response,
  NextFunction,
  RequestHandler,
} from "express";
import cors from "cors";
import { db } from "./database";

const app = express();

// Middleware
app.use(express.json({ limit: "10mb" }));
app.use(
  cors({
    origin: process.env.CORS_ORIGINS?.split(",") || ["http://localhost:3000"],
    credentials: true,
  })
);

// Health check endpoint
app.get("/health", async (req: Request, res: Response) => {
  try {
    // Test database connection
    await db.query("SELECT 1");
    res.json({
      status: "healthy",
      timestamp: new Date().toISOString(),
      services: {
        database: "connected",
        api: "running",
      },
    });
  } catch (error) {
    res.status(503).json({
      status: "unhealthy",
      error: "Database connection failed",
      timestamp: new Date().toISOString(),
    });
  }
});

// Create a new automation task
app.post("/jobs", (async (req: Request, res: Response) => {
  try {
    const {
      taskId,
      prompt,
      websiteUrl,
      maxAttempts = 3,
      userId,
      sessionId,
    } = req.body;

    if (!taskId || !prompt || !websiteUrl) {
      return res.status(400).json({
        error: "Missing required fields: taskId, prompt, websiteUrl",
      });
    }

    // Create task in database
    const task = await db.createTask({
      taskId,
      prompt,
      websiteUrl,
      maxAttempts,
      userId,
      sessionId,
    });

    // Add to simple queue (will be processed by processor)
    console.log(`📝 Task ${taskId} created and queued for processing`);

    res.json({
      success: true,
      message: "Job added to queue",
      taskId,
      task,
    });
  } catch (error: any) {
    console.error("Error creating job:", error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
}) as RequestHandler);

// Get task status
app.get("/tasks/:taskId", (async (req: Request, res: Response) => {
  try {
    const { taskId } = req.params;
    const task = await db.getTask(taskId);

    if (!task) {
      return res.status(404).json({ error: "Task not found" });
    }

    res.json(task);
  } catch (error: any) {
    console.error("Error fetching task:", error);
    res.status(500).json({ error: error.message });
  }
}) as RequestHandler);

// Get all tasks
app.get("/tasks", async (req: Request, res: Response) => {
  try {
    const limit = parseInt(req.query.limit as string) || 50;
    const offset = parseInt(req.query.offset as string) || 0;

    const tasks = await db.getTasks(limit, offset);
    res.json(tasks);
  } catch (error: any) {
    console.error("Error fetching tasks:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get task logs
app.get("/tasks/:taskId/logs", async (req: Request, res: Response) => {
  try {
    const { taskId } = req.params;
    const logs = await db.getTaskLogs(taskId);
    res.json(logs);
  } catch (error: any) {
    console.error("Error fetching task logs:", error);
    res.status(500).json({ error: error.message });
  }
});

// Delete a task
app.delete("/tasks/:taskId", (async (req: Request, res: Response) => {
  try {
    const { taskId } = req.params;

    // Check if task exists
    const task = await db.getTask(taskId);
    if (!task) {
      return res.status(404).json({ error: "Task not found" });
    }

    // Delete task (you'll need to add this method to DatabaseManager)
    await db.query("DELETE FROM automation_tasks WHERE task_id = $1", [taskId]);
    await db.query("DELETE FROM automation_logs WHERE task_id = $1", [taskId]);

    res.json({ message: "Task deleted successfully" });
  } catch (error: any) {
    console.error("Error deleting task:", error);
    res.status(500).json({ error: error.message });
  }
}) as RequestHandler);

// Error handling middleware
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  console.error("Unhandled error:", err);
  res.status(500).json({
    error: "Internal server error",
    message: err.message,
  });
});

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    error: "Not found",
    path: req.path,
  });
});

export default app;
