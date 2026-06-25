"""
Tests for audio generation service.
"""
import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO

from worker_api.audio.enums import ContentType, PlanAudioType, MonlamVoiceName
from worker_api.audio.services.audio_generate_service import (
    generate_plan_audio_service,
    _generate_audio_segments,
    _update_subtask_timestamps,
    _build_combined_wav,
    _upload_and_persist_audio,
)


class TestGeneratePlanAudioService:
    """Tests for generate_plan_audio_service function."""

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.SessionLocal")
    @patch("worker_api.audio.services.audio_generate_service.get_plan_day_by_id_any_plan")
    @patch("worker_api.audio.services.audio_generate_service._generate_audio_segments")
    @patch("worker_api.audio.services.audio_generate_service._update_subtask_timestamps")
    @patch("worker_api.audio.services.audio_generate_service._build_combined_wav")
    @patch("worker_api.audio.services.audio_generate_service._upload_and_persist_audio")
    @patch("worker_api.audio.services.audio_generate_service.generate_presigned_access_url")
    async def test_generate_day_audio_success(
        self,
        mock_presigned_url,
        mock_upload,
        mock_build_wav,
        mock_update_timestamps,
        mock_generate_segments,
        mock_get_day,
        mock_session_local,
    ):
        """Test successful audio generation for a plan day."""
        day_id = uuid4()
        plan_id = uuid4()
        
        # Mock database session
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        # Mock plan item
        mock_plan_item = MagicMock()
        mock_plan_item.id = day_id
        mock_plan_item.plan_id = plan_id
        mock_plan_item.tasks = []
        mock_get_day.return_value = mock_plan_item
        
        # Mock audio segments
        mock_generate_segments.return_value = ([b"audio_data"], [MagicMock()])
        mock_update_timestamps.return_value = 45000
        mock_build_wav.return_value = (b"wav_data", 1000)
        
        # Mock audio row
        mock_audio_row = MagicMock()
        mock_audio_row.audio_key = "audio/test.wav"
        mock_audio_row.duration_ms = 45000
        mock_upload.return_value = mock_audio_row
        
        mock_presigned_url.return_value = "https://s3.example.com/audio.wav"
        
        # Execute
        result = await generate_plan_audio_service(
            language="en",
            day_id=day_id,
            audio_type=PlanAudioType.TEXT_READING,
        )
        
        # Assert
        assert result["audio_url"] == "https://s3.example.com/audio.wav"
        assert result["audio_duration_ms"] == 45000
        assert result["s3_key"] == "audio/test.wav"
        
        mock_get_day.assert_called_once_with(db=mock_db, day_id=day_id)
        mock_generate_segments.assert_called_once()
        mock_upload.assert_called_once()

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.SessionLocal")
    @patch("worker_api.audio.services.audio_generate_service.get_plan_day_by_id_any_plan")
    @patch("worker_api.audio.services.audio_generate_service._generate_audio_segments")
    async def test_generate_day_audio_no_segments(
        self,
        mock_generate_segments,
        mock_get_day,
        mock_session_local,
    ):
        """Test audio generation returns empty when no segments are generated."""
        day_id = uuid4()
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        mock_plan_item = MagicMock()
        mock_plan_item.tasks = []
        mock_get_day.return_value = mock_plan_item
        
        # No audio segments
        mock_generate_segments.return_value = ([], [])
        
        result = await generate_plan_audio_service(
            language="en",
            day_id=day_id,
        )
        
        assert result == []

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.SessionLocal")
    @patch("worker_api.audio.services.audio_generate_service.get_sub_task_by_subtask_id")
    @patch("worker_api.audio.services.audio_generate_service.generate_tts_audio")
    @patch("worker_api.audio.services.audio_generate_service.upload_bytes")
    @patch("worker_api.audio.services.audio_generate_service.upsert_sub_task_timestamp")
    @patch("worker_api.audio.services.audio_generate_service.generate_presigned_access_url")
    async def test_generate_subtask_audio_success(
        self,
        mock_presigned_url,
        mock_upsert_timestamp,
        mock_upload,
        mock_tts,
        mock_get_subtask,
        mock_session_local,
    ):
        """Test successful audio generation for a single subtask."""
        sub_task_id = uuid4()
        task_id = uuid4()
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        # Mock subtask
        mock_subtask = MagicMock()
        mock_subtask.id = sub_task_id
        mock_subtask.task_id = task_id
        mock_subtask.content = "Test content"
        mock_subtask.content_type = ContentType.TEXT
        mock_get_subtask.return_value = mock_subtask
        
        # Mock TTS audio (44 byte header + audio data)
        wav_header = b"RIFF" + b"\x00" * 40
        audio_data = b"\x00" * 1000
        mock_tts.return_value = wav_header + audio_data
        
        mock_presigned_url.return_value = "https://s3.example.com/audio.wav"
        
        # Execute
        result = await generate_plan_audio_service(
            language="en",
            sub_task_id=sub_task_id,
            audio_type=PlanAudioType.TEXT_READING,
        )
        
        # Assert
        assert "audio_url" in result
        assert "audio_duration_ms" in result
        assert "s3_key" in result
        
        mock_get_subtask.assert_called_once_with(db=mock_db, id=sub_task_id)
        mock_tts.assert_called_once()
        mock_upload.assert_called_once()
        mock_upsert_timestamp.assert_called_once()

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.SessionLocal")
    @patch("worker_api.audio.services.audio_generate_service.get_sub_task_by_subtask_id")
    async def test_generate_subtask_audio_not_found(
        self,
        mock_get_subtask,
        mock_session_local,
    ):
        """Test error when subtask is not found."""
        sub_task_id = uuid4()
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        mock_get_subtask.return_value = None
        
        with pytest.raises(Exception) as exc_info:
            await generate_plan_audio_service(
                language="en",
                sub_task_id=sub_task_id,
            )
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.SessionLocal")
    @patch("worker_api.audio.services.audio_generate_service.get_sub_task_by_subtask_id")
    async def test_generate_subtask_audio_invalid_content_type(
        self,
        mock_get_subtask,
        mock_session_local,
    ):
        """Test error when subtask has invalid content type."""
        sub_task_id = uuid4()
        
        mock_db = MagicMock()
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        mock_subtask = MagicMock()
        mock_subtask.content_type = ContentType.VIDEO  # Invalid for audio
        mock_get_subtask.return_value = mock_subtask
        
        with pytest.raises(Exception) as exc_info:
            await generate_plan_audio_service(
                language="en",
                sub_task_id=sub_task_id,
            )
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service._generate_audio_from_text")
    async def test_generate_audio_with_text_routes_correctly(
        self,
        mock_generate_from_text,
    ):
        """Test that text input routes to _generate_audio_from_text."""
        mock_generate_from_text.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 5000,
            "s3_key": "audio/generated/test.wav"
        }
        
        result = await generate_plan_audio_service(
            text="Test text input",
            language="en",
            audio_type=PlanAudioType.TEXT_READING,
            voice_name=MonlamVoiceName.DOLKAR_LHASA_FEMALE,
        )
        
        assert result["audio_url"] == "https://s3.example.com/audio.wav"
        assert result["audio_duration_ms"] == 5000
        
        mock_generate_from_text.assert_called_once_with(
            text="Test text input",
            language="en",
            audio_type=PlanAudioType.TEXT_READING,
            voice_name=MonlamVoiceName.DOLKAR_LHASA_FEMALE,
            s3_key_prefix=None,
        )

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service._generate_audio_from_text")
    async def test_generate_audio_with_text_and_prefix(
        self,
        mock_generate_from_text,
    ):
        """Test text input with custom S3 prefix."""
        mock_generate_from_text.return_value = {
            "audio_url": "https://s3.example.com/custom/audio.wav",
            "audio_duration_ms": 3000,
            "s3_key": "custom/prefix/test.wav"
        }
        
        result = await generate_plan_audio_service(
            text="Custom prefix text",
            language="bo",
            s3_key_prefix="custom/prefix",
        )
        
        assert result["s3_key"] == "custom/prefix/test.wav"
        
        mock_generate_from_text.assert_called_once()
        call_kwargs = mock_generate_from_text.call_args.kwargs
        assert call_kwargs["s3_key_prefix"] == "custom/prefix"

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service._generate_audio_from_text")
    @patch("worker_api.audio.services.audio_generate_service.SessionLocal")
    async def test_generate_audio_text_bypasses_database(
        self,
        mock_session_local,
        mock_generate_from_text,
    ):
        """Test that text input bypasses database operations."""
        mock_generate_from_text.return_value = {
            "audio_url": "https://s3.example.com/audio.wav",
            "audio_duration_ms": 4000,
            "s3_key": "audio/generated/test.wav"
        }
        
        await generate_plan_audio_service(
            text="No database needed",
            language="en",
        )
        
        mock_session_local.assert_not_called()
        mock_generate_from_text.assert_called_once()


