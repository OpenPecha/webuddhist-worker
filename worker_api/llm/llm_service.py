import asyncio
import logging
from typing import Optional
from google import genai
from google.genai import types
from fastapi import HTTPException, status

from worker_api.config import get

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.5-flash"


def _chat_with_gemini_sync(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None
) -> dict:
    api_key = get("GEMINI_API_KEY")
    logger.info(f"GEMINI_API_KEY configured: {bool(api_key)}, key prefix: {api_key[:10] if api_key else 'N/A'}...")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY is not configured"
        )

    client = genai.Client(api_key=api_key)
    
    model_name = model or DEFAULT_MODEL
    logger.info(f"Requested model: {model}, Using model: {model_name}")
    
    config = types.GenerateContentConfig(
        temperature=1.0,
    )
    
    if system_prompt:
        config.system_instruction = system_prompt
    
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    
    try:
        logger.info(f"Calling Gemini API with prompt length: {len(prompt)}")
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )
        logger.info("Gemini API call successful")
    except Exception as e:
        logger.error(f"Gemini API error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini API error: {type(e).__name__}: {str(e)}"
        )
    
    if not response.candidates or not response.candidates[0].content.parts:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini returned no response"
        )
    
    response_text = response.candidates[0].content.parts[0].text
    
    return {
        "response": response_text,
        "model": model_name
    }


async def chat_with_gemini(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None
) -> dict:
    return await asyncio.to_thread(
        _chat_with_gemini_sync,
        prompt,
        system_prompt,
        model
    )
