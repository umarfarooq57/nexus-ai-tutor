'use client';

import { motion } from 'framer-motion';
import { Settings as SettingsIcon, User, Bell, Palette, Shield, Globe, Moon, Volume2 } from 'lucide-react';

export default function SettingsPage() {
    return (
        <div className="space-y-8 max-w-4xl">
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-4"
            >
                <div className="p-3 rounded-xl bg-gradient-to-br from-dark-600/50 to-dark-700/50 border border-white/10">
                    <SettingsIcon className="w-8 h-8 text-dark-300" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-white">Settings</h1>
                    <p className="text-dark-400">Customize your learning experience</p>
                </div>
            </motion.div>

            {/* Settings Sections */}
            <div className="space-y-6">
                {/* Profile */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass-dark rounded-xl p-6 border border-white/10"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <User className="w-5 h-5 text-primary-400" />
                        <h2 className="text-lg font-semibold text-white">Profile</h2>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <label className="text-sm text-dark-400">Display Name</label>
                            <input type="text" className="mt-1 w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-primary-500" placeholder="Your name" />
                        </div>
                        <div>
                            <label className="text-sm text-dark-400">Email</label>
                            <input type="email" className="mt-1 w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-primary-500" placeholder="your@email.com" />
                        </div>
                    </div>
                </motion.div>

                {/* Notifications */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-dark rounded-xl p-6 border border-white/10"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <Bell className="w-5 h-5 text-yellow-400" />
                        <h2 className="text-lg font-semibold text-white">Notifications</h2>
                    </div>
                    <div className="space-y-4">
                        {[
                            { label: 'Email notifications', desc: 'Receive updates via email' },
                            { label: 'Push notifications', desc: 'Browser push notifications' },
                            { label: 'Learning reminders', desc: 'Daily study reminders' },
                        ].map((item, idx) => (
                            <div key={idx} className="flex items-center justify-between">
                                <div>
                                    <p className="text-white">{item.label}</p>
                                    <p className="text-xs text-dark-400">{item.desc}</p>
                                </div>
                                <div className="w-11 h-6 bg-primary-500 rounded-full relative cursor-pointer">
                                    <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1" />
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* Appearance */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="glass-dark rounded-xl p-6 border border-white/10"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <Palette className="w-5 h-5 text-secondary-400" />
                        <h2 className="text-lg font-semibold text-white">Appearance</h2>
                    </div>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Moon className="w-4 h-4 text-dark-400" />
                                <span className="text-white">Dark Mode</span>
                            </div>
                            <div className="w-11 h-6 bg-primary-500 rounded-full relative cursor-pointer">
                                <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1" />
                            </div>
                        </div>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Volume2 className="w-4 h-4 text-dark-400" />
                                <span className="text-white">Sound Effects</span>
                            </div>
                            <div className="w-11 h-6 bg-white/20 rounded-full relative cursor-pointer">
                                <div className="w-4 h-4 bg-white rounded-full absolute left-1 top-1" />
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Save Button */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="flex justify-end"
                >
                    <button className="px-6 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg transition-colors text-white font-medium">
                        Save Changes
                    </button>
                </motion.div>
            </div>
        </div>
    );
}
