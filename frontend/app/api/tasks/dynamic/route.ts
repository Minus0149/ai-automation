import { NextRequest, NextResponse } from "next/server";
import { Database } from "@/lib/shared/utils/db";

export async function POST(request: NextRequest) {
  try {
    const { prompt, websiteUrl, framework, options } = await request.json();

    // Validate required fields
    if (!prompt || !websiteUrl) {
      return NextResponse.json(
        { error: "Prompt and website URL are required" },
        { status: 400 }
      );
    }

    // Validate framework
    if (framework && !["selenium", "seleniumbase"].includes(framework)) {
      return NextResponse.json(
        { error: "Framework must be 'selenium' or 'seleniumbase'" },
        { status: 400 }
      );
    }

    // Create task in database
    const taskData = {
      prompt,
      websiteUrl,
      status: "pending" as const,
      attempts: 0,
      maxAttempts: options?.maxAttempts || 3,
    };

    const task = await Database.createTask(taskData);

    // Add to queue with dynamic automation flag
    const queueData = {
      taskId: task.id,
      prompt,
      websiteUrl,
      framework: framework || "selenium",
      options,
      isDynamic: true,
    };

    // Send to queue
    try {
      const queueResponse = await fetch(
        `${process.env.QUEUE_URL || "http://localhost:3002"}/add-job`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            type: "dynamic_automation",
            data: queueData,
          }),
        }
      );

      if (!queueResponse.ok) {
        throw new Error("Failed to add job to queue");
      }
    } catch (queueError) {
      console.error("Queue error:", queueError);
    }

    return NextResponse.json({
      taskId: task.id,
      status: "pending",
      message: "Dynamic automation task created successfully",
      framework: framework || "selenium",
    });
  } catch (error) {
    console.error("Error creating dynamic automation task:", error);
    return NextResponse.json(
      { error: "Failed to create task" },
      { status: 500 }
    );
  }
}
