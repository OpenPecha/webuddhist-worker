"""Tests for SQS audio job consumer."""
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from worker_api.audio.enums import AudioJobStatus
from worker_api.audio.services.audio_job_consumer import process_audio_job_message


class TestProcessAudioJobMessage:
    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_job_consumer.delete_audio_job_message")
    @patch("worker_api.audio.services.audio_job_consumer.generate_plan_audio_service", new_callable=AsyncMock)
    @patch("worker_api.audio.services.audio_job_consumer.mark_audio_job_completed")
    @patch("worker_api.audio.services.audio_job_consumer.mark_audio_job_processing")
    @patch("worker_api.audio.services.audio_job_consumer.get_audio_job_by_id")
    @patch("worker_api.audio.services.audio_job_consumer.SessionLocal")
    async def test_processes_day_job_successfully(
        self,
        mock_session_local,
        mock_get_job,
        mock_mark_processing,
        mock_mark_completed,
        mock_generate,
        mock_delete,
    ):
        job_id = uuid4()
        day_id = uuid4()
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db

        existing = MagicMock()
        existing.status = AudioJobStatus.PENDING.value
        mock_get_job.return_value = existing
        mock_generate.return_value = {
            "audio_url": "https://example.com/a.wav",
            "audio_duration_ms": 1200,
            "s3_key": "audio/plan_days/a.wav",
        }

        message = {
            "ReceiptHandle": "abc",
            "Body": json.dumps(
                {
                    "job_id": str(job_id),
                    "day_id": str(day_id),
                    "sub_task_id": None,
                    "language": "bo",
                    "type": "TEXT_READING",
                    "voice_name": "dolkar_lhasa_female",
                }
            ),
        }

        await process_audio_job_message(message)

        mock_mark_processing.assert_called_once()
        mock_generate.assert_awaited_once()
        mock_mark_completed.assert_called_once()
        mock_delete.assert_called_once_with("abc")

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_job_consumer.delete_audio_job_message")
    @patch("worker_api.audio.services.audio_job_consumer.generate_plan_audio_service", new_callable=AsyncMock)
    @patch("worker_api.audio.services.audio_job_consumer.mark_audio_job_failed")
    @patch("worker_api.audio.services.audio_job_consumer.mark_audio_job_processing")
    @patch("worker_api.audio.services.audio_job_consumer.get_audio_job_by_id")
    @patch("worker_api.audio.services.audio_job_consumer.SessionLocal")
    async def test_marks_failed_on_generation_error(
        self,
        mock_session_local,
        mock_get_job,
        mock_mark_processing,
        mock_mark_failed,
        mock_generate,
        mock_delete,
    ):
        job_id = uuid4()
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db

        existing = MagicMock()
        existing.status = AudioJobStatus.PENDING.value
        mock_get_job.return_value = existing
        mock_generate.side_effect = HTTPException(status_code=404, detail={"message": "Sub task not found"})

        message = {
            "ReceiptHandle": "abc",
            "Body": json.dumps(
                {
                    "job_id": str(job_id),
                    "day_id": None,
                    "sub_task_id": str(uuid4()),
                    "language": "en",
                    "type": "TEXT_READING",
                    "voice_name": "dolkar_lhasa_female",
                }
            ),
        }

        await process_audio_job_message(message)

        mock_mark_failed.assert_called_once()
        assert "Sub task not found" in mock_mark_failed.call_args.kwargs["error_message"]
        mock_delete.assert_called_once_with("abc")

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_job_consumer.delete_audio_job_message")
    @patch("worker_api.audio.services.audio_job_consumer.generate_plan_audio_service", new_callable=AsyncMock)
    @patch("worker_api.audio.services.audio_job_consumer.get_audio_job_by_id")
    @patch("worker_api.audio.services.audio_job_consumer.SessionLocal")
    async def test_skips_completed_job(
        self,
        mock_session_local,
        mock_get_job,
        mock_generate,
        mock_delete,
    ):
        job_id = uuid4()
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db

        existing = MagicMock()
        existing.status = AudioJobStatus.COMPLETED.value
        mock_get_job.return_value = existing

        message = {
            "ReceiptHandle": "abc",
            "Body": json.dumps({"job_id": str(job_id), "language": "en"}),
        }

        await process_audio_job_message(message)

        mock_generate.assert_not_called()
        mock_delete.assert_called_once_with("abc")
