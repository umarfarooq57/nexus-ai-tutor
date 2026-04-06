/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
        domains: ['localhost', 'api.nexustutor.ai'],
        remotePatterns: [
            {
                protocol: 'https',
                hostname: '**.amazonaws.com',
            },
        ],
    },
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/:path*',
            },
        ];
    },
};

module.exports = nextConfig;
