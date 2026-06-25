import struct
from io import BytesIO
from typing import Optional, List
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from worker_api.audio.enums import ContentType, PlanAudioType, MonlamVoiceName
from worker_api.audio.models.plan_item_audio_models import PlanItemAudio
from worker_api.audio.models.plan_items_models import PlanItem
from worker_api.audio.models.plan_sub_tasks_models import PlanSubTask
from worker_api.audio.repositories.plan_items_repository import get_plan_day_by_id_any_plan
from worker_api.audio.repositories.plan_sub_tasks_repository import get_sub_task_by_subtask_id
from worker_api.audio.repositories.plan_item_audio_repository import upsert_plan_item_audio
from worker_api.audio.repositories.sub_task_timestamps_repository import upsert_sub_task_timestamp
from worker_api.audio.services.tts_service import generate_tts_audio
from worker_api.config import get
from worker_api.db.database import SessionLocal
from worker_api.uploads.S3_utils import upload_bytes, download_bytes, generate_presigned_access_url

WAV_CONTENT_TYPE = "audio/wav"


def _generate_audio_segments(
    tasks,
    audio_type: PlanAudioType,
    language: str,
    voice_name: Optional[str] = None,
) -> tuple[List[bytes], list]:
    wav_header_size = 44
    audio_segments: List[bytes] = []
    subtask_refs = []
    allowed_types = {ContentType.TEXT, ContentType.SOURCE_REFERENCE}

    for task in tasks:
        for subtask in task.sub_tasks:
            if subtask.content_type not in allowed_types:
                continue

            if subtask.audio_url:
                existing_wav = download_bytes(
                    key=subtask.audio_url,
                )
                raw_pcm = existing_wav[wav_header_size:]
            else:
                wav_bytes = generate_tts_audio(
                    subtask.content, audio_type, language, voice_name=voice_name
                )
                raw_pcm = wav_bytes[wav_header_size:]

            audio_segments.append(raw_pcm)
            subtask_refs.append(subtask)

    return audio_segments, subtask_refs


def _update_subtask_timestamps(
    db: Session,
    audio_segments: List[bytes],
    subtask_refs: list,
    sample_rate: int,
    bytes_per_sample: int,
) -> int:
    current_offset_ms = 0
    for i, raw_pcm in enumerate(audio_segments):
        segment_samples = len(raw_pcm) // bytes_per_sample
        segment_duration_ms = int((segment_samples / sample_rate) * 1000)
        upsert_sub_task_timestamp(
            db=db,
            sub_task_id=subtask_refs[i].id,
            start_ms=current_offset_ms,
            end_ms=current_offset_ms + segment_duration_ms,
            created_by="system",
        )
        current_offset_ms += segment_duration_ms
    return current_offset_ms


def _build_combined_wav(audio_segments: List[bytes]) -> tuple[bytes, int]:
    sample_rate = 24000
    bits_per_sample = 16
    num_channels = 1
    bytes_per_sample = bits_per_sample // 8

    combined_pcm = b"".join(audio_segments)
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    data_size = len(combined_pcm)
    chunk_size = 36 + data_size

    wav_header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", chunk_size, b"WAVE",
        b"fmt ", 16, 1, num_channels,
        sample_rate, byte_rate, block_align, bits_per_sample,
        b"data", data_size,
    )
    return wav_header + combined_pcm, data_size


def _upload_and_persist_audio(
    db: Session,
    combined_wav: bytes,
    duration_ms: int,
    plan_id: UUID,
    plan_item_id: UUID,
) -> PlanItemAudio:
    s3_key = f"audio/plan_days/{plan_id}/{plan_item_id}/{uuid4()}.wav"
    upload_bytes(
        file_bytes=BytesIO(combined_wav),
        key=s3_key,
        content_type=WAV_CONTENT_TYPE,
    )
    return upsert_plan_item_audio(
        db=db,
        plan_item_audio=PlanItemAudio(
            plan_item_id=plan_item_id,
            audio_key=s3_key,
            duration_ms=duration_ms,
            mime_type=WAV_CONTENT_TYPE,
            file_size_bytes=len(combined_wav),
            created_by="system",
        ),
    )


