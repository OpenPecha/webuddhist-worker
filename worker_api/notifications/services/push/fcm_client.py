import asyncio
import logging

from firebase_admin import messaging

from worker_api.notifications.services.push.firebase_init import initialize_firebase

logger = logging.getLogger(__name__)


async def send_fcm_notification(
    *,
    device_token: str,
    title: str,
    body: str,
) -> None:
    initialize_firebase()
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=device_token,
    )
    try:
        await asyncio.to_thread(messaging.send, message)
    except Exception:
        logger.exception("FCM send failed for token %s", device_token[:8])
        raise
