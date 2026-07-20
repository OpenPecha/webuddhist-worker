from typing import Any, Dict, Optional
from uuid import UUID

import httpx

from worker_api.audio.enums import AudioJobStatus
from worker_api.config import get


def _backend_url() -> str:
    backend_url = get("BACKEND_API_URL").rstrip("/")
    if not backend_url:
        raise RuntimeError("BACKEND_API_URL is not configured")
    return backend_url


def _dispatch_headers() -> Dict[str, str]:
    dispatch_token = get("NOTIFICATION_DISPATCH_SECRET_TOKEN")
    if not dispatch_token:
        raise RuntimeError("NOTIFICATION_DISPATCH_SECRET_TOKEN is not configured")
    return {"X-Dispatch-Token": dispatch_token}


async def get_audio_job_status(job_id: UUID) -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{_backend_url()}/internal/audio/jobs/{job_id}",
            headers=_dispatch_headers(),
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()


async def update_audio_job_status(
    *,
    job_id: UUID,
    status: AudioJobStatus,
    result: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"status": status.value}
    if result is not None:
        payload["result"] = result
    if error_message is not None:
        payload["error_message"] = error_message

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.patch(
            f"{_backend_url()}/internal/audio/jobs/{job_id}",
            headers=_dispatch_headers(),
            json=payload,
        )
        response.raise_for_status()
        return response.json()
