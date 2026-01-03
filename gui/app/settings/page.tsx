"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// [타입 정의]
interface DBColumn { name: string; type: string; nullable?: boolean; primary_key?: boolean; }
interface DBTable { table_name: string; columns: DBColumn[]; }
interface ServiceItem { id: string; name: string; price: number; desc?: string; status?: string; type?: string; }
interface ServicesData { installed: ServiceItem[]; available: ServiceItem[]; }
// [신규] 멤버 및 API 타입
interface Member { user_id: number; name: string; email: string; role: string; allowed_features: string[]; joined_at: string; }
interface ApiEndpoint { path: string; methods: string[]; name: string; description: string; }

export default function SettingsPage() {
    const router = useRouter();
    // [탭 상태] service: 서비스, team: 팀원(신규), general: 일반(Env/Schema)
    const [activeTab, setActiveTab] = useState("service");
    const projectName = "chat-bot-v1"; // 현재 관리 중인 프로젝트 (추후 동적 할당)

    // [데이터 상태: 기존]
    const [envContent, setEnvContent] = useState("");
    const [schemaData, setSchemaData] = useState<DBTable[]>([]);
    const [services, setServices] = useState<ServicesData>({ installed: [], available: [] });
    const [apiKey, setApiKey] = useState("");
    const [isSaving, setIsSaving] = useState(false);
    const [showMarket, setShowMarket] = useState(false);

    // [데이터 상태: 신규 (Team & Collector)]
    const [members, setMembers] = useState<Member[]>([]);
    const [inviteEmail, setInviteEmail] = useState("");
    const [apiEndpoints, setApiEndpoints] = useState<ApiEndpoint[]>([]);

    // [데이터 로드]
    useEffect(() => {
        // 1. 공통 데이터 (서비스 목록 등)
        fetch('http://localhost:8001/api/services/list')
            .then(res => res.json())
            .then(data => setServices(data))
            .catch(e => console.error("Service Load Error:", e));

        // 2. 탭별 데이터 로드 (최적화)
        if (activeTab === "team") {
            fetch(`http://localhost:8001/api/projects/${projectName}/members`)
                .then(res => res.json())
                .then(data => setMembers(data.members || []))
                .catch(e => console.error("Member Load Error:", e));
        }
        else if (activeTab === "general") {
            // Env 파일
            fetch('http://localhost:8001/api/admin/env')
                .then(res => res.json())
                .then(data => setEnvContent(data.content));
            // DB Schema (Realtime Collector)
            fetch('http://localhost:8001/api/admin/schema')
                .then(res => res.json())
                .then(data => setSchemaData(data.schema || []));
            // [신규] API Endpoints (Realtime Collector)
            fetch('http://localhost:8001/api/admin/endpoints')
                .then(res => res.json())
                .then(data => setApiEndpoints(data.endpoints || []));
        }
    }, [activeTab]);

    // [핸들러 1] Env 파일 저장
    const handleSaveEnv = async () => {
        setIsSaving(true);
        try {
            const res = await fetch('http://localhost:8001/api/admin/env', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: envContent })
            });
            if (res.ok) alert("✅ 시스템 설정이 저장되었습니다.");
        } catch (e) { alert("저장 실패"); }
        setIsSaving(false);
    };

    // [핸들러 2] API Key 저장
    const handleKeyUpdate = async () => {
        try {
            const res = await fetch('http://localhost:8001/api/services/keys', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ service_name: 'gemini', api_key: apiKey })
            });
            if (res.ok) alert("✅ API Key가 안전하게 암호화되어 저장되었습니다.");
        } catch (e) { alert("키 저장 실패"); }
    };

    // [핸들러 3] 팀원 초대 (신규 기능)
    const handleInvite = async () => {
        if (!inviteEmail) return alert("초대할 이메일을 입력해주세요.");
        try {
            const res = await fetch('http://localhost:8001/api/projects/members/invite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    project_name: projectName,
                    target_email: inviteEmail,
                    features: ["logs", "mcp-bot"] // 기본 권한 부여
                })
            });
            const data = await res.json();
            if (res.ok) {
                alert(data.message);
                setInviteEmail("");
                // 멤버 목록 새로고침
                fetch(`http://localhost:8001/api/projects/${projectName}/members`)
                    .then(r => r.json()).then(d => setMembers(d.members));
            } else {
                alert("초대 실패: " + (data.detail || "알 수 없는 오류"));
            }
        } catch (e) { alert("서버 통신 오류"); }
    };

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-200 p-6 md:p-12 font-sans">
            <div className="max-w-6xl mx-auto">

                {/* 헤더 */}
                <div className="mb-8 border-b border-slate-800 pb-4 flex justify-between items-end">
                    <div>
                        <Link href="/dashboard" className="text-xs text-blue-400 hover:text-white mb-2 block">← BACK TO DASHBOARD</Link>
                        <h1 className="text-3xl font-black text-white italic tracking-tighter">
                            SETTING <span className="text-blue-500">MANAGER</span>
                        </h1>
                        <p className="text-xs text-slate-500 mt-1">Target Project: <span className="text-white font-bold">{projectName}</span></p>
                    </div>
                    {/* 탭 메뉴 (확장됨) */}
                    <div className="flex gap-2 bg-slate-900 p-1 rounded-lg border border-slate-800">
                        {["service", "team", "general"].map(tab => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`px-6 py-2 rounded-md font-bold text-sm transition-all uppercase ${activeTab === tab ? "bg-blue-600 text-white shadow-lg" : "text-slate-500 hover:text-white"}`}
                            >
                                {tab === "service" ? "🛠️ Service" : tab === "team" ? "👥 Team" : "⚙️ General"}
                            </button>
                        ))}
                    </div>
                </div>

                {/* [TAB 1] 서비스 관리 (기존 로직 100% 유지) */}
                {activeTab === "service" && (
                    <div className="space-y-8 animate-fade-in">

                        {/* 1. Installed Services */}
                        <section>
                            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                Active Services (사용 중)
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {services.installed && services.installed.map((item, idx) => (
                                    <div key={idx} className="bg-slate-900 border border-slate-700 p-5 rounded-xl flex justify-between items-center shadow-lg">
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <h3 className="font-bold text-white">{item.name}</h3>
                                                <span className="text-[10px] bg-green-900 text-green-400 px-1.5 py-0.5 rounded font-bold uppercase">Active</span>
                                            </div>
                                            <p className="text-xs text-slate-500 mt-1">Status: Operational</p>
                                        </div>
                                        <button className="text-xs bg-slate-800 border border-slate-700 px-3 py-1.5 rounded text-slate-400 hover:bg-slate-700 hover:text-white transition-all">설정</button>
                                    </div>
                                ))}

                                {/* [+] 버튼 */}
                                <button
                                    onClick={() => setShowMarket(!showMarket)}
                                    className={`border-2 border-dashed rounded-xl p-5 flex flex-col items-center justify-center transition-all cursor-pointer h-full ${showMarket ? "border-blue-500 bg-blue-500/10 text-blue-400" : "border-slate-700 text-slate-500 hover:border-blue-500 hover:text-blue-500"}`}
                                >
                                    <span className="text-2xl font-bold">+</span>
                                    <span className="text-xs font-bold mt-1">새로운 기능 추가하기</span>
                                </button>
                            </div>
                        </section>

                        {/* 2. Marketplace (Toggle) */}
                        {showMarket && (
                            <section className="bg-gradient-to-br from-blue-900/20 to-slate-900 border border-blue-500/30 p-6 rounded-2xl shadow-2xl">
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-lg font-bold text-blue-400 flex items-center gap-2">🛒 Extension Marketplace</h2>
                                    <span className="text-xs text-slate-500">Powered by Antigravity Cloud</span>
                                </div>
                                <div className="grid grid-cols-1 gap-4">
                                    {services.available && services.available.map((item, idx) => (
                                        <div key={idx} className="bg-slate-900/80 p-4 rounded-xl flex justify-between items-center border border-slate-700 hover:border-blue-500 transition-all">
                                            <div>
                                                <h3 className="font-bold text-white flex items-center gap-2">
                                                    {item.name}
                                                    {item.price > 0 && <span className="text-[9px] bg-yellow-600 text-white px-1.5 py-0.5 rounded">PREMIUM</span>}
                                                </h3>
                                                <p className="text-xs text-slate-400 mt-1">{item.desc}</p>
                                            </div>
                                            <div className="flex items-center gap-4">
                                                <span className="text-sm font-bold text-white">
                                                    {item.price === 0 ? "FREE" : `₩${item.price.toLocaleString()}`}
                                                </span>
                                                <button className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${item.price === 0 ? "bg-slate-700 text-white hover:bg-slate-600" : "bg-blue-600 text-white hover:bg-blue-500 shadow-lg shadow-blue-900/50"}`}>
                                                    {item.price === 0 ? "설치" : "구매하기"}
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* 3. API Key Management */}
                        <section className="border-t border-slate-800 pt-8">
                            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">🔑 API Key Vault</h2>
                            <div className="bg-black p-6 rounded-xl border border-slate-800 shadow-lg">
                                <div className="max-w-2xl">
                                    <label className="block text-xs font-bold text-slate-500 mb-2 uppercase tracking-wider">Gemini API Key (Google AI)</label>
                                    <div className="flex gap-2">
                                        <input
                                            type="password"
                                            value={apiKey}
                                            onChange={(e) => setApiKey(e.target.value)}
                                            placeholder="AIzaSy..."
                                            className="bg-slate-900 border border-slate-700 text-white px-4 py-3 rounded-lg flex-1 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all font-mono"
                                        />
                                        <button
                                            onClick={handleKeyUpdate}
                                            className="bg-slate-800 hover:bg-blue-600 text-white px-6 py-3 rounded-lg text-xs font-bold transition-all border border-slate-700 hover:border-blue-500"
                                        >
                                            SECURE SAVE
                                        </button>
                                    </div>
                                    <p className="text-[10px] text-slate-600 mt-3 flex items-center gap-1">
                                        <span className="text-green-500">🔒 Encrypted:</span> 키는 서버 환경 변수(.env)에 암호화되어 저장됩니다.
                                    </p>
                                </div>
                            </div>
                        </section>
                    </div>
                )}

                {/* [TAB 2] 팀원 관리 (신규 기능) */}
                {activeTab === "team" && (
                    <div className="space-y-8 animate-fade-in">
                        {/* 초대 섹션 */}
                        <section className="bg-slate-900 p-6 rounded-xl border border-slate-800">
                            <h2 className="text-lg font-bold text-white mb-4">Invite New Member</h2>
                            <div className="flex gap-4">
                                <input
                                    type="email" placeholder="이메일 (가입된 사용자만 가능)"
                                    value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)}
                                    className="flex-1 bg-black border border-slate-700 rounded-lg px-4 py-3 text-white focus:border-blue-500 outline-none"
                                />
                                <button onClick={handleInvite} className="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6 rounded-lg">Invite</button>
                            </div>
                            <p className="text-[10px] text-slate-500 mt-2 ml-1">* 사용자를 초대하면 기본적으로 'Logs'와 'MCP Bot' 권한이 부여됩니다.</p>
                        </section>

                        {/* 멤버 리스트 */}
                        <section>
                            <h2 className="text-lg font-bold text-white mb-4">Team Members ({members.length})</h2>
                            <div className="grid gap-3">
                                {members.map((m, idx) => (
                                    <div key={idx} className="bg-[#1e293b] p-5 rounded-xl border border-slate-700 flex justify-between items-center group hover:border-blue-500 transition-colors">
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center font-bold text-white text-lg">
                                                {m.name[0]}
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold text-white">{m.name}</span>
                                                    {m.role === "ADMIN" && <span className="text-[10px] bg-red-900 text-red-300 px-2 py-0.5 rounded border border-red-800">ADMIN</span>}
                                                </div>
                                                <span className="text-xs text-slate-500">{m.email}</span>
                                            </div>
                                        </div>
                                        <div className="flex flex-col items-end gap-1">
                                            <div className="flex gap-2">
                                                {m.allowed_features.includes("all")
                                                    ? <span className="text-xs bg-green-900/30 text-green-400 px-3 py-1 rounded-full border border-green-800">Full Access</span>
                                                    : m.allowed_features.map((f, i) => (
                                                        <span key={i} className="text-xs bg-slate-800 text-slate-400 px-3 py-1 rounded-full border border-slate-700">{f}</span>
                                                    ))
                                                }
                                            </div>
                                            <span className="text-[10px] text-slate-600">Joined: {new Date(m.joined_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>
                    </div>
                )}

                {/* [TAB 3] 일반 설정 (기존 Env + 신규 Collector) */}
                {activeTab === "general" && (
                    <div className="grid grid-cols-1 gap-12 animate-fade-in">
                        {/* Env Editor */}
                        <section className="bg-black rounded-3xl border border-slate-800 shadow-2xl overflow-hidden">
                            <div className="bg-[#1e293b] px-6 py-3 text-xs font-bold text-yellow-500 flex items-center justify-between border-b border-slate-800">
                                <div className="flex items-center gap-2">
                                    <span className="w-3 h-3 rounded-full bg-yellow-500 animate-pulse"></span>
                                    <span className="uppercase tracking-widest">Global Configuration (.env)</span>
                                </div>
                                <button onClick={handleSaveEnv} className="text-blue-400 hover:text-white transition-colors">{isSaving ? "SAVING..." : "SAVE"}</button>
                            </div>
                            <textarea
                                value={envContent}
                                onChange={(e) => setEnvContent(e.target.value)}
                                className="w-full h-[300px] bg-black p-8 text-green-400 font-mono text-sm outline-none resize-none leading-relaxed scrollbar-thin scrollbar-thumb-slate-800"
                                spellCheck="false"
                            />
                        </section>

                        {/* [신규] Collector Visualization Area */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            {/* DB Schema Viewer */}
                            <div className="bg-[#1e293b] rounded-2xl border border-slate-700 overflow-hidden shadow-lg">
                                <div className="bg-slate-900 px-6 py-4 border-b border-slate-700 flex justify-between items-center">
                                    <h3 className="font-bold text-white flex items-center gap-2">🗄️ Database Architecture</h3>
                                    <span className="text-[10px] bg-blue-900 text-blue-300 px-2 py-1 rounded">LIVE SYNC</span>
                                </div>
                                <div className="p-6 max-h-[500px] overflow-y-auto space-y-6 scrollbar-thin scrollbar-thumb-slate-700">
                                    {schemaData.length > 0 ? schemaData.map((table, idx) => (
                                        <div key={idx}>
                                            <h4 className="text-blue-400 font-mono font-bold mb-2 text-sm flex items-center gap-2">
                                                <span className="text-slate-500">Table:</span> {table.table_name}
                                            </h4>
                                            <div className="space-y-1">
                                                {table.columns.map((col, cIdx) => (
                                                    <div key={cIdx} className="flex justify-between text-xs border-b border-slate-800/50 py-1 hover:bg-slate-800/30 px-1 rounded">
                                                        <span className="text-slate-300 font-mono flex items-center gap-1">
                                                            {col.primary_key && "🔑"} {col.name}
                                                        </span>
                                                        <div className="flex gap-2">
                                                            <span className="text-yellow-600 font-mono">{col.type}</span>
                                                            <span className={`font-mono ${col.nullable ? 'text-slate-600' : 'text-red-400'}`}>
                                                                {col.nullable ? 'NULL' : 'NN'}
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )) : (
                                        <div className="text-center py-10 text-slate-500 italic">Initializing Collector...</div>
                                    )}
                                </div>
                            </div>

                            {/* API Endpoints Viewer */}
                            <div className="bg-[#1e293b] rounded-2xl border border-slate-700 overflow-hidden shadow-lg">
                                <div className="bg-slate-900 px-6 py-4 border-b border-slate-700 flex justify-between items-center">
                                    <h3 className="font-bold text-white flex items-center gap-2">🔌 Active API Routes</h3>
                                    <span className="text-[10px] bg-green-900 text-green-300 px-2 py-1 rounded">{apiEndpoints.length} ENDPOINTS</span>
                                </div>
                                <div className="p-6 max-h-[500px] overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-slate-700">
                                    {apiEndpoints.map((api, idx) => (
                                        <div key={idx} className="bg-black/30 p-3 rounded border border-slate-700/50 flex flex-col gap-1 hover:border-blue-500/50 transition-colors">
                                            <div className="flex items-center gap-2">
                                                <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded min-w-[35px] text-center ${api.methods.includes('POST') ? 'bg-green-900 text-green-300' : 'bg-blue-900 text-blue-300'}`}>
                                                    {api.methods[0]}
                                                </span>
                                                <span className="text-xs font-mono text-slate-300 break-all">{api.path}</span>
                                            </div>
                                            <p className="text-[10px] text-slate-500 pl-1">{api.description || "No description provided."}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}