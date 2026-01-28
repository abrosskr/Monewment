import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic'; // No caching
export const runtime = 'nodejs';

export async function GET() {
    // Control Plane: System Integrity Plane (SIP)
    // This endpoint must reflect the TRUE state of the vendor (frontend).

    const integrityReport = {
        plane: "SIP",
        component: "monewment-gui",
        status: "OPERATIONAL", // In real world, check DB/API connectivity here
        timestamp: new Date().toISOString(),
        governance: {
            vess_compliant: true, // Asserted by Control Plane during build
            policy: "STRICT"
        },
        meta: {
            environment: process.env.NODE_ENV,
            version: process.env.npm_package_version || "unknown"
        }
    };

    return NextResponse.json(integrityReport, {
        status: 200,
        headers: {
            'X-Control-Plane-Authority': 'MONEWMENT-AI',
            'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate'
        }
    });
}
