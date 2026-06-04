import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["@planner3000/ui", "@planner3000/shared"],
  experimental: {
    typedRoutes: true,
  },
};

export default nextConfig;
