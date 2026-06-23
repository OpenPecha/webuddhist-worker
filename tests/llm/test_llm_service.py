"""
Tests for LLM service.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from worker_api.llm.llm_service import chat_with_gemini, _chat_with_gemini_sync, DEFAULT_MODEL


class TestChatWithGemini:
    """Tests for chat_with_gemini async function."""

    @pytest.mark.asyncio
    @patch("worker_api.llm.llm_service._chat_with_gemini_sync")
    async def test_chat_calls_sync_function(self, mock_sync):
        """Test that async wrapper calls sync function via asyncio.to_thread."""
        mock_sync.return_value = {
            "response": "Test response",
            "model": "gemini-2.5-flash"
        }

        result = await chat_with_gemini(
            prompt="Test prompt",
            system_prompt="Test system",
            model="gemini-2.5-flash"
        )

        assert result["response"] == "Test response"
        assert result["model"] == "gemini-2.5-flash"
        mock_sync.assert_called_once_with("Test prompt", "Test system", "gemini-2.5-flash")


class TestChatWithGeminiSync:
    """Tests for _chat_with_gemini_sync function."""

    @patch("worker_api.llm.llm_service.get")
    @patch("worker_api.llm.llm_service.genai.Client")
    def test_successful_chat(self, mock_client_class, mock_get):
        """Test successful chat with Gemini."""
        # Mock config
        mock_get.return_value = "test-api-key"

        # Mock Gemini client and response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_part = MagicMock()
        mock_part.text = "Paris is the capital of France."

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client.models.generate_content.return_value = mock_response

        # Execute
        result = _chat_with_gemini_sync(
            prompt="What is the capital of France?",
            system_prompt=None,
            model=None
        )

        # Assert
        assert result["response"] == "Paris is the capital of France."
        assert result["model"] == DEFAULT_MODEL

        mock_client_class.assert_called_once_with(api_key="test-api-key")
        mock_client.models.generate_content.assert_called_once()

    @patch("worker_api.llm.llm_service.get")
    def test_missing_api_key(self, mock_get):
        """Test error when GEMINI_API_KEY is not configured."""
        mock_get.return_value = ""

        with pytest.raises(HTTPException) as exc_info:
            _chat_with_gemini_sync(prompt="Test", system_prompt=None, model=None)

        assert exc_info.value.status_code == 500
        assert "GEMINI_API_KEY is not configured" in exc_info.value.detail

    @patch("worker_api.llm.llm_service.get")
    @patch("worker_api.llm.llm_service.genai.Client")
    def test_with_system_prompt(self, mock_client_class, mock_get):
        """Test chat with system prompt."""
        mock_get.return_value = "test-api-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_part = MagicMock()
        mock_part.text = "Response with system prompt"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client.models.generate_content.return_value = mock_response

        result = _chat_with_gemini_sync(
            prompt="Test",
            system_prompt="You are a helpful assistant",
            model=None
        )

        assert result["response"] == "Response with system prompt"

        # Verify generate_content was called
        call_args = mock_client.models.generate_content.call_args
        assert call_args is not None

    @patch("worker_api.llm.llm_service.get")
    @patch("worker_api.llm.llm_service.genai.Client")
    def test_with_custom_model(self, mock_client_class, mock_get):
        """Test chat with custom model."""
        mock_get.return_value = "test-api-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_part = MagicMock()
        mock_part.text = "Response from custom model"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client.models.generate_content.return_value = mock_response

        result = _chat_with_gemini_sync(
            prompt="Test",
            system_prompt=None,
            model="gemini-1.5-pro"
        )

        assert result["response"] == "Response from custom model"
        assert result["model"] == "gemini-1.5-pro"

        # Verify model was passed correctly
        call_args = mock_client.models.generate_content.call_args
        assert call_args.kwargs["model"] == "gemini-1.5-pro"

    @patch("worker_api.llm.llm_service.get")
    @patch("worker_api.llm.llm_service.genai.Client")
    def test_gemini_api_error(self, mock_client_class, mock_get):
        """Test error handling when Gemini API fails."""
        mock_get.return_value = "test-api-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.models.generate_content.side_effect = Exception("API connection failed")

        with pytest.raises(HTTPException) as exc_info:
            _chat_with_gemini_sync(prompt="Test", system_prompt=None, model=None)

        assert exc_info.value.status_code == 502
        assert "Gemini API error" in exc_info.value.detail
        assert "API connection failed" in exc_info.value.detail

    @patch("worker_api.llm.llm_service.get")
    @patch("worker_api.llm.llm_service.genai.Client")
    def test_no_response_candidates(self, mock_client_class, mock_get):
        """Test error when Gemini returns no candidates."""
        mock_get.return_value = "test-api-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.candidates = []

        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            _chat_with_gemini_sync(prompt="Test", system_prompt=None, model=None)

        assert exc_info.value.status_code == 502
        assert "Gemini returned no response" in exc_info.value.detail

    @patch("worker_api.llm.llm_service.get")
    @patch("worker_api.llm.llm_service.genai.Client")
    def test_no_response_parts(self, mock_client_class, mock_get):
        """Test error when Gemini candidate has no parts."""
        mock_get.return_value = "test-api-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_candidate = MagicMock()
        mock_candidate.content.parts = []

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            _chat_with_gemini_sync(prompt="Test", system_prompt=None, model=None)

        assert exc_info.value.status_code == 502
        assert "Gemini returned no response" in exc_info.value.detail

    @patch("worker_api.llm.llm_service.get")
    @patch("worker_api.llm.llm_service.genai.Client")
    def test_default_model_used(self, mock_client_class, mock_get):
        """Test that default model is used when none specified."""
        mock_get.return_value = "test-api-key"

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_part = MagicMock()
        mock_part.text = "Response"

        mock_candidate = MagicMock()
        mock_candidate.content.parts = [mock_part]

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]

        mock_client.models.generate_content.return_value = mock_response

        result = _chat_with_gemini_sync(prompt="Test", system_prompt=None, model=None)

        assert result["model"] == DEFAULT_MODEL

        call_args = mock_client.models.generate_content.call_args
        assert call_args.kwargs["model"] == DEFAULT_MODEL
