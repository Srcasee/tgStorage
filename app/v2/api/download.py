from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.v2.core.dependencies import get_db_session
from app.v2.download.telegram import TelegramStreamBackend
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v2/resources", tags=["download"])


def get_telegram_backend(request: Request, session: AsyncSession = Depends(get_db_session)) -> TelegramStreamBackend:
    """Return the configured Telegram backend without constructing a client in the API layer."""
    backend = getattr(request.app.state, "telegram_stream_backend", None)
    if backend is None:
        raise HTTPException(status_code=503, detail="Telegram download backend is not configured")
    if not isinstance(backend, TelegramStreamBackend):
        raise HTTPException(status_code=503, detail="Invalid Telegram download backend")
    return backend


@router.get("/{resource_id}/download")
async def download_resource(
    resource_id: int,
    start: int = 0,
    limit: int | None = None,
    backend: TelegramStreamBackend = Depends(get_telegram_backend),
):
    """Stream an indexed Telegram resource.

    Telegram clients, account selection and proxy/network plugins are injected
    at application startup rather than constructed per request.
    """
    try:
        stream = backend.stream(resource_id, start=start, limit=limit)
        return StreamingResponse(stream, media_type="application/octet-stream")
    except (LookupError, PermissionError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="download backend unavailable") from exc