class TestGenerateAudioSegments:
    """Tests for _generate_audio_segments helper function."""

    @patch("worker_api.audio.services.audio_generate_service.generate_tts_audio")
    def test_generate_segments_with_text_content(self, mock_tts):
        """Test generating audio segments from text content."""
        wav_data = b"RIFF" + b"\x00" * 40 + b"audio_data"
        mock_tts.return_value = wav_data
        
        mock_subtask = MagicMock()
        mock_subtask.content = "Test content"
        mock_subtask.content_type = ContentType.TEXT
        mock_subtask.audio_url = None
        
        mock_task = MagicMock()
        mock_task.sub_tasks = [mock_subtask]
        
        segments, refs = _generate_audio_segments(
            [mock_task],
            PlanAudioType.TEXT_READING,
            "en",
        )
        
        assert len(segments) == 1
        assert len(refs) == 1
        assert refs[0] == mock_subtask
        mock_tts.assert_called_once()

    @patch("worker_api.audio.services.audio_generate_service.download_bytes")
    def test_generate_segments_with_existing_audio(self, mock_download):
        """Test reusing existing audio from subtask."""
        wav_data = b"RIFF" + b"\x00" * 40 + b"existing_audio"
        mock_download.return_value = wav_data
        
        mock_subtask = MagicMock()
        mock_subtask.content_type = ContentType.TEXT
        mock_subtask.audio_url = "audio/existing.wav"
        
        mock_task = MagicMock()
        mock_task.sub_tasks = [mock_subtask]
        
        segments, refs = _generate_audio_segments(
            [mock_task],
            PlanAudioType.TEXT_READING,
            "en",
        )
        
        assert len(segments) == 1
        mock_download.assert_called_once_with(key="audio/existing.wav")

    def test_generate_segments_skips_invalid_content_types(self):
        """Test that non-text/source_reference subtasks are skipped."""
        mock_subtask = MagicMock()
        mock_subtask.content_type = ContentType.VIDEO
        
        mock_task = MagicMock()
        mock_task.sub_tasks = [mock_subtask]
        
        segments, refs = _generate_audio_segments(
            [mock_task],
            PlanAudioType.TEXT_READING,
            "en",
        )
        
        assert len(segments) == 0
        assert len(refs) == 0


