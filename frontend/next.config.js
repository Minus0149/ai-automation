/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    WORKER_URL: process.env.WORKER_URL || "http://localhost:8000",
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
    LANGCHAIN_TRACING_V2: process.env.LANGCHAIN_TRACING_V2,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "/api/:path*",
      },
    ];
  },
  serverExternalPackages: ["selenium-webdriver"],
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
