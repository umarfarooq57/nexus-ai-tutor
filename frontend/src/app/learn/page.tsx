'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    BookOpen,
    Play,
    CheckCircle,
    Lock,
    Clock,
    Star,
    ChevronRight,
    MessageSquare,
    Lightbulb,
    Code,
    Sparkles
} from 'lucide-react';
import { api } from '@/services/api';

interface Topic {
    id: string;
    title: string;
    description: string;
    status: 'completed' | 'in_progress' | 'locked';
    duration: number;
    difficulty: number;
}

interface Module {
    id: string;
    title: string;
    description: string;
    topics: Topic[];
    progress: number;
}

interface Course {
    id: string;
    title: string;
    description: string;
    modules: Module[];
    totalProgress: number;
    estimatedHours: number;
}

export default function LearnPage() {
    const [currentCourse, setCurrentCourse] = useState<Course | null>(null);
    const [activeModule, setActiveModule] = useState<string | null>(null);
    const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
    const [isLearning, setIsLearning] = useState(false);
    const [explanation, setExplanation] = useState<string>('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        // Load current course
        loadCurrentCourse();
    }, []);

    const loadCurrentCourse = async () => {
        try {
            const enrollments = await api.getCourseEnrollments();
            if (enrollments.data.length > 0) {
                const courseId = enrollments.data[0].course.id;
                const courseData = await api.getCourse(courseId);
                setCurrentCourse({
                    ...courseData.data,
                    modules: courseData.data.modules || [],
                    totalProgress: 35,
                    estimatedHours: 40
                });
                if (courseData.data.modules?.length > 0) {
                    setActiveModule(courseData.data.modules[0].id);
                }
            }
        } catch (error) {
            // Use mock data for demo
            setCurrentCourse({
                id: '1',
                title: 'Complete Machine Learning Mastery',
                description: 'Master machine learning from fundamentals to advanced techniques',
                estimatedHours: 40,
                totalProgress: 35,
                modules: [
                    {
                        id: 'm1',
                        title: 'Foundations of ML',
                        description: 'Core concepts and mathematics',
                        progress: 80,
                        topics: [
                            { id: 't1', title: 'Linear Algebra Review', description: 'Vectors, matrices, and transformations', status: 'completed', duration: 45, difficulty: 0.3 },
                            { id: 't2', title: 'Probability & Statistics', description: 'Distributions, Bayes theorem', status: 'completed', duration: 60, difficulty: 0.4 },
                            { id: 't3', title: 'Calculus for ML', description: 'Gradients and optimization', status: 'in_progress', duration: 50, difficulty: 0.5 },
                            { id: 't4', title: 'Python for Data Science', description: 'NumPy, Pandas, Matplotlib', status: 'locked', duration: 40, difficulty: 0.3 },
                        ]
                    },
                    {
                        id: 'm2',
                        title: 'Supervised Learning',
                        description: 'Regression and classification algorithms',
                        progress: 20,
                        topics: [
                            { id: 't5', title: 'Linear Regression', description: 'Simple and multiple regression', status: 'in_progress', duration: 55, difficulty: 0.4 },
                            { id: 't6', title: 'Logistic Regression', description: 'Binary and multiclass classification', status: 'locked', duration: 50, difficulty: 0.5 },
                            { id: 't7', title: 'Decision Trees', description: 'Tree-based learning algorithms', status: 'locked', duration: 45, difficulty: 0.5 },
                            { id: 't8', title: 'Support Vector Machines', description: 'Maximum margin classifiers', status: 'locked', duration: 60, difficulty: 0.6 },
                        ]
                    },
                    {
                        id: 'm3',
                        title: 'Neural Networks',
                        description: 'Deep learning fundamentals',
                        progress: 0,
                        topics: [
                            { id: 't9', title: 'Perceptrons', description: 'Single layer neural networks', status: 'locked', duration: 40, difficulty: 0.5 },
                            { id: 't10', title: 'Backpropagation', description: 'Training neural networks', status: 'locked', duration: 60, difficulty: 0.7 },
                            { id: 't11', title: 'CNNs', description: 'Convolutional neural networks', status: 'locked', duration: 70, difficulty: 0.7 },
                            { id: 't12', title: 'RNNs & LSTMs', description: 'Sequence modeling', status: 'locked', duration: 65, difficulty: 0.8 },
                        ]
                    }
                ]
            });
            setActiveModule('m1');
        }
    };

    const startLearning = async (topic: Topic) => {
        setSelectedTopic(topic);
        setIsLearning(true);
        setIsLoading(true);

        try {
            const response = await api.explainConcept({ concept: topic.title });
            setExplanation(response.data.content);
        } catch (error) {
            // Mock explanation
            setExplanation(`
# ${topic.title}

## Introduction
${topic.description}

This is a fundamental concept that forms the basis for many advanced techniques in machine learning.

## Key Concepts

### Core Principles
Understanding this topic requires grasping several key ideas:

1. **Foundation**: The mathematical underpinnings
2. **Application**: How it's used in practice
3. **Implementation**: Code examples and best practices

### Mathematical Formulation

The core equation can be expressed as:

\`\`\`
y = f(x) + ε
\`\`\`

Where:
- y is the output
- x is the input
- f is the function we want to learn
- ε is the error term

## Practical Example

\`\`\`python
import numpy as np
from sklearn.linear_model import LinearRegression

# Sample data
X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6, 8])

# Train model
model = LinearRegression()
model.fit(X, y)

# Predict
print(model.predict([[5]]))  # Output: [10.]
\`\`\`

## Key Takeaways
- This concept is essential for understanding more advanced topics
- Practice with real datasets to solidify understanding
- Connect this to previously learned material
      `);
        }
        setIsLoading(false);
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed': return <CheckCircle className="w-5 h-5 text-green-400" />;
            case 'in_progress': return <Play className="w-5 h-5 text-primary" />;
            default: return <Lock className="w-5 h-5 text-gray-500" />;
        }
    };

    const getDifficultyColor = (difficulty: number) => {
        if (difficulty < 0.4) return 'bg-green-500';
        if (difficulty < 0.7) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    if (!currentCourse) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <BookOpen className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <h2 className="text-xl font-semibold text-gray-300">No Course Enrolled</h2>
                    <p className="text-gray-500 mt-2">Browse courses to get started</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto">
            <AnimatePresence mode="wait">
                {!isLearning ? (
                    <motion.div
                        key="course-view"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        {/* Course Header */}
                        <div className="glass rounded-2xl p-6 mb-6">
                            <div className="flex items-start justify-between">
                                <div>
                                    <h1 className="text-2xl font-bold text-white mb-2">{currentCourse.title}</h1>
                                    <p className="text-gray-400">{currentCourse.description}</p>
                                    <div className="flex items-center gap-4 mt-4 text-sm text-gray-400">
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-4 h-4" />
                                            {currentCourse.estimatedHours}h total
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <Star className="w-4 h-4 text-yellow-400" />
                                            4.8 rating
                                        </span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-3xl font-bold text-primary">{currentCourse.totalProgress}%</div>
                                    <div className="text-sm text-gray-400">Complete</div>
                                </div>
                            </div>

                            {/* Progress bar */}
                            <div className="mt-4 h-2 bg-dark-200 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-primary to-secondary"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${currentCourse.totalProgress}%` }}
                                    transition={{ duration: 1, ease: "easeOut" }}
                                />
                            </div>
                        </div>

                        {/* Modules & Topics */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* Module List */}
                            <div className="space-y-3">
                                <h2 className="text-lg font-semibold text-white mb-4">Modules</h2>
                                {currentCourse.modules.map((module, idx) => (
                                    <motion.button
                                        key={module.id}
                                        onClick={() => setActiveModule(module.id)}
                                        className={`w-full text-left p-4 rounded-xl transition-all ${activeModule === module.id
                                                ? 'glass-dark border-2 border-primary'
                                                : 'glass hover:border-gray-600 border-2 border-transparent'
                                            }`}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-sm text-gray-400">Module {idx + 1}</span>
                                            <span className="text-sm font-medium text-primary">{module.progress}%</span>
                                        </div>
                                        <h3 className="font-semibold text-white">{module.title}</h3>
                                        <p className="text-sm text-gray-400 mt-1">{module.description}</p>
                                        <div className="mt-3 h-1 bg-dark-200 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-primary"
                                                style={{ width: `${module.progress}%` }}
                                            />
                                        </div>
                                    </motion.button>
                                ))}
                            </div>

                            {/* Topics List */}
                            <div className="lg:col-span-2">
                                <h2 className="text-lg font-semibold text-white mb-4">Topics</h2>
                                <div className="space-y-3">
                                    {currentCourse.modules
                                        .find(m => m.id === activeModule)
                                        ?.topics.map((topic) => (
                                            <motion.div
                                                key={topic.id}
                                                className={`glass rounded-xl p-4 ${topic.status === 'locked' ? 'opacity-60' : ''
                                                    }`}
                                                whileHover={topic.status !== 'locked' ? { scale: 1.01 } : {}}
                                            >
                                                <div className="flex items-start justify-between">
                                                    <div className="flex items-start gap-3">
                                                        {getStatusIcon(topic.status)}
                                                        <div>
                                                            <h3 className="font-semibold text-white">{topic.title}</h3>
                                                            <p className="text-sm text-gray-400 mt-1">{topic.description}</p>
                                                            <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                                                                <span className="flex items-center gap-1">
                                                                    <Clock className="w-3 h-3" />
                                                                    {topic.duration} min
                                                                </span>
                                                                <span className="flex items-center gap-1">
                                                                    <div className={`w-2 h-2 rounded-full ${getDifficultyColor(topic.difficulty)}`} />
                                                                    {topic.difficulty < 0.4 ? 'Easy' : topic.difficulty < 0.7 ? 'Medium' : 'Hard'}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {topic.status !== 'locked' && (
                                                        <motion.button
                                                            onClick={() => startLearning(topic)}
                                                            className="flex items-center gap-2 px-4 py-2 bg-primary/20 hover:bg-primary/30 text-primary rounded-lg transition-colors"
                                                            whileHover={{ scale: 1.05 }}
                                                            whileTap={{ scale: 0.95 }}
                                                        >
                                                            {topic.status === 'completed' ? 'Review' : 'Start'}
                                                            <ChevronRight className="w-4 h-4" />
                                                        </motion.button>
                                                    )}
                                                </div>
                                            </motion.div>
                                        ))}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="learning-view"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
                    >
                        {/* Main Content */}
                        <div className="lg:col-span-2">
                            <div className="glass rounded-2xl p-6">
                                <button
                                    onClick={() => setIsLearning(false)}
                                    className="text-gray-400 hover:text-white mb-4 flex items-center gap-2"
                                >
                                    ← Back to course
                                </button>

                                <h1 className="text-2xl font-bold text-white mb-6">{selectedTopic?.title}</h1>

                                {isLoading ? (
                                    <div className="flex items-center justify-center h-64">
                                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
                                    </div>
                                ) : (
                                    <div className="prose prose-invert prose-lg max-w-none">
                                        <div className="whitespace-pre-wrap text-gray-300 leading-relaxed">
                                            {explanation}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Sidebar */}
                        <div className="space-y-4">
                            {/* AI Assistant Quick Actions */}
                            <div className="glass rounded-xl p-4">
                                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                                    <Sparkles className="w-5 h-5 text-secondary" />
                                    AI Assistant
                                </h3>
                                <div className="space-y-2">
                                    <button className="w-full text-left p-3 rounded-lg bg-dark-200/50 hover:bg-dark-200 transition-colors text-sm text-gray-300 flex items-center gap-2">
                                        <MessageSquare className="w-4 h-4 text-primary" />
                                        Ask a question
                                    </button>
                                    <button className="w-full text-left p-3 rounded-lg bg-dark-200/50 hover:bg-dark-200 transition-colors text-sm text-gray-300 flex items-center gap-2">
                                        <Lightbulb className="w-4 h-4 text-yellow-400" />
                                        Get more examples
                                    </button>
                                    <button className="w-full text-left p-3 rounded-lg bg-dark-200/50 hover:bg-dark-200 transition-colors text-sm text-gray-300 flex items-center gap-2">
                                        <Code className="w-4 h-4 text-green-400" />
                                        Show code practice
                                    </button>
                                </div>
                            </div>

                            {/* Progress */}
                            <div className="glass rounded-xl p-4">
                                <h3 className="font-semibold text-white mb-3">Session Progress</h3>
                                <div className="space-y-3">
                                    <div>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-400">Reading Progress</span>
                                            <span className="text-primary">60%</span>
                                        </div>
                                        <div className="h-2 bg-dark-200 rounded-full">
                                            <div className="h-full w-3/5 bg-primary rounded-full" />
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-400">Time Spent</span>
                                            <span className="text-gray-300">12 min</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
