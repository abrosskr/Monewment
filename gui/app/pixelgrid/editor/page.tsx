'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
    Plus,
    ChevronRight,
    RotateCcw,
    Copy,
    Layout,
    Type,
    Image as ImageIcon,
    Square,
    CheckSquare,
    Circle,
    Scissors
} from 'lucide-react';

// DESIGN TOKENS (PIXELGRID PHASE 3)
const TOKENS = {
    yellow: '#FBC22C',
    purple: '#470EE1',
    bg: '#0A0A0A',
    text: '#FFFFFF',
    alert: '#FF0505',
    headerHeight: 120,
    footerHeight: 10,
};

interface GridCell {
    id: string;
    r: number;
    c: number;
    rs: number; // rowSpan
    cs: number; // colSpan
    type: string;
    style: any;
    content: string;
    isMerged: boolean;
    masterId?: string; // If this cell is covered by another merged cell
    // Phase 4: Advanced Controls
    width?: number;   // Cell width in pixels (default: 80)
    height?: number;  // Cell height in pixels (default: 80)
    customId?: string; // User-defined ID
    outline?: {
        enabled: boolean;
        width: number;
        color: string;
        style: 'solid' | 'dashed' | 'dotted';
    };
    // Image support
    imageUrl?: string;
    imageAlt?: string;
    imageFit?: 'cover' | 'contain' | 'fill';
}

