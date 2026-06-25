import struct
import pytest
from unittest.mock import patch, MagicMock
import httpx

from worker_api.audio.services.monlam_tts_service import (
    generate_monlam_tts_audio,
    DEFAULT_MONLAM_VOICE_NAME,
    _call_monlam_api,
    _generate_silence,
    _build_wav_from_pcm,
    WAV_HEADER_SIZE,
    SAMPLE_RATE,
)
from worker_api.audio.enums import MonlamVoiceName


def _create_mock_wav(pcm_size: int = 100) -> bytes:
    """Create a valid WAV file with given PCM size for testing."""
    pcm_data = b"\x00" * pcm_size
    bits_per_sample = 16
    num_channels = 1
    sample_rate = 24000
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    data_size = len(pcm_data)
    chunk_size = 36 + data_size

    wav_header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", chunk_size, b"WAVE",
        b"fmt ", 16, 1, num_channels,
        sample_rate, byte_rate, block_align, bits_per_sample,
        b"data", data_size,
    )
    return wav_header + pcm_data


class TestGenerateMonlamTtsAudio:
    def test_empty_content_raises_error(self):
        with pytest.raises(ValueError, match="Content cannot be empty"):
            generate_monlam_tts_audio("")
    
    def test_whitespace_content_raises_error(self):
        with pytest.raises(ValueError, match="Content cannot be empty"):
            generate_monlam_tts_audio("   ")
    
    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_missing_api_key_raises_error(self, mock_get, mock_chunk):
        def get_side_effect(key):
            if key == "MONLAM_BASE_URL":
                return "https://api.monlam.ai"
            if key == "MONLAM_API_KEY":
                return None
            return "default"
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["བོད་སྐད།"]
        
        with pytest.raises(RuntimeError, match="TTS generation failed at"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_successful_generation(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["བོད་སྐད།"]
        
        mock_response = MagicMock()
        mock_response.content = _create_mock_wav(100)
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = generate_monlam_tts_audio("བོད་སྐད།")
        
        assert result[:4] == b"RIFF"
        mock_post.assert_called_once()
        
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.monlam.ai/api/v1/text-to-speech/stream"
        assert call_args[1]["headers"]["X-API-Key"] == "fake_api_key"
        assert call_args[1]["json"]["text"] == "བོད་སྐད།"
        assert call_args[1]["json"]["provider"] == "test_provider"
        assert call_args[1]["json"]["model_name"] == "test_model"
    
    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_custom_voice_name(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["བོད་སྐད།"]
        
        mock_response = MagicMock()
        mock_response.content = _create_mock_wav(100)
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = generate_monlam_tts_audio("བོད་སྐད།", voice_name="custom_voice")
        
        assert result[:4] == b"RIFF"
        
        call_args = mock_post.call_args
        assert call_args[1]["json"]["voice_name"] == "custom_voice"
    
    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_default_voice_name(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["བོད་སྐད།"]
        
        mock_response = MagicMock()
        mock_response.content = _create_mock_wav(100)
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = generate_monlam_tts_audio("བོད་སྐད།")
        
        call_args = mock_post.call_args
        assert call_args[1]["json"]["voice_name"] == DEFAULT_MONLAM_VOICE_NAME
    
    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_http_status_error(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["བོད་སྐད།"]
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_post.side_effect = httpx.HTTPStatusError(
            "Error",
            request=MagicMock(),
            response=mock_response
        )
        
        with pytest.raises(RuntimeError, match="TTS generation failed at"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_request_error(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["བོད་སྐད།"]
        
        mock_post.side_effect = httpx.RequestError("Connection failed")
        
        with pytest.raises(RuntimeError, match="TTS generation failed at"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_invalid_audio_data_empty(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["བོད་སྐད།"]
        
        mock_response = MagicMock()
        mock_response.content = b""
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with pytest.raises(RuntimeError, match="TTS generation failed at"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_invalid_audio_data_not_riff(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["བོད་སྐད།"]
        
        mock_response = MagicMock()
        mock_response.content = b"INVALID_DATA"
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with pytest.raises(RuntimeError, match="TTS generation failed at"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_base_url_trailing_slash_removed(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai/",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["བོད་སྐད།"]
        
        mock_response = MagicMock()
        mock_response.content = _create_mock_wav(100)
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        generate_monlam_tts_audio("བོད་སྐད།")
        
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.monlam.ai/api/v1/text-to-speech/stream"

    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_multiple_chunks_merged_with_silence(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["chunk1", "chunk2", "chunk3"]
        
        mock_response = MagicMock()
        mock_response.content = _create_mock_wav(100)
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = generate_monlam_tts_audio("long tibetan text")
        
        assert result[:4] == b"RIFF"
        assert mock_post.call_count == 3

    @patch("worker_api.audio.services.monlam_tts_service.chunk_tibetan_text")
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_chunk_failure_aborts_with_message(self, mock_get, mock_post, mock_chunk):
        def get_side_effect(key):
            config = {
                "MONLAM_BASE_URL": "https://api.monlam.ai",
                "MONLAM_API_KEY": "fake_api_key",
                "MONLAM_TTS_PROVIDER": "test_provider",
                "MONLAM_TTS_MODEL_NAME": "test_model",
                "MONLAM_TTS_VOICE_NAME": None,
            }
            return config.get(key)
        
        mock_get.side_effect = get_side_effect
        mock_chunk.return_value = ["chunk1", "failing_chunk_text", "chunk3"]
        
        call_count = [0]
        def post_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise httpx.RequestError("Connection failed")
            mock_response = MagicMock()
            mock_response.content = _create_mock_wav(100)
            mock_response.status_code = 200
            return mock_response
        
        mock_post.side_effect = post_side_effect
        
        with pytest.raises(RuntimeError, match="TTS generation failed at: 'failing_chunk_text'"):
            generate_monlam_tts_audio("long tibetan text")


class TestGenerateSilence:
    def test_generate_silence_100ms(self):
        silence = _generate_silence(100)
        expected_samples = int((100 / 1000) * SAMPLE_RATE)
        assert len(silence) == expected_samples * 2

    def test_generate_silence_zero(self):
        silence = _generate_silence(0)
        assert len(silence) == 0


class TestBuildWavFromPcm:
    def test_build_wav_valid_header(self):
        pcm_data = b"\x00" * 100
        wav = _build_wav_from_pcm(pcm_data)
        assert wav[:4] == b"RIFF"
        assert wav[8:12] == b"WAVE"
        assert len(wav) == WAV_HEADER_SIZE + len(pcm_data)


def test_default_monlam_voice_name():
    assert DEFAULT_MONLAM_VOICE_NAME == MonlamVoiceName.DOLKAR_LHASA_FEMALE.value
