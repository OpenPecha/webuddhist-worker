from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from worker_api.notifications.services.push.fcm_client import (
    build_routine_notification_data,
    send_fcm_notification,
)


class TestBuildRoutineNotificationData:
    def test_includes_session_type_and_source_id(self):
        source_id = uuid4()
        data = build_routine_notification_data(
            session_type="PLAN",
            source_id=source_id,
        )
        assert data == {
            "session_type": "PLAN",
            "source_id": str(source_id),
        }

    def test_empty_source_id_when_missing(self):
        data = build_routine_notification_data(
            session_type="TIMER",
            source_id=None,
        )
        assert data == {
            "session_type": "TIMER",
            "source_id": "",
        }


class TestSendFcmNotification:
    @pytest.mark.asyncio
    @patch("worker_api.notifications.services.push.fcm_client.messaging.send")
    @patch("worker_api.notifications.services.push.fcm_client.initialize_firebase")
    async def test_passes_notification_and_data_payload(
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
            data=build_routine_notification_data(
                session_type="SERIES",
                source_id=source_id,
            ),
        )

        mock_initialize_firebase.assert_called_once()
        mock_send.assert_called_once()
        message = mock_send.call_args.args[0]
        assert message.notification.title == "Title"
        assert message.notification.body == "Body"
        assert message.token == "device-token"
        assert message.data == {
            "session_type": "SERIES",
            "source_id": str(source_id),
        }
