import { Pool, PoolClient } from "pg";
import * as dotenv from "dotenv";
import * as path from "path";

// Load environment variables
dotenv.config({ path: path.join(__dirname, "..", ".env") });

interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
  ssl?: boolean;
}

class DatabaseManager {
  private pool: Pool | null = null;
  private config: DatabaseConfig;

  constructor() {
    this.config = {
      host: process.env.DB_HOST || "localhost",
      port: parseInt(process.env.DB_PORT || "5432"),
      database: process.env.DB_NAME || "ai_automation",
      user: process.env.DB_USER || "automation_user",
      password: process.env.DB_PASSWORD || "automation_password_2024",
      ssl: process.env.NODE_ENV === "production",
    };
  }

  async connect(): Promise<void> {
    if (this.pool) {
      return;
    }

    try {
      this.pool = new Pool({
        ...this.config,
        max: 10,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 10000,
      });

      // Test connection
      const client = await this.pool.connect();
      await client.query("SELECT NOW()");
      client.release();

      console.log("✅ Database connected successfully");
    } catch (error) {
      console.error("❌ Database connection failed:", error);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
      console.log("🔌 Database disconnected");
    }
  }

  async query(text: string, params?: any[]): Promise<any> {
    if (!this.pool) {
      await this.connect();
    }

    try {
      const result = await this.pool!.query(text, params);
      return result;
    } catch (error) {
      console.error("❌ Database query failed:", error);
      throw error;
    }
  }

  async getClient(): Promise<PoolClient> {
    if (!this.pool) {
      await this.connect();
    }
    return this.pool!.connect();
  }

  // Task management methods
  async createTask(taskData: {
    taskId: string;
    prompt: string;
    websiteUrl: string;
    maxAttempts?: number;
    userId?: string;
    sessionId?: string;
  }) {
    const query = `
      INSERT INTO automation_tasks (task_id, prompt, website_url, max_attempts, user_id, session_id)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `;

    const values = [
      taskData.taskId,
      taskData.prompt,
      taskData.websiteUrl,
      taskData.maxAttempts || 3,
      taskData.userId,
      taskData.sessionId,
    ];

    const result = await this.query(query, values);
    return result.rows[0];
  }

  // Store attempt details
  async createAttempt(attemptData: {
    taskId: string;
    attemptNumber: number;
    status: string;
    generatedCode?: string;
    executionResult?: any;
    errorMessage?: string;
    screenshots?: any;
    executionTime?: number;
  }) {
    const query = `
      INSERT INTO automation_attempts (
        task_id, attempt_number, status, generated_code, 
        execution_result, error_message, screenshots, execution_time_ms
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      ON CONFLICT (task_id, attempt_number) 
      DO UPDATE SET 
        status = EXCLUDED.status,
        generated_code = EXCLUDED.generated_code,
        execution_result = EXCLUDED.execution_result,
        error_message = EXCLUDED.error_message,
        screenshots = EXCLUDED.screenshots,
        execution_time_ms = EXCLUDED.execution_time_ms
      RETURNING *
    `;

    // Convert execution time to integer milliseconds
    const executionTimeMs = attemptData.executionTime
      ? Math.round(attemptData.executionTime * 1000)
      : null;

    // Safe JSON serialization for executionResult
    let executionResultJson = null;
    if (attemptData.executionResult) {
      try {
        if (typeof attemptData.executionResult === "string") {
          // Verify it's valid JSON
          JSON.parse(attemptData.executionResult);
          executionResultJson = attemptData.executionResult;
        } else {
          executionResultJson = JSON.stringify(attemptData.executionResult);
        }
      } catch (error) {
        console.error(
          "Failed to serialize executionResult, storing as string:",
          error
        );
        executionResultJson = String(attemptData.executionResult);
      }
    }

    // Safe JSON serialization for screenshots
    let screenshotsJson = null;
    if (attemptData.screenshots) {
      try {
        if (typeof attemptData.screenshots === "string") {
          // Verify it's valid JSON
          JSON.parse(attemptData.screenshots);
          screenshotsJson = attemptData.screenshots;
        } else {
          screenshotsJson = JSON.stringify(attemptData.screenshots);
        }
      } catch (error) {
        console.error(
          "Failed to serialize screenshots, storing as string:",
          error
        );
        screenshotsJson = String(attemptData.screenshots);
      }
    }

    const values = [
      attemptData.taskId,
      attemptData.attemptNumber,
      attemptData.status,
      attemptData.generatedCode,
      executionResultJson,
      attemptData.errorMessage,
      screenshotsJson,
      executionTimeMs,
    ];

    const result = await this.query(query, values);
    return result.rows[0];
  }

