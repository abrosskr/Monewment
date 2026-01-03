"use client";
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
    const router = useRouter();
    const [formData, setFormData] = useState({ email: '', password: '' });

    const handleLogin = async () => {
        try {
            const res = await fetch('http://localhost:8001/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const data = await res.json();
            if (res.ok) {
                localStorage.setItem("user_id", data.user_id);
                localStorage.setItem("user_name", data.name);
                alert('👋 반가워요, ' + data.name + '님!');
                router.push('/dashboard'); 
            } else {
                alert("❌ 로그인 실패: " + data.detail);
            }
        } catch (e) {
            alert("서버 연결 오류");
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0f172a] text-slate-200">
            <div className="w-full max-w-md p-8 bg-[#1e293b] rounded-3xl border border-slate-700 shadow-2xl">
                <h1 className="text-3xl font-black text-center mb-2 text-white italic">LOGIN</h1>
                <p className="text-center text-xs text-slate-500 mb-8 uppercase tracking-widest">Access Your Engine</p>
                <div className="space-y-4">
                    <input type="email" placeholder="이메일" className="w-full bg-black border border-slate-700 rounded-xl px-4 py-3 text-sm focus:border-blue-500 outline-none transition-all" onChange={(e) => setFormData({...formData, email: e.target.value})} />
                    <input type="password" placeholder="비밀번호" className="w-full bg-black border border-slate-700 rounded-xl px-4 py-3 text-sm focus:border-blue-500 outline-none transition-all" onChange={(e) => setFormData({...formData, password: e.target.value})} />
                    <button onClick={handleLogin} className="w-full bg-white hover:bg-slate-200 text-black font-bold py-4 rounded-xl transition-all shadow-lg mt-4 uppercase tracking-wider text-xs">Enter Dashboard</button>
                </div>
                <div className="text-center mt-6"><Link href="/signup" className="text-xs text-slate-500 hover:text-white transition-colors">계정이 없으신가요? 회원가입</Link></div>
            </div>
        </div>
    );
}
