import pytest

from worker_api.constants import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    MAX_FILE_SIZE_MB,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_AUDIO_EXTENSIONS,
    CACHE_KEY_PREFIX,
)


def test_http_status_messages():
    assert HTTP_200_OK == "OK"
    assert HTTP_201_CREATED == "Created"
    assert HTTP_204_NO_CONTENT == "No Content"
    assert HTTP_400_BAD_REQUEST == "Bad Request"
    assert HTTP_401_UNAUTHORIZED == "Unauthorized"
    assert HTTP_403_FORBIDDEN == "Forbidden"
    assert HTTP_404_NOT_FOUND == "Not Found"
    assert HTTP_500_INTERNAL_SERVER_ERROR == "Internal Server Error"


def test_pagination_constants():
    assert DEFAULT_PAGE_SIZE == 10
    assert MAX_PAGE_SIZE == 100
    assert isinstance(DEFAULT_PAGE_SIZE, int)
    assert isinstance(MAX_PAGE_SIZE, int)


def test_file_upload_constants():
    assert MAX_FILE_SIZE_MB == 5
    assert isinstance(MAX_FILE_SIZE_MB, int)
    
    assert ALLOWED_IMAGE_EXTENSIONS == {'.jpg', '.jpeg', '.png', '.webp'}
    assert isinstance(ALLOWED_IMAGE_EXTENSIONS, set)
    assert '.jpg' in ALLOWED_IMAGE_EXTENSIONS
    assert '.png' in ALLOWED_IMAGE_EXTENSIONS
    
    assert ALLOWED_AUDIO_EXTENSIONS == {'.mp3', '.m4a', '.wav', '.aac', '.ogg'}
    assert isinstance(ALLOWED_AUDIO_EXTENSIONS, set)
    assert '.mp3' in ALLOWED_AUDIO_EXTENSIONS
    assert '.wav' in ALLOWED_AUDIO_EXTENSIONS


def test_cache_constants():
    assert CACHE_KEY_PREFIX == "worker:"
    assert isinstance(CACHE_KEY_PREFIX, str)