  // Get all attempts for a task
  async getTaskAttempts(taskId: string) {
    const query = `
      SELECT * FROM automation_attempts 
      WHERE task_id = $1 
      ORDER BY attempt_number ASC
    `;
    const result = await this.query(query, [taskId]);
    return result.rows.map((row: any) => ({
      ...row,
      execution_result: row.execution_result
        ? JSON.parse(row.execution_result)
        : null,
      screenshots: row.screenshots ? JSON.parse(row.screenshots) : null,
    }));
  }

  async updateTaskStatus(taskId: string, status: string, data?: any) {
    const updates: string[] = ["status = $2", "updated_at = CURRENT_TIMESTAMP"];
    const values: any[] = [taskId, status];
    let paramIndex = 3;

    if (data?.generatedCode) {
      updates.push(`generated_code = $${paramIndex++}`);
      values.push(data.generatedCode);
    }

    if (data?.executionResult) {
      updates.push(`execution_result = $${paramIndex++}`);
      // Safe JSON serialization for executionResult
      try {
        if (typeof data.executionResult === "string") {
          // Verify it's valid JSON
          JSON.parse(data.executionResult);
          values.push(data.executionResult);
        } else {
          values.push(JSON.stringify(data.executionResult));
        }
      } catch (error) {
        console.error(
          "Failed to serialize executionResult in updateTaskStatus, storing as string:",
          error
        );
        values.push(String(data.executionResult));
      }
    }

    if (data?.errorMessage) {
      updates.push(`error_message = $${paramIndex++}`);
      values.push(data.errorMessage);
    }

    if (data?.screenshots) {
      updates.push(`screenshots = $${paramIndex++}`);
      // Safe JSON serialization for screenshots
      try {
        if (typeof data.screenshots === "string") {
          // Verify it's valid JSON
          JSON.parse(data.screenshots);
          values.push(data.screenshots);
        } else {
          values.push(JSON.stringify(data.screenshots));
        }
      } catch (error) {
        console.error(
          "Failed to serialize screenshots in updateTaskStatus, storing as string:",
          error
        );
        values.push(String(data.screenshots));
      }
    }

    if (data?.executionTime) {
      updates.push(`execution_time_ms = $${paramIndex++}`);
      // Convert execution time to integer milliseconds
      const executionTimeMs = Math.round(data.executionTime * 1000);
      values.push(executionTimeMs);
    }

    if (data?.attemptCount !== undefined) {
      updates.push(`attempt_count = $${paramIndex++}`);
      values.push(data.attemptCount);
    }

    if (status === "completed") {
      updates.push("completed_at = CURRENT_TIMESTAMP");
    }

    const query = `
      UPDATE automation_tasks 
      SET ${updates.join(", ")}
      WHERE task_id = $1
      RETURNING *
    `;

    const result = await this.query(query, values);
    return result.rows[0];
  }

  async getTask(taskId: string) {
    const query = "SELECT * FROM automation_tasks WHERE task_id = $1";
    const result = await this.query(query, [taskId]);
    return result.rows[0];
  }

  // Get task with all attempt details
  async getTaskWithAttempts(taskId: string) {
    const task = await this.getTask(taskId);
    if (!task) return null;

    const attempts = await this.getTaskAttempts(taskId);
    const logs = await this.getTaskLogs(taskId);

    return {
      ...task,
      attempts,
      logs,
      execution_result: task.execution_result
        ? JSON.parse(task.execution_result)
        : null,
      screenshots: task.screenshots ? JSON.parse(task.screenshots) : null,
    };
  }

  async getTasks(limit = 50, offset = 0) {
    const query = `
      SELECT * FROM automation_tasks 
      ORDER BY created_at DESC 
      LIMIT $1 OFFSET $2
    `;
    const result = await this.query(query, [limit, offset]);
    return result.rows;
  }

  async addLog(
    taskId: string,
    level: string,
    message: string,
    source?: string
  ) {
    const query = `
      INSERT INTO automation_logs (task_id, level, message, source)
      VALUES ($1, $2, $3, $4)
    `;
    await this.query(query, [taskId, level, message, source]);
  }

  async getTaskLogs(taskId: string) {
    const query = `
      SELECT * FROM automation_logs 
      WHERE task_id = $1 
      ORDER BY timestamp ASC
    `;
    const result = await this.query(query, [taskId]);
    return result.rows;
  }
}

// Export singleton instance
export const db = new DatabaseManager();
export default db;
