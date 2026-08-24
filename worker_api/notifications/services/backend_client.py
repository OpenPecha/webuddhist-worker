import httpx

from uuid import UUID

from worker_api.config import get
from worker_api.notifications.schemas import (
    ChatNotificationTargetsResponse,
    DeactivatePushDeviceResponse,
    JoinRequestNotificationTargetsResponse,
    NotificationContent,
    RoutineNotificationTargetsResponse,
    VerseOfDayNotificationTargetsResponse,
)


def _backend_headers() -> dict[str, str]:
    dispatch_token = get("NOTIFICATION_DISPATCH_SECRET_TOKEN")
    if not dispatch_token:
        raise RuntimeError("NOTIFICATION_DISPATCH_SECRET_TOKEN is not configured")
    return {"X-Dispatch-Token": dispatch_token}


def _backend_url() -> str:
    backend_url = get("BACKEND_API_URL").rstrip("/")
    if not backend_url:
        raise RuntimeError("BACKEND_API_URL is not configured")
    return backend_url


async def fetch_routine_notification_targets() -> RoutineNotificationTargetsResponse:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{_backend_url()}/internal/routine-notification-targets",
            headers=_backend_headers(),
        )
        response.raise_for_status()
        return RoutineNotificationTargetsResponse.model_validate(response.json())


async def fetch_plan_notification_content(
    *,
    user_id: UUID,
    plan_id: UUID,
) -> NotificationContent:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{_backend_url()}/internal/plan-notification-content",
            params={"user_id": str(user_id), "plan_id": str(plan_id)},
            headers=_backend_headers(),
        )
        response.raise_for_status()
        return NotificationContent.model_validate(response.json())


async def fetch_chat_notification_targets(
    *,
    message_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> ChatNotificationTargetsResponse:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{_backend_url()}/internal/chat-notification-targets/{message_id}",
            params={"skip": skip, "limit": limit},
            headers=_backend_headers(),
        )
        response.raise_for_status()
        return ChatNotificationTargetsResponse.model_validate(response.json())


async def fetch_join_request_notification_targets(
    *,
    join_request_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> JoinRequestNotificationTargetsResponse:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{_backend_url()}/internal/join-request-notification-targets/{join_request_id}",
            params={"skip": skip, "limit": limit},
            headers=_backend_headers(),
        )
        response.raise_for_status()
        return JoinRequestNotificationTargetsResponse.model_validate(response.json())


async def fetch_verse_of_day_notification_targets() -> VerseOfDayNotificationTargetsResponse:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{_backend_url()}/internal/verse-of-day-notification-targets",
            headers=_backend_headers(),
        )
        response.raise_for_status()
        return VerseOfDayNotificationTargetsResponse.model_validate(response.json())


async def deactivate_push_device(*, push_device_id: UUID) -> DeactivatePushDeviceResponse:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{_backend_url()}/internal/push-devices/deactivate",
            json={"push_device_id": str(push_device_id)},
            headers=_backend_headers(),
        )
        response.raise_for_status()
        return DeactivatePushDeviceResponse.model_validate(response.json())
