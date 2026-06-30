import os
import re

DEFAULTS = dict(
    DATABASE_URL="postgresql://admin:pechaAdmin@localhost:5434/pecha",
    MONGO_CONNECTION_STRING="mongodb://admin:pechaAdmin@localhost:27017/pecha?authSource=admin",
    MONGO_DATABASE_NAME="webuddhist",

    AWS_ACCESS_KEY="",
    AWS_SECRET_KEY="",
    AWS_REGION="eu-central-1",
    AWS_BUCKET_NAME="app-pecha-backend",
    IMAGE_EXPIRATION_IN_SEC=3600,

    CACHE_CONNECTION_STRING="redis://localhost:6379",

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
    BACKEND_API_URL="http://127.0.0.1:8000/api/v1",

    GOOGLE_APPLICATION_CREDENTIALS="secrets/webuddhist-app-firebase-adminsdk-fbsvc-a4e82f9837.json",
    GOOGLE_CLOUD_PROJECT="",

    # Notification content defaults
    NOTIFICATION_DEFAULT_TITLE="WebBuddhist",
    NOTIFICATION_DEFAULT_BODY="Time for your daily practice.",

    # Optional Redis idempotency during dispatch
    NOTIFICATION_IDEMPOTENCY_ENABLED="false",
    NOTIFICATION_IDEMPOTENCY_TTL_SECONDS=3600,
    NOTIFICATION_IDEMPOTENCY_KEY_PREFIX="worker:notifications:sent:",
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
