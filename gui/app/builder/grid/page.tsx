'use client';
import React, { useState } from 'react';

// 1. [디자인 패턴] 스타일은 여기서 따로 관리합니다. (사용자는 건드리지 않음)
const PATTERNS: any = {
    default: "bg-[#222] border border-[#333] text-gray-300",
    highlight: "bg-blue-900 border border-blue-500 text-white font-bold",
    warning: "bg-red-900/30 border border-red-500 text-red-200",
    ghost: "bg-transparent border border-dashed border-[#444] text-gray-500",
};

// 샘플 아이콘 (Lucide 대신 텍스트로 대체)
const ICONS: any = {
    none: "",
    user: "👤",
    home: "🏠",
    settings: "⚙️",
    warning: "⚠️",
    chart: "📊"
};

export default function GridBuilder() {
    // 기본 4컬럼 그리드
    const [gridCols, setGridCols] = useState(4);

    // 블록 데이터 (여기가 엑셀의 셀 데이터입니다)
    const [blocks, setBlocks] = useState([
        // 예: 가로 2칸 합침 (colSpan: 2)
        { id: 1, text: "Main Title", icon: "home", pattern: "highlight", colSpan: 2, rowSpan: 1 },
        { id: 2, text: "User Info", icon: "user", pattern: "default", colSpan: 2, rowSpan: 1 },
        { id: 3, text: "Chart Area", icon: "chart", pattern: "default", colSpan: 4, rowSpan: 2 }, // 가로 4칸, 세로 2칸 합침 (큰 박스)
        { id: 4, text: "Warning", icon: "warning", pattern: "warning", colSpan: 4, rowSpan: 1 },
    ]);

    // 블록 추가
    const addBlock = () => {
        const newId = Math.max(...blocks.map(b => b.id), 0) + 1;
        setBlocks([...blocks, { id: newId, text: "New Cell", icon: "none", pattern: "default", colSpan: 1, rowSpan: 1 }]);
    };

    // 블록 업데이트
    const updateBlock = (id: number, field: string, value: any) => {
        setBlocks(prev => prev.map(b => b.id === id ? { ...b, [field]: value } : b));
    };

    // 블록 삭제
    const deleteBlock = (id: number) => {
        setBlocks(blocks.filter(b => b.id !== id));
    };

    return (
        <div className="h-screen w-screen flex flex-col bg-[#111] text-white">

            {/* 1. 상단: 결과물 미리보기 (CSS Grid 엔진) */}
            <div className="flex-1 overflow-auto p-10 bg-[#1A1A1A] flex items-center justify-center">
                <div
                    className="grid gap-4 w-full max-w-4xl transition-all duration-300"
                    style={{
                        gridTemplateColumns: `repeat(${gridCols}, minmax(0, 1fr))`, // 엑셀의 열 개수 설정
                        gridAutoRows: "100px" // 기본 행 높이
                    }}
                >
                    {blocks.map((block) => (
                        <div
                            key={block.id}
                            className={`${PATTERNS[block.pattern]} rounded-xl flex flex-col items-center justify-center shadow-lg relative group transition-all`}
                            style={{
                                gridColumn: `span ${block.colSpan}`, // 엑셀 셀 병합 (가로)
                                gridRow: `span ${block.rowSpan}`,    // 엑셀 셀 병합 (세로)
                            }}
                        >
                            <div className="text-3xl mb-2">{ICONS[block.icon]}</div>
                            <span>{block.text}</span>

                            {/* 호버 시 크기 정보 표시 */}
                            <div className="absolute top-2 right-2 text-xs bg-black/50 px-1 rounded opacity-0 group-hover:opacity-100">
                                {block.colSpan}x{block.rowSpan}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 2. 하단: 구조 제어 패널 (엑셀 설정창) */}
            <div className="h-[35%] bg-[#202020] border-t border-[#333] flex flex-col">
                {/* 툴바 */}
                <div className="h-12 border-b border-[#333] flex items-center justify-between px-6 bg-[#262626]">
                    <div className="flex items-center space-x-4">
                        <span className="font-bold text-[#FFD700]">Grid System</span>
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                            <span>Columns:</span>
                            <input
                                type="number" min="1" max="12"
                                value={gridCols}
                                onChange={(e) => setGridCols(Number(e.target.value))}
                                className="w-12 bg-[#111] border border-[#444] rounded px-1 text-center text-white"
                            />
                        </div>
                    </div>
                    <div className="space-x-2">
                        <button onClick={addBlock} className="bg-blue-600 px-4 py-1 rounded text-sm hover:bg-blue-500">+ Add Cell</button>
                        <button
                            onClick={() => navigator.clipboard.writeText(JSON.stringify({ type: "grid", cols: gridCols, blocks }, null, 2))}
                            className="bg-[#333] border border-[#555] px-4 py-1 rounded text-sm hover:bg-[#444]"
                        >
                            Copy Layout JSON
                        </button>
                    </div>
                </div>

                {/* 데이터 리스트 (엑셀 로우) */}
                <div className="flex-1 overflow-auto p-4">
                    <table className="w-full text-left text-sm border-collapse text-gray-300">
                        <thead className="sticky top-0 bg-[#262626] text-[#FFD700]">
                            <tr>
                                <th className="p-2 border border-[#444]">Content</th>
                                <th className="p-2 border border-[#444]">Pattern (Design)</th>
                                <th className="p-2 border border-[#444]">Icon</th>
                                <th className="p-2 border border-[#444] text-center w-20">Width (Col)</th>
                                <th className="p-2 border border-[#444] text-center w-20">Height (Row)</th>
                                <th className="p-2 border border-[#444] w-10">Del</th>
                            </tr>
                        </thead>
                        <tbody>
                            {blocks.map((block) => (
                                <tr key={block.id} className="hover:bg-[#333] transition-colors">
                                    <td className="p-1 border border-[#444]">
                                        <input
                                            value={block.text} onChange={(e) => updateBlock(block.id, 'text', e.target.value)}
                                            className="w-full bg-transparent outline-none px-2"
                                        />
                                    </td>
                                    <td className="p-1 border border-[#444]">
                                        <select
                                            value={block.pattern} onChange={(e) => updateBlock(block.id, 'pattern', e.target.value)}
                                            className="w-full bg-transparent outline-none"
                                        >
                                            {Object.keys(PATTERNS).map(p => <option key={p} value={p}>{p}</option>)}
                                        </select>
                                    </td>
                                    <td className="p-1 border border-[#444]">
                                        <select
                                            value={block.icon} onChange={(e) => updateBlock(block.id, 'icon', e.target.value)}
                                            className="w-full bg-transparent outline-none"
                                        >
                                            {Object.keys(ICONS).map(i => <option key={i} value={i}>{i} {ICONS[i]}</option>)}
                                        </select>
                                    </td>
                                    {/* 여기가 엑셀의 '병합' 기능입니다 */}
                                    <td className="p-1 border border-[#444]">
                                        <input
                                            type="number" min="1" max={gridCols}
                                            value={block.colSpan} onChange={(e) => updateBlock(block.id, 'colSpan', Number(e.target.value))}
                                            className="w-full bg-transparent text-center outline-none"
                                        />
                                    </td>
                                    <td className="p-1 border border-[#444]">
                                        <input
                                            type="number" min="1" max="4"
                                            value={block.rowSpan} onChange={(e) => updateBlock(block.id, 'rowSpan', Number(e.target.value))}
                                            className="w-full bg-transparent text-center outline-none"
                                        />
                                    </td>
                                    <td className="p-1 border border-[#444] text-center">
                                        <button onClick={() => deleteBlock(block.id)} className="text-red-400 hover:text-red-300">×</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}