class TestBuildCombinedWav:
    """Tests for _build_combined_wav helper function."""

    def test_build_wav_single_segment(self):
        """Test building WAV file from single audio segment."""
        audio_data = b"\x00" * 1000
        
        wav, size = _build_combined_wav([audio_data])
        
        assert len(wav) > len(audio_data)  # Header + data
        assert wav[:4] == b"RIFF"
        assert b"WAVE" in wav
        assert size == len(audio_data)

    def test_build_wav_multiple_segments(self):
        """Test building WAV file from multiple audio segments."""
        segment1 = b"\x00" * 500
        segment2 = b"\x01" * 500
        
        wav, size = _build_combined_wav([segment1, segment2])
        
        assert wav[:4] == b"RIFF"
        assert size == len(segment1) + len(segment2)

    def test_build_wav_empty_segments(self):
        """Test building WAV file with no segments."""
        wav, size = _build_combined_wav([])
        
        assert wav[:4] == b"RIFF"
        assert size == 0


class TestUpdateSubtaskTimestamps:
    """Tests for _update_subtask_timestamps helper function."""

    @patch("worker_api.audio.services.audio_generate_service.upsert_sub_task_timestamp")
    def test_update_timestamps(self, mock_upsert):
        """Test updating subtask timestamps."""
        mock_db = MagicMock()
        
        # 1000 bytes at 2 bytes per sample = 500 samples
        # 500 samples / 24000 Hz = 0.020833 seconds = 20.833 ms
        audio_segment = b"\x00" * 1000
        
        mock_subtask = MagicMock()
        mock_subtask.id = uuid4()
        
        duration = _update_subtask_timestamps(
            mock_db,
            [audio_segment],
            [mock_subtask],
            24000,  # sample_rate
            2,      # bytes_per_sample
        )
        
        assert duration > 0
        mock_upsert.assert_called_once()
        call_kwargs = mock_upsert.call_args.kwargs
        assert call_kwargs["sub_task_id"] == mock_subtask.id
        assert call_kwargs["start_ms"] == 0
        assert call_kwargs["end_ms"] > 0


