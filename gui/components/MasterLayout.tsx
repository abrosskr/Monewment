"use client";
import React from "react";
import YbSidebar from "@/components/YbSidebar";
import { useLayoutContext } from "./LayoutProvider";
import { usePathname } from "next/navigation";

export default function MasterLayout({ children }: { children: React.ReactNode }) {
    const { isClientMode } = useLayoutContext();
    const pathname = usePathname();

    // PixelGrid 경로나 클라이언트 모드에서는 사이드바를 숨김
    const isPixelGrid = pathname?.startsWith("/pixelgrid");

    if (isClientMode || isPixelGrid) {
        return (
            <div className="flex h-screen w-screen bg-[#0A0A0A]">
                <main className="flex-1 h-full overflow-y-auto relative">
                    {children}
                </main>
            </div>
        );
    }

    return (
        <div className="flex h-screen w-screen">
            {/* 1. 사이드바 (고정) */}
            <YbSidebar />

            {/* 2. 메인 콘텐츠 영역 */}
            <main className="flex-1 ml-[260px] h-full flex flex-col bg-[#141414] relative">
                {/* [헤더] 상단 컨트롤 */}
                <header className="h-12 w-full flex items-center justify-end px-4 space-x-4 border-b border-[#1A1A1A] bg-[#141414]">
                    <button className="p-2 text-[#A0A0A0] hover:text-white transition-colors relative">
                        🔔
                        <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-[#141414]"></span>
                    </button>
                    <div className="w-[1px] h-4 bg-[#333]"></div>
                    <button className="flex items-center space-x-2 p-1 pr-2 rounded hover:bg-[#262626] transition-colors">
                        <div className="w-6 h-6 rounded bg-[#404040] flex items-center justify-center text-xs font-bold">A</div>
                        <span className="text-[#808080] text-xs">▼</span>
                    </button>
                    <div className="flex items-center space-x-4 ml-4 text-[#808080]">
                        <span className="hover:text-white cursor-pointer">─</span>
                        <span className="hover:text-white cursor-pointer">□</span>
                        <span className="hover:text-red-500 cursor-pointer">✕</span>
                    </div>
                </header>

                {/* 실제 페이지 내용 */}
                <div className="flex-1 overflow-y-auto p-0">
                    {children}
                </div>
            </main>
        </div>
    );
}
