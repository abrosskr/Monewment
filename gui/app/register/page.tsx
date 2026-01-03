"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation'; // [업데이트] 이동 기능을 위해 추가

export default function RegisterPage() {
    const router = useRouter(); // [업데이트] 이동 함수 준비

    // 입력값을 저장하는 상자들 (해선님 원본 유지)
    const [projectName, setProjectName] = useState('');
    const [adminId, setAdminId] = useState('');
    const [password, setPassword] = useState('');
    const [isInstalling, setIsInstalling] = useState(false);

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
                    password: password
                }),
            });

            const data = await response.json();

            if (response.ok) {
                alert("✨ " + (data.message || "설치가 완료되었습니다!"));
                // [업데이트] 알림창 확인 후 대시보드 페이지로 이동합니다.
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
        <div className="flex min-h-screen items-center justify-center bg-gray-50 font-sans">
            <main className="w-full max-w-md p-8 bg-white rounded-2xl shadow-2xl border border-gray-100">

                <div className="mb-8">
                    <Link href="/" className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1 mb-4 inline-block">
                        ← 로그인으로 돌아가기
                    </Link>
                    <h2 className="text-2xl font-bold text-gray-800">새 프로젝트 시작하기</h2>
                    <p className="text-gray-500 text-sm mt-1">Monewment의 새로운 엔진 인스턴스를 생성합니다.</p>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-xs font-semibold text-gray-500 uppercase ml-1 mb-1">Project Name</label>
                        <input
                            type="text"
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                            placeholder="예: my-ai-vendor"
                            className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-green-500 outline-none transition-all text-black"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-semibold text-gray-500 uppercase ml-1 mb-1">Admin ID</label>
                        <input
                            type="text"
                            value={adminId}
                            onChange={(e) => setAdminId(e.target.value)}
                            placeholder="관리자 아이디"
                            className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-semibold text-gray-500 uppercase ml-1 mb-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="비밀번호 설정"
                            className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black"
                        />
                    </div>

                    <button
                        onClick={handleInstall}
                        disabled={isInstalling}
                        className={`w-full ${isInstalling ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'} text-white font-bold py-4 rounded-xl shadow-lg transition-all active:scale-[0.98] mt-4`}
                    >
                        {isInstalling ? '템플릿 복사 중...' : '템플릿 복사 및 설치 시작'}
                    </button>
                </div>

            </main>
        </div>
    );
}