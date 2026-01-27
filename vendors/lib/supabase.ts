import { createClient } from '@supabase/supabase-js'

// Define the two tiers
type SupabaseTier = 'brain' | 'live';

// Singleton instances to avoid recreating clients
let brainClient: any = null;
let liveClient: any = null;

export const getSupabaseClient = (tier: SupabaseTier = 'live') => {
    if (tier === 'brain') {
        if (!brainClient) {
            const url = process.env.NEXT_PUBLIC_SUPABASE_BRAIN_URL!;
            const key = process.env.NEXT_PUBLIC_SUPABASE_BRAIN_KEY!;
            if (!url || !key) console.warn("⚠️ Supabase Brain Config Missing");
            brainClient = createClient(url, key);
        }
        return brainClient;
    }

    if (tier === 'live') {
        if (!liveClient) {
            const url = process.env.NEXT_PUBLIC_SUPABASE_LIVE_URL!;
            const key = process.env.NEXT_PUBLIC_SUPABASE_LIVE_KEY!;
            if (!url || !key) console.warn("⚠️ Supabase Live Config Missing");
            liveClient = createClient(url, key);
        }
        return liveClient;
    }
}

// Default export for backward compatibility (defaults to live)
export const supabase = getSupabaseClient('live');
