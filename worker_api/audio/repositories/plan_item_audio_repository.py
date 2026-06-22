from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from worker_api.audio.models.plan_item_audio_models import PlanItemAudio


def get_plan_item_audio_by_plan_item_id(db: Session, plan_item_id: UUID) -> Optional[PlanItemAudio]:
    return (
        db.query(PlanItemAudio)
        .filter(PlanItemAudio.plan_item_id == plan_item_id)
        .first()
    )


def upsert_plan_item_audio(db: Session, plan_item_audio: PlanItemAudio) -> PlanItemAudio:
    existing = get_plan_item_audio_by_plan_item_id(db=db, plan_item_id=plan_item_audio.plan_item_id)
    if existing:
        existing.audio_key = plan_item_audio.audio_key
        existing.duration_ms = plan_item_audio.duration_ms
        existing.mime_type = plan_item_audio.mime_type
        existing.file_size_bytes = plan_item_audio.file_size_bytes
        existing.updated_by = plan_item_audio.updated_by
        db.commit()
        db.refresh(existing)
        return existing
    db.add(plan_item_audio)
    db.commit()
    db.refresh(plan_item_audio)
    return plan_item_audio
