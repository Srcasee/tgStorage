from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.v2.download.telegram import DefaultTelegramStreamBackend

router = APIRouter(prefix="/api/v2/resources", tags=["download"])


backend = DefaultTelegramStreamBackend()


@router.get("/{resource_id}/download")
async def download_resource(resource_id: int):
    """Stream a resource from storage backend.

    The backend remains replaceable. Telegram authentication, account
    selection and proxy routing are intentionally outside this API layer.
    """

    try:
        stream = backend.stream(resource_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return StreamingResponse(
        stream,
        media_type="application/octet-stream",
    )
