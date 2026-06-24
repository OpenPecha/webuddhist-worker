from fastapi import APIRouter
from starlette import status

from worker_api.audio.schemas import GeneratePlanAudioRequest
from worker_api.audio.services.audio_generate_service import generate_plan_audio_service

audio_router = APIRouter(prefix="/audio", tags=["Audio"])


@audio_router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_plan_audio(
    request: GeneratePlanAudioRequest,
):
    return await generate_plan_audio_service(
        text=request.text,
        day_id=request.day_id,
        sub_task_id=request.sub_task_id,
        language=request.language,
        audio_type=request.type,
        voice_name=request.voice_name,
        s3_key_prefix=request.s3_key_prefix,
    )
