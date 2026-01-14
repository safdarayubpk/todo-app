import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  output: "standalone",

  // Proxy API requests to backend
  async rewrites() {
    // Use environment variable for backend URL, fallback to localhost for local dev
    const backendUrl = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";

    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
