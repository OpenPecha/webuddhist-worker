import asyncio
import logging
from uuid import UUID

from firebase_admin import messaging

from worker_api.notifications.services.push.firebase_init import initialize_firebase

logger = logging.getLogger(__name__)


def build_routine_notification_data(
    *,
    session_type: str,
    source_id: UUID | None,
    title: str,
    body: str,
    image_url: str | None = None,
) -> dict[str, str]:
    """FCM data payloads require string values."""
    return {
        "session_type": session_type,
        "source_id": str(source_id) if source_id else "",
        "title": title,
        "body": body,
        "image_url": image_url or "",
    }


async def send_routine_push_notification(
    *,
    device_token: str,
    session_type: str,
    source_id: UUID | None,
    title: str,
    body: str,
    image_url: str | None = None,
) -> None:
    await send_fcm_notification(
        device_token=device_token,
        title=title,
        body=body,
        image_url=image_url,
        data=build_routine_notification_data(
            session_type=session_type,
            source_id=source_id,
            title=title,
            body=body,
            image_url=image_url,
        ),
    )


async def send_fcm_notification(
    *,
    device_token: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
    image_url: str | None = None,
) -> None:
    initialize_firebase()
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image_url,
        ),
        data=data or {},
        token=device_token,
    )
    try:
        await asyncio.to_thread(messaging.send, message)
    except Exception:
        logger.exception("FCM send failed for token %s", device_token[:8])
        raise
