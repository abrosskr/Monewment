'use client';
import React, { useState } from 'react';

// === 데이터 타입 ===
type Cell = {
    id: string; r: number; c: number;
    w: number; h: number; // Grid Span
    visible: boolean;
    name?: string;
    type?: string;
    customWidth?: number;
    customHeight?: number;
};

export default function UIArchitect() {
    // [Step 1] 캔버스 초기 설정
    const [step, setStep] = useState<'setup' | 'build'>('setup');
    const [canvasSize, setCanvasSize] = useState({ w: 1200, h: 800 });
    const [gridConfig, setGridConfig] = useState({ rows: 12, cols: 12 });

    // [Step 2] 그리드 데이터
    const [cells, setCells] = useState<Cell[]>([]);

    // 선택 로직 상태
    const [startPos, setStartPos] = useState<{ r: number, c: number } | null>(null);
    const [endPos, setEndPos] = useState<{ r: number, c: number } | null>(null);
    const [activeCellId, setActiveCellId] = useState<string | null>(null);

    // [Step 3] AI 레포트 패널 상태
    const [showReport, setShowReport] = useState(false);
    const [aiPrompt, setAiPrompt] = useState("");

    // 1. 초기화 함수
    const initializeGrid = () => {
        const newCells: Cell[] = [];
        for (let r = 0; r < gridConfig.rows; r++) {
            for (let c = 0; c < gridConfig.cols; c++) {
                newCells.push({ id: `${r}-${c}`, r, c, w: 1, h: 1, visible: true });
            }
        }
        setCells(newCells);
        setStep('build');
    };

    // 2. 셀 클릭 핸들러
    const handleCellClick = (r: number, c: number) => {
        const clickedCell = cells.find(cell => cell.r === r && cell.c === c);
        if (!clickedCell?.visible) return;

        // 이미 병합된 셀(영역)을 클릭하면 -> 속성창 열기
        if (clickedCell.w > 1 || clickedCell.h > 1) {
            setActiveCellId(clickedCell.id);
            setShowReport(false); // 속성창 볼 때는 리포트 닫기
            return;
        }

        // 다른 곳 클릭 시 속성창 닫기
        if (activeCellId) { setActiveCellId(null); }

        // 시작/끝점 로직 (영역 선택)
        if (!startPos) {
            setStartPos({ r, c });
            setEndPos(null);
        } else if (!endPos) {
            setEndPos({ r, c });
        } else {
            // 이미 둘 다 찍혀있으면 -> 다시 시작점부터
            setStartPos({ r, c });
            setEndPos(null);
        }
    };

    // 선택 영역 계산
    const getSelection = () => {
        if (!startPos) return null;
        const end = endPos || startPos;
        return {
            minR: Math.min(startPos.r, end.r), maxR: Math.max(startPos.r, end.r),
            minC: Math.min(startPos.c, end.c), maxC: Math.max(startPos.c, end.c),
        };
    };
    const selection = getSelection();

    // 3. 합치기 (Merge Logic)
    const mergeCells = () => {
        if (!selection) return;
        const { minR, maxR, minC, maxC } = selection;

        setCells(prev => prev.map(cell => {
            // 1. 기준점(왼쪽 위) 셀을 대표 셀로 만듦
            if (cell.r === minR && cell.c === minC) {
                const cellW = canvasSize.w / gridConfig.cols;
                const cellH = canvasSize.h / gridConfig.rows;
                const spanW = maxC - minC + 1;
                const spanH = maxR - minR + 1;

                return {
                    ...cell, w: spanW, h: spanH,
                    name: `Area_${minR}_${minC}`, type: 'Container',
                    customWidth: Math.round(cellW * spanW),
                    customHeight: Math.round(cellH * spanH)
                };
            }
            // 2. 범위 내 나머지 셀들은 숨김 처리
            if (cell.r >= minR && cell.r <= maxR && cell.c >= minC && cell.c <= maxC) {
                return { ...cell, visible: false };
            }
            return cell;
        }));

        // 선택 초기화
        setStartPos(null); setEndPos(null);
    };

    // 4. 나누기 (Split Logic)
    const splitCell = (targetId: string) => {
        const target = cells.find(c => c.id === targetId);
        if (!target) return;

        setCells(prev => prev.map(cell => {
            // 해당 영역 안에 숨겨져 있던 셀들을 모두 복구
            if (cell.r >= target.r && cell.r < target.r + target.h &&
                cell.c >= target.c && cell.c < target.c + target.w) {
                return { ...cell, w: 1, h: 1, visible: true, name: undefined, type: undefined };
            }
            return cell;
        }));
        setActiveCellId(null);
    };

    // 속성 업데이트
    const updateAttribute = (key: string, value: any) => {
        if (!activeCellId) return;
        setCells(prev => prev.map(c => c.id === activeCellId ? { ...c, [key]: value } : c));
    };

    // 5. AI 프롬프트 생성기
    const generateReport = () => {
        const definedAreas = cells.filter(c => c.visible && (c.w > 1 || c.h > 1));

        let report = `[Role]\nYou are an expert Frontend Developer using Next.js, TailwindCSS, and React.\n\n`;
        report += `[Task]\nCreate a UI component based on the following structure specification.\n\n`;
        report += `[Canvas Spec]\n- Total Size: ${canvasSize.w}px Width x ${canvasSize.h}px Height\n- Grid Layout Strategy: Use CSS Grid or Flexbox to match these proportions.\n\n`;
        report += `[Defined Components (Layout Areas)]\n`;

        if (definedAreas.length === 0) {
            report += "(No areas defined yet. Please merge cells to define areas.)\n";
        } else {
            definedAreas.forEach((area, idx) => {
                report += `${idx + 1}. Name: "${area.name}"\n`;
                report += `   - Type: ${area.type}\n`;
                report += `   - Size: ${area.customWidth}px (W) x ${area.customHeight}px (H)\n`;
                report += `   - Grid Position: Row ${area.r}, Col ${area.c} (Span ${area.w}x${area.h})\n\n`;
            });
        }

        report += `[Requirement]\n1. Generate the complete '.tsx' file code.\n2. Use placeholders for icons/images.\n3. Ensure the layout matches the pixel dimensions provided.`;

        setAiPrompt(report);
        setShowReport(true); // 리포트 패널 열기
    };

    // === [화면 1] 초기 설정 (Setup) ===
    if (step === 'setup') {
        return (
            <div className="flex items-center justify-center w-full h-full bg-[#050505] text-white">
                <div className="bg-[#111] p-10 rounded-2xl border border-[#333] w-[450px] shadow-2xl text-center">
                    <h1 className="text-3xl font-bold mb-2 text-[#FFD700]">📐 UI Architect</h1>
                    <p className="text-gray-500 mb-8 text-sm">Create layout structures with precision.</p>

                    <div className="space-y-6 text-left">
                        <div>
                            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">1. Total Canvas Size (px)</label>
                            <div className="flex gap-4 mt-2">
                                <input type="number" value={canvasSize.w} onChange={e => setCanvasSize({ ...canvasSize, w: +e.target.value })} className="flex-1 bg-[#222] border border-[#444] p-3 rounded text-lg font-bold text-center outline-none" />
                                <span className="text-2xl text-gray-600 pt-2">×</span>
                                <input type="number" value={canvasSize.h} onChange={e => setCanvasSize({ ...canvasSize, h: +e.target.value })} className="flex-1 bg-[#222] border border-[#444] p-3 rounded text-lg font-bold text-center outline-none" />
                            </div>
                        </div>

                        <div>
                            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider">2. Grid Slices</label>
                            <div className="flex gap-4 mt-2">
                                <input type="number" value={gridConfig.rows} onChange={e => setGridConfig({ ...gridConfig, rows: +e.target.value })} className="flex-1 bg-[#222] border border-[#444] p-2 rounded text-center" />
                                <span className="text-gray-600 py-2">Rows</span>
                                <input type="number" value={gridConfig.cols} onChange={e => setGridConfig({ ...gridConfig, cols: +e.target.value })} className="flex-1 bg-[#222] border border-[#444] p-2 rounded text-center" />
                                <span className="text-gray-600 py-2">Cols</span>
                            </div>
                        </div>

                        <button onClick={initializeGrid} className="w-full bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-xl font-bold text-lg shadow-lg mt-4">
                            Open Canvas →
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // === [화면 2] 빌더 (Builder) - Flex Layout 적용 ===
    const activeCell = cells.find(c => c.id === activeCellId);

    return (
        // [구조 변경] h-screen을 flex-col로 잡아서 3단 분리 (헤더 / 바디 / 푸터)
        <div className="flex flex-col h-screen w-screen bg-[#050505] text-white overflow-hidden">

            {/* 1. 상단 툴바 (고정 높이) */}
            <div className="h-48 shrink-0 border-b border-[#222] bg-[#111] flex flex-col p-6 z-50">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-6">
                        <span className="font-bold text-3xl text-[#FFD700]">📐 UI Architect</span>
                        <div className="h-8 w-px bg-[#333]"></div>
                        <span className="text-lg text-gray-400">Canvas: <b>{canvasSize.w}</b> × <b>{canvasSize.h}</b> px</span>
                    </div>
                </div>

                {/* 컨트롤 영역 */}
                <div className="flex items-end gap-6 h-full pb-2">
                    {/* 시작점 박스 (색상 강제 적용) */}
                    <div
                        className="flex flex-col justify-center px-6 py-3 rounded-lg border-2 w-48 h-24 transition-all duration-200"
                        style={{
                            backgroundColor: startPos ? '#FACC15' : '#1a1a1a', // Active: Yellow
                            borderColor: startPos ? '#EAB308' : '#333',
                            boxShadow: startPos ? '0 0 15px rgba(250,204,21,0.5)' : 'none'
                        }}
                    >
                        <span className="text-xs font-bold uppercase mb-1" style={{ color: startPos ? 'black' : '#6B7280' }}>Start Point</span>
                        <span className="text-2xl font-mono font-bold" style={{ color: startPos ? 'black' : '#374151' }}>
                            {startPos ? `(${startPos.r}, ${startPos.c})` : 'Click Grid'}
                        </span>
                    </div>

                    {/* 끝점 박스 (색상 강제 적용) */}
                    <div
                        className="flex flex-col justify-center px-6 py-3 rounded-lg border-2 w-48 h-24 transition-all duration-200"
                        style={{
                            backgroundColor: endPos ? '#FACC15' : '#1a1a1a',
                            borderColor: endPos ? '#EAB308' : '#333',
                            boxShadow: endPos ? '0 0 15px rgba(250,204,21,0.5)' : 'none'
                        }}
                    >
                        <span className="text-xs font-bold uppercase mb-1" style={{ color: endPos ? 'black' : '#6B7280' }}>End Point</span>
                        <span className="text-2xl font-mono font-bold" style={{ color: endPos ? 'black' : '#374151' }}>
                            {endPos ? `(${endPos.r}, ${endPos.c})` : 'Click Grid'}
                        </span>
                    </div>

                    {/* 합치기 버튼 (색상 강제 적용) */}
                    <button
                        onClick={mergeCells}
                        disabled={!endPos}
                        className="h-24 px-12 rounded-xl font-bold text-xl transition-all duration-200 ml-auto"
                        style={{
                            backgroundColor: endPos ? '#2563EB' : '#333', // Active: Blue
                            color: endPos ? 'white' : '#4B5563',
                            cursor: endPos ? 'pointer' : 'not-allowed',
                            transform: endPos ? 'scale(1)' : 'scale(1)',
                            boxShadow: endPos ? '0 10px 15px -3px rgba(37, 99, 235, 0.5)' : 'none'
                        }}
                    >
                        {endPos ? '⚡ MERGE AREA' : 'Select Range'}
                    </button>
                </div>
            </div>

            {/* 2. 메인 영역 (캔버스 + 우측 패널) - Flex로 좌우 배치 */}
            <div className="flex-1 flex overflow-hidden">

                {/* [캔버스] 남은 공간 모두 차지 (flex-1) */}
                <div className="flex-1 overflow-auto bg-[#080808] p-10 flex items-center justify-center relative">
                    <div
                        className="bg-[#111] border border-[#333] shadow-2xl grid transition-all"
                        style={{
                            width: `${canvasSize.w}px`,
                            height: `${canvasSize.h}px`,
                            gridTemplateColumns: `repeat(${gridConfig.cols}, 1fr)`,
                            gridTemplateRows: `repeat(${gridConfig.rows}, 1fr)`,
                        }}
                    >
                        {cells.map(cell => {
                            if (!cell.visible) return null;

                            // 선택 영역 확인
                            let isSelected = false;
                            if (selection) {
                                const cmR = cell.r + cell.h - 1;
                                const cmC = cell.c + cell.w - 1;
                                if (cell.r <= selection.maxR && cmR >= selection.minR && cell.c <= selection.maxC && cmC >= selection.minC) {
                                    isSelected = true;
                                }
                            }
                            const isActive = activeCellId === cell.id;

                            // [중요] 스타일 강제 적용 (CSS 변수 사용)
                            const cellStyle: React.CSSProperties = {
                                gridColumn: `span ${cell.w}`,
                                gridRow: `span ${cell.h}`,
                                // 선택되면 파란색 반투명, 활성화되면 진한 회색
                                backgroundColor: isSelected ? 'rgba(37, 99, 235, 0.4)' : (isActive ? '#222' : 'transparent'),
                                // 선택되면 파란색 실선, 활성화되면 금색 실선
                                border: isSelected ? '2px solid #3B82F6' : (isActive ? '4px solid #FFD700' : '1px solid #333'),
                                zIndex: isSelected || isActive ? 10 : 1,
                            };

                            return (
                                <div
                                    key={cell.id}
                                    onClick={() => handleCellClick(cell.r, cell.c)}
                                    className="flex flex-col items-center justify-center cursor-pointer text-xs relative select-none transition-all duration-150 hover:bg-[#151515]"
                                    style={cellStyle}
                                >
                                    {cell.w > 1 || cell.h > 1 ? (
                                        <>
                                            <div className="font-bold text-[#FFD700] text-sm mb-1">{cell.name}</div>
                                            <div className="text-gray-500 text-[10px] px-2 py-0.5 bg-black/50 rounded">{cell.customWidth}x{cell.customHeight}</div>
                                        </>
                                    ) : (
                                        <span className="text-[#333] text-[10px]">+</span>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* [우측 패널 영역] - Flex Item으로 고정 (겹침 방지) */}
                {/* 리포트나 설정창 중 하나라도 열리면 공간 차지 */}
                {(showReport || activeCell) && (
                    <div className="w-96 shrink-0 bg-[#111] border-l border-[#222] flex flex-col shadow-xl z-40 overflow-y-auto">

                        {/* 1. AI 리포트 패널 (우선순위 높음) */}
                        {showReport && (
                            <div className="flex flex-col h-full animate-in slide-in-from-right duration-300">
                                <div className="p-6 border-b border-[#222] flex justify-between items-center bg-[#151515]">
                                    <h2 className="font-bold text-[#FFD700] text-lg">🤖 AI Prompt Report</h2>
                                    <button onClick={() => setShowReport(false)} className="text-gray-500 hover:text-white">✕</button>
                                </div>
                                <div className="flex-1 p-6 bg-[#0a0a0a]">
                                    <textarea
                                        className="w-full h-full bg-[#050505] border border-[#333] p-4 text-xs font-mono text-green-400 rounded resize-none outline-none focus:border-green-600"
                                        value={aiPrompt}
                                        readOnly
                                    />
                                </div>
                                <div className="p-4 border-t border-[#222] bg-[#151515]">
                                    <button
                                        onClick={() => navigator.clipboard.writeText(aiPrompt)}
                                        className="w-full bg-green-700 hover:bg-green-600 text-white py-3 rounded font-bold shadow-lg"
                                    >
                                        📋 Copy to Clipboard
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* 2. Area Config 패널 (리포트 없을 때 보임) */}
                        {!showReport && activeCell && (
                            <div className="flex flex-col h-full animate-in slide-in-from-right duration-300">
                                <div className="p-6 border-b border-[#222] flex justify-between items-center bg-[#151515]">
                                    <h3 className="text-[#FFD700] font-bold text-lg flex items-center gap-2">
                                        <span>⚙️ Area Config</span>
                                    </h3>
                                    <button onClick={() => setActiveCellId(null)} className="text-gray-500 hover:text-white">✕</button>
                                </div>

                                <div className="p-6 space-y-6 flex-1">
                                    <div>
                                        <label className="text-[10px] font-bold text-gray-500 uppercase block mb-1">Name</label>
                                        <input type="text" value={activeCell.name || ''} onChange={e => updateAttribute('name', e.target.value)} className="w-full bg-[#1A1A1A] border border-[#333] p-3 rounded text-white focus:border-[#FFD700] outline-none" />
                                    </div>

                                    <div>
                                        <label className="text-[10px] font-bold text-gray-500 uppercase block mb-1">Type</label>
                                        <select value={activeCell.type || 'Container'} onChange={e => updateAttribute('type', e.target.value)} className="w-full bg-[#1A1A1A] border border-[#333] p-3 rounded text-white outline-none">
                                            <option value="Container">Box</option>
                                            <option value="Button">Button</option>
                                            <option value="Chart">Chart</option>
                                            <option value="Sidebar">Sidebar</option>
                                        </select>
                                    </div>

                                    <div className="bg-[#161616] p-4 rounded border border-[#2a2a2a]">
                                        <label className="text-[10px] font-bold text-gray-400 uppercase block mb-3 border-b border-[#333] pb-2">Override Size (Px)</label>
                                        <div className="flex gap-2">
                                            <input type="number" value={activeCell.customWidth || 0} onChange={e => updateAttribute('customWidth', +e.target.value)} className="w-full bg-black border border-[#333] p-2 rounded text-center text-[#FFD700]" />
                                            <input type="number" value={activeCell.customHeight || 0} onChange={e => updateAttribute('customHeight', +e.target.value)} className="w-full bg-black border border-[#333] p-2 rounded text-center text-[#FFD700]" />
                                        </div>
                                    </div>
                                </div>

                                <div className="p-6 mt-auto border-t border-[#222]">
                                    <button onClick={() => splitCell(activeCell.id)} className="w-full py-3 rounded text-sm font-bold text-red-500 border border-red-900/50 hover:bg-red-900/10">
                                        ↺ Split & Reset
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* 3. 하단 바 */}
            <div className="h-16 border-t border-[#222] bg-[#111] flex items-center justify-between px-6 z-50 shrink-0">
                <span className="text-xs text-gray-500">Monewment UI Architect v2.3</span>
                <button
                    onClick={generateReport}
                    className="bg-[#FFD700] hover:bg-yellow-400 text-black px-6 py-2 rounded-lg font-bold shadow-[0_0_15px_rgba(250,204,21,0.3)] flex items-center gap-2 transition-all active:scale-95"
                >
                    <span>🤖 Generate AI Prompt Report</span>
                    <span className="bg-black/20 px-2 rounded text-xs">Extraction</span>
                </button>
            </div>

        </div>
    );
}