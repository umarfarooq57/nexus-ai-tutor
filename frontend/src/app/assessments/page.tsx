'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Brain,
    Clock,
    CheckCircle,
    XCircle,
    ChevronRight,
    Lightbulb,
    BarChart2,
    Target,
    Zap
} from 'lucide-react';

interface Question {
    id: string;
    question: string;
    options: string[];
    difficulty: number;
}

interface QuizState {
    currentQuestion: number;
    answers: Record<string, number>;
    startTime: Date;
    isComplete: boolean;
}

interface QuizResult {
    score: number;
    correct: number;
    total: number;
    timeSpent: number;
    feedback: {
        questionId: string;
        isCorrect: boolean;
        correctAnswer: number;
        explanation: string;
    }[];
}

export default function AssessmentsPage() {
    const [mode, setMode] = useState<'menu' | 'quiz' | 'results'>('menu');
    const [questions, setQuestions] = useState<Question[]>([]);
    const [quizState, setQuizState] = useState<QuizState>({
        currentQuestion: 0,
        answers: {},
        startTime: new Date(),
        isComplete: false
    });
    const [results, setResults] = useState<QuizResult | null>(null);
    const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
    const [showHint, setShowHint] = useState(false);
    const [isAdaptive, setIsAdaptive] = useState(false);

    const quizOptions = [
        {
            title: 'Adaptive Quiz',
            description: 'AI-powered quiz that adapts to your level',
            icon: Brain,
            color: 'from-purple-500 to-pink-500',
            type: 'adaptive'
        },
        {
            title: 'Topic Practice',
            description: 'Practice specific topics you want to improve',
            icon: Target,
            color: 'from-blue-500 to-cyan-500',
            type: 'practice'
        },
        {
            title: 'Quick Challenge',
            description: '5 questions to test your knowledge',
            icon: Zap,
            color: 'from-orange-500 to-yellow-500',
            type: 'quick'
        },
        {
            title: 'Full Assessment',
            description: 'Comprehensive assessment of your skills',
            icon: BarChart2,
            color: 'from-green-500 to-emerald-500',
            type: 'full'
        }
    ];

    const startQuiz = async (type: string) => {
        setIsAdaptive(type === 'adaptive');

        // Mock questions - would fetch from API
        const mockQuestions: Question[] = [
            {
                id: 'q1',
                question: 'What is the primary purpose of gradient descent in machine learning?',
                options: [
                    'To increase the learning rate',
                    'To minimize the loss function',
                    'To add more layers to the network',
                    'To normalize the input data'
                ],
                difficulty: 0.4
            },
            {
                id: 'q2',
                question: 'Which activation function is commonly used in the output layer for binary classification?',
                options: [
                    'ReLU',
                    'Sigmoid',
                    'Tanh',
                    'Softmax'
                ],
                difficulty: 0.5
            },
            {
                id: 'q3',
                question: 'What does CNN stand for in deep learning?',
                options: [
                    'Computed Neural Network',
                    'Convolutional Neural Network',
                    'Connected Node Network',
                    'Cascaded Neuron Network'
                ],
                difficulty: 0.3
            },
            {
                id: 'q4',
                question: 'What is overfitting in machine learning?',
                options: [
                    'When the model performs poorly on training data',
                    'When the model is too simple to capture patterns',
                    'When the model performs well on training but poorly on test data',
                    'When the training takes too long'
                ],
                difficulty: 0.4
            },
            {
                id: 'q5',
                question: 'Which technique is used to prevent overfitting?',
                options: [
                    'Increasing the learning rate',
                    'Regularization',
                    'Removing all hidden layers',
                    'Using a larger dataset without augmentation'
                ],
                difficulty: 0.5
            }
        ];

        setQuestions(mockQuestions);
        setQuizState({
            currentQuestion: 0,
            answers: {},
            startTime: new Date(),
            isComplete: false
        });
        setMode('quiz');
    };

    const submitAnswer = () => {
        if (selectedAnswer === null) return;

        const currentQ = questions[quizState.currentQuestion];
        const newAnswers = { ...quizState.answers, [currentQ.id]: selectedAnswer };

        if (quizState.currentQuestion < questions.length - 1) {
            setQuizState({
                ...quizState,
                currentQuestion: quizState.currentQuestion + 1,
                answers: newAnswers
            });
            setSelectedAnswer(null);
            setShowHint(false);
        } else {
            // Quiz complete
            finishQuiz(newAnswers);
        }
    };

    const finishQuiz = (answers: Record<string, number>) => {
        const correctAnswers = [1, 1, 1, 2, 1]; // Mock correct answers
        const feedback = questions.map((q, idx) => ({
            questionId: q.id,
            isCorrect: answers[q.id] === correctAnswers[idx],
            correctAnswer: correctAnswers[idx],
            explanation: 'This is the correct answer because...'
        }));

        const correct = feedback.filter(f => f.isCorrect).length;
        const timeSpent = Math.floor((new Date().getTime() - quizState.startTime.getTime()) / 1000);

        setResults({
            score: Math.round((correct / questions.length) * 100),
            correct,
            total: questions.length,
            timeSpent,
            feedback
        });
        setMode('results');
    };

    const getDifficultyLabel = (difficulty: number) => {
        if (difficulty < 0.4) return { label: 'Easy', color: 'text-green-400' };
        if (difficulty < 0.7) return { label: 'Medium', color: 'text-yellow-400' };
        return { label: 'Hard', color: 'text-red-400' };
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="max-w-4xl mx-auto">
            <AnimatePresence mode="wait">
                {mode === 'menu' && (
                    <motion.div
                        key="menu"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-bold text-white mb-2">Assessments</h1>
                            <p className="text-gray-400">Test your knowledge with AI-powered quizzes</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {quizOptions.map((option) => (
                                <motion.button
                                    key={option.type}
                                    onClick={() => startQuiz(option.type)}
                                    className="glass rounded-2xl p-6 text-left hover:border-primary/50 border-2 border-transparent transition-all group"
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                >
                                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${option.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                                        <option.icon className="w-6 h-6 text-white" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-white mb-1">{option.title}</h3>
                                    <p className="text-sm text-gray-400">{option.description}</p>
                                </motion.button>
                            ))}
                        </div>

                        {/* Recent Results */}
                        <div className="mt-8 glass rounded-2xl p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">Recent Results</h2>
                            <div className="space-y-3">
                                {[
                                    { topic: 'Neural Networks', score: 85, date: 'Today' },
                                    { topic: 'Linear Regression', score: 92, date: 'Yesterday' },
                                    { topic: 'Python Basics', score: 78, date: '2 days ago' }
                                ].map((result, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-dark-200/50">
                                        <div>
                                            <div className="font-medium text-white">{result.topic}</div>
                                            <div className="text-sm text-gray-500">{result.date}</div>
                                        </div>
                                        <div className={`text-lg font-bold ${result.score >= 80 ? 'text-green-400' : 'text-yellow-400'}`}>
                                            {result.score}%
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                )}

                {mode === 'quiz' && questions.length > 0 && (
                    <motion.div
                        key="quiz"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                    >
                        {/* Quiz Header */}
                        <div className="glass rounded-2xl p-4 mb-6">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <span className="text-gray-400">
                                        Question {quizState.currentQuestion + 1} of {questions.length}
                                    </span>
                                    <span className={getDifficultyLabel(questions[quizState.currentQuestion].difficulty).color}>
                                        {getDifficultyLabel(questions[quizState.currentQuestion].difficulty).label}
                                    </span>
                                    {isAdaptive && (
                                        <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded-lg text-xs flex items-center gap-1">
                                            <Brain className="w-3 h-3" />
                                            Adaptive
                                        </span>
                                    )}
                                </div>
                                <div className="flex items-center gap-2 text-gray-400">
                                    <Clock className="w-4 h-4" />
                                    <span>{formatTime(Math.floor((new Date().getTime() - quizState.startTime.getTime()) / 1000))}</span>
                                </div>
                            </div>

                            {/* Progress bar */}
                            <div className="mt-3 h-2 bg-dark-200 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-primary to-secondary"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${((quizState.currentQuestion + 1) / questions.length) * 100}%` }}
                                />
                            </div>
                        </div>

                        {/* Question Card */}
                        <div className="glass rounded-2xl p-8 mb-6">
                            <h2 className="text-xl font-semibold text-white mb-6">
                                {questions[quizState.currentQuestion].question}
                            </h2>

                            <div className="space-y-3">
                                {questions[quizState.currentQuestion].options.map((option, idx) => (
                                    <motion.button
                                        key={idx}
                                        onClick={() => setSelectedAnswer(idx)}
                                        className={`w-full text-left p-4 rounded-xl border-2 transition-all ${selectedAnswer === idx
                                                ? 'border-primary bg-primary/10 text-white'
                                                : 'border-gray-700 bg-dark-200/50 text-gray-300 hover:border-gray-600'
                                            }`}
                                        whileHover={{ scale: 1.01 }}
                                        whileTap={{ scale: 0.99 }}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-semibold ${selectedAnswer === idx ? 'bg-primary text-white' : 'bg-dark-100 text-gray-400'
                                                }`}>
                                                {String.fromCharCode(65 + idx)}
                                            </div>
                                            <span>{option}</span>
                                        </div>
                                    </motion.button>
                                ))}
                            </div>

                            {/* Hint */}
                            {showHint && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="mt-4 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30"
                                >
                                    <div className="flex items-start gap-2">
                                        <Lightbulb className="w-5 h-5 text-yellow-400 mt-0.5" />
                                        <p className="text-sm text-yellow-200">
                                            Think about what gradient descent is trying to achieve in the optimization process.
                                        </p>
                                    </div>
                                </motion.div>
                            )}
                        </div>

                        {/* Actions */}
                        <div className="flex items-center justify-between">
                            <button
                                onClick={() => setShowHint(!showHint)}
                                className="flex items-center gap-2 px-4 py-2 text-gray-400 hover:text-yellow-400 transition-colors"
                            >
                                <Lightbulb className="w-4 h-4" />
                                {showHint ? 'Hide Hint' : 'Show Hint'}
                            </button>

                            <button
                                onClick={submitAnswer}
                                disabled={selectedAnswer === null}
                                className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${selectedAnswer !== null
                                        ? 'bg-primary hover:bg-primary/80 text-white'
                                        : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                    }`}
                            >
                                {quizState.currentQuestion < questions.length - 1 ? 'Next' : 'Finish'}
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </motion.div>
                )}

                {mode === 'results' && results && (
                    <motion.div
                        key="results"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        {/* Score Card */}
                        <div className="glass rounded-2xl p-8 text-center mb-6">
                            <div className={`text-6xl font-bold mb-2 ${results.score >= 80 ? 'text-green-400' : results.score >= 60 ? 'text-yellow-400' : 'text-red-400'}`}>
                                {results.score}%
                            </div>
                            <p className="text-gray-400 mb-4">
                                {results.correct} of {results.total} correct • {formatTime(results.timeSpent)}
                            </p>
                            <div className={`inline-block px-4 py-2 rounded-full ${results.score >= 80 ? 'bg-green-500/20 text-green-400' : results.score >= 60 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>
                                {results.score >= 80 ? '🎉 Excellent!' : results.score >= 60 ? '👍 Good job!' : '📚 Keep practicing!'}
                            </div>
                        </div>

                        {/* Question Review */}
                        <div className="glass rounded-2xl p-6 mb-6">
                            <h3 className="text-lg font-semibold text-white mb-4">Question Review</h3>
                            <div className="space-y-3">
                                {results.feedback.map((fb, idx) => (
                                    <div key={fb.questionId} className="flex items-center gap-3 p-3 rounded-lg bg-dark-200/50">
                                        {fb.isCorrect ? (
                                            <CheckCircle className="w-5 h-5 text-green-400" />
                                        ) : (
                                            <XCircle className="w-5 h-5 text-red-400" />
                                        )}
                                        <span className="text-gray-300">Question {idx + 1}</span>
                                        <span className={fb.isCorrect ? 'text-green-400' : 'text-red-400'}>
                                            {fb.isCorrect ? 'Correct' : 'Incorrect'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-4">
                            <button
                                onClick={() => setMode('menu')}
                                className="flex-1 py-3 rounded-xl border border-gray-600 text-gray-300 hover:bg-dark-200 transition-colors"
                            >
                                Back to Menu
                            </button>
                            <button
                                onClick={() => startQuiz('adaptive')}
                                className="flex-1 py-3 rounded-xl bg-primary hover:bg-primary/80 text-white font-semibold transition-colors"
                            >
                                Try Again
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
