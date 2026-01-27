"use client";

import { useEffect, useState } from 'react';
import { getSupabaseClient } from '@/lib/supabase';
import { Activity, Database, Server, Thermometer } from 'lucide-react';
import PhasePlaneChart from '@/components/PhasePlaneChart';

export default function DashboardPage() {
    const [activeTab, setActiveTab] = useState<'metrology' | 'lab' | 'live'>('metrology');
    const [sessions, setSessions] = useState<any[]>([]);
    const [liveRecipes, setLiveRecipes] = useState<any[]>([]);
    const [mockPhysicsData, setMockPhysicsData] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Load Data based on Tab
    useEffect(() => {
        if (activeTab === 'lab') loadLabData();
        if (activeTab === 'live') loadLiveData();
        if (activeTab === 'metrology') startMockSimulation();
    }, [activeTab]);

    const loadLabData = async () => {
        setLoading(true);
        setError(null);
        try {
            const brain = getSupabaseClient('brain');
            const { data, error } = await brain.from('cooking_sessions').select('*').order('started_at', { ascending: false }).limit(10);

            if (error) throw error;
            setSessions(data || []);
        } catch (e: any) {
            // Handle "Table not found" gracefully for demo
            if (e.message?.includes('does not exist') || e.code === '42P01') {
                setSessions([{ id: 'mock-1', recipe_name: 'Mock Steak (Table Missing)', device_id: 'dev-001', started_at: new Date().toISOString() }]);
                setError("⚠️ 'cooking_sessions' table not found in Brain DB. Showing mock data.");
            } else {
                setError(e.message);
            }
        } finally {
            setLoading(false);
        }
    };

    const loadLiveData = async () => {
        setLoading(true);
        setError(null);
        try {
            const live = getSupabaseClient('live');
            // Assuming a table 'recipes' exists in the Live project
            const { data, error } = await live.from('recipes').select('*').limit(5);
            if (error) throw error;
            setLiveRecipes(data || []);
        } catch (e: any) {
            if (e.message?.includes('does not exist') || e.code === '42P01') {
                setLiveRecipes([{ id: 1, name: 'Golden Steak (Standard)', version: 'v1.0' }]);
                setError("⚠️ 'recipes' table not found in Live DB. Showing mock data.");
            } else {
                setError(e.message);
            }
        } finally {
            setLoading(false);
        }
    };

    const startMockSimulation = () => {
        // Generate Physics Vector Spirals (Phase Plane visualization)
        const points = [];
        for (let t = 0; t < 20; t += 0.5) {
            const temp = 20 + 80 * (1 - Math.exp(-0.1 * t)); // Heating up
            const velocity = 8 * Math.exp(-0.1 * t);         // Velocity decreases
            points.push({ temp, velocity });
        }
        setMockPhysicsData(points);
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-8 font-mono">
            <header className="mb-8 flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                        V4: The Sentient Kitchen
                    </h1>
                    <p className="text-slate-500 text-sm mt-1">Digital Taste Engine & Metrology Dashboard</p>
                </div>
                <div className="flex gap-2 text-xs">
                    <span className="px-2 py-1 bg-blue-900/30 text-blue-400 rounded border border-blue-900">Edge: Online</span>
                    <span className="px-2 py-1 bg-emerald-900/30 text-emerald-400 rounded border border-emerald-900">Cloud: Dual-Core</span>
                </div>
            </header>

            {/* Tabs */}
            <div className="flex gap-4 mb-6">
                <button
                    onClick={() => setActiveTab('metrology')}
                    className={`flex items-center gap-2 px-4 py-2 rounded transition ${activeTab === 'metrology' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                >
                    <Thermometer size={18} /> Metrology
                </button>
                <button
                    onClick={() => setActiveTab('lab')}
                    className={`flex items-center gap-2 px-4 py-2 rounded transition ${activeTab === 'lab' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                >
                    <Database size={18} /> Lab (Brain)
                </button>
                <button
                    onClick={() => setActiveTab('live')}
                    className={`flex items-center gap-2 px-4 py-2 rounded transition ${activeTab === 'live' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                >
                    <Server size={18} /> Service (Live)
                </button>
            </div>

            {/* Content */}
            <main className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 min-h-[400px]">
                {error && (
                    <div className="mb-4 p-3 bg-yellow-900/30 border border-yellow-800 text-yellow-200 rounded text-sm">
                        {error}
                    </div>
                )}

                {activeTab === 'metrology' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div>
                            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                                <Activity size={20} className="text-indigo-400" /> Real-time Physics Vector
                            </h2>
                            <PhasePlaneChart data={mockPhysicsData} />
                        </div>
                        <div className="space-y-4">
                            <div className="p-4 bg-slate-900 rounded border border-slate-700">
                                <h3 className="text-slate-400 text-sm uppercase mb-2">Current State Vector (TSV)</h3>
                                <div className="grid grid-cols-2 gap-4 text-2xl font-bold">
                                    <div>
                                        <span className="text-xs text-slate-500 block">Temperature (T)</span>
                                        98.4 <span className="text-sm text-slate-600">°C</span>
                                    </div>
                                    <div>
                                        <span className="text-xs text-slate-500 block">Velocity (V)</span>
                                        +2.1 <span className="text-sm text-slate-600">°C/s</span>
                                    </div>
                                    <div>
                                        <span className="text-xs text-slate-500 block">Integral (I)</span>
                                        4,520 <span className="text-sm text-slate-600">J</span>
                                    </div>
                                    <div>
                                        <span className="text-xs text-slate-500 block">State</span>
                                        <span className="text-emerald-400 text-lg">Maillard Reaction</span>
                                    </div>
                                </div>
                            </div>
                            <div className="text-sm text-slate-500">
                                * In a real implementation, this view will subscribe to the Python Edge WebSocket.
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'lab' && (
                    <div>
                        <h2 className="text-xl font-bold mb-4 text-blue-400">Raw Cooking Sessions (From Supabase Brain)</h2>
                        {loading ? <p>Loading...</p> : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="border-b border-slate-700 text-slate-400">
                                            <th className="p-3">Session ID</th>
                                            <th className="p-3">Recipe</th>
                                            <th className="p-3">Device</th>
                                            <th className="p-3">Started At</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {sessions.map((s, i) => (
                                            <tr key={i} className="border-b border-slate-800 hover:bg-slate-800/50">
                                                <td className="p-3 font-mono text-xs">{s.id}</td>
                                                <td className="p-3">{s.recipe_name || 'Unknown'}</td>
                                                <td className="p-3 text-slate-400">{s.device_id}</td>
                                                <td className="p-3 text-slate-500">{new Date(s.started_at).toLocaleString()}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                {sessions.length === 0 && <p className="p-4 text-slate-500">No sessions found.</p>}
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'live' && (
                    <div>
                        <h2 className="text-xl font-bold mb-4 text-emerald-400">Golden Recipes (From Supabase Live)</h2>
                        {loading ? <p>Loading...</p> : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {liveRecipes.map((r, i) => (
                                    <div key={i} className="p-4 bg-slate-800 rounded border border-slate-700 hover:border-emerald-500 transition cursor-pointer">
                                        <h3 className="font-bold text-lg text-white">{r.name}</h3>
                                        <p className="text-sm text-emerald-400 mt-1">{r.version || 'v1.0'}</p>
                                        <div className="mt-4 flex justify-between items-center text-xs text-slate-500">
                                            <span>Verified Model</span>
                                            <button className="px-2 py-1 bg-emerald-900 text-emerald-200 rounded">Deploy</button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}
