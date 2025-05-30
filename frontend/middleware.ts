import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const url = request.nextUrl.clone();

  // Proxy queue API requests to the queue processor
  if (url.pathname.startsWith("/api/queue/")) {
    // Remove '/api/queue' prefix and proxy to queue processor
    const queuePath = url.pathname.replace("/api/queue", "");
    const queueUrl = `http://localhost:3002${queuePath}${url.search}`;

    return NextResponse.rewrite(new URL(queueUrl));
  }

  return NextResponse.next();
}

export const config = {
  matcher: "/api/queue/:path*",
};
