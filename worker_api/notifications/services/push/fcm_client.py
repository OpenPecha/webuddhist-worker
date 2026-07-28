import asyncio
import logging
from uuid import UUID

from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError
from firebase_admin.messaging import UnregisteredError

from worker_api.notifications.services.push.firebase_init import initialize_firebase

logger = logging.getLogger(__name__)


class PermanentPushTokenError(Exception):
    """Raised when FCM reports a device token as permanently invalid."""


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


def build_chat_notification_data(
    *,
    room_id: UUID,
    message_id: UUID,
    sender_id: UUID,
    chat_kind: str,
    group_id: UUID | None,
    title: str,
    body: str,
) -> dict[str, str]:
    """FCM data payloads require string values."""
    return {
        "notification_type": "CHAT_MESSAGE",
        "session_type": "CHAT",
        "chat_kind": chat_kind,
        "room_id": str(room_id),
        "message_id": str(message_id),
        "sender_id": str(sender_id),
        "group_id": str(group_id) if group_id else "",
        "source_id": str(room_id),
        "title": title,
        "body": body,
        "image_url": "",
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


async def send_chat_push_notification(
    *,
    device_token: str,
    room_id: UUID,
    message_id: UUID,
    sender_id: UUID,
    chat_kind: str,
    group_id: UUID | None,
    title: str,
    body: str,
) -> None:
    await send_fcm_notification(
        device_token=device_token,
        title=title,
        body=body,
        data=build_chat_notification_data(
            room_id=room_id,
            message_id=message_id,
            sender_id=sender_id,
            chat_kind=chat_kind,
            group_id=group_id,
            title=title,
            body=body,
        ),
    )


def _is_permanent_token_error(exc: Exception) -> bool:
    if isinstance(exc, UnregisteredError):
        return True
    if isinstance(exc, messaging.SenderIdMismatchError):
        return True
    if isinstance(exc, FirebaseError):
        code = str(getattr(exc, "code", "") or "").lower()
        message = str(exc).lower()
        permanent_markers = (
            "registration-token-not-registered",
            "invalid-registration-token",
            "invalid-argument",
            "requested entity was not found",
            "not found",
        )
        return any(marker in code or marker in message for marker in permanent_markers)
    return False


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
    except Exception as exc:
        logger.exception("FCM send failed for token %s", device_token[:8])
        if _is_permanent_token_error(exc):
            raise PermanentPushTokenError(str(exc)) from exc
        raise
