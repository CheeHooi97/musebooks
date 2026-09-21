const apiOrigin = process.env.API_ORIGIN || "http://localhost:2001";

/** @type {import("next").NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/v1/:path*",
        destination: apiOrigin + "/v1/:path*",
      },
    ];
  },
};

export default nextConfig;
