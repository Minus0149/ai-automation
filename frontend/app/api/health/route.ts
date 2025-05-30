import { NextResponse } from "next/server";

interface WorkerHealth {
  status: "available" | "error";
  responseTime?: number;
  error?: string;
}

interface SystemHealth {
  status: "healthy" | "unhealthy";
  timestamp: string;
  services: {
    worker: WorkerHealth;
  };
  uptime: number;
}

const startTime = Date.now();

async function checkWorkerHealth(): Promise<WorkerHealth> {
  try {
    const start = Date.now();
    const workerUrl = process.env.WORKER_URL || "http://localhost:8000";

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${workerUrl}/health`, {
      method: "GET",
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    const responseTime = Date.now() - start;

    if (response.ok) {
      return {
        status: "available",
        responseTime,
      };
    } else {
      return {
        status: "error",
        error: `Worker responded with status: ${response.status}`,
      };
    }
  } catch (error) {
    return {
      status: "error",
      error: error instanceof Error ? error.message : "Worker unreachable",
    };
  }
}

export async function GET() {
  try {
    const workerHealth = await checkWorkerHealth();

    const overallStatus: SystemHealth["status"] =
      workerHealth.status === "available" ? "healthy" : "unhealthy";

    const health: SystemHealth = {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      services: {
        worker: workerHealth,
      },
      uptime: Date.now() - startTime,
    };

    const statusCode = overallStatus === "healthy" ? 200 : 503;

    return NextResponse.json(health, { status: statusCode });
  } catch (error) {
    const errorHealth: SystemHealth = {
      status: "unhealthy",
      timestamp: new Date().toISOString(),
      services: {
        worker: { status: "error", error: "Health check failed" },
      },
      uptime: Date.now() - startTime,
    };

    return NextResponse.json(errorHealth, { status: 503 });
  }
}
