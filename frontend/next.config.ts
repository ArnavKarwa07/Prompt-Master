import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,

  // Turbopack configuration
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;
