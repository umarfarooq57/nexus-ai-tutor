'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Search,
    Bell,
    Moon,
    Sun,
    User,
    ChevronDown,
    LogOut,
    Settings,
    Sparkles
} from 'lucide-react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';

export function Header() {
    const [isDark, setIsDark] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');

    return (
        <header className="h-16 border-b border-white/10 glass-dark flex items-center justify-between px-6">
            {/* Search */}
            <div className="flex-1 max-w-md">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search courses, topics, or ask AI..."
                        className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/50 transition-all"
                    />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-xs text-gray-500">
                        <kbd className="px-1.5 py-0.5 bg-white/10 rounded">⌘</kbd>
                        <kbd className="px-1.5 py-0.5 bg-white/10 rounded">K</kbd>
                    </div>
                </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center gap-4">
                {/* AI Quick Access */}
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-primary-500/20 to-secondary-500/20 border border-primary-500/30 text-sm text-white hover:border-primary-500/50 transition-colors"
                >
                    <Sparkles className="w-4 h-4 text-primary-400" />
                    <span>Ask AI</span>
                </motion.button>

                {/* Theme Toggle */}
                <button
                    onClick={() => setIsDark(!isDark)}
                    className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                >
                    {isDark ? (
                        <Sun className="w-5 h-5 text-gray-400" />
                    ) : (
                        <Moon className="w-5 h-5 text-gray-400" />
                    )}
                </button>

                {/* Notifications */}
                <button className="relative p-2 rounded-lg hover:bg-white/5 transition-colors">
                    <Bell className="w-5 h-5 text-gray-400" />
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                </button>

                {/* User Menu */}
                <DropdownMenu.Root>
                    <DropdownMenu.Trigger asChild>
                        <button className="flex items-center gap-2 p-1 rounded-lg hover:bg-white/5 transition-colors">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                                <User className="w-4 h-4 text-white" />
                            </div>
                            <ChevronDown className="w-4 h-4 text-gray-400" />
                        </button>
                    </DropdownMenu.Trigger>

                    <DropdownMenu.Portal>
                        <DropdownMenu.Content
                            align="end"
                            sideOffset={8}
                            className="min-w-[200px] bg-dark-800 rounded-xl border border-white/10 shadow-xl overflow-hidden z-50"
                        >
                            <div className="p-3 border-b border-white/10">
                                <p className="font-medium text-white">Learner</p>
                                <p className="text-xs text-gray-500">learner@example.com</p>
                            </div>

                            <div className="p-1">
                                <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg cursor-pointer outline-none">
                                    <User className="w-4 h-4" />
                                    <span>Profile</span>
                                </DropdownMenu.Item>
                                <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg cursor-pointer outline-none">
                                    <Settings className="w-4 h-4" />
                                    <span>Settings</span>
                                </DropdownMenu.Item>
                            </div>

                            <div className="p-1 border-t border-white/10">
                                <DropdownMenu.Item className="flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg cursor-pointer outline-none">
                                    <LogOut className="w-4 h-4" />
                                    <span>Sign Out</span>
                                </DropdownMenu.Item>
                            </div>
                        </DropdownMenu.Content>
                    </DropdownMenu.Portal>
                </DropdownMenu.Root>
            </div>
        </header>
    );
}
