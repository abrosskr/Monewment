"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
    const router = useRouter();

    // [기존 상태] 입력값 관리
    const [projectName, setProjectName] = useState('');
    const [adminId, setAdminId] = useState('');
    const [password, setPassword] = useState('');

    // [신규 상태] SaaS 모델용 추가 정보 (법인 ID, 기능 목록)
    const [orgId, setOrgId] = useState('1');
    const [features, setFeatures] = useState<string[]>(['logs']); // 기본값: 로그 기능 포함
    const [isInstalling, setIsInstalling] = useState(false);

    // [신규] 기능 선택 토글 함수
    const handleToggleFeature = (feature: string) => {
        setFeatures(prev =>
            prev.includes(feature) ? prev.filter(f => f !== feature) : [...prev, feature]
        );
    };

    // [핵심] 설치 버튼 클릭 시 실행되는 함수
    const handleInstall = async () => {
        if (!projectName.trim()) return alert("프로젝트 이름을 입력해주세요.");

        setIsInstalling(true);
        try {
            // 8001번 백엔드 서버에 설치 요청 전송
            const response = await fetch('http://localhost:8001/install', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_name: projectName.trim(),
                    admin_id: adminId,
                    password: password,
                    // [신규] 추가 정보 전송
                    organization_id: parseInt(orgId) || 1,
                    features: features
                }),
            });

            const data = await response.json();

            if (response.ok) {
                alert("✨ " + (data.message || "엔진 배포 및 설정이 완료되었습니다!"));
                router.replace('/dashboard');
            } else {
                alert("❌ 실패: " + (data.detail || "오류가 발생했습니다."));
            }
        } catch (error) {
            alert("❌ 서버가 응답하지 않습니다. (8001번 서버 확인)");
        } finally {
            setIsInstalling(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 font-sans p-4">
            <main className="w-full max-w-lg p-8 bg-white rounded-2xl shadow-2xl border border-gray-100">

                <div className="mb-8 text-center">
                    <Link href="/" className="text-xs text-blue-600 hover:text-blue-800 flex items-center justify-center gap-1 mb-4">
                        ← Cancel & Return
                    </Link>
                    <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">Deploy New Engine</h2>
                    <p className="text-gray-500 text-xs mt-2 uppercase tracking-widest">Enterprise Project Initialization</p>
                </div>

                <div className="space-y-5">
                    {/* 1. 기본 정보 입력 섹션 */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="col-span-2">
                            <label className="block text-xs font-bold text-gray-500 uppercase ml-1 mb-1">Project Identifier</label>
                            <input
                                type="text"
                                value={projectName}
                                onChange={(e) => setProjectName(e.target.value)}
                                placeholder="ex: samsung-ai-bot"
                                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black font-mono text-sm"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase ml-1 mb-1">Admin ID</label>
                            <input
                                type="text"
                                value={adminId}
                                onChange={(e) => setAdminId(e.target.value)}
                                placeholder="Manager ID"
                                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black text-sm"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-500 uppercase ml-1 mb-1">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Secret Key"
                                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black text-sm"
                            />
                        </div>
                        <div className="col-span-2">
                            <label className="block text-xs font-bold text-gray-500 uppercase ml-1 mb-1">Organization ID (Client)</label>
                            <input
                                type="number"
                                value={orgId}
                                onChange={(e) => setOrgId(e.target.value)}
                                placeholder="법인/팀 ID 입력 (기본값: 1)"
                                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black text-sm"
                            />
                        </div>
                    </div>

                    {/* 2. 기능 선택 (SaaS 마켓플레이스) 섹션 */}
                    <div className="bg-gray-50 p-5 rounded-xl border border-gray-200">
                        <label className="block text-xs font-bold text-blue-600 uppercase mb-3">Select Engine Modules</label>
                        <div className="space-y-3">
                            {/* 기본 기능 */}
                            <label className="flex items-center gap-3 cursor-pointer group p-2 hover:bg-gray-100 rounded-lg transition-colors">
                                <input
                                    type="checkbox"
                                    checked={features.includes("logs")}
                                    onChange={() => handleToggleFeature("logs")}
                                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="block text-sm font-bold text-gray-700">Real-time Logging</span>
                                    <span className="text-[10px] text-gray-400">실시간 터미널 로그 스트리밍 (Basic)</span>
                                </div>
                            </label>

                            {/* 문서화 기능 */}
                            <label className="flex items-center gap-3 cursor-pointer group p-2 hover:bg-gray-100 rounded-lg transition-colors">
                                <input
                                    type="checkbox"
                                    checked={features.includes("auto-doc")}
                                    onChange={() => handleToggleFeature("auto-doc")}
                                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="block text-sm font-bold text-gray-700">AI Auto-Documentation</span>
                                    <span className="text-[10px] text-gray-400">프로젝트 구조 및 DB 자동 분석</span>
                                </div>
                            </label>

                            {/* 유료 기능 (강조) */}
                            <label className="flex items-center gap-3 cursor-pointer group p-3 rounded-lg bg-blue-50 border border-blue-100 hover:border-blue-300 transition-all">
                                <input
                                    type="checkbox"
                                    checked={features.includes("mcp-bot")}
                                    onChange={() => handleToggleFeature("mcp-bot")}
                                    className="w-4 h-4 rounded border-blue-300 text-blue-600 focus:ring-blue-500"
                                />
                                <div className="flex-1">
                                    <div className="flex justify-between items-center">
                                        <span className="block text-sm font-bold text-blue-800">AI Code Repair Bot</span>
                                        <span className="text-[9px] bg-blue-600 text-white px-1.5 py-0.5 rounded font-bold">PAID</span>
                                    </div>
                                    <span className="text-[10px] text-blue-600/70">에러 발생 시 AI가 코드 직접 수정 (49,000/월)</span>
                                </div>
                            </label>
                        </div>
                    </div>

                    <button
                        onClick={handleInstall}
                        disabled={isInstalling}
                        className={`w-full ${isInstalling ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'} text-white font-bold py-4 rounded-xl shadow-lg transition-all active:scale-[0.98] mt-2 uppercase tracking-widest text-sm`}
                    >
                        {isInstalling ? 'Deploying Engine...' : 'Initialize Project Engine'}
                    </button>
                </div>

            </main>
        </div>
    );
}