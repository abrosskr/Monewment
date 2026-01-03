"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

export default function DashboardPage() {
    const [projects, setProjects] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchProjects = async () => {
        try {
            const res = await fetch('http://localhost:8001/projects');
            const data = await res.json();
            setProjects(data.projects || []);
        } catch (err) {
            console.error("목록 로드 실패");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchProjects(); }, []);

    const handleDelete = async (name: string) => {
        if (!confirm(`정말로 '${name}' 프로젝트를 영구 삭제하시겠습니까?`)) return;
        try {
            const res = await fetch(`http://localhost:8001/projects/${name}`, { method: 'DELETE' });
            if (res.ok) {
                alert("🗑️ 삭제가 완료되었습니다.");
                fetchProjects();
            } else {
                alert("삭제에 실패했습니다.");
            }
        } catch (err) {
            alert("서버 연결 오류");
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8 font-sans text-black">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-10 text-black">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-800 tracking-tight">MONEWMENT DASHBOARD</h1>
                        <p className="text-gray-500 mt-1">현재 가동 중인 프로젝트 인스턴스 목록입니다.</p>
                    </div>
                    <Link href="/register" className="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 transition shadow-lg text-black">
                        + 새 프로젝트 설치
                    </Link>
                </div>
                {loading ? (
                    <p className="text-center text-gray-400">프로젝트 목록을 불러오는 중...</p>
                ) : projects.length === 0 ? (
                    <div className="bg-white p-20 rounded-2xl border border-dashed border-gray-300 text-center">
                        <p className="text-gray-400 text-black">설치된 프로젝트가 아직 없습니다.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {projects.map((name) => (
                            <div key={name} className="bg-white p-6 rounded-2xl shadow-md border border-gray-100 hover:shadow-xl transition-all relative group">
                                <button onClick={() => handleDelete(name)} className="absolute top-4 right-4 text-gray-300 hover:text-red-500 transition-colors">🗑️</button>
                                <div className="flex justify-between items-start mb-4">
                                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 font-bold text-xl uppercase">{name[0]}</div>
                                    <span className="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-widest text-black">Active</span>
                                </div>
                                <h3 className="text-xl font-bold text-gray-800 mb-1">{name}</h3>
                                <p className="text-xs text-gray-400 mb-6 font-mono truncate text-black">D:\projects\Monewment\projects\{name}</p>

                                {/* [핵심 수정] 버튼을 링크로 감싸서 실제 페이지 이동이 가능하게 했습니다. */}
                                <Link
                                    href={`/projects/${name}`}
                                    className="block w-full py-3 bg-gray-50 text-gray-600 rounded-xl font-semibold hover:bg-blue-50 hover:text-blue-600 transition text-center text-black"
                                >
                                    상세 관리 및 로그 확인
                                </Link>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}