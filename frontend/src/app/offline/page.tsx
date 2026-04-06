'use client';

import { WifiOff, RefreshCw, Home } from 'lucide-react';

export default function OfflinePage() {
    const handleRetry = () => {
        window.location.reload();
    };

    return (
        <div className="min-h-screen bg-dark-300 flex items-center justify-center p-4">
            <div className="text-center max-w-md">
                {/* Offline Icon */}
                <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center">
                    <WifiOff className="w-12 h-12 text-gray-400" />
                </div>

                {/* Title */}
                <h1 className="text-3xl font-bold text-white mb-3">You're Offline</h1>

                {/* Description */}
                <p className="text-gray-400 mb-8">
                    Don't worry! Your progress is saved. Connect to the internet to continue your learning journey.
                </p>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <button
                        onClick={handleRetry}
                        className="flex items-center justify-center gap-2 px-6 py-3 bg-primary hover:bg-primary/80 text-white rounded-xl font-semibold transition-colors"
                    >
                        <RefreshCw className="w-5 h-5" />
                        Try Again
                    </button>

                    <button
                        onClick={() => window.location.href = '/'}
                        className="flex items-center justify-center gap-2 px-6 py-3 bg-dark-200 hover:bg-dark-100 text-gray-300 rounded-xl font-semibold transition-colors"
                    >
                        <Home className="w-5 h-5" />
                        Go Home
                    </button>
                </div>

                {/* Offline Features */}
                <div className="mt-12 p-6 rounded-xl bg-dark-200/50 border border-gray-700">
                    <h3 className="text-lg font-semibold text-white mb-4">Available Offline</h3>
                    <ul className="text-left text-gray-400 space-y-2">
                        <li className="flex items-center gap-2">
                            <span className="text-green-400">✓</span>
                            Review cached lessons
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-green-400">✓</span>
                            View your progress
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-green-400">✓</span>
                            Access downloaded content
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-yellow-400">⏳</span>
                            Quiz answers will sync when online
                        </li>
                    </ul>
                </div>

                {/* Tips */}
                <p className="mt-6 text-sm text-gray-500">
                    💡 Tip: Download lessons for offline access
                </p>
            </div>
        </div>
    );
}
