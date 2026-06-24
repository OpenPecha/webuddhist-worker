from typing import Optional
from uuid import UUID
from pydantic import BaseModel, model_validator

from worker_api.audio.enums import PlanAudioType, MonlamVoiceName


class GeneratePlanAudioRequest(BaseModel):
    text: Optional[str] = None
    day_id: Optional[UUID] = None
    sub_task_id: Optional[UUID] = None
    language: str
    type: Optional[PlanAudioType] = PlanAudioType.TEXT_READING
    voice_name: MonlamVoiceName = MonlamVoiceName.DOLKAR_LHASA_FEMALE
    s3_key_prefix: Optional[str] = None

    @model_validator(mode="after")
    def validate_input(self):
        if self.text:
            return self
        if not self.day_id and not self.sub_task_id:
            raise ValueError("Either text, day_id, or sub_task_id must be provided")
        if self.day_id and self.sub_task_id:
            raise ValueError("Provide either day_id or sub_task_id, not both")
        return self
