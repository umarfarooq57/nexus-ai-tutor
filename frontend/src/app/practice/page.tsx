'use client';

import { motion } from 'framer-motion';
import { Code2, Play, Terminal, CheckCircle, XCircle, Lightbulb } from 'lucide-react';

export default function PracticePage() {
    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between"
            >
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-accent-500/20 to-primary-500/20 border border-white/10">
                        <Code2 className="w-8 h-8 text-accent-400" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white">Practice</h1>
                        <p className="text-dark-400">Hands-on coding challenges</p>
                    </div>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg transition-colors text-white">
                    <Play className="w-4 h-4" />
                    Start Challenge
                </button>
            </motion.div>

            {/* Practice Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                    { label: 'Problems Solved', value: '47', icon: CheckCircle, color: 'text-green-400' },
                    { label: 'Current Streak', value: '5 days', icon: Lightbulb, color: 'text-yellow-400' },
                    { label: 'Failed Attempts', value: '12', icon: XCircle, color: 'text-red-400' },
                    { label: 'Total Time', value: '23h', icon: Terminal, color: 'text-primary-400' },
                ].map((stat, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="glass-dark rounded-xl p-4 border border-white/10"
                    >
                        <stat.icon className={`w-5 h-5 ${stat.color} mb-2`} />
                        <p className="text-2xl font-bold text-white">{stat.value}</p>
                        <p className="text-xs text-dark-400">{stat.label}</p>
                    </motion.div>
                ))}
            </div>

            {/* Challenge Categories */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="glass-dark rounded-xl p-6 border border-white/10"
            >
                <h2 className="text-lg font-semibold text-white mb-4">Challenge Categories</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                        { name: 'Algorithms', count: 25, difficulty: 'Mixed', color: 'from-blue-500/20 to-cyan-500/20' },
                        { name: 'Data Structures', count: 18, difficulty: 'Intermediate', color: 'from-purple-500/20 to-pink-500/20' },
                        { name: 'Machine Learning', count: 12, difficulty: 'Advanced', color: 'from-green-500/20 to-teal-500/20' },
                    ].map((cat, idx) => (
                        <div
                            key={idx}
                            className={`p-4 rounded-xl bg-gradient-to-br ${cat.color} border border-white/10 cursor-pointer hover:border-white/20 transition-colors`}
                        >
                            <h3 className="font-medium text-white">{cat.name}</h3>
                            <p className="text-sm text-dark-400 mt-1">{cat.count} challenges</p>
                            <span className="inline-block mt-2 px-2 py-1 rounded text-xs bg-white/10 text-white">
                                {cat.difficulty}
                            </span>
                        </div>
                    ))}
                </div>
            </motion.div>

            {/* Recent Problems */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="glass-dark rounded-xl p-6 border border-white/10"
            >
                <h2 className="text-lg font-semibold text-white mb-4">Continue Practicing</h2>
                <div className="space-y-3">
                    {[
                        { name: 'Two Sum', difficulty: 'Easy', status: 'Completed', lang: 'Python' },
                        { name: 'Binary Search Tree', difficulty: 'Medium', status: 'In Progress', lang: 'Python' },
                        { name: 'Neural Network from Scratch', difficulty: 'Hard', status: 'Not Started', lang: 'Python' },
                    ].map((problem, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 cursor-pointer transition-colors">
                            <div>
                                <p className="font-medium text-white">{problem.name}</p>
                                <p className="text-xs text-dark-400">{problem.lang}</p>
                            </div>
                            <div className="flex items-center gap-3">
                                <span className={`px-2 py-1 rounded text-xs ${problem.difficulty === 'Easy' ? 'bg-green-500/20 text-green-400' :
                                        problem.difficulty === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                            'bg-red-500/20 text-red-400'
                                    }`}>
                                    {problem.difficulty}
                                </span>
                                <span className={`text-xs ${problem.status === 'Completed' ? 'text-green-400' :
                                        problem.status === 'In Progress' ? 'text-yellow-400' :
                                            'text-dark-400'
                                    }`}>
                                    {problem.status}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </motion.div>
        </div>
    );
}
