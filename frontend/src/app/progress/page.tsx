'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    TrendingUp,
    Calendar,
    Trophy,
    Target,
    BookOpen,
    Clock,
    BarChart2,
    Activity,
    Brain
} from 'lucide-react';

interface ProgressData {
    overallProgress: number;
    topicsCompleted: number;
    totalTopics: number;
    studyHours: number;
    streak: number;
    masteryByTopic: { topic: string; mastery: number }[];
    weeklyActivity: { day: string; hours: number }[];
    recentAchievements: { title: string; date: string; icon: string }[];
}

export default function ProgressPage() {
    const [progressData, setProgressData] = useState<ProgressData>({
        overallProgress: 68,
        topicsCompleted: 24,
        totalTopics: 45,
        studyHours: 47,
        streak: 12,
        masteryByTopic: [
            { topic: 'Python Basics', mastery: 95 },
            { topic: 'Linear Algebra', mastery: 82 },
            { topic: 'Machine Learning', mastery: 65 },
            { topic: 'Neural Networks', mastery: 45 },
            { topic: 'Deep Learning', mastery: 30 },
            { topic: 'NLP', mastery: 20 }
        ],
        weeklyActivity: [
            { day: 'Mon', hours: 2.5 },
            { day: 'Tue', hours: 1.8 },
            { day: 'Wed', hours: 3.2 },
            { day: 'Thu', hours: 2.0 },
            { day: 'Fri', hours: 1.5 },
            { day: 'Sat', hours: 4.0 },
            { day: 'Sun', hours: 3.5 }
        ],
        recentAchievements: [
            { title: 'First Quiz Ace', date: 'Today', icon: '🎯' },
            { title: '10 Day Streak', date: '2 days ago', icon: '🔥' },
            { title: 'ML Beginner', date: '1 week ago', icon: '🤖' }
        ]
    });

    const StatCard = ({ title, value, subtitle, icon: Icon, color }: any) => (
        <motion.div
            className="glass rounded-xl p-5"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02 }}
        >
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-gray-400 text-sm">{title}</p>
                    <p className="text-2xl font-bold text-white mt-1">{value}</p>
                    {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
                </div>
                <div className={`p-3 rounded-xl ${color}`}>
                    <Icon className="w-5 h-5 text-white" />
                </div>
            </div>
        </motion.div>
    );

    const getMasteryColor = (mastery: number) => {
        if (mastery >= 80) return 'bg-green-500';
        if (mastery >= 60) return 'bg-blue-500';
        if (mastery >= 40) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Your Progress</h1>
                <p className="text-gray-400">Track your learning journey and achievements</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <StatCard
                    title="Overall Progress"
                    value={`${progressData.overallProgress}%`}
                    subtitle="Keep going!"
                    icon={TrendingUp}
                    color="bg-gradient-to-br from-primary to-blue-600"
                />
                <StatCard
                    title="Topics Completed"
                    value={progressData.topicsCompleted}
                    subtitle={`of ${progressData.totalTopics} total`}
                    icon={BookOpen}
                    color="bg-gradient-to-br from-green-500 to-emerald-600"
                />
                <StatCard
                    title="Study Hours"
                    value={`${progressData.studyHours}h`}
                    subtitle="This month"
                    icon={Clock}
                    color="bg-gradient-to-br from-purple-500 to-pink-600"
                />
                <StatCard
                    title="Current Streak"
                    value={`${progressData.streak} days`}
                    subtitle="🔥 Keep it up!"
                    icon={Activity}
                    color="bg-gradient-to-br from-orange-500 to-red-600"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Topic Mastery */}
                <div className="lg:col-span-2 glass rounded-2xl p-6">
                    <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                        <Target className="w-5 h-5 text-primary" />
                        Topic Mastery
                    </h2>
                    <div className="space-y-4">
                        {progressData.masteryByTopic.map((item, idx) => (
                            <motion.div
                                key={item.topic}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.1 }}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-gray-300">{item.topic}</span>
                                    <span className={`font-semibold ${item.mastery >= 80 ? 'text-green-400' : item.mastery >= 50 ? 'text-yellow-400' : 'text-gray-400'}`}>
                                        {item.mastery}%
                                    </span>
                                </div>
                                <div className="h-3 bg-dark-200 rounded-full overflow-hidden">
                                    <motion.div
                                        className={`h-full rounded-full ${getMasteryColor(item.mastery)}`}
                                        initial={{ width: 0 }}
                                        animate={{ width: `${item.mastery}%` }}
                                        transition={{ duration: 1, delay: idx * 0.1 }}
                                    />
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* Recent Achievements */}
                <div className="glass rounded-2xl p-6">
                    <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                        <Trophy className="w-5 h-5 text-yellow-400" />
                        Recent Achievements
                    </h2>
                    <div className="space-y-4">
                        {progressData.recentAchievements.map((achievement, idx) => (
                            <motion.div
                                key={achievement.title}
                                className="flex items-center gap-3 p-3 rounded-xl bg-dark-200/50"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                            >
                                <span className="text-2xl">{achievement.icon}</span>
                                <div>
                                    <p className="font-medium text-white">{achievement.title}</p>
                                    <p className="text-sm text-gray-500">{achievement.date}</p>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Weekly Activity */}
            <div className="glass rounded-2xl p-6 mt-6">
                <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-secondary" />
                    Weekly Activity
                </h2>
                <div className="flex items-end justify-between h-40 gap-2">
                    {progressData.weeklyActivity.map((day, idx) => {
                        const maxHours = Math.max(...progressData.weeklyActivity.map(d => d.hours));
                        const height = (day.hours / maxHours) * 100;
                        return (
                            <motion.div
                                key={day.day}
                                className="flex-1 flex flex-col items-center gap-2"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                            >
                                <div className="w-full bg-dark-200 rounded-t-lg relative" style={{ height: '100%' }}>
                                    <motion.div
                                        className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-primary to-secondary rounded-t-lg"
                                        initial={{ height: 0 }}
                                        animate={{ height: `${height}%` }}
                                        transition={{ duration: 0.8, delay: idx * 0.1 }}
                                    />
                                </div>
                                <span className="text-xs text-gray-500">{day.day}</span>
                                <span className="text-xs text-gray-400">{day.hours}h</span>
                            </motion.div>
                        );
                    })}
                </div>
            </div>

            {/* AI Insights */}
            <div className="glass rounded-2xl p-6 mt-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5 text-purple-400" />
                    AI Learning Insights
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-xl bg-dark-200/50">
                        <p className="text-sm text-gray-400 mb-2">Optimal Study Time</p>
                        <p className="text-white font-semibold">9:00 AM - 11:00 AM</p>
                        <p className="text-xs text-gray-500 mt-1">Based on your focus patterns</p>
                    </div>
                    <div className="p-4 rounded-xl bg-dark-200/50">
                        <p className="text-sm text-gray-400 mb-2">Learning Style</p>
                        <p className="text-white font-semibold">Visual + Practical</p>
                        <p className="text-xs text-gray-500 mt-1">Diagrams & code examples work best</p>
                    </div>
                    <div className="p-4 rounded-xl bg-dark-200/50">
                        <p className="text-sm text-gray-400 mb-2">Focus Area Suggestion</p>
                        <p className="text-white font-semibold">Neural Networks</p>
                        <p className="text-xs text-gray-500 mt-1">Ready to advance from current level</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
