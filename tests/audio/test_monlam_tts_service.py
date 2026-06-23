import pytest
from unittest.mock import patch, MagicMock
import httpx

from worker_api.audio.services.monlam_tts_service import (
    generate_monlam_tts_audio,
    DEFAULT_MONLAM_VOICE_NAME,
)
from worker_api.audio.enums import MonlamVoiceName


class TestGenerateMonlamTtsAudio:
    def test_empty_content_raises_error(self):
        with pytest.raises(ValueError, match="Content cannot be empty"):
            generate_monlam_tts_audio("")
    
    def test_whitespace_content_raises_error(self):
        with pytest.raises(ValueError, match="Content cannot be empty"):
            generate_monlam_tts_audio("   ")
    
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_missing_api_key_raises_error(self, mock_get):
        def get_side_effect(key):
            if key == "MONLAM_BASE_URL":
                return "https://api.monlam.ai"
            if key == "MONLAM_API_KEY":
                return None
            return "default"
        
        mock_get.side_effect = get_side_effect
        
        with pytest.raises(RuntimeError, match="MONLAM_API_KEY is not configured"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_successful_generation(self, mock_get, mock_post):
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
        
        mock_response = MagicMock()
        mock_response.content = b"RIFF" + b"\x00" * 100
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = generate_monlam_tts_audio("བོད་སྐད།")
        
        assert result == b"RIFF" + b"\x00" * 100
        mock_post.assert_called_once()
        
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.monlam.ai/api/v1/text-to-speech/stream"
        assert call_args[1]["headers"]["X-API-Key"] == "fake_api_key"
        assert call_args[1]["json"]["text"] == "བོད་སྐད།"
        assert call_args[1]["json"]["provider"] == "test_provider"
        assert call_args[1]["json"]["model_name"] == "test_model"
    
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_custom_voice_name(self, mock_get, mock_post):
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
        
        mock_response = MagicMock()
        mock_response.content = b"RIFF" + b"\x00" * 100
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = generate_monlam_tts_audio("བོད་སྐད།", voice_name="custom_voice")
        
        assert result == b"RIFF" + b"\x00" * 100
        
        call_args = mock_post.call_args
        assert call_args[1]["json"]["voice_name"] == "custom_voice"
    
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_default_voice_name(self, mock_get, mock_post):
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
        
        mock_response = MagicMock()
        mock_response.content = b"RIFF" + b"\x00" * 100
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = generate_monlam_tts_audio("བོད་སྐད།")
        
        call_args = mock_post.call_args
        assert call_args[1]["json"]["voice_name"] == DEFAULT_MONLAM_VOICE_NAME
    
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_http_status_error(self, mock_get, mock_post):
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
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_post.side_effect = httpx.HTTPStatusError(
            "Error",
            request=MagicMock(),
            response=mock_response
        )
        
        with pytest.raises(RuntimeError, match="Monlam TTS request failed with status 500"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_request_error(self, mock_get, mock_post):
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
        
        mock_post.side_effect = httpx.RequestError("Connection failed")
        
        with pytest.raises(RuntimeError, match="Monlam TTS request failed"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_invalid_audio_data_empty(self, mock_get, mock_post):
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
        
        mock_response = MagicMock()
        mock_response.content = b""
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with pytest.raises(RuntimeError, match="Monlam TTS generation returned invalid audio data"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_invalid_audio_data_not_riff(self, mock_get, mock_post):
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
        
        mock_response = MagicMock()
        mock_response.content = b"INVALID_DATA"
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with pytest.raises(RuntimeError, match="Monlam TTS generation returned invalid audio data"):
            generate_monlam_tts_audio("བོད་སྐད།")
    
    @patch("worker_api.audio.services.monlam_tts_service.httpx.post")
    @patch("worker_api.audio.services.monlam_tts_service.get")
    def test_base_url_trailing_slash_removed(self, mock_get, mock_post):
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
        
        mock_response = MagicMock()
        mock_response.content = b"RIFF" + b"\x00" * 100
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        generate_monlam_tts_audio("བོད་སྐད།")
        
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.monlam.ai/api/v1/text-to-speech/stream"


def test_default_monlam_voice_name():
    assert DEFAULT_MONLAM_VOICE_NAME == MonlamVoiceName.DOLKAR_LHASA_FEMALE.value
