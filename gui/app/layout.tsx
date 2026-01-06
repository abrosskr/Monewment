import type { Metadata } from "next";
import "./globals.css";
// [표준] @/ 절대 경로 사용
import YbSidebar from "@/components/YbSidebar";

export const metadata: Metadata = {
  title: "YellowBlock Workspace",
  description: "Project Management System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className="bg-[#141414] text-[#E5E5E5] font-sans antialiased overflow-hidden">
        <div className="flex h-screen w-screen">

          {/* 1. 사이드바 (고정) */}
          <YbSidebar />

          {/* 2. 메인 콘텐츠 영역 */}
          <main className="flex-1 ml-[260px] h-full flex flex-col bg-[#141414] relative">

            {/* [헤더] 1.png 디자인 반영 (우측 상단 컨트롤) */}
            <header className="h-12 w-full flex items-center justify-end px-4 space-x-4 border-b border-[#1A1A1A] bg-[#141414]">

              {/* 알림 아이콘 */}
              <button className="p-2 text-[#A0A0A0] hover:text-white transition-colors relative">
                🔔
                {/* 알림 배지 (Red Dot) */}
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-[#141414]"></span>
              </button>

              {/* 구분선 */}
              <div className="w-[1px] h-4 bg-[#333]"></div>

              {/* 프로필/메뉴 드롭다운 */}
              <button className="flex items-center space-x-2 p-1 pr-2 rounded hover:bg-[#262626] transition-colors">
                <div className="w-6 h-6 rounded bg-[#404040] flex items-center justify-center text-xs font-bold">A</div>
                <span className="text-[#808080] text-xs">▼</span>
              </button>

              {/* (선택사항) 윈도우 컨트롤 흉내내기 - 웹이라 기능은 없지만 디자인용 */}
              <div className="flex items-center space-x-4 ml-4 text-[#808080]">
                <span className="hover:text-white cursor-pointer">─</span>
                <span className="hover:text-white cursor-pointer">□</span>
                <span className="hover:text-red-500 cursor-pointer">✕</span>
              </div>
            </header>

            {/* 실제 페이지 내용 (빈 캔버스) */}
            <div className="flex-1 overflow-y-auto p-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}