class TestGenerateAudioFromText:
    """Tests for _generate_audio_from_text helper function."""

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.generate_tts_audio")
    @patch("worker_api.audio.services.audio_generate_service.upload_bytes")
    @patch("worker_api.audio.services.audio_generate_service.generate_presigned_access_url")
    async def test_generate_audio_from_text_success(
        self,
        mock_presigned_url,
        mock_upload,
        mock_tts,
    ):
        """Test successful audio generation from text."""
        from worker_api.audio.services.audio_generate_service import _generate_audio_from_text
        
        wav_header = b"RIFF" + b"\x00" * 40
        audio_data = b"\x00" * 1000
        mock_tts.return_value = wav_header + audio_data
        mock_presigned_url.return_value = "https://s3.example.com/audio.wav"
        
        result = await _generate_audio_from_text(
            text="Test text for audio generation",
            language="en",
            audio_type=PlanAudioType.TEXT_READING,
        )
        
        assert result["audio_url"] == "https://s3.example.com/audio.wav"
        assert result["audio_duration_ms"] > 0
        assert "s3_key" in result
        assert result["s3_key"].startswith("audio/generated/")
        assert result["s3_key"].endswith(".wav")
        
        mock_tts.assert_called_once_with(
            "Test text for audio generation",
            PlanAudioType.TEXT_READING,
            "en",
            voice_name=MonlamVoiceName.DOLKAR_LHASA_FEMALE,
        )
        mock_upload.assert_called_once()

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.generate_tts_audio")
    @patch("worker_api.audio.services.audio_generate_service.upload_bytes")
    @patch("worker_api.audio.services.audio_generate_service.generate_presigned_access_url")
    async def test_generate_audio_from_text_with_custom_prefix(
        self,
        mock_presigned_url,
        mock_upload,
        mock_tts,
    ):
        """Test audio generation with custom S3 key prefix."""
        from worker_api.audio.services.audio_generate_service import _generate_audio_from_text
        
        wav_header = b"RIFF" + b"\x00" * 40
        audio_data = b"\x00" * 500
        mock_tts.return_value = wav_header + audio_data
        mock_presigned_url.return_value = "https://s3.example.com/custom/audio.wav"
        
        result = await _generate_audio_from_text(
            text="Custom prefix test",
            language="en",
            s3_key_prefix="custom/prefix",
        )
        
        assert result["s3_key"].startswith("custom/prefix/")
        assert result["s3_key"].endswith(".wav")
        
        upload_call = mock_upload.call_args
        uploaded_key = upload_call.kwargs["key"]
        assert uploaded_key.startswith("custom/prefix/")

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.generate_tts_audio")
    @patch("worker_api.audio.services.audio_generate_service.upload_bytes")
    @patch("worker_api.audio.services.audio_generate_service.generate_presigned_access_url")
    async def test_generate_audio_from_text_with_voice_name(
        self,
        mock_presigned_url,
        mock_upload,
        mock_tts,
    ):
        """Test audio generation with specific voice name."""
        from worker_api.audio.services.audio_generate_service import _generate_audio_from_text
        
        wav_header = b"RIFF" + b"\x00" * 40
        audio_data = b"\x00" * 800
        mock_tts.return_value = wav_header + audio_data
        mock_presigned_url.return_value = "https://s3.example.com/audio.wav"
        
        result = await _generate_audio_from_text(
            text="Voice test",
            language="bo",
            voice_name=MonlamVoiceName.YANGCHEN_LHASA_FEMALE,
        )
        
        assert "audio_url" in result
        mock_tts.assert_called_once_with(
            "Voice test",
            PlanAudioType.TEXT_READING,
            "bo",
            voice_name=MonlamVoiceName.YANGCHEN_LHASA_FEMALE,
        )

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.generate_tts_audio")
    @patch("worker_api.audio.services.audio_generate_service.upload_bytes")
    @patch("worker_api.audio.services.audio_generate_service.generate_presigned_access_url")
    async def test_generate_audio_from_text_recitation_type(
        self,
        mock_presigned_url,
        mock_upload,
        mock_tts,
    ):
        """Test audio generation with RECITATION type."""
        from worker_api.audio.services.audio_generate_service import _generate_audio_from_text
        
        wav_header = b"RIFF" + b"\x00" * 40
        audio_data = b"\x00" * 1200
        mock_tts.return_value = wav_header + audio_data
        mock_presigned_url.return_value = "https://s3.example.com/audio.wav"
        
        result = await _generate_audio_from_text(
            text="Recitation text",
            language="bo",
            audio_type=PlanAudioType.RECITATION,
        )
        
        assert result["audio_duration_ms"] > 0
        mock_tts.assert_called_once_with(
            "Recitation text",
            PlanAudioType.RECITATION,
            "bo",
            voice_name=MonlamVoiceName.DOLKAR_LHASA_FEMALE,
        )

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.generate_tts_audio")
    @patch("worker_api.audio.services.audio_generate_service.upload_bytes")
    @patch("worker_api.audio.services.audio_generate_service.generate_presigned_access_url")
    async def test_generate_audio_from_text_instruction_type(
        self,
        mock_presigned_url,
        mock_upload,
        mock_tts,
    ):
        """Test audio generation with INSTRUCTION type."""
        from worker_api.audio.services.audio_generate_service import _generate_audio_from_text
        
        wav_header = b"RIFF" + b"\x00" * 40
        audio_data = b"\x00" * 600
        mock_tts.return_value = wav_header + audio_data
        mock_presigned_url.return_value = "https://s3.example.com/audio.wav"
        
        result = await _generate_audio_from_text(
            text="Instruction text",
            language="en",
            audio_type=PlanAudioType.INSTRUCTION,
        )
        
        assert "s3_key" in result
        mock_tts.assert_called_once_with(
            "Instruction text",
            PlanAudioType.INSTRUCTION,
            "en",
            voice_name=MonlamVoiceName.DOLKAR_LHASA_FEMALE,
        )

    @pytest.mark.asyncio
    @patch("worker_api.audio.services.audio_generate_service.generate_tts_audio")
    @patch("worker_api.audio.services.audio_generate_service.upload_bytes")
    @patch("worker_api.audio.services.audio_generate_service.generate_presigned_access_url")
    async def test_generate_audio_from_text_duration_calculation(
        self,
        mock_presigned_url,
        mock_upload,
        mock_tts,
    ):
        """Test correct duration calculation from audio data."""
        from worker_api.audio.services.audio_generate_service import _generate_audio_from_text
        
        wav_header = b"RIFF" + b"\x00" * 40
        audio_data = b"\x00" * 48000
        mock_tts.return_value = wav_header + audio_data
        mock_presigned_url.return_value = "https://s3.example.com/audio.wav"
        
        result = await _generate_audio_from_text(
            text="Duration test",
            language="en",
        )
        
        expected_duration_ms = int((48000 / 2 / 24000) * 1000)
        assert result["audio_duration_ms"] == expected_duration_ms
