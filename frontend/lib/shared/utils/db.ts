import { Pool } from "pg";
import { AutomationTask, CreateTaskData, UpdateTaskData } from "../types";

const pool = new Pool({
  connectionString:
    process.env.DATABASE_URL ||
    "postgresql://automation_user:automation_password_2024@localhost:5432/ai_automation",
  ssl:
    process.env.NODE_ENV === "production"
      ? { rejectUnauthorized: false }
      : false,
});

export class Database {
  static async createTask(data: CreateTaskData): Promise<AutomationTask> {
    const query = `
      INSERT INTO automation_tasks (task_id, prompt, website_url, status, attempt_count, max_attempts)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `;

    const taskId = `task-${Date.now()}-${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    const values = [
      taskId,
      data.prompt,
      data.websiteUrl,
      data.status,
      data.attempts,
      data.maxAttempts,
    ];
    const result = await pool.query(query, values);

    return this.mapRowToTask(result.rows[0]);
  }

  static async getTask(id: string): Promise<AutomationTask | null> {
    try {
      const query = "SELECT * FROM automation_tasks WHERE task_id = $1";
      const result = await pool.query(query, [id]);

      if (result.rows.length === 0) {
        return null;
      }

      return this.mapRowToTask(result.rows[0]);
    } catch (error) {
      console.error("Error fetching task:", error);
      throw error; // Re-throw to be caught by the API route
    }
  }

  static async updateTask(
    id: string,
    data: UpdateTaskData
  ): Promise<AutomationTask | null> {
    const fields = [];
    const values = [];
    let paramCount = 1;

    if (data.status !== undefined) {
      fields.push(`status = $${paramCount++}`);
      values.push(data.status);
    }

    if (data.attempts !== undefined) {
      fields.push(`attempt_count = $${paramCount++}`);
      values.push(data.attempts);
    }

    if (data.result !== undefined) {
      fields.push(`execution_result = $${paramCount++}`);
      values.push(JSON.stringify(data.result));
    }

    fields.push(`updated_at = $${paramCount++}`);
    values.push(new Date());

    values.push(id);

    const query = `
      UPDATE automation_tasks 
      SET ${fields.join(", ")}
      WHERE task_id = $${paramCount}
      RETURNING *
    `;

    const result = await pool.query(query, values);

    if (result.rows.length === 0) {
      return null;
    }

    return this.mapRowToTask(result.rows[0]);
  }

  static async getTasks(
    limit: number = 20,
    offset: number = 0
  ): Promise<AutomationTask[]> {
    const query = `
      SELECT * FROM automation_tasks 
      ORDER BY created_at DESC 
      LIMIT $1 OFFSET $2
    `;

    const result = await pool.query(query, [limit, offset]);

    return result.rows.map((row: any) => this.mapRowToTask(row));
  }

  static async getTaskStats(): Promise<{
    total: number;
    successful: number;
    failed: number;
    pending: number;
    processing: number;
  }> {
    const result = await pool.query(`
      SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful,
        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
        COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
        COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing
      FROM automation_tasks
    `);

    return {
      total: parseInt(result.rows[0].total),
      successful: parseInt(result.rows[0].successful),
      failed: parseInt(result.rows[0].failed),
      pending: parseInt(result.rows[0].pending),
      processing: parseInt(result.rows[0].processing),
    };
  }

  private static mapRowToTask(row: any): AutomationTask {
    try {
      return {
        id: row.task_id,
        prompt: row.prompt,
        websiteUrl: row.website_url,
        status: row.status,
        attempts: row.attempt_count || 0,
        maxAttempts: row.max_attempts || 3,
        createdAt: row.created_at,
        updatedAt: row.updated_at,
        result: row.execution_result
          ? JSON.parse(row.execution_result)
          : undefined,
      };
    } catch (error) {
      console.error("Error mapping task row:", error, "Row data:", row);
      // Return basic task without result if JSON parsing fails
      return {
        id: row.task_id,
        prompt: row.prompt,
        websiteUrl: row.website_url,
        status: row.status,
        attempts: row.attempt_count || 0,
        maxAttempts: row.max_attempts || 3,
        createdAt: row.created_at,
        updatedAt: row.updated_at,
        result: undefined,
      };
    }
  }

  // Get task with all attempt details
  static async getTaskWithAttempts(taskId: string) {
    const task = await this.getTask(taskId);
    if (!task) return null;

    const attempts = await this.getTaskAttempts(taskId);
    const logs = await this.getTaskLogs(taskId);

    return {
      ...task,
      attempts,
      logs,
      execution_result: task.result,
    };
  }

  // Get all attempts for a task
  static async getTaskAttempts(taskId: string) {
    try {
      const query = `
        SELECT * FROM automation_attempts 
        WHERE task_id = $1 
        ORDER BY attempt_number ASC
      `;
      const result = await pool.query(query, [taskId]);
      return result.rows.map((row: any) => {
        try {
          return {
            ...row,
            execution_result: row.execution_result
              ? JSON.parse(row.execution_result)
              : null,
            screenshots: row.screenshots ? JSON.parse(row.screenshots) : null,
          };
        } catch (jsonError) {
          console.error(`JSON parse error for attempt ${row.id}:`, jsonError);
          return {
            ...row,
            execution_result: null,
            screenshots: null,
          };
        }
      });
    } catch (error) {
      console.error("Error fetching task attempts:", error);
      return [];
    }
  }

  // Get task logs
  static async getTaskLogs(taskId: string) {
    try {
      const query = `
        SELECT * FROM automation_logs 
        WHERE task_id = $1 
        ORDER BY timestamp ASC
      `;
      const result = await pool.query(query, [taskId]);
      return result.rows;
    } catch (error) {
      console.error("Error fetching task logs:", error);
      return [];
    }
  }

  static async initializeDatabase(): Promise<void> {
    // The database schema is already initialized by Docker init.sql
    // Just verify connection
    await pool.query("SELECT 1");
    console.log("Database connection verified");
  }
}
