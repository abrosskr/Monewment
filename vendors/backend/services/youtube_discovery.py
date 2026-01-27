import subprocess
import json
import random
from typing import List

class YouTubeDiscoveryService:
    """
    [Auto-Discovery]
    Finds relevant cooking videos without manual URL input.
    Uses 'yt-dlp' search functionality.
    """
    
    SEARCH_QUERIES = [
        "Korean street food recipe",
        "Michelin star chef cooking",
        "Authentic Italian pasta recipe",
        "Gordon Ramsay cooking tips",
        "Serious Eats science of cooking",
        "Maangchi best recipes",
        "Japanese izakaya food recipe"
    ]

    def discover_videos(self, count: int = 3) -> List[str]:
        """
        Searches YouTube and returns a list of unique video URLs.
        """
        query = random.choice(self.SEARCH_QUERIES)
        print(f"🕵️ [YouTube-Discovery] Searching for: '{query}'...")

        try:
            # yt-dlp search command: ytsearchN:query
            # --get-id returns only the video IDs
            cmd = [
                "yt-dlp",
                "--get-id",
                f"ytsearch{count}:{query}",
                "--no-warnings"
            ]
            
            # Execute
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                print(f"   ⚠️ Discovery Failed: {result.stderr}")
                return []

            video_ids = result.stdout.strip().split('\n')
            video_ids = [vid.strip() for vid in video_ids if vid.strip()]
            
            urls = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]
            
            print(f"   ✅ Discovered {len(urls)} videos.")
            return urls

        except FileNotFoundError:
            print("   ❌ Error: 'yt-dlp' is not installed or not in PATH.")
            return []
        except Exception as e:
            print(f"   ❌ Discovery Error: {e}")
            return []
