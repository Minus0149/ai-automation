import { NextRequest, NextResponse } from "next/server";
import { Database } from "@/lib/shared/utils/db";
import { createLogger } from "@/lib/shared/utils/logger";

const logger = createLogger("task-detail-api");

// Get task status
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  try {
    if (!id) {
      return NextResponse.json(
        { error: "Task ID is required" },
        { status: 400 }
      );
    }

    logger.info(`Fetching detailed status for task: ${id}`);

    // Get task with all attempt details
    let taskWithAttempts;
    try {
      taskWithAttempts = await Database.getTaskWithAttempts(id);
    } catch (dbError) {
      logger.error("Database error in getTaskWithAttempts:", dbError);
      return NextResponse.json(
        {
          error: "Database error while fetching task",
          details: dbError instanceof Error ? dbError.message : String(dbError),
          taskId: id,
        },
        { status: 500 }
      );
    }

    if (!taskWithAttempts) {
      logger.info(`Task not found: ${id}`);
      return NextResponse.json({ error: "Task not found" }, { status: 404 });
    }

    logger.info(`Task found, processing response for: ${id}`);

    // Safely extract attempts and logs arrays
    const attempts = Array.isArray(taskWithAttempts.attempts)
      ? taskWithAttempts.attempts
      : [];
    const logs = Array.isArray(taskWithAttempts.logs)
      ? taskWithAttempts.logs
      : [];

    logger.info(`Task has ${attempts.length} attempts and ${logs.length} logs`);

    // Format the response with all attempt details
    const response = {
      task: {
        id: taskWithAttempts.id || id,
        prompt: taskWithAttempts.prompt || "",
        websiteUrl: taskWithAttempts.websiteUrl || "",
        status: taskWithAttempts.status || "pending",
        attempts: attempts.length,
        maxAttempts: taskWithAttempts.maxAttempts || 3,
        createdAt: taskWithAttempts.createdAt || new Date(),
        updatedAt: taskWithAttempts.updatedAt || new Date(),
        completedAt: (taskWithAttempts as any).completedAt || null,
        executionTime: taskWithAttempts.result?.executionTime || null,
        finalCode: taskWithAttempts.result?.generatedCode || null,
        finalResult:
          taskWithAttempts.execution_result || taskWithAttempts.result,
        finalError: taskWithAttempts.result?.error || null,
      },
      attempts: attempts.map((attempt: any) => ({
        attemptNumber: attempt.attempt_number || 1,
        status: attempt.status || "unknown",
        generatedCode: attempt.generated_code || "",
        executionResult: attempt.execution_result || null,
        errorMessage: attempt.error_message || "",
        screenshots: attempt.screenshots || [],
        executionTime: attempt.execution_time_ms || 0,
        createdAt: attempt.created_at || new Date(),
      })),
      logs: logs.map((log: any) => ({
        level: log.level || "info",
        message: log.message || "",
        source: log.source || "unknown",
        timestamp: log.timestamp || new Date(),
      })),
    };

    logger.info(`Returning successful response for task: ${id}`);
    return NextResponse.json(response);
  } catch (error) {
    logger.error("Unexpected error in API route:", error);

    // Return a more detailed error for debugging
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    const errorStack = error instanceof Error ? error.stack : "No stack trace";

    return NextResponse.json(
      {
        error: "Internal server error while fetching task status",
        details: errorMessage,
        stack: errorStack,
        taskId: id,
      },
      { status: 500 }
    );
  }
}
