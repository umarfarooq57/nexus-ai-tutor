'use client';

import { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, Activity, Zap, Heart } from 'lucide-react';

export function DigitalTwinVisualization() {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Neural network visualization
        const nodes: { x: number; y: number; vx: number; vy: number; connections: number[] }[] = [];
        const numNodes = 30;

        // Initialize nodes
        for (let i = 0; i < numNodes; i++) {
            nodes.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                connections: [],
            });
        }

        // Create connections
        nodes.forEach((node, i) => {
            const numConnections = Math.floor(Math.random() * 3) + 1;
            for (let j = 0; j < numConnections; j++) {
                const target = Math.floor(Math.random() * numNodes);
                if (target !== i) {
                    node.connections.push(target);
                }
            }
        });

        let animationId: number;
        let time = 0;

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            time += 0.01;

            // Update and draw
            nodes.forEach((node, i) => {
                // Update position
                node.x += node.vx;
                node.y += node.vy;

                // Bounce off walls
                if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
                if (node.y < 0 || node.y > canvas.height) node.vy *= -1;

                // Draw connections
                node.connections.forEach((targetIndex) => {
                    const target = nodes[targetIndex];
                    const gradient = ctx.createLinearGradient(node.x, node.y, target.x, target.y);

                    const alpha = 0.1 + Math.sin(time + i * 0.1) * 0.05;
                    gradient.addColorStop(0, `rgba(12, 141, 230, ${alpha})`);
                    gradient.addColorStop(1, `rgba(168, 85, 247, ${alpha})`);

                    ctx.beginPath();
                    ctx.strokeStyle = gradient;
                    ctx.lineWidth = 1;
                    ctx.moveTo(node.x, node.y);
                    ctx.lineTo(target.x, target.y);
                    ctx.stroke();
                });

                // Draw node
                const pulseSize = 3 + Math.sin(time * 2 + i) * 1;
                const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, pulseSize * 2);
                gradient.addColorStop(0, 'rgba(12, 141, 230, 0.8)');
                gradient.addColorStop(0.5, 'rgba(168, 85, 247, 0.4)');
                gradient.addColorStop(1, 'rgba(168, 85, 247, 0)');

                ctx.beginPath();
                ctx.fillStyle = gradient;
                ctx.arc(node.x, node.y, pulseSize, 0, Math.PI * 2);
                ctx.fill();
            });

            animationId = requestAnimationFrame(animate);
        };

        animate();

        return () => cancelAnimationFrame(animationId);
    }, []);

    return (
        <div className="glass-dark rounded-2xl p-6 overflow-hidden">
            <div className="flex items-center gap-2 mb-4">
                <Brain className="w-5 h-5 text-primary-400" />
                <h2 className="text-lg font-semibold text-white">Your Digital Twin</h2>
            </div>

            {/* Neural Network Visualization */}
            <div className="relative h-48 mb-4 rounded-xl overflow-hidden bg-dark-900/50">
                <canvas
                    ref={canvasRef}
                    width={280}
                    height={192}
                    className="w-full h-full"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-dark-900/80 to-transparent" />
                <div className="absolute bottom-2 left-2 right-2 flex items-center justify-center">
                    <motion.div
                        animate={{ scale: [1, 1.05, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="px-3 py-1 rounded-full bg-primary-500/20 border border-primary-500/30 text-xs text-primary-400"
                    >
                        AI Analyzing Your Learning Patterns
                    </motion.div>
                </div>
            </div>

            {/* Cognitive Metrics */}
            <div className="grid grid-cols-2 gap-3">
                <CognitiveMetric
                    icon={<Activity className="w-4 h-4" />}
                    label="Focus Level"
                    value={87}
                    color="primary"
                />
                <CognitiveMetric
                    icon={<Zap className="w-4 h-4" />}
                    label="Learning Speed"
                    value={92}
                    color="secondary"
                />
                <CognitiveMetric
                    icon={<Brain className="w-4 h-4" />}
                    label="Retention"
                    value={78}
                    color="accent"
                />
                <CognitiveMetric
                    icon={<Heart className="w-4 h-4" />}
                    label="Engagement"
                    value={95}
                    color="primary"
                />
            </div>
        </div>
    );
}

function CognitiveMetric({
    icon,
    label,
    value,
    color
}: {
    icon: React.ReactNode;
    label: string;
    value: number;
    color: 'primary' | 'secondary' | 'accent';
}) {
    const colors = {
        primary: 'from-primary-500 to-primary-600',
        secondary: 'from-secondary-500 to-secondary-600',
        accent: 'from-accent-500 to-accent-600',
    };

    return (
        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center gap-2 mb-2">
                <span className="text-gray-400">{icon}</span>
                <span className="text-xs text-gray-400">{label}</span>
            </div>
            <div className="flex items-center gap-2">
                <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${value}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                        className={`h-full bg-gradient-to-r ${colors[color]} rounded-full`}
                    />
                </div>
                <span className="text-sm font-medium text-white">{value}%</span>
            </div>
        </div>
    );
}
