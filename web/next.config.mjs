import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typedRoutes: true,
  outputFileTracingRoot: __dirname,
  async rewrites() {
    const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      { source: '/api/proxy/:path*', destination: `${api}/:path*` }
    ];
  }
};

export default nextConfig;
