'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Mic,
    MicOff,
    Send,
    Bot,
    User,
    Sparkles,
    Code,
    BookOpen,
    Brain,
    Volume2,
    VolumeX,
    RefreshCw,
    Settings,
    ChevronDown
} from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    audioUrl?: string;
    thoughts?: { thought: string; action?: string }[];
}

interface Agent {
    id: string;
    name: string;
    role: string;
    subject: string;
}

const AVAILABLE_AGENTS: Agent[] = [
    { id: 'ml', name: 'Dr. Neural', role: 'ML Expert', subject: 'Machine Learning' },
    { id: 'python', name: 'PyMaster', role: 'Python Expert', subject: 'Python Programming' },
    { id: 'math', name: 'Prof. Euler', role: 'Math Expert', subject: 'Mathematics' },
    { id: 'data', name: 'Dr. Data', role: 'Data Science Expert', subject: 'Data Science' },
    { id: 'devops', name: 'CloudOps', role: 'DevOps Expert', subject: 'DevOps & Cloud' },
    { id: 'socratic', name: 'Socrates AI', role: 'Socratic Tutor', subject: 'General' }
];

export default function AssistantPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: "Hello! I'm your AI learning assistant. I can help you with Machine Learning, Python, Mathematics, Data Science, and more. How can I help you today?",
            timestamp: new Date()
        }
    ]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState<Agent>(AVAILABLE_AGENTS[0]);
    const [showAgentSelector, setShowAgentSelector] = useState(false);
    const [audioEnabled, setAudioEnabled] = useState(true);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleSendMessage = async () => {
        if (!inputText.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputText,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        const messageToSend = inputText;
        setInputText('');
        setIsLoading(true);

        try {
            // Call Gemini API via backend
            const response = await fetch('http://localhost:8000/api/v1/agent/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: messageToSend,
                    subject: selectedAgent.subject,
                })
            });

            const data = await response.json();

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response || data.error || 'I apologize, but I could not process your request.',
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);

            // Text-to-speech if enabled
            if (audioEnabled && data.response) {
                await speakText(data.response);
            }
        } catch (error) {
            // Error response
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I could not connect to the AI service. Please check if the backend server is running.',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const getMockResponse = (input: string, agent: Agent): string => {
        // Keep responses concise and directly answer the question
        const lowerInput = input.toLowerCase();

        if (agent.id === 'ml') {
            if (lowerInput.includes('neural')) {
                return 'Neural networks are computing systems inspired by the brain, made of interconnected nodes (neurons) that process data in layers.';
            }
            return 'Machine Learning enables systems to learn patterns from data. What specific ML topic would you like to know about?';
        }

        if (agent.id === 'python') {
            if (lowerInput.includes('function')) {
                return 'In Python, functions are defined with `def`:\n\n```python\ndef greet(name):\n    return f"Hello, {name}!"\n```';
            }
            return 'I can help with Python! What specific code or concept do you need help with?';
        }

        if (agent.id === 'math') {
            return 'I can help solve math problems. Please share the specific equation or concept you need help with.';
        }

        // Default concise response
        return `I can help with that. Could you please be more specific about what aspect of "${input.substring(0, 30)}..." you need help with?`;
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
                await processVoiceInput(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (error) {
            console.error('Error starting recording:', error);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const processVoiceInput = async (audioBlob: Blob) => {
        setIsLoading(true);

        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');

            const response = await fetch('/api/v1/voice/transcribe/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: formData
            });

            const data = await response.json();

            if (data.text) {
                setInputText(data.text);
            }
        } catch (error) {
            console.error('Transcription error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const speakText = async (text: string) => {
        setIsSpeaking(true);

        try {
            const response = await fetch('/api/v1/voice/speak/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    text: text.substring(0, 500), // Limit text length
                    voice: 'professor'
                })
            });

            const data = await response.json();

            if (data.audio) {
                const audioData = atob(data.audio);
                const audioArray = new Uint8Array(audioData.length);
                for (let i = 0; i < audioData.length; i++) {
                    audioArray[i] = audioData.charCodeAt(i);
                }
                const audioBlob = new Blob([audioArray], { type: 'audio/mp3' });
                const audioUrl = URL.createObjectURL(audioBlob);

                const audio = new Audio(audioUrl);
                audio.onended = () => setIsSpeaking(false);
                audio.play();
            }
        } catch (error) {
            // Fallback to browser TTS
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.onend = () => setIsSpeaking(false);
                window.speechSynthesis.speak(utterance);
            }
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-120px)]">
            {/* Header */}
            <div className="glass rounded-xl p-4 mb-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                            <Bot className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-lg font-semibold text-white">AI Learning Assistant</h1>
                            <p className="text-sm text-gray-400">Powered by Agentic AI</p>
                        </div>
                    </div>

                    {/* Agent Selector */}
                    <div className="relative">
                        <button
                            onClick={() => setShowAgentSelector(!showAgentSelector)}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-dark-200 hover:bg-dark-100 transition-colors"
                        >
                            <Sparkles className="w-4 h-4 text-secondary" />
                            <span className="text-white">{selectedAgent.name}</span>
                            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${showAgentSelector ? 'rotate-180' : ''}`} />
                        </button>

                        <AnimatePresence>
                            {showAgentSelector && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="absolute right-0 mt-2 w-64 glass rounded-xl p-2 z-50"
                                >
                                    {AVAILABLE_AGENTS.map((agent) => (
                                        <button
                                            key={agent.id}
                                            onClick={() => {
                                                setSelectedAgent(agent);
                                                setShowAgentSelector(false);
                                            }}
                                            className={`w-full text-left p-3 rounded-lg transition-colors ${selectedAgent.id === agent.id
                                                ? 'bg-primary/20 text-primary'
                                                : 'hover:bg-dark-200 text-gray-300'
                                                }`}
                                        >
                                            <div className="font-medium">{agent.name}</div>
                                            <div className="text-xs text-gray-500">{agent.role}</div>
                                        </button>
                                    ))}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Audio Toggle */}
                    <button
                        onClick={() => setAudioEnabled(!audioEnabled)}
                        className={`p-2 rounded-lg transition-colors ${audioEnabled ? 'bg-primary/20 text-primary' : 'bg-dark-200 text-gray-400'}`}
                    >
                        {audioEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto glass rounded-xl p-4 mb-4 space-y-4">
                {messages.map((message) => (
                    <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex items-start gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${message.role === 'user' ? 'bg-primary' : 'bg-gradient-to-br from-secondary to-purple-600'
                            }`}>
                            {message.role === 'user' ? (
                                <User className="w-4 h-4 text-white" />
                            ) : (
                                <Bot className="w-4 h-4 text-white" />
                            )}
                        </div>

                        <div className={`max-w-[80%] ${message.role === 'user' ? 'text-right' : ''}`}>
                            <div className={`p-4 rounded-2xl ${message.role === 'user'
                                ? 'bg-primary-500 text-white rounded-br-none'
                                : 'bg-slate-700 text-white rounded-bl-none'
                                }`}>
                                <div className="whitespace-pre-wrap">{message.content}</div>
                            </div>

                            {message.thoughts && message.thoughts.length > 0 && (
                                <div className="mt-2 p-2 rounded-lg bg-dark-300/50 text-xs text-gray-500">
                                    <div className="flex items-center gap-1 mb-1">
                                        <Brain className="w-3 h-3" />
                                        <span>Agent Thoughts</span>
                                    </div>
                                    {message.thoughts.map((t, i) => (
                                        <div key={i} className="ml-2">{t.thought}</div>
                                    ))}
                                </div>
                            )}

                            <div className="text-xs text-gray-500 mt-1">
                                {message.timestamp.getHours().toString().padStart(2, '0')}:{message.timestamp.getMinutes().toString().padStart(2, '0')}
                            </div>
                        </div>
                    </motion.div>
                ))}

                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-3"
                    >
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-secondary to-purple-600 flex items-center justify-center">
                            <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex items-center gap-2 px-4 py-3 rounded-2xl bg-dark-200 rounded-bl-none">
                            <RefreshCw className="w-4 h-4 text-primary animate-spin" />
                            <span className="text-gray-400">Thinking...</span>
                        </div>
                    </motion.div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="glass rounded-xl p-4">
                <div className="flex items-center gap-3">
                    {/* Voice Record Button */}
                    <motion.button
                        onClick={isRecording ? stopRecording : startRecording}
                        className={`p-3 rounded-xl transition-colors ${isRecording
                            ? 'bg-red-500 text-white animate-pulse'
                            : 'bg-dark-200 text-gray-400 hover:text-white'
                            }`}
                        whileTap={{ scale: 0.95 }}
                    >
                        {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                    </motion.button>

                    {/* Text Input */}
                    <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder="Ask me anything about learning..."
                        className="flex-1 bg-slate-800 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-primary-500 transition-colors"
                    />

                    {/* Send Button */}
                    <motion.button
                        onClick={handleSendMessage}
                        disabled={!inputText.trim() || isLoading}
                        className={`p-3 rounded-xl transition-colors ${inputText.trim() && !isLoading
                            ? 'bg-primary text-white hover:bg-primary/80'
                            : 'bg-dark-200 text-gray-500 cursor-not-allowed'
                            }`}
                        whileTap={{ scale: 0.95 }}
                    >
                        <Send className="w-5 h-5" />
                    </motion.button>
                </div>

                {/* Quick Actions */}
                <div className="flex items-center gap-2 mt-3">
                    <span className="text-xs text-gray-500">Quick:</span>
                    {['Explain a concept', 'Help with code', 'Quiz me', 'Create study plan'].map((action) => (
                        <button
                            key={action}
                            onClick={() => setInputText(action)}
                            className="px-3 py-1 rounded-full bg-dark-200 text-xs text-gray-400 hover:bg-dark-100 hover:text-white transition-colors"
                        >
                            {action}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
