import type { Config } from "tailwindcss";

const config: Config = {
    // [표준] app 폴더와 루트의 components 폴더를 모두 감시
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                yb: {
                    yellow: "#FFD700",   // 포인트 노란색
                    black: "#1A1A1A",    // 전체 배경 (진한 검정)
                    surface: "#262626",  // 카드/팝업 배경 (약간 밝은 검정)
                    gray: "#404040",     // 테두리 선 색상
                    text: "#E5E5E5",     // 본문 글자색 (눈 안 아픈 흰색)
                    dim: "#9CA3AF",      // 흐린 글자색
                },
            },
            borderRadius: {
                'yb': '8px',
            },
        },
    },
    plugins: [],
};
export default config;