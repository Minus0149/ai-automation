import { Queue } from "bullmq";
import { createClient } from "redis";
import { AutomationJob } from "../types";
import { createLogger } from "./logger";

const logger = createLogger("redis");

const redisConnection = {
  host: process.env.REDIS_HOST || "localhost",
  port: parseInt(process.env.REDIS_PORT || "6379"),
  password: process.env.REDIS_PASSWORD,
};

export const automationQueue = new Queue("automation", {
  connection: redisConnection,
});

export async function addAutomationJob(jobData: AutomationJob): Promise<void> {
  await automationQueue.add("process-automation", jobData, {
    attempts: 3,
    backoff: {
      type: "exponential",
      delay: 2000,
    },
  });
}

export function createRedisClient() {
  return createClient({
    url: process.env.REDIS_URL || "redis://localhost:6379",
  });
}
