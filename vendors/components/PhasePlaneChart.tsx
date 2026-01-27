"use client";

import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DataPoint {
    temp: number;      // X-axis: Temperature (T)
    velocity: number;  // Y-axis: Velocity (dT/dt)
}

export default function PhasePlaneChart({ data }: { data: DataPoint[] }) {
    return (
        <div className="w-full h-[400px] bg-slate-900 rounded-lg p-4">
            <h3 className="text-blue-300 font-mono mb-2 text-center">Phase Plane (T vs dT/dt)</h3>
            <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        type="number"
                        dataKey="temp"
                        name="Temp"
                        unit="°C"
                        stroke="#94a3b8"
                        domain={['auto', 'auto']}
                    />
                    <YAxis
                        type="number"
                        dataKey="velocity"
                        name="Velocity"
                        unit="°C/s"
                        stroke="#94a3b8"
                    />
                    <Tooltip
                        cursor={{ strokeDasharray: '3 3' }}
                        contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }}
                    />
                    <Scatter name="Physics Vector" data={data} fill="#8884d8" line lineType="fitting" />
                </ScatterChart>
            </ResponsiveContainer>
        </div>
    );
}
