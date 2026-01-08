'use client';

import React, { useState, useEffect } from 'react';
import {
    Monitor,
    Palette,
    Settings2,
    Layout,
    Layers,
    Save,
    FolderOpen,
    Plus,
    Trash2,
    ChevronRight,
    Type
} from 'lucide-react';

import { useRouter } from 'next/navigation';

// Design Tokens (Internal Style for Phase 1)
const DESIGN_TOKENS = `
  :root {
    --space-xs: 4px; --space-sm: 8px; --space-md: 16px; --space-lg: 24px; --space-xl: 32px;
    --radius-sm: 4px; --radius-md: 8px; --radius-full: 9999px;
    --font-xs: 12px; --font-sm: 14px; --font-md: 16px; --font-lg: 20px; --font-xl: 24px;
    
    --pg-obsidian: #0A0A0A;
    --pg-coal: #121212;
    --pg-solar: #FFD700;
    --pg-cyber: #3B82F6;
    --pg-border: #262626;
  }
`;

export default function PixelGridSetup() {
    const router = useRouter();
    const [pageName, setPageName] = useState('New Project');
    const [canvasSize, setCanvasSize] = useState({ w: 1920, h: 1080, unit: 'px' });
    const [pageType, setPageType] = useState('Page');
    const [gridDim, setGridDim] = useState({ r: 12, c: 12 });
    const [palette, setPalette] = useState(Array(10).fill('#333333'));
    const [reusableTemplates, setReusableTemplates] = useState<any[]>([]);
    const [theme, setTheme] = useState('obsidian');

    const updatePalette = (index: number, color: string) => {
        const newPalette = [...palette];
        newPalette[index] = color;
        setPalette(newPalette);
    };

    const handleCreatePage = () => {
        const config = {
            name: pageName,
            w: canvasSize.w,
            h: canvasSize.h,
            type: pageType,
            r: gridDim.r,
            c: gridDim.c,
            palette,
            theme
        };
        localStorage.setItem('pixelgrid_config', JSON.stringify(config));
        router.push('/pixelgrid/editor');
    };

    return (
        <div className="min-h-screen bg-[#0A0A0A] text-white p-8 font-sans selection:bg-[#FFD700] selection:text-black">
            <style>{DESIGN_TOKENS}</style>

            {/* Header */}
            <header className="max-w-7xl mx-auto mb-12 flex items-center justify-between border-b border-[#262626] pb-8">
                <div>
                    <h1 className="text-4xl font-black tracking-tighter flex items-center gap-3">
                        PixelGrid <span className="text-[10px] bg-[#FFD700] text-black px-2 py-0.5 rounded-full uppercase font-bold tracking-widest">v1.alpha</span>
                    </h1>
                    <p className="text-gray-500 text-sm mt-1 uppercase tracking-widest font-medium">Developer UI Authoring Engine</p>
                </div>
                <div className="flex gap-4">
                    <button className="px-6 py-3 bg-[#121212] border border-[#262626] rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-[#1A1A1A] transition-all flex items-center gap-2">
                        <FolderOpen size={14} /> Saved Projects
                    </button>
                    <button className="px-6 py-3 bg-[#FFD700] text-black rounded-xl text-xs font-black uppercase tracking-widest hover:scale-105 transition-all flex items-center gap-2 shadow-[0_0_20px_rgba(255,215,0,0.3)]">
                        <Plus size={16} /> Create New Canvas
                    </button>
                </div>
            </header>

            <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10">

                {/* Left: Configuration Column */}
                <div className="lg:col-span-4 space-y-8">

                    {/* Card: Basic Settings */}
                    <section className="bg-[#121212] border border-[#262626] rounded-3xl p-8 space-y-6">
                        <h2 className="text-xs font-black text-gray-500 uppercase tracking-[0.3em] flex items-center gap-2 mb-4">
                            <Settings2 size={16} className="text-[#FFD700]" /> Canvas Settings
                        </h2>

                        <div className="space-y-4">
                            <label className="block">
                                <span className="text-[10px] font-black uppercase text-gray-600 mb-2 block">Project Identification</span>
                                <input
                                    type="text"
                                    value={pageName}
                                    onChange={e => setPageName(e.target.value)}
                                    className="w-full bg-black border border-[#262626] rounded-xl px-4 py-3 focus:border-[#FFD700] outline-none transition-all text-sm font-bold"
                                />
                            </label>

                            <div className="grid grid-cols-2 gap-4">
                                <label className="block">
                                    <span className="text-[10px] font-black uppercase text-gray-600 mb-2 block">Width</span>
                                    <input
                                        type="number"
                                        value={canvasSize.w}
                                        onChange={e => setCanvasSize({ ...canvasSize, w: +e.target.value })}
                                        className="w-full bg-black border border-[#262626] rounded-xl px-4 py-3 focus:border-[#FFD700] outline-none transition-all text-sm font-mono"
                                    />
                                </label>
                                <label className="block">
                                    <span className="text-[10px] font-black uppercase text-gray-600 mb-2 block">Height</span>
                                    <input
                                        type="number"
                                        value={canvasSize.h}
                                        onChange={e => setCanvasSize({ ...canvasSize, h: +e.target.value })}
                                        className="w-full bg-black border border-[#262626] rounded-xl px-4 py-3 focus:border-[#FFD700] outline-none transition-all text-sm font-mono"
                                    />
                                </label>
                            </div>

                            <label className="block">
                                <span className="text-[10px] font-black uppercase text-gray-600 mb-2 block">Layout Context</span>
                                <select
                                    value={pageType}
                                    onChange={e => setPageType(e.target.value)}
                                    className="w-full bg-black border border-[#262626] rounded-xl px-4 py-3 focus:border-[#FFD700] outline-none transition-all text-sm font-bold appearance-none"
                                >
                                    <option>Page</option>
                                    <option>Modal</option>
                                    <option>Popup</option>
                                    <option>Component</option>
                                </select>
                            </label>
                        </div>
                    </section>

                    {/* Card: Grid Specification */}
                    <section className="bg-[#121212] border border-[#262626] rounded-3xl p-8">
                        <h2 className="text-xs font-black text-gray-500 uppercase tracking-[0.3em] flex items-center gap-2 mb-6">
                            <Layout size={16} className="text-[#3B82F6]" /> Grid Specification
                        </h2>
                        <div className="grid grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <span className="text-[10px] font-black text-gray-600 uppercase">Rows</span>
                                <input type="number" value={gridDim.r} onChange={e => setGridDim({ ...gridDim, r: +e.target.value })} className="w-full bg-black border border-[#262626] rounded-xl p-4 text-2xl font-black text-center" />
                            </div>
                            <div className="space-y-2">
                                <span className="text-[10px] font-black text-gray-600 uppercase">Columns</span>
                                <input type="number" value={gridDim.c} onChange={e => setGridDim({ ...gridDim, c: +e.target.value })} className="w-full bg-black border border-[#262626] rounded-xl p-4 text-2xl font-black text-center" />
                            </div>
                        </div>
                        <p className="text-[9px] text-gray-600 mt-4 text-center font-bold uppercase tracking-widest">Initial resolution: {gridDim.r * gridDim.c} cells</p>
                    </section>

                </div>

                {/* Right: Style & Templates Column */}
                <div className="lg:col-span-8 space-y-8">

                    {/* Card: Style & Palette */}
                    <section className="bg-[#121212] border border-[#262626] rounded-[2.5rem] p-10 flex flex-col md:flex-row gap-12">
                        <div className="flex-1 space-y-8">
                            <div>
                                <h2 className="text-xs font-black text-gray-500 uppercase tracking-[0.3em] flex items-center gap-2 mb-6">
                                    <Palette size={16} className="text-[#FFD700]" /> Brand Palette
                                </h2>
                                <div className="grid grid-cols-5 gap-3">
                                    {palette.map((color, i) => (
                                        <div key={i} className="group relative">
                                            <input
                                                type="color"
                                                value={color}
                                                onChange={(e) => updatePalette(i, e.target.value)}
                                                className="w-full h-12 rounded-xl border-2 border-[#262626] cursor-pointer hover:scale-105 transition-all overflow-hidden bg-transparent"
                                            />
                                            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[8px] font-mono text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                                                {color.toUpperCase()}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div>
                                <h2 className="text-xs font-black text-gray-500 uppercase tracking-[0.3em] flex items-center gap-2 mb-6">
                                    <Type size={16} className="text-[#3B82F6]" /> Typography Presets
                                </h2>
                                <div className="flex flex-wrap gap-2">
                                    {['H1', 'H2', 'H3', 'Body', 'Caption'].map((t, idx) => (
                                        <div key={t} className="px-4 py-2 bg-black border border-[#262626] rounded-lg text-xs font-black text-gray-400 hover:text-[#FFD700] hover:border-[#FFD700] cursor-default transition-all">
                                            {t} <span className="text-[9px] ml-1 opacity-50">[{24 - idx * 2}px]</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="md:w-64 flex flex-col justify-end">
                            <div className="p-6 bg-black rounded-3xl border border-[#262626] space-y-4">
                                <p className="text-[10px] font-black uppercase text-gray-500">Theme Engine</p>
                                <div className="flex gap-2">
                                    <button className={`flex-1 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${theme === 'obsidian' ? 'bg-[#FFD700] text-black shadow-lg' : 'bg-[#1A1A1A] text-gray-500 hover:text-white'}`} onClick={() => setTheme('obsidian')}>Obsidian</button>
                                    <button className={`flex-1 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${theme === 'light' ? 'bg-white text-black shadow-lg' : 'bg-[#1A1A1A] text-gray-500 hover:text-white'}`} onClick={() => setTheme('light')}>Light</button>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Card: Reusable Assets */}
                    <section className="bg-[#121212] border border-[#262626] rounded-[2.5rem] p-10 min-h-[400px] flex flex-col">
                        <h2 className="text-xs font-black text-gray-500 uppercase tracking-[0.3em] flex items-center gap-2 mb-10">
                            <Layers size={16} className="text-[#FFD700]" /> Reusable Design Templates
                        </h2>

                        {reusableTemplates.length === 0 ? (
                            <div className="flex-1 flex flex-col items-center justify-center space-y-4 border-2 border-dashed border-[#262626] rounded-[2rem]">
                                <div className="w-16 h-16 bg-[#1A1A1A] rounded-full flex items-center justify-center text-gray-700">
                                    <FolderOpen size={32} />
                                </div>
                                <div className="text-center">
                                    <p className="text-sm font-bold text-gray-500 tracking-tight">현재 사용 가능한 디자인이 없음</p>
                                    <p className="text-[9px] text-gray-700 uppercase tracking-widest mt-1 font-bold">Start by creating your first masterpiece</p>
                                </div>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Placeholder for template rendering */}
                            </div>
                        )}

                        <button
                            onClick={handleCreatePage}
                            className="mt-10 w-full py-6 bg-[#FFD700] text-black hover:scale-[1.02] active:scale-95 rounded-3xl font-black uppercase text-sm tracking-[0.2em] shadow-2xl shadow-yellow-500/20 transition-all flex items-center justify-center gap-3 group"
                        >
                            <Plus size={20} className="group-hover:rotate-90 transition-transform" /> 페이지 생성 (Initialize Canvas Editor) <ChevronRight size={20} className="group-hover:translate-x-2 transition-transform" />
                        </button>
                    </section>

                </div>

            </main>

            <footer className="max-w-7xl mx-auto mt-20 pt-8 border-t border-[#262626] flex justify-between items-center text-gray-600 text-[10px] font-black uppercase tracking-[0.2em]">
                <span>&copy; 2026 MONEWMENT - PIXELGRID ENGINE</span>
                <div className="flex gap-8">
                    <span className="hover:text-[#FFD700] cursor-pointer">Documentation</span>
                    <span className="hover:text-[#FFD700] cursor-pointer">API Keys</span>
                    <span className="hover:text-[#FFD700] cursor-pointer">Feedback</span>
                </div>
            </footer>
        </div>
    );
}
