'use client';

import React, { useState } from 'react';
import useSWR, { mutate } from 'swr';
import {
    ServerStackIcon,
    CpuChipIcon,
    CurrencyDollarIcon,
    SignalIcon,
    PlayIcon,
    ArrowDownTrayIcon,
    ClockIcon,
    DocumentChartBarIcon
} from '@heroicons/react/24/outline';

// Mock Fetcher
const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function DeepSyncPage() {
    const { data: status } = useSWR('/api/admin/ants/status', fetcher, { refreshInterval: 3000 });
    const { data: list } = useSWR('/api/admin/ants/list', fetcher, { refreshInterval: 3000 });
    // New: Render Jobs
    const { data: jobs, error: jobsError } = useSWR('/api/v1/render/jobs', fetcher, { refreshInterval: 2000 });

    const [inputFile, setInputFile] = useState('');
    const [frame, setFrame] = useState(1);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            const res = await fetch('/api/v1/render/jobs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_id: 1,
                    job_type: 'RENDER_3D', // Correct Enum
                    params: {
                        input_file_id: 101, // Mock Input ID for now
                        frame: Number(frame)
                    }
                })
            });
            if (res.ok) {
                mutate('/api/v1/render/jobs');
                alert('Job Service Started!');
            } else {
                alert('Failed to submit job');
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="p-6 space-y-8">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                    <SignalIcon className="w-6 h-6 text-green-400" />
                    DeepSync Grid Network
                </h1>
                <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400 border border-green-500/30 animate-pulse">
                    Live Connection
                </span>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatsCard
                    title="Active Nodes"
                    value={status?.working_nodes ?? 0}
                    total={status?.total_nodes ?? 0}
                    unit="Ants"
                    icon={<ServerStackIcon className="w-6 h-6 text-blue-400" />}
                />
                <StatsCard
                    title="Total Compute"
                    value={status?.total_tflops ?? 0}
                    unit="TFLOPS"
                    icon={<CpuChipIcon className="w-6 h-6 text-purple-400" />}
                />
                <StatsCard
                    title="Revenue Rate"
                    value={`$${status?.revenue_per_hour ?? 0}`}
                    unit="/ hr"
                    icon={<CurrencyDollarIcon className="w-6 h-6 text-yellow-400" />}
                />
                <StatsCard
                    title="Active Jobs"
                    value={jobs?.jobs?.length ?? 0}
                    unit="Tasks"
                    icon={<DocumentChartBarIcon className="w-6 h-6 text-orange-400" />}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left: Job Submission */}
                <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden backdrop-blur-md p-6 h-fit">
                    <h2 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
                        <PlayIcon className="w-5 h-5 text-pink-500" />
                        New Render Job
                    </h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Source File (.blend)</label>
                            <select
                                className="w-full bg-black/40 border border-white/10 rounded p-2 text-white"
                                value={inputFile}
                                onChange={e => setInputFile(e.target.value)}
                            >
                                <option value="">Select a file from Vault...</option>
                                <option value="101">cyberpunk_city_v2.blend (ID: 101)</option>
                                <option value="102">character_hero_base.blend (ID: 102)</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-gray-400 mb-1">Target Frame</label>
                            <input
                                type="number"
                                className="w-full bg-black/40 border border-white/10 rounded p-2 text-white"
                                value={frame}
                                onChange={e => setFrame(Number(e.target.value))}
                                min={1}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white font-bold py-3 rounded transition flex justify-center items-center gap-2"
                        >
                            {isSubmitting ? 'Dispatching...' : 'Dispatch Job'}
                        </button>
                    </form>
                </div>

                {/* Right: Job List */}
                <div className="lg:col-span-2 bg-white/5 border border-white/10 rounded-xl overflow-hidden backdrop-blur-md">
                    <div className="p-4 border-b border-white/10">
                        <h2 className="text-lg font-semibold text-gray-200">Job Console</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-400">
                            <thead className="bg-white/5 text-gray-200 uppercase text-xs">
                                <tr>
                                    <th className="p-4">Job ID</th>
                                    <th className="p-4">Type</th>
                                    <th className="p-4">Status</th>
                                    <th className="p-4">Created</th>
                                    <th className="p-4">Output</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {jobs?.jobs?.map((job: any) => (
                                    <tr key={job.job_id} className="hover:bg-white/5 transition">
                                        <td className="p-4 font-mono text-white text-xs">{job.job_id.substring(0, 8)}...</td>
                                        <td className="p-4 font-medium text-purple-300">{job.type}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${job.status === 'COMPLETED' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                                                    job.status === 'FAILED' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                                                        'bg-yellow-500/20 text-yellow-400 border-yellow-500/30 animate-pulse'
                                                }`}>
                                                {job.status}
                                            </span>
                                        </td>
                                        <td className="p-4 flex items-center gap-1">
                                            <ClockIcon className="w-4 h-4" />
                                            {new Date(job.created_at).toLocaleTimeString()}
                                        </td>
                                        <td className="p-4">
                                            {job.output_file_id ? (
                                                <a
                                                    href={`/api/v1/vault/proxy/${job.output_file_id}`}
                                                    target="_blank"
                                                    className="flex items-center gap-1 text-blue-400 hover:text-blue-300 transition"
                                                >
                                                    <ArrowDownTrayIcon className="w-4 h-4" />
                                                    Download
                                                </a>
                                            ) : (
                                                <span className="text-gray-600">-</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {(!jobs?.jobs || jobs.jobs.length === 0) && (
                            <div className="p-8 text-center text-gray-500">
                                No active jobs. Connect nodes to start rendering.
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Node List (Collapsed or Below) */}
            <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden backdrop-blur-md opacity-70 hover:opacity-100 transition">
                <div className="p-4 border-b border-white/10 flex justify-between items-center">
                    <h2 className="text-sm font-semibold text-gray-400">Network Topology (Connected Ants)</h2>
                </div>
                {/* Reusing existing node list logic briefly or just keeping it simple */}
                <div className="p-4 text-xs text-gray-500">
                    {list?.length} Active Connections. (See full list in Admin Panel)
                </div>
            </div>
        </div>
    );
}

function StatsCard({ title, value, total, unit, icon }: any) {
    return (
        <div className="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-md hover:bg-white/10 transition group">
            <div className="flex justify-between items-start mb-2">
                <div className="p-2 bg-white/5 rounded-lg group-hover:scale-110 transition">{icon}</div>
                {total && <span className="text-xs text-gray-500">Total: {total}</span>}
            </div>
            <div className="text-2xl font-bold text-white mb-1">
                {value} <span className="text-sm text-gray-400 font-normal">{unit}</span>
            </div>
            <div className="text-sm text-gray-400">{title}</div>
        </div>
    )
}
