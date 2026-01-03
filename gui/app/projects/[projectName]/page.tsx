"use client";

import React, { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import ReactMarkdown from 'react-markdown'; // [추가] npm install react-markdown 필요

export default function ProjectDetailPage() {
    const params = useParams();
    const projectName = params.projectName as string;
    const [logs, setLogs] = useState("로그를 불러오는 중...");
    const [isRunning, setIsRunning] = useState(false);
    const [docContent, setDocContent] = useState(""); // [추가] 문서 데이터 상태

    const scrollRef = useRef<HTMLDivElement>(null);

    // [최적화 추가] AI 분석 문서 데이터 로드
    const fetchDoc = async () => {
        try {
            const res = await fetch('http://localhost:8001/api/docs/structure');
            const data = await res.json();
            setDocContent(data.content);
        } catch (err) {
            console.error("문서 로드 실패");
        }
    };

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
            }
        } catch (err) { alert("서버 통신 오류"); }
    };

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    useEffect(() => {
        fetchLogs();
        fetchDoc(); // [추가] 페이지 로드 시 문서 호출
        const interval = setInterval(fetchLogs, 3000);
        return () => clearInterval(interval);
    }, [projectName]);

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-200 p-8 font-mono">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
                    <div>
                        <Link href="/dashboard" className="text-slate-500 hover:text-white mb-2 inline-block text-sm">← Dashboard</Link>
                        <h1 className="text-2xl font-bold text-white uppercase tracking-tighter">
                            Control Center: <span className="text-blue-400">{projectName}</span>
                        </h1>
                    </div>
                    <div className="flex gap-4">
                        <button
                            onClick={() => handleControl(isRunning ? 'stop' : 'start')}
                            className={`px-8 py-2 rounded-xl font-bold transition-all shadow-lg ${isRunning ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
                        >
                            {isRunning ? '■ STOP ENGINE' : '▶ START ENGINE'}
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* [왼쪽] 실시간 로그 터미널 (해선님 원본 유지) */}
                    <div className="flex flex-col">
                        <div className="bg-slate-800 px-4 py-2 rounded-t-lg text-xs font-bold text-slate-400 border-x border-t border-slate-700">
                            LIVE_REALTIME_LOG_STREAM
                        </div>
                        <div ref={scrollRef} className="bg-black p-6 rounded-b-lg border border-slate-800 shadow-2xl h-[600px] overflow-y-auto">
                            <pre className="whitespace-pre-wrap text-sm leading-relaxed font-mono text-green-500 opacity-90">
                                {logs}
                            </pre>
                        </div>
                    </div>

                    {/* [오른쪽] AI 분석 문서 뷰어 (신규 추가) */}
                    <div className="flex flex-col">
                        <div className="bg-blue-900 px-4 py-2 rounded-t-lg text-xs font-bold text-blue-200 border-x border-t border-blue-800">
                            🧠 AI_SYSTEM_BLUEPRINT_VIEWER
                        </div>
                        <div className="bg-white p-8 rounded-b-lg h-[600px] overflow-y-auto shadow-2xl text-slate-800">
                            <article className="prose prose-slate max-w-none">
                                <ReactMarkdown>{docContent}</ReactMarkdown>
                            </article>
                        </div>
                    </div>
                </div>

                <div className="mt-6 text-[10px] text-slate-600 flex justify-between items-center uppercase tracking-widest">
                    <span>* System polling every 3 seconds</span>
                    <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-slate-700'}`}></span>
                        <span className={isRunning ? 'text-green-500 font-bold' : ''}>Status: {isRunning ? 'Running' : 'Idle'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}