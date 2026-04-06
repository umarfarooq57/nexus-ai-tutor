'use client';

import { motion } from 'framer-motion';
import { Brain, Activity, Cpu, Sparkles, TrendingUp, Clock, Target } from 'lucide-react';

export default function DigitalTwinPage() {
    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-4"
            >
                <div className="p-3 rounded-xl bg-gradient-to-br from-secondary-500/20 to-primary-500/20 border border-white/10">
                    <Brain className="w-8 h-8 text-secondary-400" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-white">Digital Twin</h1>
                    <p className="text-dark-400">Your AI-powered learning profile</p>
                </div>
            </motion.div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass-dark rounded-xl p-6 border border-white/10"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <Activity className="w-5 h-5 text-green-400" />
                        <span className="text-sm text-dark-400">Cognitive State</span>
                    </div>
                    <p className="text-2xl font-bold text-white">Optimal</p>
                    <p className="text-xs text-green-400 mt-1">Ready for complex topics</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-dark rounded-xl p-6 border border-white/10"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <TrendingUp className="w-5 h-5 text-primary-400" />
                        <span className="text-sm text-dark-400">Learning Velocity</span>
                    </div>
                    <p className="text-2xl font-bold text-white">1.2x</p>
                    <p className="text-xs text-primary-400 mt-1">Above average pace</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="glass-dark rounded-xl p-6 border border-white/10"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <Target className="w-5 h-5 text-secondary-400" />
                        <span className="text-sm text-dark-400">Mastery Level</span>
                    </div>
                    <p className="text-2xl font-bold text-white">Intermediate</p>
                    <p className="text-xs text-secondary-400 mt-1">67% to Advanced</p>
                </motion.div>
            </div>

            {/* Brain Visualization Placeholder */}
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
                className="glass-dark rounded-xl p-8 border border-white/10 text-center"
            >
                <div className="flex flex-col items-center gap-4">
                    <div className="p-6 rounded-full bg-gradient-to-br from-primary-500/20 to-secondary-500/20">
                        <Cpu className="w-16 h-16 text-primary-400" />
                    </div>
                    <h2 className="text-xl font-semibold text-white">Neural Learning Map</h2>
                    <p className="text-dark-400 max-w-md">
                        Your personalized learning model is continuously adapting to optimize your educational journey.
                    </p>
                    <div className="flex items-center gap-2 text-sm text-green-400">
                        <Sparkles className="w-4 h-4" />
                        <span>AI Model Active</span>
                    </div>
                </div>
            </motion.div>

            {/* Recent Activity */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="glass-dark rounded-xl p-6 border border-white/10"
            >
                <h3 className="text-lg font-semibold text-white mb-4">Recent Learning Events</h3>
                <div className="space-y-3">
                    {[
                        { time: '2 hours ago', event: 'Completed Python Basics module', type: 'success' },
                        { time: '5 hours ago', event: 'Struggled with recursion concepts', type: 'warning' },
                        { time: '1 day ago', event: 'Achieved 90% on Data Structures quiz', type: 'success' },
                    ].map((item, idx) => (
                        <div key={idx} className="flex items-center gap-4 p-3 rounded-lg bg-white/5">
                            <Clock className="w-4 h-4 text-dark-400" />
                            <span className="text-xs text-dark-400 w-24">{item.time}</span>
                            <span className={`text-sm ${item.type === 'success' ? 'text-green-400' : 'text-yellow-400'}`}>
                                {item.event}
                            </span>
                        </div>
                    ))}
                </div>
            </motion.div>
        </div>
    );
}
