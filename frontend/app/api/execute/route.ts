import { NextRequest, NextResponse } from "next/server";
import { createLogger } from "@/lib/shared/utils/logger";

const logger = createLogger("execute-api");

export async function POST(request: NextRequest) {
  try {
    const { code, websiteUrl, timeout = 60 } = await request.json();

    if (!code || !websiteUrl) {
      return NextResponse.json(
        { error: "Code and website URL are required" },
        { status: 400 }
      );
    }

    logger.info(`Executing code for website: ${websiteUrl}`);

    // Forward request to Python worker
    const workerUrl = process.env.WORKER_URL || "http://localhost:8000";
    const response = await fetch(`${workerUrl}/execute`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
        website_url: websiteUrl,
        timeout,
      }),
    });

    if (!response.ok) {
      throw new Error(`Worker responded with status: ${response.status}`);
    }

    const result = await response.json();

    logger.info(`Code execution completed: success=${result.success}`);

    return NextResponse.json(result);
  } catch (error) {
    logger.error("Error executing code:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
        logs: [],
        screenshots: [],
        executionTime: 0,
      },
      { status: 500 }
    );
  }
}
