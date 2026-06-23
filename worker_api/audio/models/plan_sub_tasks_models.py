from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from uuid import uuid4
from worker_api.db.database import Base
from worker_api.audio.enums import ContentTypeEnum
from _datetime import datetime
import _datetime


class PlanSubTask(Base):
    __tablename__ = "sub_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    audio_url = Column(String(255), nullable=True)
    content_type = Column(ContentTypeEnum, nullable=False)
    content = Column(Text, nullable=True)
    duration = Column(String(255), nullable=True)
    source_text_id = Column(UUID(as_uuid=True), nullable=True)
    pecha_segment_id = Column(String(255), nullable=True)
    segment_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)

    display_order = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc), nullable=False)
    created_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(_datetime.timezone.utc))
    updated_by = Column(String(255))

    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(String(255))

    task = relationship("PlanTask", back_populates="sub_tasks")
    timestamp = relationship(
        "SubTaskTimestamp",
        back_populates="sub_task",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_sub_tasks_task_order", "task_id", "display_order"),
        Index("idx_sub_tasks_content_type", "content_type"),
    )
