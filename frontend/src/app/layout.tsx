import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import '../styles/globals.css';
import { Providers } from '@/components/Providers';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
});

const jetbrainsMono = JetBrains_Mono({
    subsets: ['latin'],
    variable: '--font-mono',
});

export const metadata: Metadata = {
    title: 'NEXUS AI Tutor | Ultra Pro Max',
    description: 'The Most Advanced Self-Learning AI Education Platform',
    keywords: ['AI', 'Machine Learning', 'Education', 'Tutoring', 'Personalized Learning'],
    authors: [{ name: 'NEXUS AI Team' }],
    manifest: '/manifest.json',
    themeColor: '#6366f1',
    appleWebApp: {
        capable: true,
        statusBarStyle: 'black-translucent',
        title: 'NEXUS AI',
    },
    openGraph: {
        title: 'NEXUS AI Tutor',
        description: 'Learn AI/ML, Data Science, Full-Stack & DevOps with personalized AI teaching',
        type: 'website',
    },
    other: {
        'mobile-web-app-capable': 'yes',
        'apple-mobile-web-app-capable': 'yes',
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark h-full">
            <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased h-full bg-dark-900 mesh-bg`}>
                <Providers>
                    <div className="flex h-screen overflow-hidden">
                        <Sidebar />
                        <div className="flex-1 flex flex-col h-full overflow-hidden relative">
                            <Header />
                            <main className="flex-1 overflow-y-auto p-6 scroll-smooth">
                                {children}
                            </main>
                        </div>
                    </div>
                </Providers>
            </body>
        </html>
    );
}
