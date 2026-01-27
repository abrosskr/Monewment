
"use client"

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Activity, Flame, Thermometer } from 'lucide-react'

// TSV Data Type
type PhysicsLog = {
  id: number
  logged_at: string
  temp: number
  velocity: number
  accel: number
  integral: number
}

export default function VendorsDashboard() {
  const [logs, setLogs] = useState<PhysicsLog[]>([])
  const [isConnected, setIsConnected] = useState(false)

  // 1. Initial Load
  useEffect(() => {
    const fetchInitialData = async () => {
      const { data, error } = await supabase
        .from('physics_logs')
        .select('*')
        .order('id', { ascending: false })
        .limit(100)

      if (data) {
        setLogs(data.reverse()) // Show oldest to newest
        setIsConnected(true)
      }
    }
    fetchInitialData()

    // 2. Real-time Subscription
    const channel = supabase
      .channel('realtime_logs')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'physics_logs' }, (payload) => {
        const newLog = payload.new as PhysicsLog
        setLogs(prev => [...prev.slice(1), newLog]) // Keep window of 100
      })
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [])

  // Latest Values
  const current = logs.length > 0 ? logs[logs.length - 1] : { temp: 0, velocity: 0, integral: 0 }

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8 font-sans">
      <header className="mb-8 flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-500 to-red-500 bg-clip-text text-transparent">
            VENDORS <span className="text-sm font-light text-slate-400">Sentient Kitchen Core</span>
          </h1>
          <p className="text-slate-500 mt-1">Live Metrology Dashboard (Mumbai Region)</p>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${isConnected ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          {isConnected ? 'System Online' : 'Connecting...'}
        </div>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <KPI title="Temperature (T)" value={`${current.temp.toFixed(1)}°C`} icon={<Thermometer className="text-orange-500" />} color="border-orange-500/30" />
        <KPI title="Velocity (V)" value={`${current.velocity.toFixed(3)}`} icon={<Activity className="text-blue-500" />} color="border-blue-500/30" />
        <KPI title="Cookedness (I)" value={`${current.integral.toFixed(0)}`} icon={<Flame className="text-red-500" />} color="border-red-500/30" />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chart 1: Temperature & Integral */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 text-slate-300">Energy Profile (T)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={logs}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="logged_at" tick={false} stroke="#64748b" />
                <YAxis stroke="#64748b" domain={['auto', 'auto']} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                <Line type="monotone" dataKey="temp" stroke="#f97316" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="integral" stroke="#ef4444" strokeWidth={1} dot={false} yAxisId={1} hide />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Velocity & Acceleration */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 text-slate-300">Reaction Velocity (V)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={logs}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="logged_at" tick={false} stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                <Line type="monotone" dataKey="velocity" stroke="#3b82f6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-8 text-center text-slate-600 text-sm">
        Powered by Monewment & Supabase (Live)
      </footer>
    </div>
  )
}

function KPI({ title, value, icon, color }: { title: string, value: string, icon: any, color: string }) {
  return (
    <div className={`bg-slate-900 border ${color} rounded-xl p-6 flex items-center justify-between`}>
      <div>
        <p className="text-slate-400 text-sm font-medium">{title}</p>
        <p className="text-3xl font-bold mt-1 tracking-tight">{value}</p>
      </div>
      <div className="p-3 bg-slate-800 rounded-lg">{icon}</div>
    </div>
  )
}
