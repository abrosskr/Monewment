"use client";

import React, { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function ProjectDetailPage() {
    const params = useParams();
    const projectName = params.projectName as string;
    const [logs, setLogs] = useState("로그를 불러오는 중...");
    const [isRunning, setIsRunning] = useState(false);

    // [최적화] 로그 창 하단으로 스크롤을 내리기 위한 참조점
    const scrollRef = useRef<HTMLDivElement>(null);

    const fetchLogs = async () => {
        try {
            const res = await fetch(`http://localhost:8001/projects/${projectName}/logs`);
            const data = await res.json();
            setLogs(data.logs || "기록된 로그가 없습니다.");
        } catch (err) {
            setLogs("로그를 가져오는 데 실패했습니다.");
        }
    };

    const handleControl = async (action: 'start' | 'stop') => {
        try {
            const res = await fetch(`http://localhost:8001/projects/${projectName}/${action}`, { method: 'POST' });
            if (res.ok) {
                setIsRunning(action === 'start');
                alert(action === 'start' ? "🚀 가동을 시작했습니다!" : "🛑 가동을 중지했습니다.");
            }
        } catch (err) { alert("서버 통신 오류"); }
    };

    // [최적화] 로그 데이터가 바뀔 때마다 스크롤을 맨 아래로 이동
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 3000);
        return () => clearInterval(interval);
    }, [projectName]);

    return (
        <div className="min-h-screen bg-gray-900 text-green-400 p-8 font-mono">
            <div className="max-w-5xl mx-auto">
                <div className="flex justify-between items-center mb-6 border-b border-gray-700 pb-4">
                    <div>
                        <Link href="/dashboard" className="text-gray-400 hover:text-white mb-2 inline-block">← Dashboard</Link>
                        <h1 className="text-2xl font-bold text-white uppercase tracking-tighter">
                            Project: <span className="text-blue-400">{projectName}</span>
                        </h1>
                    </div>
                    <div className="flex gap-4">
                        <button
                            onClick={() => handleControl(isRunning ? 'stop' : 'start')}
                            className={`px-6 py-2 rounded-xl font-bold transition-all ${isRunning ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-green-600 hover:bg-green-700 text-white'}`}
                        >
                            {isRunning ? '■ STOP ENGINE' : '▶ START ENGINE'}
                        </button>
                        <button onClick={fetchLogs} className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors">새로고침</button>
                    </div>
                </div>

                {/* [최적화] scrollRef 연결 */}
                <div ref={scrollRef} className="bg-black p-6 rounded-lg border border-gray-800 shadow-2xl h-[600px] overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm leading-relaxed font-mono">
                        {logs}
                    </pre>
                </div>

                <div className="mt-4 text-xs text-gray-500 flex justify-between">
                    <span>* 이 화면은 3초마다 자동으로 업데이트됩니다.</span>
                    <span className="text-blue-900 font-bold uppercase tracking-widest">System Status: {isRunning ? 'Running' : 'Idle'}</span>
                </div>
            </div>
        </div>
    );
}