export default function PixelGridEditor() {
    // Page 1 Data (Load from LocalStorage)
    const [config, setConfig] = useState<any>({ name: 'New Project', w: 1920, h: 1080, r: 12, c: 12, palette: [] });

    useEffect(() => {
        const saved = localStorage.getItem('pixelgrid_config');
        if (saved) {
            const parsed = JSON.parse(saved);
            setConfig(parsed);
        }
    }, []);

    // Grid State
    const [grid, setGrid] = useState<GridCell[]>([]);
    const [selection, setSelection] = useState<{ start: [number, number], end: [number, number] } | null>(null);
    const [promptText, setPromptText] = useState('');
    const [isDirty, setIsDirty] = useState(false);
    const [toast, setToast] = useState<string | null>(null);
    const [exportMode, setExportMode] = useState<'JSON' | 'React'>('JSON');

    // Style Editor State
    const [editState, setEditState] = useState({
        type: 'div',
        fontSize: '14',
        fontWeight: 'Regular',
        color: '#FFFFFF',
        bg: '#121212',
        padding: '12',
        textAlign: 'Left',
        content: '',
        // Phase 4 additions
        width: '80',
        height: '80',
        customId: '',
        outlineEnabled: false,
        outlineWidth: '2',
        outlineColor: '#FFFFFF',
        outlineStyle: 'solid' as 'solid' | 'dashed' | 'dotted',
        imageUrl: '',
        imageAlt: '',
        imageFit: 'cover' as 'cover' | 'contain' | 'fill'
    });

    // Initialize Grid
    useEffect(() => {
        const initialGrid: GridCell[] = [];
        for (let r = 0; r < config.r; r++) {
            for (let c = 0; c < config.c; c++) {
                initialGrid.push({
                    id: `${r}-${c}`,
                    r, c, rs: 1, cs: 1,
                    type: 'div',
                    style: { bg: '#121212', color: '#FFFFFF', fontSize: '14', padding: '12', textAlign: 'Left' },
                    content: '',
                    isMerged: false,
                    width: 80,
                    height: 80
                });
            }
        }
        setGrid(initialGrid);
    }, [config]);

    // Keyboard Shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
            if (e.key.toLowerCase() === 'm') handleMerge();
            if (e.key.toLowerCase() === 'u') handleUnmerge();
            if (e.key === 'Escape') setSelection(null);

            if (selection && ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                e.preventDefault();
                const [r, c] = selection.end;
                let nr = r, nc = c;
                if (e.key === 'ArrowUp') nr = Math.max(0, r - 1);
                if (e.key === 'ArrowDown') nr = Math.min(config.r - 1, r + 1);
                if (e.key === 'ArrowLeft') nc = Math.max(0, c - 1);
                if (e.key === 'ArrowRight') nc = Math.min(config.c - 1, c + 1);

                if (e.shiftKey) {
                    setSelection({ ...selection, end: [nr, nc] });
                } else {
                    setSelection({ start: [nr, nc], end: [nr, nc] });
                    const cell = grid.find(c_ => c_.r === nr && c_.c === nc);
                    if (cell) updateEditStateFromCell(cell);
                }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [selection, grid, config]);

    const updateEditStateFromCell = (cell: GridCell) => {
        setEditState({
            type: cell.type,
            fontSize: cell.style.fontSize || '14',
            fontWeight: cell.style.fontWeight || 'Regular',
            color: cell.style.color || '#FFFFFF',
            bg: cell.style.bg || '#121212',
            padding: cell.style.padding || '12',
            textAlign: cell.style.textAlign || 'Left',
            content: cell.content || '',
            // Phase 4 fields
            width: String(cell.width || 80),
            height: String(cell.height || 80),
            customId: cell.customId || '',
            outlineEnabled: cell.outline?.enabled || false,
            outlineWidth: String(cell.outline?.width || 2),
            outlineColor: cell.outline?.color || '#FFFFFF',
            outlineStyle: cell.outline?.style || 'solid',
            imageUrl: cell.imageUrl || '',
            imageAlt: cell.imageAlt || '',
            imageFit: cell.imageFit || 'cover'
        });
    };

    // Selection Logic
    const handleCellClick = (r: number, c: number) => {
        if (!selection) {
            const cell = grid.find(c_ => c_.r === r && c_.c === c);
            if (cell) updateEditStateFromCell(cell);
            setSelection({ start: [r, c], end: [r, c] });
        } else if (selection.start[0] === r && selection.start[1] === c) {
            setSelection(null);
        } else {
            setSelection({ start: selection.start, end: [r, c] });
        }
    };

    const selectedRange = useMemo(() => {
        if (!selection) return null;
        const r1 = Math.min(selection.start[0], selection.end[0]);
        const r2 = Math.max(selection.start[0], selection.end[0]);
        const c1 = Math.min(selection.start[1], selection.end[1]);
        const c2 = Math.max(selection.start[1], selection.end[1]);
        return { r1, r2, c1, c2 };
    }, [selection]);

    // Batch Apply Style
    const applyStyle = () => {
        if (!selectedRange) return;
        const { r1, r2, c1, c2 } = selectedRange;

        const newGrid = grid.map(cell => {
            if (cell.r >= r1 && cell.r <= r2 && cell.c >= c1 && cell.c <= c2) {
                return {
                    ...cell,
                    type: editState.type,
                    content: editState.content,
                    style: {
                        ...cell.style,
                        bg: editState.bg,
                        color: editState.color,
                        fontSize: editState.fontSize,
                        fontWeight: editState.fontWeight,
                        padding: editState.padding,
                        textAlign: editState.textAlign
                    },
                    // Phase 4 fields
                    width: parseInt(editState.width),
                    height: parseInt(editState.height),
                    customId: editState.customId || undefined,
                    outline: editState.outlineEnabled ? {
                        enabled: true,
                        width: parseInt(editState.outlineWidth),
                        color: editState.outlineColor,
                        style: editState.outlineStyle
                    } : undefined,
                    imageUrl: editState.imageUrl || undefined,
                    imageAlt: editState.imageAlt || undefined,
                    imageFit: editState.imageFit
                };
            }
            return cell;
        });

        setGrid(newGrid);
        setIsDirty(true);
        setToast("스타일이 적용되었습니다");
        setTimeout(() => setToast(null), 1500);
    };

    // Merge Logic
    const handleMerge = () => {
        if (!selectedRange) return;
        const { r1, r2, c1, c2 } = selectedRange;
        const rs = r2 - r1 + 1;
        const cs = c2 - c1 + 1;
        if (rs === 1 && cs === 1) return;

        const masterCellId = `${r1}-${c1}`;
        const autoGeneratedId = `m-${r1}-${c1}`;
        const newGrid = grid.map(cell => {
            if (cell.r === r1 && cell.c === c1) {
                return { ...cell, rs, cs, isMerged: true, customId: cell.customId || autoGeneratedId };
            }
            if (cell.r >= r1 && cell.r <= r2 && cell.c >= c1 && cell.c <= c2) {
                return { ...cell, isMerged: true, masterId: masterCellId };
            }
            return cell;
        });

        setGrid(newGrid);
        setSelection(null);
        setIsDirty(true);
    };

    const handleUnmerge = () => {
        if (!selection) return;
        const [r, c] = selection.start;
        const cell = grid.find(c_ => c_.r === r && c_.c === c);
        if (!cell || !cell.isMerged) return;

        const masterId = cell.masterId || cell.id;
        const newGrid = grid.map(c_ => {
            if (c_.id === masterId || c_.masterId === masterId) {
                return { ...c_, rs: 1, cs: 1, isMerged: false, masterId: undefined };
            }
            return c_;
        });

        setGrid(newGrid);
        setSelection(null);
        setIsDirty(true);
    };

    const isCurrentMasterMerged = useMemo(() => {
        if (!selection) return false;
        const [r, c] = selection.start;
        const cell = grid.find(c_ => c_.r === r && c_.c === c);
        return cell?.isMerged && cell.rs * cell.cs > 1;
    }, [selection, grid]);

    // Code Export Logic
    const generatePrompt = () => {
        const activeCells = grid.filter(c => !c.masterId);

        if (exportMode === 'JSON') {
            const prompt = {
                project: config.name,
                viewport: `${config.w}x${config.h}`,
                gridSystem: `${config.r}x${config.c}`,
                brandPalette: config.palette,
                components: activeCells.map(c => ({
                    id: c.customId,
                    type: c.type,
                    pos: { r: c.r, c: c.c, rs: c.rs, cs: c.cs },
                    dimensions: { width: c.width, height: c.height },
                    style: c.style,
                    outline: c.outline,
                    text: c.content || (c.type === 'button' ? 'Action' : c.type === 'text' ? 'Sample Text' : ''),
                    ...(c.type === 'image' && { imageUrl: c.imageUrl, imageAlt: c.imageAlt, imageFit: c.imageFit })
                }))
            };
            setPromptText(JSON.stringify(prompt, null, 2));
        } else {
            // React/Tailwind Export
            let jsx = `export default function ${config.name.replace(/\s+/g, '')}() {\n`;
            jsx += `  return (\n`;
            jsx += `    <div className="grid grid-cols-${config.c} grid-rows-${config.r} gap-1 bg-black w-full h-screen p-4">\n`;

            activeCells.forEach(c => {
                const s = c.style;
                const alignClass = s.textAlign === 'Center' ? 'text-center items-center justify-center' : s.textAlign === 'Right' ? 'text-right items-end justify-end' : 'text-left items-start justify-start';
                const gridClass = `row-start-${c.r + 1} row-span-${c.rs} col-start-${c.c + 1} col-span-${c.cs}`;

                if (c.type === 'image') {
                    jsx += `      <img${c.customId ? ` id="${c.customId}"` : ''} src="${c.imageUrl || ''}" alt="${c.imageAlt || 'Image'}" style={{ objectFit: '${c.imageFit || 'cover'}' }} className="${gridClass} w-full h-full" />\n`;
                } else if (c.type === 'button') {
                    jsx += `      <button style={{ backgroundColor: '${s.bg}', color: '${s.color}', fontSize: '${s.fontSize}px', padding: '${s.padding}px' }} className="${gridClass} ${alignClass} font-bold hover:opacity-80 transition-all active:scale-95">\n`;
                    jsx += `         ${c.content || 'Button'}\n`;
                    jsx += `      </button>\n`;
                } else if (c.type === 'input') {
                    jsx += `      <input type="text" placeholder="${c.content || 'Placeholder...'}" style={{ color: '${s.color}', fontSize: '${s.fontSize}px', padding: '${s.padding}px' }} className="${gridClass} bg-white/10 border border-white/20 outline-none focus:ring-1 ring-yellow-400" />\n`;
                } else if (c.type === 'text') {
                    jsx += `      <p style={{ color: '${s.color}', fontSize: '${s.fontSize}px', padding: '${s.padding}px' }} className="${gridClass} ${alignClass} flex font-medium">\n`;
                    jsx += `         ${c.content || 'Sample Typography'}\n`;
                    jsx += `      </p>\n`;
                } else {
                    jsx += `      <div style={{ backgroundColor: '${s.bg}', padding: '${s.padding}px' }} className="${gridClass} border border-white/5 shadow-inner" />\n`;
                }
            });

            jsx += `    </div>\n`;
            jsx += `  );\n}`;
            setPromptText(jsx);
        }
        setIsDirty(false);
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(promptText);
        setToast("클립보드에 복사가 완료되었어요");
        setTimeout(() => setToast(null), 3000);
    };

    // Component Renderer (Grid Internal)
    const renderComponent = (cell: GridCell) => {
        const isSelected = selectedRange && cell.r >= selectedRange.r1 && cell.r <= selectedRange.r2 && cell.c >= selectedRange.c1 && cell.c <= selectedRange.c2;

        // Real-time Preview: Mix cell state with editor state if selected
        const s = isSelected ? {
            ...cell.style,
            bg: editState.bg,
            color: editState.color,
            fontSize: editState.fontSize,
            fontWeight: editState.fontWeight,
            padding: editState.padding,
            textAlign: editState.textAlign
        } : cell.style;

        const type = isSelected ? editState.type : cell.type;
        const content = (isSelected && editState.content) ? editState.content : cell.content;

        const common = { color: s.color, fontSize: `${s.fontSize}px`, padding: `${s.padding}px`, textAlign: (s.textAlign?.toLowerCase() || 'left') as any };
        const flexAlign = s.textAlign === 'Center' ? 'center' : s.textAlign === 'Right' ? 'flex-end' : 'flex-start';

        switch (type) {
            case 'button':
                return <button style={{ ...common, backgroundColor: s.bg, fontWeight: s.fontWeight === 'Bold' ? 'bold' : 'normal' }} className="w-[85%] h-[60%] border border-white/10 active:scale-95 transition-all truncate px-4">{content || 'Button'}</button>;
            case 'input':
                return <div style={{ ...common, width: '90%' }} className="bg-white/5 border border-white/10 flex items-center gap-2 opacity-50"><Type size={12} /> {content || 'Input...'}</div>;
            case 'text':
                return <div style={{ ...common, fontWeight: s.fontWeight === 'Bold' ? 'bold' : 'normal', width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: flexAlign }} className="px-2 leading-tight overflow-hidden text-ellipsis whitespace-pre-wrap">{content || 'Typography'}</div>;
            case 'toggle':
                return <div className="flex items-center gap-2 scale-75"><div className="w-10 h-5 bg-white/10 relative"><div className="absolute right-1 top-1 w-3 h-3 bg-yellow-400 shadow-[0_0_10px_#FFD700]"></div></div></div>;
            case 'slider':
                return <div className="w-[80%] h-1 bg-white/10 relative"><div className="absolute left-0 top-1/2 -translate-y-1/2 w-[60%] h-full bg-yellow-400"></div><div className="absolute left-[60%] top-1/2 -translate-y-1/2 w-3 h-3 bg-white -translate-x-1/2 shadow-xl border-2 border-yellow-400"></div></div>;
            case 'image':
                const imgUrl = (isSelected && editState.imageUrl) ? editState.imageUrl : cell.imageUrl;
                const imgAlt = (isSelected && editState.imageAlt) ? editState.imageAlt : cell.imageAlt;
                const imgFit = (isSelected && editState.imageFit) ? editState.imageFit : cell.imageFit;
                if (imgUrl) {
                    return <img src={imgUrl} alt={imgAlt || 'Image'} style={{ width: '100%', height: '100%', objectFit: imgFit || 'cover' }} />;
                }
                return <div className="flex flex-col items-center gap-1 opacity-20"><ImageIcon size={20} /> <span className="text-[8px] font-bold">IMAGE</span></div>;
            default:
                return <span className="text-[10px] font-bold opacity-5 tracking-tighter">[{cell.r},{cell.c}]</span>;
        }
    };

    return (
        <div className="flex flex-col h-screen text-white select-none overflow-hidden" style={{ backgroundColor: TOKENS.bg }}>

            {/* A. Top (Header) */}
            <header className="h-[120px] px-8 grid grid-cols-[3fr_2fr_3fr_2fr] gap-6 items-center backdrop-blur-3xl z-50">
                <div className="flex flex-col cursor-default my-[10px] ml-[30px]">
                    <h1 className="text-[36px] font-black tracking-tighter" style={{ color: '#FBC22C' }}>
                        PixelGrid
                    </h1>
                </div>

                <div className="p-4 bg-white/[0.03] group transition-all hover:bg-white/[0.05] my-[10px] h-[100px] flex flex-col justify-center">
                    <div className="flex items-center justify-between mb-1">
                        <span className="text-[9px] font-black text-gray-500 uppercase tracking-widest">Active Canvas</span>
                        <Layout size={10} className="text-yellow-400 opacity-50" />
                    </div>
                    <p className="text-sm font-black truncate">{config.name}</p>
                    <p className="text-[10px] font-mono opacity-40">{config.w}x{config.h}px • {config.r}x{config.c} Grid</p>
                </div>

                <div className="p-4 bg-white/[0.03] font-mono flex flex-col justify-center my-[10px] h-[100px]">
                    <div className="flex items-center gap-6">
                        <div className="flex flex-col">
                            <span className="text-[8px] font-black text-gray-500 uppercase mb-1">Selection Start</span>
                            <span className={`text-[24px] font-black ${selection ? 'text-white' : 'text-white/10'}`}>{selection ? `[${selection.start[0]},${selection.start[1]}]` : '--'}</span>
                        </div>
                        <ChevronRight size={20} className="opacity-20 mt-4" />
                        <div className="flex flex-col">
                            <span className="text-[8px] font-black text-gray-500 uppercase mb-1">Selection End</span>
                            <span className={`text-[24px] font-black ${selection ? 'text-white' : 'text-white/10'}`}>{selection ? `[${selection.end[0]},${selection.end[1]}]` : '--'}</span>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col my-[10px] h-[100px] mr-[30px]">
                    {isCurrentMasterMerged ? (
                        <button onClick={handleUnmerge} className="w-full h-full bg-red-600/20 text-red-400 border border-red-500/30 hover:bg-red-600/30 font-black uppercase tracking-widest text-[10px] transition-all flex items-center justify-center gap-2 group">
                            <RotateCcw size={16} className="group-hover:rotate-180 transition-transform duration-500" /> 병합 취소 (U)
                        </button>
                    ) : (
                        <button disabled={!selection} onClick={handleMerge} className={`w-full h-full font-black uppercase tracking-widest text-[10px] transition-all flex items-center justify-center gap-2 ${selection ? 'bg-[#470EE1] text-black hover:scale-105 shadow-2xl shadow-purple-500/20' : 'bg-white/5 opacity-30 cursor-not-allowed text-white/20'}`}>
                            <Plus size={16} /> 셀 병합 (M)
                        </button>
                    )}
                </div>
            </header>

            {/* B. Middle (Workspace) */}
            <main className="flex-1 px-8 grid grid-cols-[2fr_6fr_2fr] gap-8" style={{ height: `calc(100vh - 210px)` }}>

                {/* Left Panel: Prompt for AI */}
                <div className="flex flex-col bg-white/[0.02] p-8 overflow-hidden backdrop-blur-md ml-[30px]">
                    <h3 className="text-[10px] font-black text-white/40 uppercase tracking-[0.4em] mb-10 flex items-center gap-2">Prompt for AI</h3>
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex gap-4">
                            {['JSON', 'React'].map(m => (
                                <button key={m} onClick={() => setExportMode(m as any)} className={`text-[10px] font-black uppercase tracking-widest transition-all ${exportMode === m ? 'text-yellow-400 border-b-2 border-yellow-400 pb-1' : 'text-white/20 hover:text-white/40'}`}>{m}</button>
                            ))}
                        </div>
                        <button onClick={() => { setGrid(grid.map(c => ({ ...c, rs: 1, cs: 1, isMerged: false, masterId: undefined, type: 'div' }))); setIsDirty(true); }} className="text-white/20 hover:text-white/50 transition-colors"><RotateCcw size={14} /></button>
                    </div>

                    <button onClick={generatePrompt} className="w-full py-5 mb-5 font-black uppercase tracking-[0.2em] text-[10px] transition-all flex items-center justify-center gap-2 group" style={{ backgroundColor: isDirty ? TOKENS.alert : '#181818', color: '#FFFFFF', border: `1px solid ${isDirty ? TOKENS.alert : 'rgba(255,255,255,0.05)'}` }}>
                        {isDirty ? '코드 수정반영함' : '프롬프트 생성하기'} <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                    </button>

                    <textarea readOnly value={promptText} className="flex-1 w-full bg-black/40 border border-white/5 p-6 text-[10px] font-mono outline-none resize-none placeholder:opacity-10 custom-scrollbar leading-relaxed" placeholder="Generate structure to see source code..." />

                    <div className="flex gap-3 mt-6">
                        <button onClick={copyToClipboard} className="flex-1 py-4 bg-[#FBC22C] text-black text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-2 hover:scale-105 active:scale-95 transition-all shadow-xl shadow-yellow-500/10">
                            <Copy size={12} /> 소스 복사하기
                        </button>
                    </div>
                </div>

                {/* Center Panel: Grid Canvas */}
                <div className="bg-black/50 overflow-auto flex items-start justify-center p-16 custom-scrollbar relative shadow-2xl mt-[30px]">
                    <div className="grid bg-transparent relative" style={{ gridTemplateColumns: `repeat(${config.c}, 1fr)`, gridTemplateRows: `repeat(${config.r}, 1fr)`, width: `${config.c * 80}px`, height: `${config.r * 80}px` }}>
                        {grid.map((cell) => {
                            // Skip cells that are covered by a merged cell
                            if (cell.masterId) return null;

                            const isSelected = selectedRange && cell.r >= selectedRange.r1 && cell.r <= selectedRange.r2 && cell.c >= selectedRange.c1 && cell.c <= selectedRange.c2;

                            // Build cell style
                            const isMergedCell = cell.rs > 1 || cell.cs > 1;
                            const cellStyle: React.CSSProperties = {
                                gridRow: `${cell.r + 1} / ${cell.r + 1 + cell.rs}`,
                                gridColumn: `${cell.c + 1} / ${cell.c + 1 + cell.cs}`,
                                width: isMergedCell ? '100%' : (cell.width ? `${cell.width}px` : undefined),
                                height: isMergedCell ? '100%' : (cell.height ? `${cell.height}px` : undefined)
                            };

                            // Apply outline if enabled
                            if (cell.outline?.enabled) {
                                cellStyle.outline = `${cell.outline.width}px ${cell.outline.style} ${cell.outline.color}`;
                                cellStyle.outlineOffset = '-1px';
                            }

                            return (
                                <div key={cell.id} onClick={() => handleCellClick(cell.r, cell.c)} className={`relative transition-all duration-300 cursor-cell bg-[#0A0A0A] flex items-center justify-center group border border-[#333333] ${isSelected ? 'z-10 bg-[#470EE1]/10 ring-2 ring-inset ring-[#470EE1] shadow-[0_0_30px_rgba(71,14,225,0.2)]' : 'hover:bg-white/5'}`} style={cellStyle}>
                                    {renderComponent(cell)}
                                    {cell.rs * cell.cs > 1 && (
                                        <div className="absolute top-2 right-2 flex items-center gap-1.5 px-1.5 py-0.5 bg-purple-600 shadow-lg">
                                            <div className="w-1 h-1 bg-white animate-pulse"></div>
                                            <span className="text-[7px] font-black text-white">{cell.rs}x{cell.cs}</span>
                                        </div>
                                    )}
                                    {isSelected && <div className="absolute inset-0 border border-white/10 pointer-events-none animate-pulse"></div>}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Right Panel: Style Editor */}
                <div className="flex flex-col bg-white/[0.02] p-8 overflow-y-auto custom-scrollbar backdrop-blur-md mr-[30px]">
                    <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-[0.4em] mb-10 flex items-center gap-2"><Scissors size={12} className="text-yellow-400" /> Selection Editor</h3>

                    <div className="flex flex-col gap-[10px]">
                        {/* Cell ID */}
                        <label className="block">
                            <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Cell ID</span>
                            <input value={editState.customId} onChange={e => setEditState({ ...editState, customId: e.target.value })} placeholder="e.g., header-logo" className="w-full bg-black/40 border border-white/5 px-5 py-3 text-xs font-mono focus:border-yellow-400 outline-none transition-all placeholder:opacity-20" />
                        </label>

                        {/* Component Type */}
                        <label className="block">
                            <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Component Type</span>
                            <div className="grid grid-cols-2 gap-2">
                                {['div', 'button', 'text', 'input', 'slider', 'toggle', 'image'].map(t => (
                                    <button key={t} onClick={() => setEditState({ ...editState, type: t })} className={`py-3 text-[9px] font-black uppercase transition-all border ${editState.type === t ? 'bg-yellow-400 text-black border-yellow-400' : 'bg-black/40 text-gray-500 border-white/5 hover:border-white/20'}`}>{t === 'div' ? 'Container' : t}</button>
                                ))}
                            </div>
                        </label>

                        {/* Component Content */}
                        <label className="block">
                            <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Component Content</span>
                            <input value={editState.content} onChange={e => setEditState({ ...editState, content: e.target.value })} placeholder="Enter label or value..." className="w-full bg-black/40 border border-white/5 px-5 py-4 text-xs font-bold focus:border-yellow-400 outline-none transition-all placeholder:opacity-20" />
                        </label>

                        {/* Dimensions */}
                        <div className="grid grid-cols-2 gap-4">
                            <label className="block">
                                <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Width (PX)</span>
                                <input type="number" value={editState.width} onChange={e => setEditState({ ...editState, width: e.target.value })} className="w-full bg-black/40 border border-white/5 px-5 py-3 text-xs font-mono outline-none focus:border-yellow-400 transition-all" />
                            </label>
                            <label className="block">
                                <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Height (PX)</span>
                                <input type="number" value={editState.height} onChange={e => setEditState({ ...editState, height: e.target.value })} className="w-full bg-black/40 border border-white/5 px-5 py-3 text-xs font-mono outline-none focus:border-yellow-400 transition-all" />
                            </label>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <label className="block">
                                <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">FontSize (PX)</span>
                                <input type="number" value={editState.fontSize} onChange={e => setEditState({ ...editState, fontSize: e.target.value })} className="w-full bg-black/40 border border-white/5 px-5 py-3 text-xs font-mono outline-none focus:border-yellow-400 transition-all" />
                            </label>
                            <label className="block">
                                <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Weight</span>
                                <div className="grid grid-cols-2 gap-2">
                                    {['Regular', 'Bold'].map(w => (
                                        <button key={w} onClick={() => setEditState({ ...editState, fontWeight: w })} className={`py-3 text-[9px] font-black uppercase transition-all border ${editState.fontWeight === w ? 'bg-yellow-400 text-black border-yellow-400' : 'bg-black/40 text-gray-500 border-white/5 hover:border-white/20'}`}>{w}</button>
                                    ))}
                                </div>
                            </label>
                        </div>

                        <label className="block">
                            <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Color Palette</span>
                            <div className="flex flex-wrap gap-2.5 mb-4">
                                {config.palette?.map((c: string, i: number) => (
                                    <button key={i} onClick={() => setEditState({ ...editState, bg: c })} className={`w-8 h-8 border-2 transition-transform hover:scale-110 active:scale-95 ${editState.bg === c ? 'border-white scale-110 shadow-lg' : 'border-white/5'}`} style={{ backgroundColor: c }} />
                                ))}
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div className="p-3 bg-black/40 border border-white/5">
                                    <span className="text-[7px] uppercase opacity-30 block mb-2 font-black">Background</span>
                                    <input type="color" value={editState.bg} onChange={e => setEditState({ ...editState, bg: e.target.value })} className="w-full h-8 bg-transparent cursor-pointer" />
                                </div>
                                <div className="p-3 bg-black/40 border border-white/5">
                                    <span className="text-[7px] uppercase opacity-30 block mb-2 font-black">Foreground</span>
                                    <input type="color" value={editState.color} onChange={e => setEditState({ ...editState, color: e.target.value })} className="w-full h-8 bg-transparent cursor-pointer" />
                                </div>
                            </div>
                        </label>

                        <label className="block">
                            <div className="flex justify-between mb-3">
                                <span className="text-[9px] font-black uppercase text-gray-600 tracking-widest">Global Padding</span>
                                <span className="text-[9px] font-mono text-yellow-400">{editState.padding}px</span>
                            </div>
                            <input type="range" min="0" max="64" value={editState.padding} onChange={e => setEditState({ ...editState, padding: e.target.value })} className="w-full accent-yellow-400 h-1.5 bg-white/10 rounded-full appearance-none cursor-pointer" />
                        </label>

                        {/* Outline Control */}
                        <label className="block">
                            <div className="flex justify-between items-center mb-3">
                                <span className="text-[9px] font-black uppercase text-gray-600 tracking-widest">Outline</span>
                                <button onClick={() => setEditState({ ...editState, outlineEnabled: !editState.outlineEnabled })} className={`px-3 py-1 text-[8px] font-black uppercase transition-all ${editState.outlineEnabled ? 'bg-yellow-400 text-black' : 'bg-black/40 text-gray-500 border border-white/5'}`}>
                                    {editState.outlineEnabled ? 'ON' : 'OFF'}
                                </button>
                            </div>
                            {editState.outlineEnabled && (
                                <div className="space-y-3 mt-3">
                                    <div>
                                        <div className="flex justify-between mb-2">
                                            <span className="text-[8px] uppercase text-gray-600">Width</span>
                                            <span className="text-[8px] font-mono text-yellow-400">{editState.outlineWidth}px</span>
                                        </div>
                                        <input type="range" min="1" max="10" value={editState.outlineWidth} onChange={e => setEditState({ ...editState, outlineWidth: e.target.value })} className="w-full accent-yellow-400 h-1 bg-white/10 rounded-full appearance-none cursor-pointer" />
                                    </div>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="p-2 bg-black/40 border border-white/5">
                                            <span className="text-[7px] uppercase opacity-30 block mb-2 font-black">Color</span>
                                            <input type="color" value={editState.outlineColor} onChange={e => setEditState({ ...editState, outlineColor: e.target.value })} className="w-full h-6 bg-transparent cursor-pointer" />
                                        </div>
                                        <div className="p-2 bg-black/40 border border-white/5">
                                            <span className="text-[7px] uppercase opacity-30 block mb-2 font-black">Style</span>
                                            <select value={editState.outlineStyle} onChange={e => setEditState({ ...editState, outlineStyle: e.target.value as 'solid' | 'dashed' | 'dotted' })} className="w-full bg-transparent text-[10px] text-white outline-none cursor-pointer">
                                                <option value="solid">Solid</option>
                                                <option value="dashed">Dashed</option>
                                                <option value="dotted">Dotted</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </label>

                        {/* Image Settings (only when type === 'image') */}
                        {editState.type === 'image' && (
                            <div className="space-y-3">
                                <label className="block">
                                    <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Image URL</span>
                                    <input value={editState.imageUrl} onChange={e => setEditState({ ...editState, imageUrl: e.target.value })} placeholder="https://..." className="w-full bg-black/40 border border-white/5 px-5 py-3 text-xs font-mono focus:border-yellow-400 outline-none transition-all placeholder:opacity-20" />
                                </label>
                                <label className="block">
                                    <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Alt Text</span>
                                    <input value={editState.imageAlt} onChange={e => setEditState({ ...editState, imageAlt: e.target.value })} placeholder="Image description" className="w-full bg-black/40 border border-white/5 px-5 py-3 text-xs font-mono focus:border-yellow-400 outline-none transition-all placeholder:opacity-20" />
                                </label>
                                <label className="block">
                                    <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Object Fit</span>
                                    <div className="grid grid-cols-3 gap-2">
                                        {['cover', 'contain', 'fill'].map(fit => (
                                            <button key={fit} onClick={() => setEditState({ ...editState, imageFit: fit as 'cover' | 'contain' | 'fill' })} className={`py-3 border text-[9px] font-black uppercase transition-all ${editState.imageFit === fit ? 'bg-[#FBC22C] text-black border-yellow-400' : 'bg-black/40 text-gray-500 border-white/5 hover:border-white/10'}`}>{fit}</button>
                                        ))}
                                    </div>
                                </label>
                            </div>
                        )}

                        <label className="block">
                            <span className="text-[9px] font-black uppercase text-gray-600 mb-3 block tracking-widest">Content Alignment</span>
                            <div className="grid grid-cols-3 gap-2">
                                {['Left', 'Center', 'Right'].map(a => (
                                    <button key={a} onClick={() => setEditState({ ...editState, textAlign: a })} className={`py-3 border text-[9px] font-black uppercase transition-all ${editState.textAlign === a ? 'bg-[#FBC22C] text-black border-yellow-400' : 'bg-black/40 text-gray-500 border-white/5 hover:border-white/10'}`}>{a}</button>
                                ))}
                            </div>
                        </label>

                        <div className="pt-2">
                            <button onClick={applyStyle} disabled={!selection} className={`w-full py-5 font-black uppercase text-[10px] tracking-[0.3em] transition-all shadow-2xl active:scale-95 ${selection ? 'bg-[#FBC22C] text-black hover:scale-[1.03] shadow-yellow-500/20' : 'bg-white/5 text-gray-600 cursor-not-allowed border border-white/5'}`}>
                                디자인 속성 적용
                            </button>
                        </div>
                    </div>
                </div>
            </main>

            {/* C. Bottom (Footer) */}
            <footer className="h-[70px] bg-transparent"></footer>

            {/* Notifications */}
            {toast && (
                <div className="fixed bottom-12 left-1/2 -translate-x-1/2 px-10 py-5 bg-[#470EE1] text-white font-black shadow-[0_20px_60px_rgba(71,14,225,0.4)] animate-in fade-in slide-in-from-bottom-10 duration-500 z-[100] flex items-center gap-4 border border-white/10">
                    <div className="p-2 bg-yellow-400 text-black"><CheckSquare size={16} /></div>
                    <span className="tracking-tight">{toast}</span>
                </div>
            )}

            <style jsx>{`
                .custom-scrollbar::-webkit-scrollbar { width: 5px; height: 5px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.05); transition: background 0.3s; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.1); }
                input[type='range']::-webkit-slider-thumb {
                    appearance: none;
                    width: 16px;
                    height: 16px;
                    background: #FBC22C;
                    cursor: pointer;
                    box-shadow: 0 0 10px rgba(251, 194, 44, 0.4);
                    border: 2px solid white;
                    border-radius: 50%;
                }
            `}</style>
        </div>
    );
}
