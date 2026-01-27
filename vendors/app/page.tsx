"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

export default function Home() {
  const [dbStatus, setDbStatus] = useState<string>("Initializing...");
  const [hotData, setHotData] = useState<any[]>([]);
  const [coldData, setColdData] = useState<any>(null);
  const [mode, setMode] = useState<"Lite" | "Full">("Lite");

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      setDbStatus("Connecting to Supabase...");
      // Mock check for now as keys are placeholders
      if (process.env.NEXT_PUBLIC_SUPABASE_URL?.includes("your-project")) {
        setDbStatus("⚠️ Config Missing (Using Mock Mode)");
      } else {
        const { error } = await supabase.from("test_connection_ping").select("*").limit(1);

        // If we get an error, it means we connected!
        // Common errors that prove connection:
        // 1. "Could not find the table..." (PostgREST schema cache error)
        // 2. Code "42P01" (Postgres undefined table error)
        if (error) {
          const Msg = error.message.toLowerCase();
          if (Msg.includes("could not find the table") || Msg.includes("relation") || error.code === '42P01') {
            // SUCCESS: We reached Supabase, it just told us the table is missing.
            setDbStatus("✅ Connected to Supabase (Dual-Core Ready)");
            return;
          }
          throw error; // Throw real connection errors (network, auth)
        }

        setDbStatus("✅ Connected to Supabase (Dual-Core Ready)");
      }
    } catch (e: any) {
      setDbStatus(`❌ Connection Failed: ${e.message}`);
    }
  };

  const loadHotData = () => {
    // Simulate fetching metadata from Supabase (500MB limit safe)
    setHotData([
      { id: 1, name: "Vendor A", type: "Supplier", managedBy: "Supabase" },
      { id: 2, name: "Vendor B", type: "Logistics", managedBy: "Supabase" },
    ]);
  };

  const loadColdData = async () => {
    // Simulate fetching heavy data from Monewment API (1GB+ Storage)
    setColdData({
      source: "Monewment Core API (Simulated)",
      payloadSize: "1.2 GB",
      content: "Heavy binary/archive data loaded on-demand...",
    });
  };

  return (
    <div className="min-h-screen p-8 bg-gray-900 text-white font-mono">
      <h1 className="text-3xl font-bold mb-4 text-blue-400">
        🛡️ Monewment Vendors (Federation Node)
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Status Panel */}
        <div className="border border-gray-700 p-6 rounded-lg bg-gray-800">
          <h2 className="text-xl font-bold mb-4 border-b border-gray-600 pb-2">System Status</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Database (Supabase):</span>
              <span className="font-bold">{dbStatus}</span>
            </div>
            <div className="flex justify-between">
              <span>Storage Strategy:</span>
              <span className="text-green-400">Federated (Hybrid)</span>
            </div>
            <div className="flex justify-between">
              <span>Daily Egress Limit:</span>
              <span className="text-yellow-400">50 MB / Day</span>
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="border border-gray-700 p-6 rounded-lg bg-gray-800">
          <h2 className="text-xl font-bold mb-4 border-b border-gray-600 pb-2">Optimization Controls</h2>
          <div className="flex gap-4">
            <button
              onClick={loadHotData}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded transition"
            >
              Load Metadata (Lite)
            </button>
            <button
              onClick={loadColdData}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded transition"
            >
              Load Heavy Payload
            </button>
          </div>
        </div>
      </div>

      {/* Data View */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="border border-blue-900/50 p-4 rounded bg-blue-900/10">
          <h3 className="font-bold text-blue-300 mb-2">🔥 Hot Data (Supabase)</h3>
          <pre className="text-sm overflow-auto text-gray-300">
            {hotData.length ? JSON.stringify(hotData, null, 2) : "No data loaded."}
          </pre>
        </div>

        <div className="border border-purple-900/50 p-4 rounded bg-purple-900/10">
          <h3 className="font-bold text-purple-300 mb-2">🧊 Cold Data (Monewment Core)</h3>
          <pre className="text-sm overflow-auto text-gray-300">
            {coldData ? JSON.stringify(coldData, null, 2) : "No heavy data requested."}
          </pre>
        </div>
      </div>
    </div>
  );
}
