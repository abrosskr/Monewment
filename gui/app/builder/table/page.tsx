'use client';
import React, { useState } from 'react';

// 기본 4x4 그리드 (총 16칸)
const INITIAL_COLS = 4;
const INITIAL_ROWS = 4;

// 셀 데이터 타입
type Cell = {
    id: string;
    r: number; // 행 위치
    c: number; // 열 위치
    w: number; // 너비 (colSpan)
    h: number; // 높이 (rowSpan)
    visible: boolean; // 병합되어 숨겨진 셀인지 여부
    content: string;
    style: string; // design pattern
};

// 초기 셀 생성 함수
const createInitialCells = (rows: number, cols: number) => {
    const cells: Cell[] = [];
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            cells.push({
                id: `${r}-${c}`, r, c, w: 1, h: 1, visible: true,
                content: `Cell ${r},${c}`, style: 'default'
            });
        }
    }
    return cells;
};

export default function TableBuilder() {
    const [cells, setCells] = useState<Cell[]>(createInitialCells(INITIAL_ROWS, INITIAL_COLS));

    // 선택 영역 (시작점, 끝점)
    const [startCell, setStartCell] = useState<{ r: number, c: number } | null>(null);
    const [endCell, setEndCell] = useState<{ r: number, c: number } | null>(null);

    // 1. 셀 클릭 핸들러 (영역 잡기)
    const handleCellClick = (r: number, c: number) => {
        if (!startCell) {
            setStartCell({ r, c }); // 시작점 찍음
            setEndCell(null);
        } else if (!endCell) {
            setEndCell({ r, c });   // 끝점 찍음 (영역 완성)
        } else {
            setStartCell({ r, c }); // 다시 시작점 찍음 (초기화)
            setEndCell(null);
        }
    };

    // 선택된 영역 계산
    const getSelectionRange = () => {
        if (!startCell) return null;
        const end = endCell || startCell; // 끝점 없으면 시작점 하나만 선택된 것
        return {
            minR: Math.min(startCell.r, end.r),
            maxR: Math.max(startCell.r, end.r),
            minC: Math.min(startCell.c, end.c),
            maxC: Math.max(startCell.c, end.c),
        };
    };

    const selection = getSelectionRange();

    // 2. [핵심] 합치기 (Merge)
    const mergeCells = () => {
        if (!selection) return;
        const { minR, maxR, minC, maxC } = selection;

        // 선택된 영역의 너비/높이 계산
        const newW = maxC - minC + 1;
        const newH = maxR - minR + 1;

        setCells(prev => prev.map(cell => {
            // 1. 기준점(왼쪽 위)은 크기를 키움
            if (cell.r === minR && cell.c === minC) {
                return { ...cell, w: newW, h: newH, content: 'Merged Box', style: 'highlight' };
            }
            // 2. 나머지 범위 내의 셀들은 숨김 (visible: false)
            if (cell.r >= minR && cell.r <= maxR && cell.c >= minC && cell.c <= maxC) {
                return { ...cell, visible: false };
            }
            return cell;
        }));

        // 선택 해제
        setStartCell(null);
        setEndCell(null);
    };

    // 3. 나누기 (Reset)
    const splitCells = () => {
        if (!startCell) return;
        const target = cells.find(c => c.r === startCell.r && c.c === startCell.c);
        if (!target || (target.w === 1 && target.h === 1)) return; // 이미 1x1이면 무시

        // 해당 영역 안에 있는 모든 숨겨진 셀들을 다시 보이게 함
        const maxR = target.r + target.h - 1;
        const maxC = target.c + target.w - 1;

        setCells(prev => prev.map(cell => {
            if (cell.r >= target.r && cell.r <= maxR && cell.c >= target.c && cell.c <= maxC) {
                return { ...cell, w: 1, h: 1, visible: true, style: 'default', content: `Cell ${cell.r},${cell.c}` };
            }
            return cell;
        }));

        setStartCell(null);
        setEndCell(null);
    };

    return (
        <div className="h-screen w-screen flex flex-col bg-[#111] text-white">

            {/* 툴바 */}
            <div className="h-16 border-b border-[#333] flex items-center justify-between px-6 bg-[#1A1A1A]">
                <div className="text-[#FFD700] font-bold text-lg">Table Builder (HWP Style)</div>
                <div className="flex space-x-3">
                    <div className="text-sm text-gray-400 flex items-center mr-4">
                        {selection ? `Selected: (${selection.minR},${selection.minC}) ~ (${selection.maxR},${selection.maxC})` : 'Select cells...'}
                    </div>
                    <button
                        onClick={mergeCells} disabled={!endCell}
                        className={`px-4 py-2 rounded text-sm font-bold transition-all ${!endCell ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-500'}`}
                    >
                        ⚝ Merge (합치기)
                    </button>
                    <button
                        onClick={splitCells} disabled={!startCell}
                        className="px-4 py-2 rounded text-sm font-bold bg-[#333] border border-[#555] hover:bg-[#444]"
                    >
                        ↺ Split (나누기)
                    </button>
                    <button
                        onClick={() => navigator.clipboard.writeText(JSON.stringify(cells.filter(c => c.visible), null, 2))}
                        className="px-4 py-2 rounded text-sm bg-green-700 hover:bg-green-600 text-white"
                    >
                        💾 JSON Copy
                    </button>
                </div>
            </div>

            {/* 테이블 영역 */}
            <div className="flex-1 overflow-auto p-10 flex justify-center items-start">
                <div
                    className="grid gap-1 bg-[#333] p-1 border border-[#444]"
                    style={{
                        // CSS Grid로 테이블 흉내내기
                        gridTemplateColumns: `repeat(${INITIAL_COLS}, 150px)`,
                        gridTemplateRows: `repeat(${INITIAL_ROWS}, 100px)`,
                    }}
                >
                    {cells.map((cell) => {
                        if (!cell.visible) return null; // 병합된 칸은 렌더링 안 함

                        // 현재 셀이 선택 영역 안에 있는지 확인 (스타일링용)
                        let isSelected = false;
                        if (selection) {
                            const { minR, maxR, minC, maxC } = selection;
                            // 병합된 셀은 자신의 범위가 영역과 겹치는지 체크
                            const cellMaxR = cell.r + cell.h - 1;
                            const cellMaxC = cell.c + cell.w - 1;
                            if (
                                !(cellMaxR < minR || cell.r > maxR || cellMaxC < minC || cell.c > maxC)
                            ) {
                                isSelected = true;
                            }
                        }

                        return (
                            <div
                                key={cell.id}
                                onClick={() => handleCellClick(cell.r, cell.c)}
                                className={`
                  relative flex items-center justify-center border transition-all cursor-pointer select-none
                  ${isSelected ? 'bg-blue-900/50 border-blue-400 z-10' : 'bg-[#222] border-[#333] hover:bg-[#2a2a2a]'}
                  ${cell.style === 'highlight' ? 'bg-[#1a1a1a] text-white font-bold' : 'text-gray-400'}
                `}
                                style={{
                                    gridColumn: `span ${cell.w}`, // 병합 너비
                                    gridRow: `span ${cell.h}`,    // 병합 높이
                                }}
                            >
                                <span className="text-sm">{cell.content}</span>

                                {/* 병합된 셀 표시 */}
                                {cell.w > 1 || cell.h > 1 ? (
                                    <span className="absolute top-1 right-2 text-[10px] text-blue-400">Merged</span>
                                ) : null}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}