"use client";

import React from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 font-sans">
      <main className="w-full max-w-md p-8 bg-white rounded-2xl shadow-2xl border border-gray-100">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-extrabold text-blue-600 tracking-tighter">MONEWMENT</h1>
          <p className="text-gray-400 text-sm mt-1 uppercase tracking-widest">AI Agent Gateway</p>
        </div>

        <div className="space-y-5">
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase ml-1 mb-1 text-black">Account ID</label>
            <input type="text" placeholder="아이디를 입력하세요" className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black" />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase ml-1 mb-1 text-black">Password</label>
            <input type="password" placeholder="비밀번호를 입력하세요" className="w-full px-4 py-3 rounded-xl bg-gray-50 border border-gray-200 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all text-black" />
          </div>
          <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl shadow-lg transition-all active:scale-[0.98]">접속하기</button>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-50 text-black">
          <div className="flex justify-center gap-4 text-sm text-gray-500 mb-6">
            <button className="hover:text-blue-600 transition text-black">아이디 찾기</button>
            <span className="text-gray-300">|</span>
            <button className="hover:text-blue-600 transition text-black">비밀번호 찾기</button>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-400 mb-2 text-black">계정이 없으신가요?</p>
            <Link href="/register" className="inline-block text-blue-600 font-bold hover:text-blue-800 transition underline underline-offset-4">
              새로운 프로젝트 시작하기 (회원가입)
            </Link>
          </div>
        </div>
      </main>
      <div className="absolute bottom-6 text-[10px] text-gray-300 tracking-widest uppercase">Monewment Hub v1.0.0-stable</div>
    </div>
  );
}