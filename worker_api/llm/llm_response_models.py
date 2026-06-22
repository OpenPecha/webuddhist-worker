from typing import Optional
from pydantic import BaseModel, Field


class LLMChatRequest(BaseModel):
    prompt: str = Field(..., description="User prompt to send to Gemini")
    system_prompt: Optional[str] = Field(None, description="Optional system instruction for Gemini")
    model: Optional[str] = Field(None, description="Optional Gemini model name (defaults to gemini-2.5-flash)")


class LLMChatResponse(BaseModel):
    response: str = Field(..., description="Gemini's response text")
    model: str = Field(..., description="Model used for generation")
