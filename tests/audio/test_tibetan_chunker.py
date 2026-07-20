"""Tests for Tibetan text chunking."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from worker_api.audio.services.tibetan_chunker import (
    _get_tokenizer,
    chunk_tibetan_text,
)
import worker_api.audio.services.tibetan_chunker as chunker_module


def _token(text: str, syllables: int | None):
    return SimpleNamespace(
        text=text,
        syls=["x"] * syllables if syllables is not None else None,
    )


class TestGetTokenizer:
    def setup_method(self):
        chunker_module._tokenizer = None

    def teardown_method(self):
        chunker_module._tokenizer = None

    @patch("worker_api.audio.services.tibetan_chunker.WordTokenizer")
    def test_creates_tokenizer_once(self, mock_word_tokenizer):
        instance = MagicMock()
        mock_word_tokenizer.return_value = instance

        first = _get_tokenizer()
        second = _get_tokenizer()

        assert first is second
        mock_word_tokenizer.assert_called_once()


class TestChunkTibetanText:
    def test_empty_text_returns_empty(self):
        assert chunk_tibetan_text("") == []
        assert chunk_tibetan_text("   ") == []

    @patch("worker_api.audio.services.tibetan_chunker._get_tokenizer")
    def test_single_chunk_under_limit(self, mock_get_tokenizer):
        tokenizer = MagicMock()
        tokenizer.tokenize.return_value = [
            _token("ཁྱེད", 2),
            _token("རང", 1),
        ]
        mock_get_tokenizer.return_value = tokenizer

        chunks = chunk_tibetan_text("ཁྱེད་རང", max_syllables=15)

        assert chunks == ["ཁྱེདརང"]
        tokenizer.tokenize.assert_called_once_with("ཁྱེད་རང", split_affixes=False)

    @patch("worker_api.audio.services.tibetan_chunker._get_tokenizer")
    def test_splits_when_exceeding_max_syllables(self, mock_get_tokenizer):
        tokenizer = MagicMock()
        tokenizer.tokenize.return_value = [
            _token("aaa", 3),
            _token("bbb", 3),
            _token("ccc", 3),
        ]
        mock_get_tokenizer.return_value = tokenizer

        chunks = chunk_tibetan_text("aaa bbb ccc", max_syllables=6)

        assert chunks == ["aaabbb", "ccc"]

    @patch("worker_api.audio.services.tibetan_chunker._get_tokenizer")
    def test_missing_syls_counts_as_one(self, mock_get_tokenizer):
        tokenizer = MagicMock()
        tokenizer.tokenize.return_value = [
            _token("x", None),
            _token("y", None),
        ]
        mock_get_tokenizer.return_value = tokenizer

        chunks = chunk_tibetan_text("xy", max_syllables=1)

        assert chunks == ["x", "y"]
