"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const router = useRouter();
  const [projectName, setProjectName] = useState("");
  const [password, setPassword] = useState("");
  // [신규] 기능 선택 상태 관리
  const [features, setFeatures] = useState<string[]>(["logs"]);

  const handleToggleFeature = (feature: string) => {
    setFeatures(prev =>
      prev.includes(feature) ? prev.filter(f => f !== feature) : [...prev, feature]
    );
  };

  const handleInstall = async () => {
    if (!projectName) return alert("프로젝트 이름을 입력하세요.");

    try {
      const res = await fetch('http://localhost:8001/install', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: projectName,
          admin_id: "admin",
          password: password,
          features: features
        })
      });

      const data = await res.json();
      if (res.ok) {
        alert(data.message);
        router.push('/dashboard');
      } else {
        alert("생성 실패: " + data.detail);
      }
    } catch (err) {
      alert("서버 연결에 실패했습니다.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 font-sans p-4">
      <main className="w-full max-w-lg p-8 bg-white rounded-2xl shadow-2xl border border-gray-100">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-blue-600 tracking-tighter uppercase">New Project</h1>
          <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest">엔진 배포 및 초기화</p>
        </div>

        <div className="space-y-6">
          {/* 입력 필드 섹션 */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase ml-1 mb-1">New Project Name</label>
              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="프로젝트 영문 이름을 입력하세요 (예: my-ai-bot)"
                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase ml-1 mb-1">Access Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="관제실 접근 비밀번호를 설정하세요"
                className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black"
              />
            </div>
          </div>

          {/* [신규] 기능 선택 체크박스 섹션 */}
          <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
            <label className="block text-xs font-bold text-blue-600 uppercase mb-3">Engine Features Selection</label>
            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={features.includes("logs")}
                  onChange={() => handleToggleFeature("logs")}
                  className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-semibold text-gray-700">실시간 로그 모니터링 시스템 (권장)</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={features.includes("auto-doc")}
                  onChange={() => handleToggleFeature("auto-doc")}
                  className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-semibold text-gray-700">AI 설계 문서 자동 생성 (STRUCTURE.md)</span>
              </label>
            </div>
          </div>

          <button
            onClick={handleInstall}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg transition-all active:scale-[0.98]"
          >
            CREATE & DEPLOY ENGINE
          </button>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-100 text-center">
          <Link href="/" className="text-sm text-gray-500 hover:text-blue-600 transition font-medium">
            ← 이미 프로젝트가 있나요? 로그인하기
          </Link>
        </div>
      </main>
      <div className="absolute bottom-6 text-[10px] text-gray-300 tracking-widest uppercase">Monewment Engine Deployer v4.1</div>
    </div>
  );
}