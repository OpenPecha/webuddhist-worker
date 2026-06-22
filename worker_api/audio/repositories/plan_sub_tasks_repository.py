from uuid import UUID
from sqlalchemy.orm import Session

from worker_api.audio.models.plan_sub_tasks_models import PlanSubTask


def get_sub_task_by_subtask_id(db: Session, id: UUID) -> PlanSubTask:
    return db.query(PlanSubTask).filter(PlanSubTask.id == id).first()
