from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from worker_api.notifications.services.push.fcm_client import (
    build_routine_notification_data,
    send_fcm_notification,
)


class TestBuildRoutineNotificationData:
    def test_includes_session_metadata_and_content(self):
        source_id = uuid4()
        data = build_routine_notification_data(
            session_type="PLAN",
            source_id=source_id,
            title="Day 1",
            body="Begin practice.",
            image_url="https://example.com/plan.png",
        )
        assert data == {
            "session_type": "PLAN",
            "source_id": str(source_id),
            "title": "Day 1",
            "body": "Begin practice.",
            "image_url": "https://example.com/plan.png",
        }

    def test_empty_optional_fields_when_missing(self):
        data = build_routine_notification_data(
            session_type="SERIES",
            source_id=None,
            title="Series title",
            body="Default body",
        )
        assert data == {
            "session_type": "SERIES",
            "source_id": "",
            "title": "Series title",
            "body": "Default body",
            "image_url": "",
        }


class TestSendFcmNotification:
    @pytest.mark.asyncio
    @patch("worker_api.notifications.services.push.fcm_client.messaging.send")
    @patch("worker_api.notifications.services.push.fcm_client.initialize_firebase")
    async def test_passes_notification_image_and_data_payload(
        self,
        mock_initialize_firebase,
        mock_send,
    ):
        source_id = uuid4()
        mock_send.return_value = "message-id"

        await send_fcm_notification(
            device_token="device-token",
            title="Title",
            body="Body",
            image_url="https://example.com/image.png",
            data=build_routine_notification_data(
                session_type="SERIES",
                source_id=source_id,
                title="Title",
                body="Body",
                image_url="https://example.com/image.png",
            ),
        )

        mock_initialize_firebase.assert_called_once()
        mock_send.assert_called_once()
        message = mock_send.call_args.args[0]
        assert message.notification.title == "Title"
        assert message.notification.body == "Body"
        assert message.notification.image == "https://example.com/image.png"
        assert message.token == "device-token"
        assert message.data == {
            "session_type": "SERIES",
            "source_id": str(source_id),
            "title": "Title",
            "body": "Body",
            "image_url": "https://example.com/image.png",
        }
