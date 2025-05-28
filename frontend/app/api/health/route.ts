import { NextResponse } from "next/server";
import { createLogger } from "@/lib/shared/utils/logger";
import { Database } from "@/lib/shared/utils/db";
import { createClient } from "redis";

const logger = createLogger("health-api");

interface SystemHealth {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  services: {
    database: {
      status: "connected" | "disconnected" | "error";
      responseTime?: number;
      error?: string;
    };
    redis: {
      status: "connected" | "disconnected" | "error";
      responseTime?: number;
      error?: string;
    };
    worker: {
      status: "available" | "unavailable" | "error";
      responseTime?: number;
      error?: string;
    };
  };
  queue: {
    pending: number;
    processing: number;
    completed: number;
    failed: number;
  };
  tasks: {
    total: number;
    successful: number;
    failed: number;
    successRate: number;
  };
  uptime: number;
}

const startTime = Date.now();

async function checkDatabaseHealth(): Promise<
  SystemHealth["services"]["database"]
> {
  try {
    const start = Date.now();
    await Database.getTaskStats();
    const responseTime = Date.now() - start;

    return {
      status: "connected",
      responseTime,
    };
  } catch (error) {
    return {
      status: "error",
      error: error instanceof Error ? error.message : "Unknown database error",
    };
  }
}

async function checkRedisHealth(): Promise<SystemHealth["services"]["redis"]> {
  try {
    const start = Date.now();

    // Upstash Redis configuration
    let clientConfig: any = {};

    const upstashUrl = process.env.UPSTASH_REDIS_REST_URL;
    const upstashToken = process.env.UPSTASH_REDIS_REST_TOKEN;

    if (
      upstashUrl &&
      upstashToken &&
      !upstashUrl.includes("your-upstash-redis-endpoint") &&
      !upstashToken.includes("your_upstash_redis_token")
    ) {
      // Use Upstash Redis configuration
      try {
        const redisUrl = upstashUrl.replace("/rest", "");
        clientConfig = {
          url: `${redisUrl}?token=${upstashToken}`,
          socket: {
            tls: redisUrl.startsWith("rediss://"),
            connectTimeout: 5000,
          },
        };
      } catch (error) {
        logger.error("Invalid Upstash configuration", { error });
        throw error;
      }
    } else {
      // Fallback to traditional Redis
      const redisUrl = process.env.REDIS_URL || process.env.UPSTASH_REDIS_URL;
      if (redisUrl && !redisUrl.includes("your-upstash-redis-endpoint")) {
        clientConfig = {
          url: redisUrl,
          socket: {
            tls: redisUrl.startsWith("rediss://") ? true : false,
            connectTimeout: 5000,
          },
        };
      } else {
        clientConfig = {
          url: `redis://${process.env.REDIS_HOST || "localhost"}:${
            process.env.REDIS_PORT || "6379"
          }`,
          socket: {
            connectTimeout: 5000,
          },
        };
      }
    }

    const client = createClient(clientConfig);
    await client.connect();
    await client.ping();
    const responseTime = Date.now() - start;
    await client.disconnect();

    return {
      status: "connected",
      responseTime,
    };
  } catch (error) {
    return {
      status: "error",
      error: error instanceof Error ? error.message : "Unknown Redis error",
    };
  }
}

async function checkWorkerHealth(): Promise<
  SystemHealth["services"]["worker"]
> {
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

async function getQueueStats() {
  try {
    // Upstash Redis configuration
    let clientConfig: any = {};

    const upstashUrl = process.env.UPSTASH_REDIS_REST_URL;
    const upstashToken = process.env.UPSTASH_REDIS_REST_TOKEN;

    if (upstashUrl && upstashToken) {
      // Use Upstash Redis configuration
      const redisUrl = upstashUrl.replace("/rest", "");
      clientConfig = {
        url: `${redisUrl}?token=${upstashToken}`,
        socket: {
          tls: redisUrl.startsWith("rediss://"),
        },
      };
    } else {
      // Fallback to traditional Redis
      const redisUrl = process.env.REDIS_URL || process.env.UPSTASH_REDIS_URL;
      if (redisUrl) {
        clientConfig = {
          url: redisUrl,
          socket: {
            tls: redisUrl.startsWith("rediss://") ? {} : undefined,
          },
        };
      } else {
        clientConfig = {
          url: `redis://${process.env.REDIS_HOST || "localhost"}:${
            process.env.REDIS_PORT || "6379"
          }`,
        };
      }
    }

    const client = createClient(clientConfig);
    await client.connect();

    // Get queue stats (simplified - would need BullMQ queue instance for detailed stats)
    const queueStats = {
      pending: 0,
      processing: 0,
      completed: 0,
      failed: 0,
    };

    await client.disconnect();
    return queueStats;
  } catch (error) {
    logger.error("Failed to get queue stats:", error);
    return {
      pending: 0,
      processing: 0,
      completed: 0,
      failed: 0,
    };
  }
}

async function getTaskStats() {
  try {
    const stats = await Database.getTaskStats();
    const total = stats.total || 0;
    const successful = stats.successful || 0;
    const failed = stats.failed || 0;
    const successRate = total > 0 ? (successful / total) * 100 : 0;

    return {
      total,
      successful,
      failed,
      successRate: Math.round(successRate * 100) / 100,
    };
  } catch (error) {
    logger.error("Failed to get task stats:", error);
    return {
      total: 0,
      successful: 0,
      failed: 0,
      successRate: 0,
    };
  }
}

export async function GET() {
  try {
    logger.info("Health check requested");

    // Perform all health checks in parallel
    const [databaseHealth, redisHealth, workerHealth, queueStats, taskStats] =
      await Promise.all([
        checkDatabaseHealth(),
        checkRedisHealth(),
        checkWorkerHealth(),
        getQueueStats(),
        getTaskStats(),
      ]);

    // Determine overall system status
    const allServices = [databaseHealth, redisHealth, workerHealth];
    const hasErrors = allServices.some((service) => service.status === "error");
    const hasDisconnected = allServices.some(
      (service) =>
        service.status === "disconnected" || service.status === "unavailable"
    );

    let overallStatus: SystemHealth["status"];
    if (hasErrors) {
      overallStatus = "unhealthy";
    } else if (hasDisconnected) {
      overallStatus = "degraded";
    } else {
      overallStatus = "healthy";
    }

    const health: SystemHealth = {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      services: {
        database: databaseHealth,
        redis: redisHealth,
        worker: workerHealth,
      },
      queue: queueStats,
      tasks: taskStats,
      uptime: Date.now() - startTime,
    };

    const statusCode =
      overallStatus === "healthy"
        ? 200
        : overallStatus === "degraded"
        ? 200
        : 503;

    return NextResponse.json(health, { status: statusCode });
  } catch (error) {
    logger.error("Health check failed:", error);

    const errorHealth: SystemHealth = {
      status: "unhealthy",
      timestamp: new Date().toISOString(),
      services: {
        database: { status: "error", error: "Health check failed" },
        redis: { status: "error", error: "Health check failed" },
        worker: { status: "error", error: "Health check failed" },
      },
      queue: { pending: 0, processing: 0, completed: 0, failed: 0 },
      tasks: { total: 0, successful: 0, failed: 0, successRate: 0 },
      uptime: Date.now() - startTime,
    };

    return NextResponse.json(errorHealth, { status: 503 });
  }
}
