import { NextRequest, NextResponse } from "next/server";

const QUEUE_URL = process.env.QUEUE_URL || "http://localhost:3002";

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${QUEUE_URL}/models`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error proxying to queue:", error);
    return NextResponse.json(
      { error: "Failed to communicate with queue processor" },
      { status: 500 }
    );
  }
}