async def _generate_audio_from_text(
    text: str,
    language: str,
    audio_type: PlanAudioType = PlanAudioType.TEXT_READING,
    voice_name: MonlamVoiceName = MonlamVoiceName.DOLKAR_LHASA_FEMALE,
    s3_key_prefix: Optional[str] = None,
):
    SAMPLE_RATE = 24000
    BYTES_PER_SAMPLE = 2
    WAV_HEADER_SIZE = 44

    wav_bytes = generate_tts_audio(
        text, audio_type, language, voice_name=voice_name
    )
    raw_pcm = wav_bytes[WAV_HEADER_SIZE:]

    segment_samples = len(raw_pcm) // BYTES_PER_SAMPLE
    duration_ms = int((segment_samples / SAMPLE_RATE) * 1000)

    combined_wav, _ = _build_combined_wav([raw_pcm])

    if s3_key_prefix:
        s3_key = f"{s3_key_prefix}/{uuid4()}.wav"
    else:
        s3_key = f"audio/generated/{uuid4()}.wav"
    
    upload_bytes(
        file_bytes=BytesIO(combined_wav),
        key=s3_key,
        content_type=WAV_CONTENT_TYPE,
    )

    audio_url = generate_presigned_access_url(
        key=s3_key,
    )

    return {
        "audio_url": audio_url,
        "audio_duration_ms": duration_ms,
        "s3_key": s3_key,
    }


async def generate_plan_audio_service(
    language: str,
    text: Optional[str] = None,
    day_id: Optional[UUID] = None,
    sub_task_id: Optional[UUID] = None,
    audio_type: PlanAudioType = PlanAudioType.TEXT_READING,
    voice_name: MonlamVoiceName = MonlamVoiceName.DOLKAR_LHASA_FEMALE,
    s3_key_prefix: Optional[str] = None,
):
    if text:
        return await _generate_audio_from_text(
            text=text,
            language=language,
            audio_type=audio_type,
            voice_name=voice_name,
            s3_key_prefix=s3_key_prefix,
        )

    if sub_task_id:
        return await _generate_subtask_audio(
            sub_task_id=sub_task_id,
            audio_type=audio_type,
            language=language,
            voice_name=voice_name,
        )

    SAMPLE_RATE = 24000
    BYTES_PER_SAMPLE = 2

    with SessionLocal() as db:
        plan_item: PlanItem = get_plan_day_by_id_any_plan(db=db, day_id=day_id)

        audio_segments, subtask_refs = _generate_audio_segments(
            plan_item.tasks, audio_type, language, voice_name
        )
        if not audio_segments:
            return []

        duration_ms = _update_subtask_timestamps(
            db=db,
            audio_segments=audio_segments,
            subtask_refs=subtask_refs,
            sample_rate=SAMPLE_RATE,
            bytes_per_sample=BYTES_PER_SAMPLE,
        )

        combined_wav, _ = _build_combined_wav(audio_segments)

        audio_row = _upload_and_persist_audio(
            db=db,
            combined_wav=combined_wav,
            duration_ms=duration_ms,
            plan_id=plan_item.plan_id,
            plan_item_id=plan_item.id,
        )

    audio_url = generate_presigned_access_url(
        key=audio_row.audio_key,
    )

    return {
        "audio_url": audio_url,
        "audio_duration_ms": audio_row.duration_ms,
        "s3_key": audio_row.audio_key,
    }


async def _generate_subtask_audio(
    sub_task_id: UUID,
    audio_type: PlanAudioType,
    language: str,
    voice_name: Optional[str] = None,
):
    SAMPLE_RATE = 24000
    BYTES_PER_SAMPLE = 2
    WAV_HEADER_SIZE = 44

    with SessionLocal() as db:
        subtask: PlanSubTask = get_sub_task_by_subtask_id(db=db, id=sub_task_id)
        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "BAD_REQUEST", "message": "Sub task not found"},
            )

        allowed_types = {ContentType.TEXT, ContentType.SOURCE_REFERENCE}
        if subtask.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "BAD_REQUEST",
                    "message": "Sub task content type must be TEXT or SOURCE_REFERENCE for audio generation",
                },
            )

        wav_bytes = generate_tts_audio(
            subtask.content, audio_type, language, voice_name=voice_name
        )
        raw_pcm = wav_bytes[WAV_HEADER_SIZE:]

        segment_samples = len(raw_pcm) // BYTES_PER_SAMPLE
        duration_ms = int((segment_samples / SAMPLE_RATE) * 1000)

        combined_wav, _ = _build_combined_wav([raw_pcm])

        s3_key = f"audio/plan_subtasks/{subtask.task_id}/{sub_task_id}/{uuid4()}.wav"
        upload_bytes(
            file_bytes=BytesIO(combined_wav),
            key=s3_key,
            content_type=WAV_CONTENT_TYPE,
        )

        subtask.audio_url = s3_key
        subtask.duration = str(duration_ms)
        db.commit()

        upsert_sub_task_timestamp(
            db=db,
            sub_task_id=sub_task_id,
            start_ms=0,
            end_ms=duration_ms,
            created_by="system",
        )

    audio_url = generate_presigned_access_url(
        key=s3_key,
    )

    return {
        "audio_url": audio_url,
        "audio_duration_ms": duration_ms,
        "s3_key": s3_key,
    }
