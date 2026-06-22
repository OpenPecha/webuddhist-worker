"""
Constants used throughout the worker API application.
"""

# HTTP Status Messages
HTTP_200_OK = "OK"
HTTP_201_CREATED = "Created"
HTTP_204_NO_CONTENT = "No Content"
HTTP_400_BAD_REQUEST = "Bad Request"
HTTP_401_UNAUTHORIZED = "Unauthorized"
HTTP_403_FORBIDDEN = "Forbidden"
HTTP_404_NOT_FOUND = "Not Found"
HTTP_500_INTERNAL_SERVER_ERROR = "Internal Server Error"

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# File Upload
MAX_FILE_SIZE_MB = 5
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.wav', '.aac', '.ogg'}

# Cache Keys
CACHE_KEY_PREFIX = "worker:"
