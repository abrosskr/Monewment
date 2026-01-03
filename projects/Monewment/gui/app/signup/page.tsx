"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function SignupPage() {
    const router = useRouter();
    const [formData, setFormData] = useState({ email: '', password: '', name: '' });

    const handleSubmit = async () => {
        try {
            const res = await fetch('http://localhost:8001/api/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const data = await res.json();

            if (res.ok) {
                alert("✨ 가입을 환영합니다! 로그인 해주세요.");
                router.push('/login');
            } else {
                alert("❌ 가입 실패: " + data.detail);
            }
        } catch (e) {
            alert("서버 연결 오류");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0f172a] text-slate-200">
            <div className="w-full max-w-md p-8 bg-[#1e293b] rounded-3xl border border-slate-700 shadow-2xl">
                <h1 className="text-3xl font-black text-center mb-2 text-white italic">JOIN <span className="text-blue-500">MONEWMENT</span></h1>
                <p className="text-center text-xs text-slate-500 mb-8 uppercase tracking-widest">Enterprise AI DevOps Platform</p>

                <div className="space-y-4">
                    <input
                        type="text" placeholder="이름 (Name)"
                        className="w-full bg-black border border-slate-700 rounded-xl px-4 py-3 text-sm focus:border-blue-500 outline-none transition-all"
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                    <input
                        type="email" placeholder="이메일 (Email)"
                        className="w-full bg-black border border-slate-700 rounded-xl px-4 py-3 text-sm focus:border-blue-500 outline-none transition-all"
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    />
                    <input
                        type="password" placeholder="비밀번호 (Password)"
                        className="w-full bg-black border border-slate-700 rounded-xl px-4 py-3 text-sm focus:border-blue-500 outline-none transition-all"
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    />
                    <button
                        onClick={handleSubmit}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl transition-all shadow-lg mt-4 uppercase tracking-wider text-xs"
                    >
                        Sign Up Now
                    </button>
                </div>

                <div className="text-center mt-6">
                    <Link href="/login" className="text-xs text-slate-500 hover:text-white transition-colors border-b border-transparent hover:border-slate-500 pb-0.5">
                        이미 계정이 있으신가요? 로그인하기
                    </Link>
                </div>
            </div>
        </div>
    );
}