import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static export for GitHub Pages
  output: "export",
  trailingSlash: true,

  // GitHub Pages is served from /litemind-cli/ subdirectory
  basePath: "/litemind-cli",

  // Don't use image optimization — not available in static export
  images: {
    unoptimized: true,
  },

  // React strict mode for dev
  reactStrictMode: true,
};

export default nextConfig;
