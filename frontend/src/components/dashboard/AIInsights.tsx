'use client';

import { motion } from 'framer-motion';
import { Brain, Sparkles, TrendingUp, AlertCircle } from 'lucide-react';

export function AIInsights() {
    const insights = [
        {
            type: 'recommendation',
            icon: <Sparkles className="w-4 h-4" />,
            title: 'Focus on Backpropagation',
            description: 'Based on your quiz results, spending more time on gradient calculations will boost your understanding.',
            color: 'secondary',
        },
        {
            type: 'strength',
            icon: <TrendingUp className="w-4 h-4" />,
            title: 'Strong in Data Structures',
            description: 'Your mastery in arrays and linked lists is excellent. Ready for trees and graphs!',
            color: 'accent',
        },
        {
            type: 'attention',
            icon: <AlertCircle className="w-4 h-4" />,
            title: 'Review Needed: SQL Joins',
            description: 'Memory retention dropping. A quick 10-minute review will reinforce this concept.',
            color: 'primary',
        },
    ];

    return (
        <div className="glass-dark rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-6">
                <Brain className="w-5 h-5 text-primary-400" />
                <h2 className="text-xl font-semibold text-white">AI Learning Insights</h2>
            </div>

            <div className="space-y-4">
                {insights.map((insight, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-colors"
                    >
                        <div className={`
              p-2 rounded-lg 
              ${insight.color === 'primary' && 'bg-primary-500/20 text-primary-400'}
              ${insight.color === 'secondary' && 'bg-secondary-500/20 text-secondary-400'}
              ${insight.color === 'accent' && 'bg-accent-500/20 text-accent-400'}
            `}>
                            {insight.icon}
                        </div>
                        <div className="flex-1">
                            <h3 className="font-medium text-white mb-1">{insight.title}</h3>
                            <p className="text-sm text-gray-400">{insight.description}</p>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
