from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from worker_api.audio.enums import AudioJobStatus
from worker_api.audio.models.audio_job_models import AudioJob


def get_audio_job_by_id(db: Session, job_id: UUID) -> Optional[AudioJob]:
    return db.query(AudioJob).filter(AudioJob.id == job_id).first()


def mark_audio_job_processing(db: Session, job_id: UUID) -> Optional[AudioJob]:
    job = get_audio_job_by_id(db=db, job_id=job_id)
    if not job:
        return None
    job.status = AudioJobStatus.PROCESSING.value
    job.started_at = datetime.now(timezone.utc)
    job.attempt_count = (job.attempt_count or 0) + 1
    job.error_message = None
    db.commit()
    db.refresh(job)
    return job


def mark_audio_job_completed(
    db: Session,
    job_id: UUID,
    result: Dict[str, Any],
) -> Optional[AudioJob]:
    job = get_audio_job_by_id(db=db, job_id=job_id)
    if not job:
        return None
    job.status = AudioJobStatus.COMPLETED.value
    job.result = result
    job.error_message = None
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job


def mark_audio_job_failed(
    db: Session,
    job_id: UUID,
    error_message: str,
) -> Optional[AudioJob]:
    job = get_audio_job_by_id(db=db, job_id=job_id)
    if not job:
        return None
    job.status = AudioJobStatus.FAILED.value
    job.error_message = error_message
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
