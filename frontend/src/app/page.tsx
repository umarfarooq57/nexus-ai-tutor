'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import {
    Brain,
    Sparkles,
    BookOpen,
    Code2,
    TrendingUp,
    Zap,
    Target,
    Clock
} from 'lucide-react';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { ProgressRing } from '@/components/dashboard/ProgressRing';
import { LearningPath } from '@/components/dashboard/LearningPath';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { AIInsights } from '@/components/dashboard/AIInsights';
import { DigitalTwinVisualization } from '@/components/dashboard/DigitalTwinVisualization';

export default function DashboardPage() {
    return (
        <div className="space-y-8">
            {/* Welcome Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="relative overflow-hidden rounded-2xl glass-dark p-8"
            >
                <div className="absolute inset-0 animated-gradient opacity-10" />
                <div className="relative z-10 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-white mb-2">
                            Welcome back, <span className="text-primary-400">Learner</span>! 🚀
                        </h1>
                        <p className="text-gray-400 text-lg">
                            Your AI tutor is ready to help you master new skills today.
                        </p>
                    </div>
                    <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                        className="hidden lg:block"
                    >
                        <Brain className="w-24 h-24 text-primary-400 opacity-50" />
                    </motion.div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                    <StatsCard
                        icon={<Clock className="w-5 h-5" />}
                        label="Study Time Today"
                        value="2h 34m"
                        trend="+15%"
                        color="primary"
                    />
                    <StatsCard
                        icon={<Target className="w-5 h-5" />}
                        label="Daily Goal"
                        value="75%"
                        trend="On Track"
                        color="accent"
                    />
                    <StatsCard
                        icon={<Zap className="w-5 h-5" />}
                        label="Current Streak"
                        value="12 days"
                        trend="🔥"
                        color="secondary"
                    />
                    <StatsCard
                        icon={<TrendingUp className="w-5 h-5" />}
                        label="Overall Progress"
                        value="68%"
                        trend="+5%"
                        color="accent"
                    />
                </div>
            </motion.div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column - Learning Progress */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="lg:col-span-2 space-y-6"
                >
                    {/* Continue Learning */}
                    <div className="glass-dark rounded-2xl p-6">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-secondary-400" />
                                Continue Learning
                            </h2>
                            <Link
                                href="/learn"
                                className="text-primary-400 hover:text-primary-300 text-sm"
                            >
                                View All →
                            </Link>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Course Cards */}
                            <CourseCard
                                title="Neural Networks Deep Dive"
                                category="AI/ML"
                                progress={65}
                                nextTopic="Backpropagation"
                                icon={<Brain className="w-6 h-6" />}
                            />
                            <CourseCard
                                title="Full-Stack Development"
                                category="Web Dev"
                                progress={42}
                                nextTopic="REST API Design"
                                icon={<Code2 className="w-6 h-6" />}
                            />
                        </div>
                    </div>

                    {/* AI Learning Insights */}
                    <AIInsights />

                    {/* Learning Path */}
                    <LearningPath />
                </motion.div>

                {/* Right Column - Digital Twin & Activity */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                    className="space-y-6"
                >
                    {/* Digital Twin Visualization */}
                    <DigitalTwinVisualization />

                    {/* Recent Activity */}
                    <RecentActivity />
                </motion.div>
            </div>
        </div>
    );
}

// Course Card Component
function CourseCard({
    title,
    category,
    progress,
    nextTopic,
    icon
}: {
    title: string;
    category: string;
    progress: number;
    nextTopic: string;
    icon: React.ReactNode;
}) {
    return (
        <motion.div
            whileHover={{ scale: 1.02 }}
            className="relative overflow-hidden rounded-xl bg-dark-800/50 border border-white/10 p-5 card-hover cursor-pointer"
        >
            <div className="flex items-start justify-between mb-4">
                <div className="p-2 rounded-lg bg-primary-500/20 text-primary-400">
                    {icon}
                </div>
                <span className="text-xs font-medium text-secondary-400 bg-secondary-500/20 px-2 py-1 rounded-full">
                    {category}
                </span>
            </div>

            <h3 className="font-semibold text-white mb-1">{title}</h3>
            <p className="text-sm text-gray-500 mb-4">Next: {nextTopic}</p>

            {/* Progress Bar */}
            <div className="space-y-2">
                <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Progress</span>
                    <span className="text-primary-400">{progress}%</span>
                </div>
                <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                        className="h-full bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full"
                    />
                </div>
            </div>

            {/* Glow Effect */}
            <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity pointer-events-none">
                <div className="absolute inset-0 bg-gradient-to-r from-primary-500/10 to-secondary-500/10" />
            </div>
        </motion.div>
    );
}
