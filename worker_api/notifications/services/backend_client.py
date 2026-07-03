import httpx

from uuid import UUID

from worker_api.config import get
from worker_api.notifications.schemas import NotificationContent, RoutineNotificationTargetsResponse


async def fetch_routine_notification_targets() -> RoutineNotificationTargetsResponse:
    backend_url = get("BACKEND_API_URL").rstrip("/")
    if not backend_url:
        raise RuntimeError("BACKEND_API_URL is not configured")

    dispatch_token = get("NOTIFICATION_DISPATCH_SECRET_TOKEN")
    if not dispatch_token:
        raise RuntimeError("NOTIFICATION_DISPATCH_SECRET_TOKEN is not configured")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{backend_url}/internal/routine-notification-targets",
            headers={"X-Dispatch-Token": dispatch_token},
        )
        response.raise_for_status()
        return RoutineNotificationTargetsResponse.model_validate(response.json())


async def fetch_plan_notification_content(
    *,
    user_id: UUID,
    plan_id: UUID,
) -> NotificationContent:
    backend_url = get("BACKEND_API_URL").rstrip("/")
    if not backend_url:
        raise RuntimeError("BACKEND_API_URL is not configured")

    dispatch_token = get("NOTIFICATION_DISPATCH_SECRET_TOKEN")
    if not dispatch_token:
        raise RuntimeError("NOTIFICATION_DISPATCH_SECRET_TOKEN is not configured")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{backend_url}/internal/plan-notification-content",
            params={"user_id": str(user_id), "plan_id": str(plan_id)},
            headers={"X-Dispatch-Token": dispatch_token},
        )
        response.raise_for_status()
        return NotificationContent.model_validate(response.json())
