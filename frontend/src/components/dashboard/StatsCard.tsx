'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface StatsCardProps {
    icon: ReactNode;
    label: string;
    value: string;
    trend?: string;
    color?: 'primary' | 'secondary' | 'accent';
}

export function StatsCard({ icon, label, value, trend, color = 'primary' }: StatsCardProps) {
    const colorClasses = {
        primary: 'from-primary-500/20 to-primary-600/10 border-primary-500/30',
        secondary: 'from-secondary-500/20 to-secondary-600/10 border-secondary-500/30',
        accent: 'from-accent-500/20 to-accent-600/10 border-accent-500/30',
    };

    const iconColors = {
        primary: 'text-primary-400',
        secondary: 'text-secondary-400',
        accent: 'text-accent-400',
    };

    return (
        <motion.div
            whileHover={{ scale: 1.02, y: -2 }}
            className={cn(
                'relative overflow-hidden rounded-xl p-4 border backdrop-blur-sm',
                'bg-gradient-to-br',
                colorClasses[color]
            )}
        >
            <div className="flex items-center gap-3">
                <div className={cn('p-2 rounded-lg bg-white/5', iconColors[color])}>
                    {icon}
                </div>
                <div>
                    <p className="text-xs text-gray-400">{label}</p>
                    <div className="flex items-baseline gap-2">
                        <span className="text-xl font-bold text-white">{value}</span>
                        {trend && (
                            <span className={cn(
                                'text-xs',
                                trend.startsWith('+') ? 'text-green-400' :
                                    trend.startsWith('-') ? 'text-red-400' : 'text-gray-400'
                            )}>
                                {trend}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* Animated glow */}
            <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity">
                <div className={cn(
                    'absolute inset-0 blur-xl',
                    color === 'primary' && 'bg-primary-500/10',
                    color === 'secondary' && 'bg-secondary-500/10',
                    color === 'accent' && 'bg-accent-500/10'
                )} />
            </div>
        </motion.div>
    );
}
