import { Queue } from "bullmq";
import { createClient } from "redis";
import { AutomationJob } from "../types";
import { createLogger } from "./logger";

const logger = createLogger("redis");

// Upstash Redis configuration with better error handling
const getUpstashRedisConnection = () => {
  // For Upstash, we can use either REST API or Redis protocol
  const upstashUrl = process.env.UPSTASH_REDIS_REST_URL;
  const upstashToken = process.env.UPSTASH_REDIS_REST_TOKEN;

  if (
    upstashUrl &&
    upstashToken &&
    !upstashUrl.includes("your-upstash-redis-endpoint") &&
    !upstashToken.includes("your_upstash_redis_token")
  ) {
    // Use Upstash REST API (recommended for serverless)
    try {
      const url = new URL(upstashUrl);
      return {
        host: url.hostname,
        port: url.port ? parseInt(url.port) : 6379,
        username: "default",
        password: upstashToken,
        tls: upstashUrl.startsWith("rediss://") ? {} : undefined,
      };
    } catch (error) {
      logger.error("Invalid Upstash URL format, falling back to local Redis", {
        upstashUrl,
        error,
      });
    }
  }

  // Fallback to traditional Redis URL
  const redisUrl = process.env.REDIS_URL || process.env.UPSTASH_REDIS_URL;
  if (redisUrl && !redisUrl.includes("your-upstash-redis-endpoint")) {
    try {
      const url = new URL(redisUrl);
      return {
        host: url.hostname,
        port: parseInt(url.port) || 6379,
        username: url.username || "default",
        password: url.password,
        tls: redisUrl.startsWith("rediss://") ? {} : undefined,
      };
    } catch (error) {
      logger.error("Invalid Redis URL format, falling back to local Redis", {
        redisUrl,
        error,
      });
    }
  }

  // Local Redis fallback
  logger.info("Using local Redis fallback configuration");
  return {
    host: process.env.REDIS_HOST || "localhost",
    port: parseInt(process.env.REDIS_PORT || "6379"),
    password: process.env.REDIS_PASSWORD,
  };
};

const redisConnection = getUpstashRedisConnection();

export const automationQueue = new Queue("automation", {
  connection: redisConnection,
});

export async function addAutomationJob(jobData: AutomationJob): Promise<void> {
  try {
    await automationQueue.add("process-automation", jobData, {
      attempts: 3,
      backoff: {
        type: "exponential",
        delay: 2000,
      },
    });
  } catch (error) {
    logger.error("Failed to add automation job", { error, jobData });
    throw error;
  }
}

export function createRedisClient() {
  const connection = getUpstashRedisConnection();

  // Create Redis client with Upstash configuration
  const upstashUrl = process.env.UPSTASH_REDIS_REST_URL;
  const upstashToken = process.env.UPSTASH_REDIS_REST_TOKEN;

  if (
    upstashUrl &&
    upstashToken &&
    !upstashUrl.includes("your-upstash-redis-endpoint") &&
    !upstashToken.includes("your_upstash_redis_token")
  ) {
    try {
      // Use Upstash Redis URL format
      const cleanUrl = upstashUrl.replace("/rest", "");
      return createClient({
        url: `${cleanUrl}?token=${upstashToken}`,
        socket: {
          tls: cleanUrl.startsWith("rediss://"),
          connectTimeout: 10000,
        },
      });
    } catch (error) {
      logger.error("Failed to create Upstash Redis client, falling back", {
        error,
      });
    }
  }

  // Fallback to standard Redis URL
  const redisUrl =
    process.env.REDIS_URL ||
    process.env.UPSTASH_REDIS_URL ||
    "redis://localhost:6379";

  return createClient({
    url: redisUrl,
    socket: {
      tls: redisUrl.startsWith("rediss://") ? true : false,
      connectTimeout: 10000,
    },
  });
}
