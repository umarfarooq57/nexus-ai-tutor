'use client';

import { motion } from 'framer-motion';
import { HelpCircle, Book, MessageSquare, Video, Mail, ExternalLink } from 'lucide-react';

export default function HelpPage() {
    return (
        <div className="space-y-8">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-4"
            >
                <div className="p-3 rounded-xl bg-gradient-to-br from-accent-500/20 to-secondary-500/20 border border-white/10">
                    <HelpCircle className="w-8 h-8 text-accent-400" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-white">Help Center</h1>
                    <p className="text-dark-400">Get support and learn how to use NEXUS AI</p>
                </div>
            </motion.div>

            {/* Quick Help Options */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                    { title: 'Documentation', desc: 'Browse our comprehensive guides', icon: Book, color: 'from-blue-500/20 to-cyan-500/20' },
                    { title: 'AI Assistant', desc: 'Ask our AI for instant help', icon: MessageSquare, color: 'from-purple-500/20 to-pink-500/20' },
                    { title: 'Video Tutorials', desc: 'Watch step-by-step guides', icon: Video, color: 'from-green-500/20 to-teal-500/20' },
                ].map((item, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className={`glass-dark rounded-xl p-6 border border-white/10 cursor-pointer hover:border-white/20 transition-all bg-gradient-to-br ${item.color}`}
                    >
                        <item.icon className="w-8 h-8 text-white mb-4" />
                        <h3 className="text-lg font-semibold text-white">{item.title}</h3>
                        <p className="text-sm text-dark-400 mt-2">{item.desc}</p>
                    </motion.div>
                ))}
            </div>

            {/* FAQ Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="glass-dark rounded-xl p-6 border border-white/10"
            >
                <h2 className="text-lg font-semibold text-white mb-4">Frequently Asked Questions</h2>
                <div className="space-y-3">
                    {[
                        'How do I start a new course?',
                        'How does the AI personalize my learning?',
                        'Can I download content for offline use?',
                        'How do I track my progress?',
                        'What certifications are available?',
                    ].map((question, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 cursor-pointer transition-colors">
                            <span className="text-white">{question}</span>
                            <ExternalLink className="w-4 h-4 text-dark-400" />
                        </div>
                    ))}
                </div>
            </motion.div>

            {/* Contact */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="glass-dark rounded-xl p-6 border border-white/10 text-center"
            >
                <Mail className="w-8 h-8 text-primary-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white">Still need help?</h3>
                <p className="text-dark-400 mt-2">Contact our support team at support@nexus-ai.com</p>
                <button className="mt-4 px-6 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg transition-colors text-white">
                    Contact Support
                </button>
            </motion.div>
        </div>
    );
}
