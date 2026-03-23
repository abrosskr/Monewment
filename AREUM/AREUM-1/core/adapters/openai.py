from openai import AsyncOpenAI
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ant_openai")

async def openai_mercenary_execute(
    model_name: str, 
    api_key: str, 
    prompt: str, 
    system_instruction: Optional[str] = None
) -> Dict[str, Any]:
    """
    [ANT-OPENAI] Executes a task using OpenAI's API.
    Normalizes response to Imperial Standard format.
    """
    try:
        client = AsyncOpenAI(api_key=api_key)
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        
        return {
            "status": "success",
            "model": model_name,
            "text": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "candidates_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    except Exception as e:
        logger.error(f"[ANT-OPENAI] Failure: {e}")
        return {
            "status": "error",
            "error_type": "MercenaryFailure",
            "message": str(e)
        }
