"use client";
import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

function LoginContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [saveId, setSaveId] = useState(false);
    const [isClientMode, setIsClientMode] = useState(false);

    useEffect(() => {
        // Context detection via Query Param
        const context = searchParams.get("context");
        if (context === "client") {
            setIsClientMode(true);
            const saved = localStorage.getItem("monewment_saved_email");
            if (saved) {
                setFormData(prev => ({ ...prev, email: saved }));
                setSaveId(true);
            }
        }
    }, [searchParams]);

    const handleLogin = async () => {
        try {
            // Queen Server is at port 8000 (Force IPv4)
            const res = await fetch('http://127.0.0.1:8000/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const data = await res.json();

            if (res.ok) {
                localStorage.setItem("user_id", data.user_id);
                localStorage.setItem("user_name", data.name);
                localStorage.setItem("access_token", data.access_token);

                if (isClientMode) {
                    // 1. Persistence: Save ID locally in browser
                    if (saveId) localStorage.setItem("monewment_saved_email", formData.email);
                    else localStorage.removeItem("monewment_saved_email");

                    // 2. Network Sync: Tell Queen to push token to Worker
                    try {
                        await fetch('http://127.0.0.1:8000/api/admin/ants/sync_token', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                client_id: "ant-desktop-01",
                                token: data.access_token
                            })
                        });
                    } catch (syncErr) {
                        console.error("Token Sync Failed:", syncErr);
                    }
                }

                alert('👋 ' + data.name + '님, 환영합니다!');
                router.push('/admin/deepsync');
            } else {
                alert("❌ 로그인 실패: " + (data.detail || JSON.stringify(data)));
            }
        } catch (e: any) {
            console.error(e);
            alert("서버 연결 오류 상세: " + (e.message || e) + "\n(127.0.0.1:8000 접속 실패)");
        }
    };

    return (
        <div className="min-h-screen flex flex-col lg:flex-row bg-white font-sans">
            {/* Draggable Region for Edge App Mode */}
            {isClientMode && (
                <div className="fixed top-0 left-0 w-full h-12 flex items-center px-6 z-50 select-none cursor-move"
                    style={{ WebkitAppRegion: 'drag' } as any}>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        <span className="text-[10px] text-slate-400 uppercase tracking-widest font-black">Monewment Enterprise</span>
                    </div>
                </div>
            )}

            {/* Left Column: White / Login Form */}
            <div className="flex-1 flex flex-col justify-center px-8 md:px-16 lg:px-24 w-full lg:max-w-[50%] animate-in fade-in slide-in-from-left duration-700 overflow-y-auto py-10 lg:py-0">
                <div className="mb-14">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 bg-[#a855f7] rounded-full opacity-20"></div>
                        <h1 className="text-4xl font-black text-slate-900 tracking-tight">Log In</h1>
                    </div>
                    <p className="text-slate-500 text-sm">Welcome back! Please enter your details.</p>
                </div>

                <div className="space-y-6">
                    <div>
                        <label className="block text-[11px] font-black text-slate-900 uppercase tracking-wider mb-2">Email Address</label>
                        <input
                            type="email"
                            placeholder="mail@monewment.com"
                            value={formData.email}
                            className="w-full border-2 border-slate-100 rounded-xl px-5 py-4 text-slate-900 outline-none focus:border-[#a855f7]/50 transition-all font-medium"
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        />
                    </div>

                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="block text-[11px] font-black text-slate-900 uppercase tracking-wider">Access Key</label>
                            <Link href="/signup" className="text-[10px] text-[#a855f7] hover:underline font-bold uppercase transition-colors">forgot password?</Link>
                        </div>
                        <div className="relative">
                            <input
                                type="password"
                                placeholder="••••••••"
                                className="w-full border-2 border-slate-100 rounded-xl px-5 py-4 text-slate-900 outline-none focus:border-[#a855f7]/50 transition-all font-medium"
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            />
                            <div className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-400 cursor-pointer text-lg">
                                👁️
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 pb-2">
                        <input
                            type="checkbox"
                            id="saveId"
                            checked={saveId}
                            onChange={(e) => setSaveId(e.target.checked)}
                            className="w-4 h-4 rounded border-2 border-slate-200 accent-[#a855f7] cursor-pointer"
                        />
                        <label htmlFor="saveId" className="text-[11px] text-slate-500 font-bold uppercase tracking-widest cursor-pointer select-none">REMEMBER ID</label>
                    </div>

                    <button
                        onClick={handleLogin}
                        className="w-full bg-[#a855f7] hover:bg-[#9333ea] text-white font-black py-5 rounded-xl transition-all shadow-lg shadow-[#a855f7]/30 text-base active:scale-[0.98] transform"
                    >
                        Log in
                    </button>

                    <div className="relative py-6">
                        <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-100"></div></div>
                        <div className="relative flex justify-center text-[10px]"><span className="bg-white px-4 text-slate-400 font-bold uppercase tracking-tighter">Or Continue With</span></div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <button className="flex items-center justify-center gap-3 border-2 border-slate-100 rounded-xl py-4 hover:bg-slate-50 transition-all font-bold text-slate-700 text-sm">
                            <img src="https://www.google.com/favicon.ico" className="w-4 h-4" /> Google
                        </button>
                        <button className="flex items-center justify-center gap-3 border-2 border-slate-100 rounded-xl py-4 hover:bg-slate-50 transition-all font-bold text-slate-700 text-sm">
                            <img src="https://www.facebook.com/favicon.ico" className="w-4 h-4" /> Facebook
                        </button>
                    </div>
                </div>

                <div className="mt-16 text-center">
                    <p className="text-xs text-slate-400 font-bold uppercase tracking-widest">
                        Don't have account? <Link href="/signup" className="text-[#a855f7] hover:underline ml-2">Sign up</Link>
                    </p>
                </div>
            </div>

            {/* Right Column: Dark Side with Image (#2d2d2f) */}
            <div className="hidden lg:flex flex-1 bg-[#2d2d2f] relative overflow-hidden items-center justify-center animate-in fade-in duration-1000">
                <div className="absolute inset-0">
                    <img src="/login-side-bg.png" className="w-full h-full object-cover opacity-60 mix-blend-overlay" alt="Background" />
                </div>
                {/* Overlay gradient to match #2d2d2f */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#2d2d2f]/80 via-transparent to-[#2d2d2f]/90"></div>

                <div className="relative z-10 text-center px-12">
                    <h2 className="text-6xl font-black italic mb-4 tracking-tighter text-white drop-shadow-2xl">MONEWMENT</h2>
                    <p className="text-blue-400/80 uppercase tracking-[0.5em] text-[10px] font-black mb-8">Enterprise GenAI Infrastructure</p>
                    <div className="w-16 h-[2px] bg-white/20 mx-auto"></div>
                </div>

                <div className="absolute bottom-10 right-10 text-[9px] text-white/20 font-mono uppercase tracking-widest">
                    Cluster v4.8.2-client
                </div>
            </div>
        </div>
    );
}

export default function LoginPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-white font-black text-slate-900 tracking-tighter">INITIALIZING SYSTEM...</div>}>
            <LoginContent />
        </Suspense>
    );
}

