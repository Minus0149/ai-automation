import { Pool } from "pg";
import { AutomationTask, CreateTaskData, UpdateTaskData } from "../types";

const pool = new Pool({
  connectionString:
    process.env.DATABASE_URL ||
    "postgresql://postgres:password@localhost:5432/ai_automation_db",
  ssl:
    process.env.NODE_ENV === "production"
      ? { rejectUnauthorized: false }
      : false,
});

export class Database {
  static async createTask(data: CreateTaskData): Promise<AutomationTask> {
    const query = `
      INSERT INTO tasks (prompt, website_url, status, attempts, max_attempts)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;

    const values = [
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
    const query = "SELECT * FROM tasks WHERE id = $1";
    const result = await pool.query(query, [id]);

    if (result.rows.length === 0) {
      return null;
    }

    return this.mapRowToTask(result.rows[0]);
  }

  static async updateTask(
    id: string,
    data: UpdateTaskData
  ): Promise<AutomationTask | null> {
    const fields: string[] = [];
    const values: any[] = [];
    let paramCount = 1;

    if (data.status !== undefined) {
      fields.push(`status = $${paramCount++}`);
      values.push(data.status);
    }

    if (data.attempts !== undefined) {
      fields.push(`attempts = $${paramCount++}`);
      values.push(data.attempts);
    }

    if (data.result !== undefined) {
      fields.push(`result = $${paramCount++}`);
      values.push(JSON.stringify(data.result));
    }

    fields.push(`updated_at = $${paramCount++}`);
    values.push(new Date());

    values.push(id);

    const query = `
      UPDATE tasks 
      SET ${fields.join(", ")}
      WHERE id = $${paramCount}
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
      SELECT * FROM tasks 
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
      FROM tasks
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
    return {
      id: row.id,
      prompt: row.prompt,
      websiteUrl: row.website_url,
      status: row.status,
      attempts: row.attempts,
      maxAttempts: row.max_attempts,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
      result: row.result ? JSON.parse(row.result) : undefined,
    };
  }

  static async initializeDatabase(): Promise<void> {
    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS tasks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        prompt TEXT NOT NULL,
        website_url TEXT NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        attempts INTEGER NOT NULL DEFAULT 0,
        max_attempts INTEGER NOT NULL DEFAULT 3,
        result JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      );

      CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
      CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
    `;

    await pool.query(createTableQuery);
  }
}
