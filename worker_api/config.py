import os
import re

DEFAULTS = dict(
    SITE_LANGUAGE="en",
    SITE_NAME="WebBuddhist Worker",
    ACCESS_TOKEN_EXPIRE_MINUTES=3000000,
    APP_NAME="WebBuddhist Worker Backend",
    AWS_ACCESS_KEY="",
    AWS_SECRET_KEY="",
    AWS_REGION="eu-central-1",
    AWS_BUCKET_NAME="app-pecha-backend",
    AWS_BUCKET_OWNER="",
    BASE_URL="https://webuddhist.com/",
    CLIENT_ID="",
    COMPRESSED_QUALITY=80,
    DATABASE_URL="postgresql://admin:pechaAdmin@localhost:5434/pecha",
    DEFAULT_LANGUAGE="en",
    DEFAULT_PAGE_SIZE=10,
    DEPLOYMENT_MODE="DEBUG",
    DOMAIN_NAME="dev-pecha-esukhai.us.auth0.com",
    IMAGE_EXPIRATION_IN_SEC=3600,
    JWT_ALGORITHM="HS256",
    JWT_AUD="https://pecha.org",
    JWT_ISSUER="https://pecha.org",
    JWT_SECRET_KEY="",
    MAX_FILE_SIZE_MB=1,
    MAX_FILE_SIZE = 5 * 1024 * 1024,
    MAX_AUDIO_FILE_SIZE = 50 * 1024 * 1024,
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'},
    ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.wav', '.aac', '.ogg'},
    MONGO_CONNECTION_STRING="mongodb://admin:pechaAdmin@localhost:27017/pecha?authSource=admin",

    WEBUDDHIST_STUDIO_BASE_URL="https://studio.webuddhist.com",
    MONGO_DATABASE_NAME="webuddhist",
    REFRESH_TOKEN_EXPIRE_DAYS=30,
    VERSION="0.0.1",
    # Cache Configuration
    CACHE_HOST="localhost",
    CACHE_PORT=6379,
    CACHE_DB=0,
    CACHE_PREFIX="worker:",
    CACHE_DEFAULT_TIMEOUT=3000000,
    CACHE_CONNECTION_STRING="redis://localhost:6379",
    
    # Cache timeout configurations for different types (in seconds)
    CACHE_TEXT_TIMEOUT=1800,
    CACHE_COLLECTION_TIMEOUT=1800,
    CACHE_USER_TIMEOUT=900,
    CACHE_TOPIC_TIMEOUT=1800,
    CACHE_SHEET_TIMEOUT=60,

    SHORT_URL_GENERATION_ENDPOINT="https://pech.as/api/v1",
    
    EXTERNAL_SEARCH_API_URL="https://pecha-backend-dev.web.app/",

    PECHA_BACKEND_ENDPOINT="http://127.0.0.1:8000/api/v1",

    # Search configuration
    ELASTICSEARCH_URL= None,
    ELASTICSEARCH_API=None,
    ELASTICSEARCH_CONTENT_INDEX = "pecha-texts",
    ELASTICSEARCH_SEGMENT_INDEX = "pecha-segments",
    ELASTICSEARCH_SHEET_INDEX = "pecha-sheets",

    MAILTRAP_API_KEY = "",
    SENDER_EMAIL="",
    SENDER_NAME="",

    OPENPECHA_SEARCH_API_URL="",

    ### text uploader script configuration
    APPLICATION = "webuddhist",
    ACCESS_TOKEN="",
    COLLECTION_LANGUAGES = ["bo", "en", "zh"],

    #pecha api configuration
    EXTERNAL_PECHA_API_URL="",
    EXTERNAL_DEV_PECHA_API_URL="",
    EXTERNAL_OPENPECHA_API_KEY="",
    EXTERNAL_PECHA_APP_NAME="webuddhist",

    EXTERNAL_TITLE_SEARCH_API_URL="",

    SQS_TIMEOUT=1800,

    GROUP_INVITE_EXPIRY_MINUTES=30,
    WEBUDDHIST_EMAIL_LOGO_URL="",

    # Request observability (per-endpoint memory and latency logging)
    REQUEST_OBSERVABILITY_ENABLED="true",
    REQUEST_OBSERVABILITY_MEMORY_WARN_MB=50,
    REQUEST_OBSERVABILITY_SKIP_PATHS="/health,/internal/dispatch-due-notifications,/internal/dispatch-routine-notifications",

    # TTS Configuration
    GEMINI_API_KEY="",
    MONLAM_BASE_URL="",
    MONLAM_API_KEY="",
    MONLAM_TTS_PROVIDER="",
    MONLAM_TTS_MODEL_NAME="",
    MONLAM_TTS_VOICE_NAME="",

    # Notification dispatch (Cloud Scheduler -> worker)
    NOTIFICATION_DISPATCH_SECRET_TOKEN="Dispatch",
    NOTIFICATION_DISPATCH_BATCH_SIZE=100,
    NOTIFICATION_DISPATCH_ENABLED="true",

    GOOGLE_APPLICATION_CREDENTIALS="/etc/secrets/firebase-service-account.json",

    # Notification content defaults
    NOTIFICATION_DEFAULT_TITLE="WebBuddhist",
    NOTIFICATION_DEFAULT_BODY="Time for your daily practice.",

    # Optional Redis idempotency during dispatch
    NOTIFICATION_IDEMPOTENCY_ENABLED="false",
    NOTIFICATION_IDEMPOTENCY_TTL_SECONDS=3600,
    NOTIFICATION_IDEMPOTENCY_KEY_PREFIX="worker:notifications:sent:",
    PLAN_BACKEND="https://api.webuddhist.com",
)

TIME_FORMAT_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return str(DEFAULTS[key])


def get_float(key: str) -> float:
    try:
        return float(get(key))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Could not convert the value for key '{key}' to float: {e}")


def get_int(key: str) -> int:
    try:
        return int(get(key))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Could not convert the value for key '{key}' to int: {e}")


def get_bool(key: str) -> bool:
    return get(key).lower() in {"1", "true", "yes", "on"}
