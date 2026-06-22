from fastapi import APIRouter
from starlette import status

from worker_api.llm.llm_response_models import LLMChatRequest, LLMChatResponse
from worker_api.llm.llm_service import chat_with_gemini

llm_router = APIRouter(prefix="/llm", tags=["LLM"])


@llm_router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(request: LLMChatRequest) -> LLMChatResponse:
    result = await chat_with_gemini(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        model=request.model
    )
    return LLMChatResponse(**result)
