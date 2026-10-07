const apiOrigin = process.env.API_ORIGIN || "http://localhost:2001";
const capacitorBuild = process.env.CAPACITOR_BUILD === "1";

/** @type {import("next").NextConfig} */
const nextConfig = {
  ...(capacitorBuild ? { output: "export" } : {}),
  images: { unoptimized: true },
  ...(!capacitorBuild ? {
    async rewrites() {
      return [
        {
          source: "/v1/:path*",
          destination: apiOrigin + "/v1/:path*",
        },
      ];
    },
  } : {}),
};

export default nextConfig;
