'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Trophy,
    Star,
    Flame,
    Target,
    Medal,
    Crown,
    Sparkles,
    Lock,
    Gift,
    TrendingUp,
    Calendar
} from 'lucide-react';

interface Achievement {
    id: string;
    name: string;
    description: string;
    icon: string;
    rarity: 'common' | 'rare' | 'epic' | 'legendary';
    xp: number;
    earned: boolean;
    earnedAt?: string;
    progress?: number;
}

interface Badge {
    id: string;
    name: string;
    icon: string;
    tier: number;
    earned: boolean;
}

interface DailyChallenge {
    id: string;
    title: string;
    description: string;
    icon: string;
    target: number;
    current: number;
    xpReward: number;
    completed: boolean;
}

interface LeaderboardEntry {
    rank: number;
    name: string;
    xp: number;
    level: number;
    isCurrentUser: boolean;
}

export default function AchievementsPage() {
    const [activeTab, setActiveTab] = useState<'achievements' | 'badges' | 'leaderboard' | 'challenges'>('achievements');
    const [xp, setXp] = useState(2450);
    const [level, setLevel] = useState(8);
    const [streak, setStreak] = useState(12);

    const [achievements] = useState<Achievement[]>([
        { id: '1', name: 'First Steps', description: 'Complete your first lesson', icon: '👣', rarity: 'common', xp: 25, earned: true, earnedAt: '2 weeks ago' },
        { id: '2', name: 'Week Warrior', description: '7 day learning streak', icon: '🔥', rarity: 'common', xp: 150, earned: true, earnedAt: '5 days ago' },
        { id: '3', name: 'Quiz Ace', description: 'Score 100% on a quiz', icon: '💯', rarity: 'rare', xp: 100, earned: true, earnedAt: 'Today' },
        { id: '4', name: 'Knowledge Seeker', description: 'Complete 50 lessons', icon: '🎓', rarity: 'rare', xp: 300, earned: false, progress: 72 },
        { id: '5', name: 'Monthly Master', description: '30 day learning streak', icon: '🔥', rarity: 'rare', xp: 500, earned: false, progress: 40 },
        { id: '6', name: 'Perfectionist', description: 'Get 10 perfect quiz scores', icon: '💎', rarity: 'epic', xp: 500, earned: false, progress: 30 },
        { id: '7', name: 'Legend', description: 'Reach Level 25', icon: '👑', rarity: 'legendary', xp: 2000, earned: false, progress: 32 },
        { id: '8', name: 'Unstoppable', description: '100 day learning streak', icon: '🏆', rarity: 'legendary', xp: 2000, earned: false, progress: 12 },
    ]);

    const [dailyChallenges] = useState<DailyChallenge[]>([
        { id: '1', title: 'Complete 3 lessons', description: 'Learn something new', icon: '📚', target: 3, current: 2, xpReward: 150, completed: false },
        { id: '2', title: 'Score 80%+ on quiz', description: 'Test your knowledge', icon: '🎯', target: 80, current: 85, xpReward: 100, completed: true },
        { id: '3', title: 'Study for 30 min', description: 'Stay focused', icon: '⏱️', target: 30, current: 22, xpReward: 75, completed: false },
    ]);

    const [leaderboard] = useState<LeaderboardEntry[]>([
        { rank: 1, name: 'Alex Chen', xp: 15420, level: 25, isCurrentUser: false },
        { rank: 2, name: 'Sarah Miller', xp: 12850, level: 22, isCurrentUser: false },
        { rank: 3, name: 'Mike Johnson', xp: 11200, level: 20, isCurrentUser: false },
        { rank: 4, name: 'Emma Wilson', xp: 9800, level: 18, isCurrentUser: false },
        { rank: 5, name: 'You', xp: 2450, level: 8, isCurrentUser: true },
    ]);

    const getRarityColor = (rarity: string) => {
        switch (rarity) {
            case 'common': return 'from-gray-400 to-gray-500';
            case 'rare': return 'from-blue-400 to-blue-600';
            case 'epic': return 'from-purple-400 to-purple-600';
            case 'legendary': return 'from-yellow-400 to-orange-500';
            default: return 'from-gray-400 to-gray-500';
        }
    };

    const getRarityBorder = (rarity: string) => {
        switch (rarity) {
            case 'common': return 'border-gray-500';
            case 'rare': return 'border-blue-500';
            case 'epic': return 'border-purple-500';
            case 'legendary': return 'border-yellow-500 animate-pulse';
            default: return 'border-gray-500';
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            {/* Header Stats */}
            <div className="glass rounded-2xl p-6 mb-6">
                <div className="flex items-center justify-between flex-wrap gap-4">
                    {/* Level & XP */}
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                                <span className="text-2xl font-bold text-white">{level}</span>
                            </div>
                            <div className="absolute -bottom-1 -right-1 w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                                <Star className="w-4 h-4 text-white" />
                            </div>
                        </div>
                        <div>
                            <div className="text-sm text-gray-400">Level {level}</div>
                            <div className="text-2xl font-bold text-white">{xp.toLocaleString()} XP</div>
                            <div className="w-48 h-2 bg-dark-200 rounded-full mt-2">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-primary to-secondary rounded-full"
                                    initial={{ width: 0 }}
                                    animate={{ width: '45%' }}
                                />
                            </div>
                            <div className="text-xs text-gray-500 mt-1">550 XP to Level {level + 1}</div>
                        </div>
                    </div>

                    {/* Streak */}
                    <div className="flex items-center gap-3 px-6 py-3 rounded-xl bg-gradient-to-r from-orange-500/20 to-red-500/20 border border-orange-500/30">
                        <Flame className="w-8 h-8 text-orange-400" />
                        <div>
                            <div className="text-2xl font-bold text-white">{streak}</div>
                            <div className="text-sm text-orange-400">Day Streak 🔥</div>
                        </div>
                    </div>

                    {/* Quick Stats */}
                    <div className="flex gap-4">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-white">{achievements.filter(a => a.earned).length}</div>
                            <div className="text-sm text-gray-400">Achievements</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-white">42</div>
                            <div className="text-sm text-gray-400">Lessons</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-white">15</div>
                            <div className="text-sm text-gray-400">Quizzes</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex gap-2 mb-6 overflow-x-auto">
                {[
                    { id: 'achievements', label: 'Achievements', icon: Trophy },
                    { id: 'badges', label: 'Badges', icon: Medal },
                    { id: 'challenges', label: 'Daily Challenges', icon: Target },
                    { id: 'leaderboard', label: 'Leaderboard', icon: Crown },
                ].map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-xl whitespace-nowrap transition-all ${activeTab === tab.id
                                ? 'bg-primary text-white'
                                : 'bg-dark-200 text-gray-400 hover:text-white'
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Content */}
            <AnimatePresence mode="wait">
                {activeTab === 'achievements' && (
                    <motion.div
                        key="achievements"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="grid grid-cols-1 md:grid-cols-2 gap-4"
                    >
                        {achievements.map((achievement) => (
                            <motion.div
                                key={achievement.id}
                                className={`glass rounded-xl p-4 border-2 ${achievement.earned ? getRarityBorder(achievement.rarity) : 'border-gray-700 opacity-75'
                                    }`}
                                whileHover={{ scale: 1.02 }}
                            >
                                <div className="flex items-start gap-4">
                                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${getRarityColor(achievement.rarity)} flex items-center justify-center text-2xl ${!achievement.earned && 'grayscale'}`}>
                                        {achievement.earned ? achievement.icon : <Lock className="w-6 h-6 text-gray-400" />}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                            <h3 className="font-semibold text-white">{achievement.name}</h3>
                                            <span className={`text-xs px-2 py-0.5 rounded-full bg-gradient-to-r ${getRarityColor(achievement.rarity)} text-white`}>
                                                {achievement.rarity}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-400 mt-1">{achievement.description}</p>

                                        {achievement.earned ? (
                                            <div className="flex items-center gap-2 mt-2 text-sm">
                                                <Sparkles className="w-4 h-4 text-yellow-400" />
                                                <span className="text-yellow-400">+{achievement.xp} XP</span>
                                                <span className="text-gray-500">• {achievement.earnedAt}</span>
                                            </div>
                                        ) : achievement.progress !== undefined && (
                                            <div className="mt-2">
                                                <div className="flex justify-between text-xs text-gray-500 mb-1">
                                                    <span>Progress</span>
                                                    <span>{achievement.progress}%</span>
                                                </div>
                                                <div className="h-1.5 bg-dark-200 rounded-full">
                                                    <div
                                                        className={`h-full rounded-full bg-gradient-to-r ${getRarityColor(achievement.rarity)}`}
                                                        style={{ width: `${achievement.progress}%` }}
                                                    />
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </motion.div>
                )}

                {activeTab === 'challenges' && (
                    <motion.div
                        key="challenges"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                    >
                        <div className="glass rounded-xl p-6 mb-4">
                            <div className="flex items-center gap-3 mb-4">
                                <Calendar className="w-6 h-6 text-primary" />
                                <h2 className="text-lg font-semibold text-white">Today's Challenges</h2>
                                <span className="ml-auto text-sm text-gray-400">Resets in 14h 32m</span>
                            </div>

                            <div className="space-y-4">
                                {dailyChallenges.map((challenge) => (
                                    <div
                                        key={challenge.id}
                                        className={`p-4 rounded-xl border-2 ${challenge.completed
                                                ? 'bg-green-500/10 border-green-500/50'
                                                : 'bg-dark-200/50 border-gray-700'
                                            }`}
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${challenge.completed ? 'bg-green-500' : 'bg-dark-100'
                                                }`}>
                                                {challenge.completed ? '✓' : challenge.icon}
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="font-semibold text-white">{challenge.title}</h3>
                                                <p className="text-sm text-gray-400">{challenge.description}</p>
                                                {!challenge.completed && (
                                                    <div className="mt-2">
                                                        <div className="h-2 bg-dark-200 rounded-full">
                                                            <div
                                                                className="h-full bg-primary rounded-full"
                                                                style={{ width: `${(challenge.current / challenge.target) * 100}%` }}
                                                            />
                                                        </div>
                                                        <div className="text-xs text-gray-500 mt-1">
                                                            {challenge.current}/{challenge.target}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                            <div className="text-right">
                                                <div className="flex items-center gap-1 text-yellow-400">
                                                    <Star className="w-4 h-4" />
                                                    <span className="font-semibold">{challenge.xpReward}</span>
                                                </div>
                                                <div className="text-xs text-gray-500">XP</div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Bonus Challenge */}
                        <div className="glass rounded-xl p-6 border-2 border-purple-500/50 bg-purple-500/5">
                            <div className="flex items-center gap-4">
                                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                                    <Gift className="w-7 h-7 text-white" />
                                </div>
                                <div className="flex-1">
                                    <h3 className="font-semibold text-white">Complete All Challenges</h3>
                                    <p className="text-sm text-gray-400">Finish all daily challenges for a bonus reward!</p>
                                </div>
                                <div className="text-right">
                                    <div className="flex items-center gap-1 text-purple-400">
                                        <Sparkles className="w-5 h-5" />
                                        <span className="font-bold text-xl">+200</span>
                                    </div>
                                    <div className="text-xs text-gray-500">Bonus XP</div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {activeTab === 'leaderboard' && (
                    <motion.div
                        key="leaderboard"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="glass rounded-xl p-6"
                    >
                        <div className="flex items-center gap-3 mb-6">
                            <TrendingUp className="w-6 h-6 text-primary" />
                            <h2 className="text-lg font-semibold text-white">Weekly Leaderboard</h2>
                        </div>

                        <div className="space-y-3">
                            {leaderboard.map((entry, idx) => (
                                <div
                                    key={entry.rank}
                                    className={`flex items-center gap-4 p-4 rounded-xl ${entry.isCurrentUser
                                            ? 'bg-primary/20 border-2 border-primary'
                                            : 'bg-dark-200/50'
                                        } ${idx < 3 ? 'border-l-4' : ''} ${idx === 0 ? 'border-l-yellow-500' :
                                            idx === 1 ? 'border-l-gray-400' :
                                                idx === 2 ? 'border-l-orange-600' : ''
                                        }`}
                                >
                                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${idx === 0 ? 'bg-yellow-500 text-white' :
                                            idx === 1 ? 'bg-gray-400 text-white' :
                                                idx === 2 ? 'bg-orange-600 text-white' :
                                                    'bg-dark-100 text-gray-400'
                                        }`}>
                                        {entry.rank}
                                    </div>
                                    <div className="flex-1">
                                        <div className="font-semibold text-white">{entry.name}</div>
                                        <div className="text-sm text-gray-400">Level {entry.level}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-bold text-white">{entry.xp.toLocaleString()}</div>
                                        <div className="text-sm text-gray-500">XP</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
