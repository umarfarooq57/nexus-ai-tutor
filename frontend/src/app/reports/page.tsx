'use client';

import { motion } from 'framer-motion';
import { FileText, Download, Calendar, TrendingUp, Award, Clock } from 'lucide-react';

export default function ReportsPage() {
    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between"
            >
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-primary-500/20 to-secondary-500/20 border border-white/10">
                        <FileText className="w-8 h-8 text-primary-400" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white">Reports</h1>
                        <p className="text-dark-400">Your learning analytics and progress reports</p>
                    </div>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg transition-colors text-white">
                    <Download className="w-4 h-4" />
                    Export All
                </button>
            </motion.div>

            {/* Report Types */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { title: 'Weekly Progress', desc: 'Summary of this week\'s learning', icon: Calendar, color: 'from-blue-500/20 to-cyan-500/20' },
                    { title: 'Performance Analysis', desc: 'Strengths and areas to improve', icon: TrendingUp, color: 'from-green-500/20 to-teal-500/20' },
                    { title: 'Certificate Reports', desc: 'Completed courses and achievements', icon: Award, color: 'from-purple-500/20 to-pink-500/20' },
                ].map((report, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className={`glass-dark rounded-xl p-6 border border-white/10 cursor-pointer hover:border-white/20 transition-all bg-gradient-to-br ${report.color}`}
                    >
                        <report.icon className="w-8 h-8 text-white mb-4" />
                        <h3 className="text-lg font-semibold text-white">{report.title}</h3>
                        <p className="text-sm text-dark-400 mt-2">{report.desc}</p>
                        <button className="mt-4 text-sm text-primary-400 hover:text-primary-300">
                            View Report →
                        </button>
                    </motion.div>
                ))}
            </div>

            {/* Recent Reports */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="glass-dark rounded-xl p-6 border border-white/10"
            >
                <h2 className="text-lg font-semibold text-white mb-4">Generated Reports</h2>
                <div className="space-y-3">
                    {[
                        { name: 'January 2026 Monthly Report', date: 'Jan 15, 2026', type: 'PDF', size: '2.4 MB' },
                        { name: 'Python Course Completion', date: 'Jan 10, 2026', type: 'PDF', size: '1.8 MB' },
                        { name: 'Q4 2025 Learning Summary', date: 'Dec 31, 2025', type: 'PDF', size: '4.2 MB' },
                    ].map((report, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                            <div className="flex items-center gap-4">
                                <FileText className="w-5 h-5 text-primary-400" />
                                <div>
                                    <p className="font-medium text-white">{report.name}</p>
                                    <div className="flex items-center gap-2 text-xs text-dark-400">
                                        <Clock className="w-3 h-3" />
                                        <span>{report.date}</span>
                                        <span>•</span>
                                        <span>{report.size}</span>
                                    </div>
                                </div>
                            </div>
                            <button className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                                <Download className="w-4 h-4 text-dark-400" />
                            </button>
                        </div>
                    ))}
                </div>
            </motion.div>
        </div>
    );
}
