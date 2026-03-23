import google.generativeai as genai
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ant_gemini")

async def gemini_mercenary_execute(
    model_name: str, 
    api_key: str, 
    prompt: str, 
    system_instruction: Optional[str] = None
) -> Dict[str, Any]:
    """
    [ANT-GEMINI] Executes a task using Google's Generative AI.
    Normalizes response to Imperial Standard format.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )
        
        # We use a wrapper or direct call. Since this is async environment, 
        # we should use the async version if available or run in thread.
        # genai SDK supports async.
        response = await model.generate_content_async(prompt)
        
        return {
            "status": "success",
            "model": model_name,
            "text": response.text,
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            }
        }
    except Exception as e:
        logger.error(f"[ANT-GEMINI] Failure: {e}")
        return {
            "status": "error",
            "error_type": "MercenaryFailure",
            "message": str(e)
        }
