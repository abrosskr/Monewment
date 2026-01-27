
import { createClient } from '@supabase/supabase-js'

// Load environment variables (Tier 3: Live)
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_LIVE_URL
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_LIVE_KEY

if (!supabaseUrl || !supabaseKey) {
    console.warn('⚠️ Supabase credentials not found in env!')
}

// Create a single supabase client for interacting with your database
export const supabase = createClient(
    supabaseUrl || '',
    supabaseKey || ''
)
