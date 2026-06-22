from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from starlette import status

from worker_api.audio.models.plan_items_models import PlanItem
from worker_api.audio.models.plan_tasks_models import PlanTask
from worker_api.audio.models.plan_sub_tasks_models import PlanSubTask


def get_plan_day_by_id_any_plan(db: Session, day_id: UUID) -> PlanItem:
    plan_item = (
        db.query(PlanItem)
        .options(
            joinedload(PlanItem.tasks).joinedload(PlanTask.sub_tasks).joinedload(PlanSubTask.timestamp),
        )
        .filter(PlanItem.id == day_id)
        .first()
    )
    if not plan_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "BAD_REQUEST", "message": "Plan day not found"},
        )
    return plan_item
