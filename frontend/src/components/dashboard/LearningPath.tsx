'use client';

import { motion } from 'framer-motion';
import { CheckCircle, Circle, Lock, ArrowRight } from 'lucide-react';

export function LearningPath() {
    const pathSteps = [
        { title: 'Python Fundamentals', status: 'completed', duration: '8h' },
        { title: 'Data Structures', status: 'completed', duration: '12h' },
        { title: 'Machine Learning Basics', status: 'current', duration: '15h', progress: 65 },
        { title: 'Deep Learning', status: 'locked', duration: '20h' },
        { title: 'Neural Networks', status: 'locked', duration: '18h' },
    ];

    return (
        <div className="glass-dark rounded-2xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">Your Learning Path</h2>
                <button className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1">
                    View Full Path <ArrowRight className="w-4 h-4" />
                </button>
            </div>

            <div className="relative">
                {/* Connection Line */}
                <div className="absolute left-[19px] top-8 bottom-8 w-0.5 bg-white/10" />

                <div className="space-y-4">
                    {pathSteps.map((step, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className={`
                flex items-center gap-4 p-4 rounded-xl transition-all
                ${step.status === 'current' && 'bg-primary-500/10 border border-primary-500/30'}
                ${step.status === 'completed' && 'bg-white/5'}
                ${step.status === 'locked' && 'opacity-50'}
              `}
                        >
                            {/* Status Icon */}
                            <div className="relative z-10">
                                {step.status === 'completed' && (
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        className="w-10 h-10 rounded-full bg-accent-500/20 flex items-center justify-center"
                                    >
                                        <CheckCircle className="w-5 h-5 text-accent-400" />
                                    </motion.div>
                                )}
                                {step.status === 'current' && (
                                    <motion.div
                                        animate={{ scale: [1, 1.1, 1] }}
                                        transition={{ duration: 2, repeat: Infinity }}
                                        className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center border-2 border-primary-400"
                                    >
                                        <Circle className="w-5 h-5 text-primary-400 fill-primary-400" />
                                    </motion.div>
                                )}
                                {step.status === 'locked' && (
                                    <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                                        <Lock className="w-4 h-4 text-gray-500" />
                                    </div>
                                )}
                            </div>

                            {/* Content */}
                            <div className="flex-1">
                                <h3 className={`font-medium ${step.status === 'locked' ? 'text-gray-500' : 'text-white'}`}>
                                    {step.title}
                                </h3>
                                <p className="text-sm text-gray-500">{step.duration} estimated</p>
                            </div>

                            {/* Progress for current */}
                            {step.status === 'current' && step.progress && (
                                <div className="flex items-center gap-2">
                                    <div className="w-20 h-2 bg-white/10 rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${step.progress}%` }}
                                            transition={{ duration: 1 }}
                                            className="h-full bg-primary-500 rounded-full"
                                        />
                                    </div>
                                    <span className="text-sm text-primary-400">{step.progress}%</span>
                                </div>
                            )}
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}
