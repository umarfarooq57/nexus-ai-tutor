'use client';

import { motion } from 'framer-motion';
import { Clock, BookOpen, Target, Zap } from 'lucide-react';

export function RecentActivity() {
    const activities = [
        {
            icon: <BookOpen className="w-4 h-4" />,
            title: 'Completed: Activation Functions',
            time: '2 hours ago',
            color: 'accent',
        },
        {
            icon: <Target className="w-4 h-4" />,
            title: 'Quiz: 85% on Gradient Descent',
            time: '3 hours ago',
            color: 'primary',
        },
        {
            icon: <Zap className="w-4 h-4" />,
            title: 'Achievement: Fast Learner',
            time: 'Yesterday',
            color: 'secondary',
        },
        {
            icon: <BookOpen className="w-4 h-4" />,
            title: 'Started: Loss Functions',
            time: 'Yesterday',
            color: 'primary',
        },
    ];

    return (
        <div className="glass-dark rounded-2xl p-6">
            <div className="flex items-center gap-2 mb-6">
                <Clock className="w-5 h-5 text-gray-400" />
                <h2 className="text-lg font-semibold text-white">Recent Activity</h2>
            </div>

            <div className="space-y-4">
                {activities.map((activity, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center gap-3"
                    >
                        <div className={`
              p-2 rounded-lg
              ${activity.color === 'primary' && 'bg-primary-500/20 text-primary-400'}
              ${activity.color === 'secondary' && 'bg-secondary-500/20 text-secondary-400'}
              ${activity.color === 'accent' && 'bg-accent-500/20 text-accent-400'}
            `}>
                            {activity.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm text-white truncate">{activity.title}</p>
                            <p className="text-xs text-gray-500">{activity.time}</p>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
