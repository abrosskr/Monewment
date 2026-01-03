"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

export default function DashboardPage() {
    const [projects, setProjects] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    // [최적화] 사용자 이름 표시를 위한 상태 추가
    const [userName, setUserName] = useState("User");

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

    useEffect(() => {
        fetchProjects();
        // 로컬 스토리지에서 사용자 이름 가져오기
        const storedName = localStorage.getItem("user_name");
        if (storedName) setUserName(storedName);
    }, []);

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
            <div className="max-w-6xl mx-auto"> {/* max-w-4xl -> 6xl로 확장하여 여유 공간 확보 */}

                {/* 헤더 영역 수정: 버튼 그룹 추가 */}
                <div className="flex justify-between items-end mb-10 text-black border-b border-gray-200 pb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-800 tracking-tight">MONEWMENT DASHBOARD</h1>
                        <p className="text-gray-500 mt-1">
                            Welcome back, <span className="font-bold text-blue-600">{userName}</span>. 현재 가동 중인 엔진 목록입니다.
                        </p>
                    </div>
                    <div className="flex gap-3">
                        {/* [신규] 통합 설정 버튼 추가 */}
                        <Link href="/settings" className="bg-gray-800 text-white px-6 py-3 rounded-xl font-bold hover:bg-gray-700 transition shadow-lg flex items-center gap-2">
                            <span>⚙️</span> 통합 설정 (팀/시스템)
                        </Link>
                        {/* 기존 프로젝트 생성 버튼 */}
                        <Link href="/register" className="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 transition shadow-lg flex items-center gap-2">
                            <span>+</span> 새 프로젝트 설치
                        </Link>
                    </div>
                </div>

                {loading ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mb-4"></div>
                        <p className="text-gray-400">엔진 상태를 스캔하는 중...</p>
                    </div>
                ) : projects.length === 0 ? (
                    <div className="bg-white p-20 rounded-2xl border-2 border-dashed border-gray-200 text-center hover:border-blue-300 transition-colors">
                        <p className="text-gray-400 text-lg mb-2">설치된 프로젝트가 아직 없습니다.</p>
                        <p className="text-sm text-gray-300">우측 상단의 버튼을 눌러 첫 번째 AI 엔진을 설치하세요.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {projects.map((name) => (
                            <div key={name} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all relative group">
                                <button onClick={() => handleDelete(name)} className="absolute top-4 right-4 text-gray-300 hover:text-red-500 transition-colors z-10 p-1">🗑️</button>

                                <div className="flex justify-between items-start mb-4">
                                    <div className="w-12 h-12 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center text-blue-600 font-black text-xl uppercase shadow-inner">
                                        {name[0]}
                                    </div>
                                    <span className="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-widest flex items-center gap-1">
                                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                                        Active
                                    </span>
                                </div>

                                <h3 className="text-xl font-bold text-gray-800 mb-1 truncate" title={name}>{name}</h3>
                                <p className="text-xs text-gray-400 mb-6 font-mono truncate bg-gray-50 p-1 rounded">
                                    /projects/{name}
                                </p>

                                <Link
                                    href={`/projects/${name}`} // 상세 페이지는 아직 없지만 경로는 유지
                                    className="block w-full py-3 bg-gray-50 text-gray-600 rounded-xl font-bold text-sm hover:bg-blue-600 hover:text-white transition-all text-center border border-gray-100 group-hover:border-blue-500/30"
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