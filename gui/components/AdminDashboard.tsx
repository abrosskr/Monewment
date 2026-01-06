'use client';

import React, { useEffect, useState } from 'react';
import {
    Users,
    Layers,
    Activity,
    DollarSign,
    Terminal,
    ShieldCheck,
    Server,
    AlertTriangle,
    PlusCircle,
    FolderPlus,
    Network,
    ChevronRight,
    ChevronDown,
    Box,
    CheckCircle2,
    Clock,
    Info,
    ExternalLink,
    Cpu,
    Monitor,
    Zap,
    Globe
} from 'lucide-react';

interface Cluster {
    id: number;
    name: string;
    region: string;
    status: string;
    organizations: Organization[];
}

interface Organization {
    id: number;
    name: string;
    status: string;
    projects: Project[];
    quota: { cpu: number; ram: number; gpu: number };
}

interface Project {
    id: number;
    name: string;
    status: string;
}

const AdminDashboard: React.FC = () => {
    const [mounted, setMounted] = useState(false);
    const [hierarchy, setHierarchy] = useState<Cluster[]>([]);
    const [loading, setLoading] = useState(true);
    const [expandedOrgs, setExpandedOrgs] = useState<number[]>([]);
    const [showGuide, setShowGuide] = useState(true);
    const [statusMsg, setStatusMsg] = useState<string | null>(null);

    useEffect(() => {
        setMounted(true);
        fetchHierarchy();
        const interval = setInterval(fetchHierarchy, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchHierarchy = async () => {
        try {
            const res = await fetch('http://localhost:8001/api/admin/hierarchy');
            const data = await res.json();
            setHierarchy(data.hierarchy || []);
        } catch (e) {
            console.error("Failed to fetch hierarchy", e);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateCluster = async () => {
        const name = "Cluster-" + Math.floor(Math.random() * 1000);
        const region = "kr-seoul-1";

        setStatusMsg("⏳ Creating Cluster: " + name + "...");
        try {
            const res = await fetch('http://localhost:8001/api/admin/clusters', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    region,
                    cpu_capacity: 1000,
                    ram_capacity_gb: 4096,
                    gpu_capacity: 64
                })
            });
            if (res.ok) {
                setStatusMsg("✅ New cluster deployed: " + name);
                fetchHierarchy();
            }
        } catch (e) {
            setStatusMsg("❌ Failed to create cluster");
        }
    };

    const handleApproveOrg = async (orgId: number, clusterId: number) => {
        setStatusMsg("⏳ Approving Organization...");
        try {
            const res = await fetch('http://localhost:8001/api/admin/organizations/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    org_id: orgId,
                    cluster_id: clusterId,
                    quota_cpu: 20,
                    quota_ram_gb: 64,
                    quota_gpu: 2
                })
            });
            if (res.ok) {
                setStatusMsg("✅ Organization approved and quotas assigned!");
                fetchHierarchy();
            }
        } catch (e) {
            setStatusMsg("❌ Approval failed");
        }
    };

    useEffect(() => {
        fetchHierarchy();
        const interval = setInterval(fetchHierarchy, 30000);
        return () => clearInterval(interval);
    }, []);

    const toggleOrg = (id: number) => {
        setExpandedOrgs(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
    };

    const handleExpandProject = async (orgId: number) => {
        const projectName = "Project-" + Math.floor(Math.random() * 1000);

        setStatusMsg("⏳ Expanding Project: " + projectName + "...");
        try {
            const res = await fetch('http://localhost:8001/api/admin/projects/expand', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ org_id: orgId, project_name: projectName })
            });
            if (res.ok) {
                setStatusMsg("🚀 프로젝트가 배포되었습니다: " + projectName);
                fetchHierarchy();
            }
        } catch (e) {
            setStatusMsg("❌ 배포 중 오류 발생");
        }
    };

    if (!mounted) return null;

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-[80vh] space-y-4">
            <div className="relative w-16 h-16">
                <div className="absolute inset-0 rounded-full border-4 border-blue-500/20"></div>
                <div className="absolute inset-0 rounded-full border-4 border-t-blue-500 animate-spin"></div>
            </div>
            <p className="text-gray-500 font-mono text-xs uppercase tracking-[0.2em] animate-pulse">Initializing Overlord System...</p>
        </div>
    );

    return (
        <div className="p-10 max-w-[1600px] mx-auto space-y-12 pb-32">

            {/* 💡 Floating Status Toast */}
            {statusMsg && (
                <div className="fixed bottom-10 left-1/2 -translate-x-1/2 z-[9999] px-8 py-4 bg-blue-600 text-white rounded-2xl font-black shadow-[0_20px_50px_rgba(37,99,235,0.5)] border border-white/20 animate-in slide-in-from-bottom-10 flex items-center gap-3">
                    <Activity size={20} className="animate-pulse" />
                    {statusMsg}
                    <button onClick={() => setStatusMsg(null)} className="ml-4 opacity-50 hover:opacity-100 font-mono">X</button>
                </div>
            )}

            {/* 👑 Dynamic Header Section */}
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div>
                    <div className="flex items-center gap-2 mb-3">
                        <div className="h-[1px] w-6 bg-blue-500"></div>
                        <span className="text-[10px] font-black uppercase tracking-[0.4em] text-blue-500">Platform Command & Control</span>
                    </div>
                    <h1 className="text-5xl font-black tracking-tighter text-white leading-none">
                        Super <span className="text-blue-500">Admin</span> Engine
                    </h1>
                    <p className="text-gray-500 mt-4 text-sm font-medium max-w-xl">
                        전체 리전 클러스터 상태를 모니터링하고 가상 자원 쿼타 및 입점 업체 하위 프로젝트를 직접 제어합니다.
                    </p>
                </div>

                <div className="flex items-center gap-4">
                    <div className="px-6 py-3 bg-white/[0.03] border border-white/[0.05] rounded-3xl backdrop-blur-xl flex items-center gap-8">
                        <div className="text-center">
                            <p className="text-[9px] text-gray-600 font-black uppercase tracking-widest mb-1">Clusters</p>
                            <p className="text-xl font-bold text-white leading-none">{hierarchy.length}</p>
                        </div>
                        <div className="w-[1px] h-8 bg-white/10"></div>
                        <div className="text-center">
                            <p className="text-[9px] text-gray-600 font-black uppercase tracking-widest mb-1">Global Region</p>
                            <p className="text-xl font-bold text-white leading-none">KR-1</p>
                        </div>
                    </div>
                    <button
                        onClick={handleCreateCluster}
                        className="h-14 px-8 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl font-black uppercase tracking-tighter transition-all flex items-center gap-3 group shadow-[0_0_40px_-10px_rgba(37,99,235,0.6)]"
                    >
                        <PlusCircle size={20} className="group-hover:rotate-90 transition-transform" />
                        New Cluster Connection
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-10 items-start">

                {/* 🌳 Left: The Master Hierarchy Tree (High Readability) */}
                <div className="xl:col-span-8 space-y-8">

                    {/* Quick Filter & View Options */}
                    <div className="flex items-center justify-between px-2">
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-widest">
                                <Layers size={14} className="text-blue-500" /> System Hierarchy
                            </div>
                        </div>
                        <div className="flex gap-2 text-[10px] font-bold text-gray-500 uppercase tracking-wider">
                            <span className="text-gray-300">Expand All</span>
                            <span>/</span>
                            <span>Collapse All</span>
                        </div>
                    </div>

                    <div className="space-y-6">
                        {hierarchy.map((cluster, cIdx) => (
                            <div key={cluster.id} className="relative group">
                                {/* Cluster Card */}
                                <div className="bg-[#0f0f0f] border border-white/[0.05] rounded-[2.5rem] p-4 group-hover:border-blue-500/30 transition-all duration-500 overflow-hidden shadow-2xl relative">
                                    <div className="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none group-hover:scale-110 transition-transform duration-1000">
                                        <Globe size={160} />
                                    </div>

                                    {/* Cluster Header */}
                                    <div className="flex items-center justify-between p-4 mb-2">
                                        <div className="flex items-center gap-5">
                                            <div className="w-16 h-16 bg-blue-500/10 rounded-3xl flex items-center justify-center text-blue-500 shadow-inner">
                                                <Server size={32} strokeWidth={1.5} />
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2 mb-1">
                                                    <h3 className="text-xl font-bold text-white tracking-tight">{cluster.name}</h3>
                                                    <span className="px-2 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-500 text-[10px] font-black uppercase border border-emerald-500/20">
                                                        {cluster.status}
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-4 text-xs font-medium text-gray-500">
                                                    <span className="flex items-center gap-1.5"><Monitor size={12} /> {cluster.region}</span>
                                                    <span className="w-1 h-1 rounded-full bg-gray-800"></span>
                                                    <span className="flex items-center gap-1.5 text-blue-400/80"><Cpu size={12} /> Global Infrastructure Hub</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex gap-2">
                                            <button className="p-3 bg-white/[0.02] hover:bg-white/[0.05] rounded-2xl text-gray-500 hover:text-white transition-all">
                                                <Activity size={18} />
                                            </button>
                                        </div>
                                    </div>

                                    {/* Organizations Container with Tree Line Logic */}
                                    <div className="mt-4 px-4 pb-4 space-y-4">
                                        {cluster.organizations.length === 0 && (
                                            <div className="flex flex-col items-center justify-center py-16 border-2 border-dashed border-white/[0.03] rounded-[2rem]">
                                                <div className="p-4 bg-white/[0.02] rounded-full mb-4 text-gray-600">
                                                    <ShieldCheck size={32} />
                                                </div>
                                                <p className="text-gray-500 font-bold text-sm tracking-tight text-center">
                                                    No organizations linked to this cluster.<br />
                                                    <span className="text-gray-700 font-normal text-xs uppercase tracking-widest">Awaiting approval or connection</span>
                                                </p>
                                            </div>
                                        )}

                                        {cluster.organizations.map((org, oIdx) => (
                                            <div key={org.id} className="relative pl-8">
                                                {/* Custom Tree Line */}
                                                <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-gradient-to-b from-blue-500/40 via-blue-500/10 to-transparent ml-4 -mt-4"></div>
                                                <div className="absolute left-0 top-1/2 w-4 h-[2px] bg-blue-500/40 ml-4"></div>

                                                <div className={`group/org bg-white/[0.015] border border-white/[0.03] rounded-3xl overflow-hidden transition-all hover:border-blue-500/20 ${expandedOrgs.includes(org.id) ? 'bg-white/[0.03]' : ''}`}>
                                                    <div
                                                        className="p-6 flex items-center justify-between cursor-pointer"
                                                        onClick={() => toggleOrg(org.id)}
                                                    >
                                                        <div className="flex items-center gap-4">
                                                            <div className={`p-2 rounded-xl transition-colors ${expandedOrgs.includes(org.id) ? 'bg-blue-500 text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]' : 'bg-white/5 text-gray-400'}`}>
                                                                {expandedOrgs.includes(org.id) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                                                            </div>
                                                            <div>
                                                                <h4 className="text-base font-bold text-white group-hover/org:text-blue-400 transition-colors uppercase tracking-tight">{org.name}</h4>
                                                                <div className="flex items-center gap-2 mt-1">
                                                                    <span className="text-[9px] font-black text-gray-600 uppercase tracking-widest">Active Quota:</span>
                                                                    <div className="flex gap-3 text-[10px] font-mono text-blue-500/60 font-black">
                                                                        <span>C:{org.quota.cpu}</span>
                                                                        <span>R:{org.quota.ram}G</span>
                                                                        <span>G:{org.quota.gpu}</span>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <button
                                                            onClick={(e) => { e.stopPropagation(); handleExpandProject(org.id); }}
                                                            className="px-4 py-2 bg-blue-600 text-white border border-blue-400/50 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-500 transition-all shadow-[0_0_20px_-5px_rgba(37,99,235,0.4)] flex items-center gap-2"
                                                        >
                                                            <FolderPlus size={14} />
                                                            Deploy Project
                                                        </button>
                                                    </div>

                                                    {/* Nested Projects */}
                                                    {expandedOrgs.includes(org.id) && (
                                                        <div className="px-6 pb-6 pt-0 animate-in slide-in-from-top-2 duration-300">
                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                                                {org.projects.map(project => (
                                                                    <div key={project.id} className="p-4 bg-white/[0.02] border border-white/[0.03] rounded-2xl flex items-center justify-between group/proj hover:bg-white/[0.05] transition-colors border-l-2 border-l-blue-500/40">
                                                                        <div className="flex items-center gap-3">
                                                                            <Box size={14} className="text-blue-500/70" />
                                                                            <span className="text-sm font-bold text-gray-300 group-hover/proj:text-white transition-colors uppercase tracking-tight">{project.name}</span>
                                                                        </div>
                                                                        <div className="flex items-center gap-3">
                                                                            <span className="text-[9px] font-mono text-gray-700">NODE-{project.id}</span>
                                                                            <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                                                                        </div>
                                                                    </div>
                                                                ))}
                                                                {org.projects.length === 0 && (
                                                                    <div className="col-span-2 py-8 text-center bg-black/20 rounded-2xl border border-dashed border-white/5">
                                                                        <p className="text-[10px] text-gray-600 font-bold uppercase tracking-[0.2em]">Zero service nodes initialized</p>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* 📊 Right Space: Unified Intelligence & Guide */}
                <div className="xl:col-span-4 space-y-10 sticky top-10">

                    {/* Quick Guide Panel (How to use) */}
                    {showGuide && (
                        <div className="bg-blue-600 rounded-[2.5rem] p-8 shadow-[0_30px_60px_-15px_rgba(37,99,235,0.4)] relative overflow-hidden text-white group animate-in zoom-in-95 duration-500">
                            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-125 transition-transform duration-700">
                                <ShieldCheck size={120} />
                            </div>
                            <h3 className="text-2xl font-black tracking-tighter mb-4 flex items-center gap-2">
                                <Info size={24} /> Admin Guide
                            </h3>
                            <ul className="space-y-5 text-sm font-medium text-blue-50 relative z-10">
                                <li className="flex gap-4">
                                    <div className="w-6 h-6 rounded-lg bg-white/20 flex-shrink-0 flex items-center justify-center font-black text-xs">1</div>
                                    <p><span className="font-black underline decoration-2 decoration-blue-300">New Cluster</span> 로 인프라를 연결하세요.</p>
                                </li>
                                <li className="flex gap-4">
                                    <div className="w-6 h-6 rounded-lg bg-white/20 flex-shrink-0 flex items-center justify-center font-black text-xs">2</div>
                                    <p><span className="font-black underline decoration-2 decoration-blue-300">Approvals</span> 큐에서 기업 입점을 승인하고 vCPU/RAM 자원을 할당하세요.</p>
                                </li>
                                <li className="flex gap-4">
                                    <div className="w-6 h-6 rounded-lg bg-white/20 flex-shrink-0 flex items-center justify-center font-black text-xs">3</div>
                                    <p><span className="font-black underline decoration-2 decoration-blue-300">Direct Expand</span> 로 각 기업 하위에 프로젝트 공간을 즉시 생성할 수 있습니다.</p>
                                </li>
                            </ul>
                            <button
                                onClick={() => setShowGuide(false)}
                                className="mt-8 w-full py-4 bg-white text-blue-600 rounded-2xl font-black uppercase text-[10px] tracking-widest hover:bg-blue-50 transition-colors shadow-xl"
                            >
                                GOT IT, LET'S COMMAND
                            </button>
                        </div>
                    )}

                    {/* Bottom-Up Approvals Intelligence */}
                    <div className="bg-[#0c0c0c] border border-white/[0.05] rounded-[2.5rem] p-8 shadow-2xl space-y-8">
                        <div className="flex items-center justify-between">
                            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-gray-500 flex items-center gap-2">
                                <Clock size={16} className="text-amber-500" /> Pending Approval
                            </h3>
                            <span className="w-6 h-6 bg-amber-500/10 rounded-full flex items-center justify-center text-amber-500 text-[10px] font-black">1</span>
                        </div>

                        <div className="space-y-4">
                            <div className="p-6 rounded-3xl bg-white/[0.02] border border-white/[0.05] relative overflow-hidden group hover:border-amber-500/30 transition-all">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex flex-col">
                                        <span className="text-[10px] font-black uppercase text-amber-500 mb-1">Join Request</span>
                                        <p className="text-lg font-bold text-white tracking-tight leading-tight">DeepAILab Inc.</p>
                                    </div>
                                    <span className="text-[9px] text-gray-600 font-mono">3m ago</span>
                                </div>

                                <div className="space-y-3 mb-6">
                                    <div className="flex justify-between text-[10px] text-gray-500 font-bold uppercase tracking-widest">
                                        <span>Tier</span>
                                        <span className="text-white">Enterprise</span>
                                    </div>
                                    <div className="flex justify-between text-[10px] text-gray-500 font-bold uppercase tracking-widest">
                                        <span>Region</span>
                                        <span className="text-white">Seoul-1</span>
                                    </div>
                                </div>

                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleApproveOrg(1, hierarchy[0]?.id || 1)}
                                        className="flex-1 py-3 bg-amber-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-amber-500 transition-colors shadow-[0_0_20px_-5px_rgba(245,158,11,0.4)] flex items-center justify-center gap-2"
                                    >
                                        <ShieldCheck size={14} />
                                        PROCEED APPROVAL
                                    </button>
                                    <button className="px-4 py-3 bg-white/5 text-gray-500 rounded-xl text-[10px] font-black hover:bg-white/10 transition-colors">
                                        Details
                                    </button>
                                </div>
                            </div>

                            {!showGuide && (
                                <button
                                    onClick={() => setShowGuide(true)}
                                    className="w-full py-4 border border-dashed border-white/5 rounded-2xl text-[10px] font-black uppercase tracking-widest text-gray-700 hover:text-blue-500 hover:border-blue-500/20 transition-all"
                                >
                                    Open Onboarding Guide
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Vitals & Intelligence */}
                    <div className="bg-[#0c0c0c] border border-white/[0.05] rounded-[2.5rem] p-8 shadow-2xl">
                        <h3 className="text-xs font-black uppercase tracking-[0.2em] text-gray-500 mb-10 flex items-center gap-2">
                            <Zap size={16} className="text-blue-500 fill-blue-500" /> Platform Vitals
                        </h3>

                        <div className="space-y-10">
                            <div className="space-y-4">
                                <div className="flex justify-between items-end">
                                    <div className="space-y-1">
                                        <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Active Utilization</p>
                                        <p className="text-2xl font-black text-white leading-none">42.8<span className="text-blue-500 text-sm ml-1">%</span></p>
                                    </div>
                                    <Activity size={24} className="text-blue-500/50" />
                                </div>
                                <div className="h-1.5 w-full bg-white/[0.05] rounded-full overflow-hidden">
                                    <div className="h-full bg-blue-500 w-[42%] shadow-[0_0_20px_rgba(59,130,246,0.6)] animate-pulse"></div>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-white/[0.02] border border-white/[0.03] rounded-2xl">
                                    <p className="text-[8px] font-black text-gray-600 uppercase tracking-widest mb-1 text-center">Revenue Today</p>
                                    <p className="text-center text-sm font-bold text-emerald-500">$2,410.5</p>
                                </div>
                                <div className="p-4 bg-white/[0.02] border border-white/[0.03] rounded-2xl">
                                    <p className="text-[8px] font-black text-gray-600 uppercase tracking-widest mb-1 text-center">VM Nodes</p>
                                    <p className="text-center text-sm font-bold text-white">128</p>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
