export interface AutomationJob {
  taskId: string;
  prompt: string;
  websiteUrl: string;
  attempt: number;
  maxAttempts: number;
}
