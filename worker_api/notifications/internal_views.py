from fastapi import APIRouter, Depends
from starlette import status

from worker_api.notifications.dependencies import verify_dispatch_token
from worker_api.notifications.schemas import (
    DispatchDueNotificationsResponse,
    DispatchRoutineNotificationsResponse,
    RoutineNotificationTargetsResponse,
)
from worker_api.notifications.services.dispatch_service import dispatch_due_notifications_service
from worker_api.notifications.services.routine_dispatch_service import (
    dispatch_routine_notifications_service,
)
from worker_api.notifications.services.routine_notification_service import (
    get_routine_notification_targets,
)

internal_router = APIRouter(prefix="/internal", tags=["Internal"])


@internal_router.post(
    "/dispatch-due-notifications",
    status_code=status.HTTP_200_OK,
)
async def dispatch_due_notifications(
    _: None = Depends(verify_dispatch_token),
) -> DispatchDueNotificationsResponse:
    return await dispatch_due_notifications_service()


@internal_router.get(
    "/routine-notification-targets",
    status_code=status.HTTP_200_OK,
)
async def routine_notification_targets(
    _: None = Depends(verify_dispatch_token),
) -> RoutineNotificationTargetsResponse:
    return get_routine_notification_targets()


@internal_router.post(
    "/dispatch-routine-notifications",
    status_code=status.HTTP_200_OK,
)
async def dispatch_routine_notifications(
    _: None = Depends(verify_dispatch_token),
) -> DispatchRoutineNotificationsResponse:
    return await dispatch_routine_notifications_service()
