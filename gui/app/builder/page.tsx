'use client';
import React, { useState, useEffect } from 'react';
import UIRenderer from '@/components/ui-engine/Renderer';

// 초기 샘플 데이터 (엑셀의 행들)
const INITIAL_ROWS = [
    { id: 1, type: 'text', content: 'Grid Builder Test', className: 'text-2xl font-bold text-white' },
    { id: 2, type: 'button', label: 'Click Me', variant: 'primary', className: 'w-full' },
    { id: 3, type: 'input', placeholder: 'Enter text...', className: '' },
];

export default function BuilderPage() {
    // 이것이 우리의 "엑셀 데이터"입니다.
    const [rows, setRows] = useState<any[]>(INITIAL_ROWS);
    const [previewSchema, setPreviewSchema] = useState<any>(null);

    // 엑셀 데이터가 바뀌면 -> 미리보기(JSON)를 실시간 업데이트
    useEffect(() => {
        const schema = {
            type: 'container',
            style: { className: 'w-full h-full p-8 flex flex-col space-y-4 bg-[#141414]' },
            children: rows.map(row => ({
                type: row.type,
                props: {
                    content: row.content,
                    label: row.label,
                    placeholder: row.placeholder,
                    variant: row.variant
                },
                style: { className: row.className }
            }))
        };
        setPreviewSchema(schema);
    }, [rows]);

    // 엑셀 셀 수정 함수
    const updateRow = (id: number, field: string, value: string) => {
        setRows(prev => prev.map(r => r.id === id ? { ...r, [field]: value } : r));
    };

    // 행 추가
    const addRow = () => {
        const newId = Math.max(...rows.map(r => r.id), 0) + 1;
        setRows([...rows, { id: newId, type: 'button', label: 'New Item', className: '' }]);
    };

    // 행 삭제
    const deleteRow = (id: number) => {
        setRows(rows.filter(r => r.id !== id));
    };

    return (
        <div className="h-screen w-screen flex flex-col bg-[#1A1A1A] text-white">

            {/* 1. 상단: 실시간 미리보기 (Preview) */}
            <div className="flex-1 border-b border-[#333] relative overflow-auto bg-black/50">
                <div className="absolute top-4 left-4 bg-[#333] px-3 py-1 rounded text-xs text-[#FFD700]">
                    LIVE PREVIEW
                </div>
                <div className="max-w-3xl mx-auto h-full border-x border-[#262626] bg-[#141414]">
                    {/* 우리의 엔진이 여기서 돌아갑니다 */}
                    <UIRenderer schema={previewSchema} />
                </div>
            </div>

            {/* 2. 하단: 엑셀형 에디터 (Grid Editor) */}
            <div className="h-[40%] bg-[#1A1A1A] flex flex-col">
                <div className="h-10 border-b border-[#333] flex items-center px-4 justify-between bg-[#202020]">
                    <span className="font-bold text-sm">Component List</span>
                    <button onClick={addRow} className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-500">
                        + Add Row
                    </button>
                </div>

                <div className="flex-1 overflow-auto p-4">
                    <table className="w-full text-left text-sm border-collapse">
                        <thead className="text-[#808080] bg-[#262626] sticky top-0">
                            <tr>
                                <th className="p-2 border border-[#333] w-20">Type</th>
                                <th className="p-2 border border-[#333]">Content / Label</th>
                                <th className="p-2 border border-[#333]">Styles (Tailwind)</th>
                                <th className="p-2 border border-[#333] w-24">Option</th>
                                <th className="p-2 border border-[#333] w-16">Del</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map((row) => (
                                <tr key={row.id} className="hover:bg-[#262626]">
                                    {/* Type 선택 */}
                                    <td className="border border-[#333] p-1">
                                        <select
                                            value={row.type}
                                            onChange={(e) => updateRow(row.id, 'type', e.target.value)}
                                            className="w-full bg-transparent outline-none text-[#FFD700]"
                                        >
                                            <option value="container">Box</option>
                                            <option value="text">Text</option>
                                            <option value="button">Button</option>
                                            <option value="input">Input</option>
                                        </select>
                                    </td>

                                    {/* 내용 입력 (엑셀처럼) */}
                                    <td className="border border-[#333] p-1">
                                        <input
                                            type="text"
                                            value={row.content || row.label || row.placeholder || ''}
                                            onChange={(e) => {
                                                updateRow(row.id, 'content', e.target.value);
                                                updateRow(row.id, 'label', e.target.value);
                                                updateRow(row.id, 'placeholder', e.target.value);
                                            }}
                                            className="w-full bg-transparent outline-none"
                                        />
                                    </td>

                                    {/* 스타일 입력 */}
                                    <td className="border border-[#333] p-1">
                                        <input
                                            type="text"
                                            value={row.className}
                                            onChange={(e) => updateRow(row.id, 'className', e.target.value)}
                                            placeholder="e.g. w-full bg-blue-500"
                                            className="w-full bg-transparent outline-none text-[#A0A0A0]"
                                        />
                                    </td>

                                    {/* 옵션 (버튼 색상 등) */}
                                    <td className="border border-[#333] p-1">
                                        {row.type === 'button' && (
                                            <select
                                                value={row.variant}
                                                onChange={(e) => updateRow(row.id, 'variant', e.target.value)}
                                                className="w-full bg-transparent outline-none text-xs"
                                            >
                                                <option value="primary">Blue</option>
                                                <option value="secondary">Gray</option>
                                                <option value="danger">Red</option>
                                            </select>
                                        )}
                                    </td>

                                    {/* 삭제 버튼 */}
                                    <td className="border border-[#333] p-1 text-center">
                                        <button onClick={() => deleteRow(row.id)} className="text-red-500 hover:text-white">✕</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* JSON 내보내기 버튼 */}
                <div className="h-12 border-t border-[#333] flex items-center justify-end px-4 space-x-2 bg-[#202020]">
                    <span className="text-xs text-gray-500">작업이 끝나면 JSON을 복사해서 파일에 붙여넣으세요.</span>
                    <button
                        onClick={() => navigator.clipboard.writeText(JSON.stringify(previewSchema, null, 2))}
                        className="bg-[#FFD700] text-black font-bold px-4 py-2 rounded text-sm hover:bg-yellow-400"
                    >
                        Copy JSON Code
                    </button>
                </div>
            </div>
        </div>
    );
}