import { NextRequest, NextResponse } from "next/server";

const WORKER_URL = process.env.WORKER_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${WORKER_URL}/models/available`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Worker request failed: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching available models:", error);
    return NextResponse.json(
      {
        error: "Failed to fetch available models",
        available: false,
        models: {},
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const { provider, model_name } = await request.json();

    if (!provider || !model_name) {
      return NextResponse.json(
        { error: "Provider and model_name are required" },
        { status: 400 }
      );
    }

    const response = await fetch(`${WORKER_URL}/models/switch`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        provider,
        model_name,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.detail || `Worker request failed: ${response.status}`
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error switching model:", error);
    return NextResponse.json(
      {
        error:
          error instanceof Error ? error.message : "Failed to switch model",
        success: false,
      },
      { status: 500 }
    );
  }
}
