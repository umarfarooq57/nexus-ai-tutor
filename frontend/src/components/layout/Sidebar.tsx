'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Home,
    BookOpen,
    Brain,
    Code2,
    BarChart3,
    FileText,
    Settings,
    ChevronLeft,
    Sparkles,
    Target,
    Award,
    MessageSquare,
    HelpCircle,
    Zap
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Learn', href: '/learn', icon: BookOpen },
    { name: 'Digital Twin', href: '/digital-twin', icon: Brain },
    { name: 'Practice', href: '/practice', icon: Code2 },
    { name: 'Assessments', href: '/assessments', icon: Target },
    { name: 'Progress', href: '/progress', icon: BarChart3 },
    { name: 'Achievements', href: '/achievements', icon: Award },
    { name: 'Reports', href: '/reports', icon: FileText },
];

const bottomNav = [
    { name: 'AI Assistant', href: '/assistant', icon: MessageSquare },
    { name: 'Help', href: '/help', icon: HelpCircle },
    { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
    const pathname = usePathname();
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <motion.aside
            initial={false}
            animate={{ width: isCollapsed ? 80 : 280 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="relative flex flex-col h-full glass-dark border-r border-white/10"
        >
            {/* Logo */}
            <div className="flex items-center h-16 px-4 border-b border-white/10">
                <Link href="/" className="flex items-center gap-3">
                    <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                        className="relative"
                    >
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                            <Zap className="w-6 h-6 text-white" />
                        </div>
                        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 blur-lg opacity-50" />
                    </motion.div>

                    <AnimatePresence>
                        {!isCollapsed && (
                            <motion.div
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -10 }}
                                transition={{ duration: 0.2 }}
                            >
                                <span className="text-xl font-bold text-white">NEXUS</span>
                                <span className="text-xs text-primary-400 block -mt-1">AI Tutor</span>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-4 px-3">
                <ul className="space-y-1">
                    {navigation.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <li key={item.name}>
                                <Link
                                    href={item.href}
                                    className={cn(
                                        'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200',
                                        'hover:bg-white/5',
                                        isActive && 'bg-primary-500/20 text-primary-400'
                                    )}
                                >
                                    <item.icon className={cn(
                                        'w-5 h-5 flex-shrink-0',
                                        isActive ? 'text-primary-400' : 'text-gray-400'
                                    )} />

                                    <AnimatePresence>
                                        {!isCollapsed && (
                                            <motion.span
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                exit={{ opacity: 0 }}
                                                className={cn(
                                                    'text-sm font-medium truncate',
                                                    isActive ? 'text-white' : 'text-gray-400'
                                                )}
                                            >
                                                {item.name}
                                            </motion.span>
                                        )}
                                    </AnimatePresence>

                                    {isActive && !isCollapsed && (
                                        <motion.div
                                            layoutId="activeIndicator"
                                            className="ml-auto w-1.5 h-1.5 rounded-full bg-primary-400"
                                        />
                                    )}
                                </Link>
                            </li>
                        );
                    })}
                </ul>

                {/* Separator */}
                <div className="my-4 mx-3 h-px bg-white/10" />

                {/* Bottom Navigation */}
                <ul className="space-y-1">
                    {bottomNav.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <li key={item.name}>
                                <Link
                                    href={item.href}
                                    className={cn(
                                        'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200',
                                        'hover:bg-white/5',
                                        isActive && 'bg-primary-500/20 text-primary-400'
                                    )}
                                >
                                    <item.icon className={cn(
                                        'w-5 h-5 flex-shrink-0',
                                        isActive ? 'text-primary-400' : 'text-gray-400'
                                    )} />

                                    <AnimatePresence>
                                        {!isCollapsed && (
                                            <motion.span
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                exit={{ opacity: 0 }}
                                                className={cn(
                                                    'text-sm font-medium truncate',
                                                    isActive ? 'text-white' : 'text-gray-400'
                                                )}
                                            >
                                                {item.name}
                                            </motion.span>
                                        )}
                                    </AnimatePresence>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* AI Status Card */}
            <AnimatePresence>
                {!isCollapsed && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        className="mx-3 mb-4 p-4 rounded-xl bg-gradient-to-br from-primary-500/20 to-secondary-500/20 border border-white/10"
                    >
                        <div className="flex items-center gap-2 mb-2">
                            <Sparkles className="w-4 h-4 text-secondary-400" />
                            <span className="text-xs font-medium text-white">AI Teaching Agent</span>
                        </div>
                        <p className="text-xs text-gray-400 mb-3">
                            Ready to personalize your learning experience
                        </p>
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                            <span className="text-xs text-green-400">Active</span>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Collapse Button */}
            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-dark-800 border border-white/10 flex items-center justify-center hover:bg-dark-700 transition-colors"
            >
                <motion.div
                    animate={{ rotate: isCollapsed ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                >
                    <ChevronLeft className="w-4 h-4 text-gray-400" />
                </motion.div>
            </button>
        </motion.aside>
    );
}
