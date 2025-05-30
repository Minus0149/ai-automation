import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { prompt, website_url, framework, task_id, project_config } = body;

    // Validate required fields
    if (!prompt || !website_url) {
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

    // Call worker directly with LangChain enhanced automation
    const workerResponse = await fetch(
      "http://localhost:8000/execute-enhanced",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          website_url: website_url.trim(),
          framework: framework || "selenium",
          task_id: task_id?.trim() || `enhanced_${Date.now()}`,
          project_config: project_config || {
            projectType: "selenium_automation",
            features: [
              "Dynamic page analysis",
              "Error handling",
              "Comprehensive logging",
            ],
            includeTests: true,
            includeDocker: true,
            includeCICD: false,
          },
          timeout: 300,
        }),
      }
    );

    if (!workerResponse.ok) {
      const errorText = await workerResponse.text();
      console.error("Worker service error:", errorText);
      return NextResponse.json(
        { error: "Failed to execute enhanced automation" },
        { status: 500 }
      );
    }

    const result = await workerResponse.json();

    return NextResponse.json({
      success: result.success,
      taskId: result.task_id || task_id?.trim() || `enhanced_${Date.now()}`,
      logs: result.logs || [],
      screenshots: result.screenshots || [],
      execution_time: result.execution_time || 0,
      framework: result.framework || framework,
      generated_code: result.generated_code || "",
      project_structure: result.project_structure || {},
      context_chain: result.context_chain || [],
      function_calls: result.function_calls || [],
      chat_history: result.chat_history || [],
      error: result.error || null,
      features: [
        "LangChain-powered AI agent",
        "Complete project structure generation",
        "Incremental code modification",
        "Persistent chat history",
        "Advanced function calling",
        "Dynamic page analysis",
        "Context-aware automation",
      ],
    });
  } catch (error) {
    console.error("Error executing enhanced automation:", error);
    return NextResponse.json(
      {
        error: "Internal server error",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
