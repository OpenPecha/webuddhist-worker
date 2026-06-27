"""
Tests for audio generation API endpoints.
"""
import pytest
from uuid import uuid4
from unittest.mock import patch, AsyncMock

from worker_api.audio.enums import PlanAudioType, MonlamVoiceName


class TestGeneratePlanAudio:
    """Tests for POST /audio/generate endpoint."""

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_with_day_id(self, mock_service, client):
        """Test generating audio for a plan day."""
        day_id = uuid4()
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 45000,
            "s3_key": "audio/plan_days/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "day_id": str(day_id),
                "language": "en",
                "type": "TEXT_READING"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "audio_url" in data
        assert "audio_duration_ms" in data
        assert "s3_key" in data
        assert data["audio_duration_ms"] == 45000

        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["day_id"] == day_id
        assert call_kwargs["language"] == "en"
        assert call_kwargs["audio_type"] == PlanAudioType.TEXT_READING

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_with_sub_task_id(self, mock_service, client):
        """Test generating audio for a single subtask."""
        sub_task_id = uuid4()
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 12000,
            "s3_key": "audio/plan_subtasks/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "sub_task_id": str(sub_task_id),
                "language": "bo",
                "type": "RECITATION",
                "voice_name": "dolkar_lhasa_female"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "audio_url" in data
        assert data["audio_duration_ms"] == 12000

        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["sub_task_id"] == sub_task_id
        assert call_kwargs["language"] == "bo"
        assert call_kwargs["audio_type"] == PlanAudioType.RECITATION
        assert call_kwargs["voice_name"] == MonlamVoiceName.DOLKAR_LHASA_FEMALE

    def test_generate_audio_missing_both_ids(self, client):
        """Test validation error when both day_id and sub_task_id are missing."""
        response = client.post(
            "/api/v1/audio/generate",
            json={
                "language": "en",
                "type": "TEXT_READING"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_generate_audio_with_both_ids(self, client):
        """Test validation error when both day_id and sub_task_id are provided."""
        response = client.post(
            "/api/v1/audio/generate",
            json={
                "day_id": str(uuid4()),
                "sub_task_id": str(uuid4()),
                "language": "en",
                "type": "TEXT_READING"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_generate_audio_missing_language(self, client):
        """Test validation error when language is missing."""
        response = client.post(
            "/api/v1/audio/generate",
            json={
                "day_id": str(uuid4()),
                "type": "TEXT_READING"
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_with_instruction_type(self, mock_service, client):
        """Test generating instruction audio."""
        day_id = uuid4()
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 30000,
            "s3_key": "audio/plan_days/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "day_id": str(day_id),
                "language": "en",
                "type": "INSTRUCTION"
            }
        )

        assert response.status_code == 200
        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["audio_type"] == PlanAudioType.INSTRUCTION

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_default_type(self, mock_service, client):
        """Test that TEXT_READING is the default audio type."""
        day_id = uuid4()
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 30000,
            "s3_key": "audio/plan_days/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "day_id": str(day_id),
                "language": "en"
            }
        )

        assert response.status_code == 200
        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["audio_type"] == PlanAudioType.TEXT_READING

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_tibetan_with_voice(self, mock_service, client):
        """Test generating Tibetan audio with specific voice."""
        sub_task_id = uuid4()
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 15000,
            "s3_key": "audio/plan_subtasks/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "sub_task_id": str(sub_task_id),
                "language": "bo",
                "type": "TEXT_READING",
                "voice_name": "sonamtsering_lhasa_male"
            }
        )

        assert response.status_code == 200
        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["voice_name"] == MonlamVoiceName.SONAMTSERING_LHASA_MALE

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_with_text_input(self, mock_service, client):
        """Test generating audio from direct text input."""
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 8000,
            "s3_key": "audio/generated/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "text": "This is a test text for audio generation",
                "language": "en",
                "type": "TEXT_READING"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "audio_url" in data
        assert "audio_duration_ms" in data
        assert "s3_key" in data
        assert data["audio_duration_ms"] == 8000

        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["text"] == "This is a test text for audio generation"
        assert call_kwargs["language"] == "en"
        assert call_kwargs["audio_type"] == PlanAudioType.TEXT_READING

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_with_text_and_s3_prefix(self, mock_service, client):
        """Test generating audio from text with custom S3 prefix."""
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 5000,
            "s3_key": "custom/prefix/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "text": "Custom prefix test",
                "language": "en",
                "s3_key_prefix": "custom/prefix"
            }
        )

        assert response.status_code == 200
        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["text"] == "Custom prefix test"
        assert call_kwargs["s3_key_prefix"] == "custom/prefix"

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_with_text_and_voice_name(self, mock_service, client):
        """Test generating audio from text with specific voice."""
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 6000,
            "s3_key": "audio/generated/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "text": "Tibetan text for voice test",
                "language": "bo",
                "voice_name": "yangchen_lhasa_female"
            }
        )

        assert response.status_code == 200
        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["text"] == "Tibetan text for voice test"
        assert call_kwargs["voice_name"] == MonlamVoiceName.YANGCHEN_LHASA_FEMALE

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_text_bypasses_id_requirement(self, mock_service, client):
        """Test that providing text makes day_id/sub_task_id optional."""
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 5000,
            "s3_key": "audio/generated/test.wav"
        }
        
        response = client.post(
            "/api/v1/audio/generate",
            json={
                "text": "Text input bypasses ID requirement",
                "language": "en"
            }
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_text_with_recitation_type(self, mock_service, client):
        """Test generating recitation audio from text."""
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 10000,
            "s3_key": "audio/generated/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "text": "Recitation text",
                "language": "bo",
                "type": "RECITATION",
                "voice_name": "dolkar_lhasa_female"
            }
        )

        assert response.status_code == 200
        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["audio_type"] == PlanAudioType.RECITATION

    @pytest.mark.asyncio
    @patch("worker_api.audio.audio_views.generate_plan_audio_service")
    async def test_generate_audio_text_with_instruction_type(self, mock_service, client):
        """Test generating instruction audio from text."""
        mock_service.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 7000,
            "s3_key": "audio/generated/test.wav"
        }

        response = client.post(
            "/api/v1/audio/generate",
            json={
                "text": "Instruction text",
                "language": "en",
                "type": "INSTRUCTION"
            }
        )

        assert response.status_code == 200
        mock_service.assert_called_once()
        call_kwargs = mock_service.call_args.kwargs
        assert call_kwargs["audio_type"] == PlanAudioType.INSTRUCTION
