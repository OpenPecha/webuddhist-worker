"""Tests for SQS audio job consumer."""
import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from worker_api.audio.enums import AudioJobStatus
from worker_api.audio.services.audio_job_consumer import process_audio_job_message


class TestProcessAudioJobMessage:
    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_job_consumer.delete_audio_job_message")
    @patch("worker_api.audio.services.audio_job_consumer.generate_plan_audio_service", new_callable=AsyncMock)
    @patch("worker_api.audio.services.audio_job_consumer.update_audio_job_status", new_callable=AsyncMock)
    @patch("worker_api.audio.services.audio_job_consumer.get_audio_job_status", new_callable=AsyncMock)
    async def test_processes_day_job_successfully(
        self,
        mock_get_job,
        mock_update_status,
        mock_generate,
        mock_delete,
    ):
        job_id = uuid4()
        day_id = uuid4()
        mock_get_job.return_value = {"job_id": str(job_id), "status": AudioJobStatus.PENDING.value}
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

        assert mock_update_status.await_count == 2
        assert mock_update_status.await_args_list[0].kwargs["status"] == AudioJobStatus.PROCESSING
        assert mock_update_status.await_args_list[1].kwargs["status"] == AudioJobStatus.COMPLETED
        mock_generate.assert_awaited_once()
        mock_delete.assert_called_once_with("abc")

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_job_consumer.delete_audio_job_message")
    @patch("worker_api.audio.services.audio_job_consumer.generate_plan_audio_service", new_callable=AsyncMock)
    @patch("worker_api.audio.services.audio_job_consumer.update_audio_job_status", new_callable=AsyncMock)
    @patch("worker_api.audio.services.audio_job_consumer.get_audio_job_status", new_callable=AsyncMock)
    async def test_marks_failed_on_generation_error(
        self,
        mock_get_job,
        mock_update_status,
        mock_generate,
        mock_delete,
    ):
        job_id = uuid4()
        mock_get_job.return_value = {"job_id": str(job_id), "status": AudioJobStatus.PENDING.value}
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

        assert mock_update_status.await_args_list[-1].kwargs["status"] == AudioJobStatus.FAILED
        assert "Sub task not found" in mock_update_status.await_args_list[-1].kwargs["error_message"]
        mock_delete.assert_called_once_with("abc")

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_job_consumer.delete_audio_job_message")
    @patch("worker_api.audio.services.audio_job_consumer.generate_plan_audio_service", new_callable=AsyncMock)
    @patch("worker_api.audio.services.audio_job_consumer.update_audio_job_status", new_callable=AsyncMock)
    @patch("worker_api.audio.services.audio_job_consumer.get_audio_job_status", new_callable=AsyncMock)
    async def test_skips_completed_job(
        self,
        mock_get_job,
        mock_update_status,
        mock_generate,
        mock_delete,
    ):
        job_id = uuid4()
        mock_get_job.return_value = {"job_id": str(job_id), "status": AudioJobStatus.COMPLETED.value}

        message = {
            "ReceiptHandle": "abc",
            "Body": json.dumps({"job_id": str(job_id), "language": "en"}),
        }

        await process_audio_job_message(message)

        mock_generate.assert_not_called()
        mock_update_status.assert_not_awaited()
        mock_delete.assert_called_once_with("abc")
