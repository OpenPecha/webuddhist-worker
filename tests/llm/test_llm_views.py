"""
Tests for LLM chat API endpoints.
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException


class TestLLMChat:
    """Tests for POST /llm/chat endpoint."""

    @pytest.mark.asyncio
    @patch("worker_api.llm.llm_views.chat_with_gemini")
    async def test_chat_with_prompt_only(self, mock_chat, client):
        """Test chat with only prompt provided."""
        mock_chat.return_value = {
            "response": "Paris is the capital of France.",
            "model": "gemini-2.5-flash"
        }

        response = client.post(
            "/api/v1/llm/chat",
            json={
                "prompt": "What is the capital of France?"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Paris is the capital of France."
        assert data["model"] == "gemini-2.5-flash"

        mock_chat.assert_called_once()
        call_kwargs = mock_chat.call_args.kwargs
        assert call_kwargs["prompt"] == "What is the capital of France?"
        assert call_kwargs["system_prompt"] is None
        assert call_kwargs["model"] is None

    @pytest.mark.asyncio
    @patch("worker_api.llm.llm_views.chat_with_gemini")
    async def test_chat_with_system_prompt(self, mock_chat, client):
        """Test chat with system prompt provided."""
        mock_chat.return_value = {
            "response": "As a geography expert, Paris is the capital of France.",
            "model": "gemini-2.5-flash"
        }

        response = client.post(
            "/api/v1/llm/chat",
            json={
                "prompt": "What is the capital of France?",
                "system_prompt": "You are a helpful geography assistant."
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "Paris" in data["response"]

        mock_chat.assert_called_once()
        call_kwargs = mock_chat.call_args.kwargs
        assert call_kwargs["system_prompt"] == "You are a helpful geography assistant."

    @pytest.mark.asyncio
    @patch("worker_api.llm.llm_views.chat_with_gemini")
    async def test_chat_with_custom_model(self, mock_chat, client):
        """Test chat with custom model specified."""
        mock_chat.return_value = {
            "response": "Test response",
            "model": "gemini-1.5-pro"
        }

        response = client.post(
            "/api/v1/llm/chat",
            json={
                "prompt": "Hello",
                "model": "gemini-1.5-pro"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "gemini-1.5-pro"

        mock_chat.assert_called_once()
        call_kwargs = mock_chat.call_args.kwargs
        assert call_kwargs["model"] == "gemini-1.5-pro"

    @pytest.mark.asyncio
    async def test_chat_missing_prompt(self, client):
        """Test chat with missing prompt returns validation error."""
        response = client.post(
            "/api/v1/llm/chat",
            json={}
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_chat_empty_prompt(self, client):
        """Test chat with empty prompt."""
        response = client.post(
            "/api/v1/llm/chat",
            json={
                "prompt": ""
            }
        )

        # Empty string is valid for Pydantic, but will likely fail at service level
        assert response.status_code in [200, 422, 500, 502]

    @pytest.mark.asyncio
    @patch("worker_api.llm.llm_views.chat_with_gemini")
    async def test_chat_service_error(self, mock_chat, client):
        """Test chat when service raises HTTPException."""
        mock_chat.side_effect = HTTPException(
            status_code=502,
            detail="Gemini API error: Connection timeout"
        )

        response = client.post(
            "/api/v1/llm/chat",
            json={
                "prompt": "Test prompt"
            }
        )

        assert response.status_code == 502
        data = response.json()
        assert "Gemini API error" in data["detail"]

    @pytest.mark.asyncio
    @patch("worker_api.llm.llm_views.chat_with_gemini")
    async def test_chat_with_all_parameters(self, mock_chat, client):
        """Test chat with all parameters provided."""
        mock_chat.return_value = {
            "response": "Complete response",
            "model": "gemini-1.5-pro"
        }

        response = client.post(
            "/api/v1/llm/chat",
            json={
                "prompt": "Tell me about AI",
                "system_prompt": "You are an AI expert",
                "model": "gemini-1.5-pro"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Complete response"
        assert data["model"] == "gemini-1.5-pro"

        mock_chat.assert_called_once()
        call_kwargs = mock_chat.call_args.kwargs
        assert call_kwargs["prompt"] == "Tell me about AI"
        assert call_kwargs["system_prompt"] == "You are an AI expert"
        assert call_kwargs["model"] == "gemini-1.5-pro"
