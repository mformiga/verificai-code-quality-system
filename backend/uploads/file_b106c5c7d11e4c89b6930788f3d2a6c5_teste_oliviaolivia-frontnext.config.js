/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true
  },
  typescript: {
    ignoreBuildErrors: true
  },
  allowedDevOrigins: [
    'local.agricultura.gov.br',
    'olivia.rhmg.agricultura.gov.br'
  ]
};

module.exports = nextConfig;
