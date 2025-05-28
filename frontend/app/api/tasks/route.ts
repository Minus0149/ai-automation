import { NextRequest, NextResponse } from "next/server";
import { Database } from "@/lib/shared/utils/db";
import { addAutomationJob } from "@/lib/shared/utils/redis";
import { createLogger } from "@/lib/shared/utils/logger";
import { TaskRequest, TaskResponse } from "@/lib/shared/types";

const logger = createLogger("task-api");

// Initialize database on startup
Database.initializeDatabase().catch((error) => {
  logger.error("Failed to initialize database:", error);
});

// Create new automation task
export async function POST(request: NextRequest) {
  try {
    const body: TaskRequest = await request.json();
    const { prompt, websiteUrl, options = {} } = body;

    if (!prompt || !websiteUrl) {
      return NextResponse.json(
        { error: "Prompt and website URL are required" },
        { status: 400 }
      );
    }

    // Validate URL format
    try {
      new URL(websiteUrl);
    } catch {
      return NextResponse.json(
        { error: "Invalid website URL format" },
        { status: 400 }
      );
    }

    logger.info(`Creating new automation task for ${websiteUrl}`, {
      prompt,
      options,
    });

    // Create task in database
    const task = await Database.createTask({
      prompt,
      websiteUrl,
      status: "pending",
      attempts: 0,
      maxAttempts: options.maxAttempts || 3,
    });

    // Add job to queue
    await addAutomationJob({
      taskId: task.id,
      prompt,
      websiteUrl,
      attempt: 1,
      maxAttempts: task.maxAttempts,
    });

    logger.info(`Task created successfully: ${task.id}`);

    const response: TaskResponse = {
      taskId: task.id,
      status: "created",
      message: "Task has been queued for processing",
    };

    return NextResponse.json(response, { status: 201 });
  } catch (error) {
    logger.error("Error creating task:", error);
    return NextResponse.json(
      { error: "Internal server error while creating task" },
      { status: 500 }
    );
  }
}

// List all tasks
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get("page") || "1");
    const limit = parseInt(searchParams.get("limit") || "20");

    if (page < 1 || limit < 1 || limit > 100) {
      return NextResponse.json(
        { error: "Invalid page or limit parameters" },
        { status: 400 }
      );
    }

    const offset = (page - 1) * limit;

    logger.info(`Fetching tasks: page ${page}, limit ${limit}`);

    const tasks = await Database.getTasks(limit, offset);

    return NextResponse.json({
      tasks,
      total: tasks.length,
      page,
      limit,
    });
  } catch (error) {
    logger.error("Error fetching tasks:", error);
    return NextResponse.json(
      { error: "Internal server error while fetching tasks" },
      { status: 500 }
    );
  }
}
