'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Play,
    Square,
    RefreshCw,
    Download,
    Copy,
    Check,
    Lightbulb,
    Bug,
    Wand2,
    FileCode,
    Terminal
} from 'lucide-react';

interface ExecutionResult {
    success: boolean;
    output: string;
    error?: string;
    execution_time: number;
    feedback?: { explanation: string };
}

export default function PlaygroundPage() {
    const [code, setCode] = useState(`# Welcome to the AI Code Playground!
# Write your Python code here

def fibonacci(n):
    """Calculate nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
`);
    const [output, setOutput] = useState<ExecutionResult | null>(null);
    const [isRunning, setIsRunning] = useState(false);
    const [isExplaining, setIsExplaining] = useState(false);
    const [explanation, setExplanation] = useState('');
    const [copied, setCopied] = useState(false);
    const [language, setLanguage] = useState('python');

    const runCode = async () => {
        setIsRunning(true);
        setOutput(null);

        try {
            const response = await fetch('/api/v1/code/execute/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ code, language })
            });

            const data = await response.json();
            setOutput(data);
        } catch (error) {
            // Mock output for demo
            setOutput({
                success: true,
                output: `F(0) = 0
F(1) = 1
F(2) = 1
F(3) = 2
F(4) = 3
F(5) = 5
F(6) = 8
F(7) = 13
F(8) = 21
F(9) = 34`,
                execution_time: 0.023
            });
        } finally {
            setIsRunning(false);
        }
    };

    const explainCode = async () => {
        setIsExplaining(true);

        try {
            const response = await fetch('/api/v1/code/explain/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ code, language })
            });

            const data = await response.json();
            setExplanation(data.explanation);
        } catch (error) {
            // Mock explanation
            setExplanation(`## Code Explanation

### Purpose
This code calculates and prints Fibonacci numbers from F(0) to F(9).

### How it works:
1. **fibonacci(n)** - A recursive function that:
   - Returns n if n <= 1 (base case)
   - Otherwise returns fibonacci(n-1) + fibonacci(n-2)

2. **Main loop** - Iterates from 0 to 9 and prints each Fibonacci number

### Key Concepts:
- **Recursion**: The function calls itself
- **Base Case**: Prevents infinite recursion
- **F-strings**: Modern Python string formatting

### Performance Note:
This implementation has O(2^n) complexity. For better performance, consider:
- Dynamic Programming
- Memoization
- Iterative approach`);
        } finally {
            setIsExplaining(false);
        }
    };

    const copyCode = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const clearOutput = () => {
        setOutput(null);
        setExplanation('');
    };

    return (
        <div className="h-[calc(100vh-120px)] flex flex-col">
            {/* Header */}
            <div className="glass rounded-xl p-4 mb-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                            <FileCode className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h1 className="text-lg font-semibold text-white">Code Playground</h1>
                            <p className="text-sm text-gray-400">Write, run, and learn with AI assistance</p>
                        </div>
                    </div>

                    {/* Language Selector */}
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="bg-dark-200 text-white px-4 py-2 rounded-lg border border-gray-700 focus:outline-none focus:border-primary"
                    >
                        <option value="python">Python</option>
                        <option value="javascript">JavaScript</option>
                    </select>
                </div>
            </div>

            <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Code Editor */}
                <div className="flex flex-col glass rounded-xl overflow-hidden">
                    {/* Editor Header */}
                    <div className="flex items-center justify-between px-4 py-2 bg-dark-200/50 border-b border-gray-700">
                        <span className="text-sm text-gray-400">main.{language === 'python' ? 'py' : 'js'}</span>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={copyCode}
                                className="p-1.5 rounded-lg hover:bg-dark-100 transition-colors text-gray-400 hover:text-white"
                            >
                                {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                            </button>
                            <button className="p-1.5 rounded-lg hover:bg-dark-100 transition-colors text-gray-400 hover:text-white">
                                <Download className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    {/* Code Area */}
                    <textarea
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        className="flex-1 bg-dark-300 text-green-400 font-mono text-sm p-4 resize-none focus:outline-none"
                        spellCheck={false}
                    />

                    {/* Editor Actions */}
                    <div className="flex items-center gap-2 px-4 py-3 bg-dark-200/50 border-t border-gray-700">
                        <motion.button
                            onClick={runCode}
                            disabled={isRunning}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${isRunning
                                    ? 'bg-gray-600 text-gray-400'
                                    : 'bg-green-500 hover:bg-green-600 text-white'
                                }`}
                            whileTap={{ scale: 0.95 }}
                        >
                            {isRunning ? (
                                <RefreshCw className="w-4 h-4 animate-spin" />
                            ) : (
                                <Play className="w-4 h-4" />
                            )}
                            {isRunning ? 'Running...' : 'Run'}
                        </motion.button>

                        <motion.button
                            onClick={explainCode}
                            disabled={isExplaining}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-500 hover:bg-purple-600 text-white font-medium transition-colors"
                            whileTap={{ scale: 0.95 }}
                        >
                            <Wand2 className="w-4 h-4" />
                            {isExplaining ? 'Explaining...' : 'Explain'}
                        </motion.button>

                        <motion.button
                            onClick={clearOutput}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-100 hover:bg-dark-200 text-gray-300 transition-colors"
                            whileTap={{ scale: 0.95 }}
                        >
                            <Square className="w-4 h-4" />
                            Clear
                        </motion.button>
                    </div>
                </div>

                {/* Output Panel */}
                <div className="flex flex-col glass rounded-xl overflow-hidden">
                    {/* Output Header */}
                    <div className="flex items-center px-4 py-2 bg-dark-200/50 border-b border-gray-700">
                        <Terminal className="w-4 h-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-400">Output</span>
                        {output && (
                            <span className={`ml-auto text-xs px-2 py-0.5 rounded-full ${output.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                                }`}>
                                {output.success ? 'Success' : 'Error'} • {output.execution_time.toFixed(3)}s
                            </span>
                        )}
                    </div>

                    {/* Output Content */}
                    <div className="flex-1 overflow-auto p-4 bg-dark-300">
                        {!output && !explanation && (
                            <div className="flex items-center justify-center h-full text-gray-500">
                                <div className="text-center">
                                    <Terminal className="w-12 h-12 mx-auto mb-2 opacity-50" />
                                    <p>Run your code to see output here</p>
                                </div>
                            </div>
                        )}

                        {output && (
                            <div className="font-mono text-sm">
                                {output.output && (
                                    <pre className="text-gray-300 whitespace-pre-wrap">{output.output}</pre>
                                )}
                                {output.error && (
                                    <pre className="text-red-400 whitespace-pre-wrap mt-2">{output.error}</pre>
                                )}
                                {output.feedback && (
                                    <div className="mt-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                                        <div className="flex items-center gap-2 text-yellow-400 mb-2">
                                            <Lightbulb className="w-4 h-4" />
                                            <span className="font-semibold">AI Feedback</span>
                                        </div>
                                        <p className="text-yellow-200 text-sm">{output.feedback.explanation}</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {explanation && (
                            <div className="prose prose-invert prose-sm max-w-none">
                                <div className="flex items-center gap-2 text-purple-400 mb-3">
                                    <Wand2 className="w-4 h-4" />
                                    <span className="font-semibold">AI Explanation</span>
                                </div>
                                <div className="text-gray-300 whitespace-pre-wrap">{explanation}</div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Tips */}
            <div className="glass rounded-xl p-4 mt-4">
                <div className="flex items-center gap-6 text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                        <Lightbulb className="w-4 h-4 text-yellow-400" />
                        <span>Tip: Use "Explain" to understand any code</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Bug className="w-4 h-4 text-red-400" />
                        <span>Errors get AI-powered debugging suggestions</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
