from typing import List, Dict, Any
import os
import re
from app.engines.v_academy.core import VAcademyEngine, PhysicalPrimitive
from app.core.logging import logger

class LearningService:
    """
    [The Chef's Eye]
    Service to process YouTube URLs and extract Physical Knowledge.
    """
    
    def __init__(self, academy_engine: VAcademyEngine, db_session: Any = None):
        self.engine = academy_engine
        if db_session:
            from app.services.nutrition_service import NutritionService
            self.nutrition_service = NutritionService(db_session)

    async def learn_from_youtube(self, url: str, language: str = "auto") -> Dict[str, Any]:
        """
        [The Knowledge Absorption Pipeline]
        1. Multi-Language Fetch: Ingest labels/transcripts in any language.
        2. Physics Distillation: Convert to Atomic Primitives.
        3. Global Repository: Store in V-Academy's Library.
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            logger.error("youtube_transcript_api not installed.")
            return {"error": "Missing dependency"}

        logger.info(f"📹 [V-Learning] Analyzing Global Source ({language}): {url}")
        
        # Extract Video ID
        video_id = None
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
             video_id = url.split("youtu.be/")[1].split("?")[0]
             
        if not video_id:
            return {"error": "Invalid YouTube URL"}

        full_text = ""
        
        # Try youtube-transcript-api first (Lightweight)
        try:
            # Instantiate 'transcriptor' (Seems detailed usage requires instance)
            transcriptor = YouTubeTranscriptApi()
            transcript_text_list = transcriptor.list(video_id)
            
            transcript_list = []
            if isinstance(transcript_text_list, list) and len(transcript_text_list) > 0:
                 if isinstance(transcript_text_list[0], dict) and 'text' in transcript_text_list[0]:
                     transcript_list = transcript_text_list
                 else:
                     transcript_list = transcript_text_list
            
            # Combine text (if API worked)
            full_text = " ".join([t.get('text', '') for t in transcript_list])
            
            if not full_text:
                raise Exception("API returned empty or invalid transcript structure.")
            
            logger.info(f"   ✅ Transcript extracted via API ({len(full_text)} chars)")

        except Exception as e_api:
            # Fallback: yt-dlp (Heavy but robust)
            logger.warning(f"   ⚠️ API Switch: Triggering yt-dlp fallback due to: {e_api}")
            
            # SAFETY: Aggressive Delay to prevent IP Ban (10-15 seconds)
            import time
            import random
            delay = random.uniform(10.0, 15.0)
            logger.info(f"   🛡️ Safety Guard: Pausing for {delay:.2f}s before yt-dlp fallback (Anti-429)...")
            time.sleep(delay)
            
            import yt_dlp
            
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'ko'],
                'outtmpl': f'temp_{video_id}',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'socket_timeout': 30,
                'sleep_subtitles': 5, # Delay between subtitle requests
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True) # download=True needed for subs
                    
                # Find the vtt file
                import glob
                vtt_files = glob.glob(f"temp_{video_id}*.vtt")
                
                if vtt_files:
                    target_vtt = vtt_files[0]
                    # Valid VTT parsing (simple)
                    with open(target_vtt, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Filter timestamps and headers
                        seen_lines = set()
                        for line in lines:
                            line = line.strip()
                            if '-->' in line or line == 'WEBVTT' or not line: continue
                            if line not in seen_lines:
                                full_text += line + " "
                                seen_lines.add(line)
                    
                    # Cleanup
                    for v in vtt_files:
                        os.remove(v)
                    
                    logger.info(f"   ✅ Backup Success: Extracted {len(full_text)} chars via yt-dlp")

                else:
                     logger.warning("   ⚠️ Subtitles unavailable. Falling back to Description & Metadata...")
                     
                     # Method C: Metadata Fallback
                     # If info dict is available, use description and title
                     if info:
                         title = info.get('title', '')
                         desc = info.get('description', '')
                         # Heuristic: Description often contains the recipe
                         full_text = f"{title}\n{desc}"
                         logger.info(f"   ✅ Metadata Rescue: Using Title + Description ({len(full_text)} chars)")
                     else:
                         logger.error("   ❌ Fallback Failed: No Metadata available via yt-dlp")
                         return {"error": f"All methods failed. API: {e_api} | DLP: No VTT/Metadata"}
                     
            except Exception as e_dlp:
                logger.error(f"   ❌ Fallback Failed: {e_dlp}")
                return {"error": f"All methods failed. API: {e_api} | DLP: {e_dlp}"}
        
        # Analyze
        if not full_text:
             return {"error": "No text extracted from either method."}

        primitives = self.engine.process_transcript(full_text, language=language)
        
        # Analyze Nutrition (Prototype: Simulating Ingredient Extraction from Transcript)
        # In a real scenario, we'd use an LLM or Named Entity Recognition (NER) to get ["Spaghetti 200g"]
        detected_ingredients = []
        # Simple simulation based on keywords
        if "pasta" in full_text.lower() or "spaghetti" in full_text.lower():
            detected_ingredients.append("Ottogi Spaghetti 100g")
            detected_ingredients.append("Divella Spaghetti 100g")
        
        nutrition_result = {}
        if hasattr(self, 'nutrition_service'):
            nutrition_result = self.nutrition_service.calculate_recipe_nutrition(detected_ingredients)
        
        return {
            "source": url,
            "video_id": video_id,
            "detected_primitives": [p.model_dump() for p in primitives],
            "nutrition_analysis": nutrition_result,
            "global_library_size": len(self.engine.PRIMITIVE_LIBRARY),
            "status": "Knowledge Absorbed (Physics + Nutrition)"
        }
