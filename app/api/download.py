from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.download.resource_resolver import ResourceResolver
from app.download.telethon_provider import TelethonFileProvider
from app.download.telegram import TelegramStreamBackend
from app.download.telegram_reader import TelegramChunkReader
from app.telegram.client_provider import (
    DatabaseTelegramClientProvider,
    TelegramClientAuthorizationError,
)
from app.telegram.runtime_registry import get_pool, get_runtime

router = APIRouter(tags=["download"])


def _parse_range(value: str | None, size: int) -> tuple[int, int] | None:
    if not value:
        return None
    if not value.startswith("bytes=") or "," in value:
        raise HTTPException(status_code=416, detail="invalid Range header")

    spec = value[6:].strip()
    if "-" not in spec:
        raise HTTPException(status_code=416, detail="invalid Range header")
    start_text, end_text = spec.split("-", 1)

    if not start_text:
        try:
            suffix = int(end_text)
        except ValueError as exc:
            raise HTTPException(status_code=416, detail="invalid Range header") from exc
        if suffix <= 0 or size <= 0:
            raise HTTPException(status_code=416, detail="range not satisfiable")
        return max(size - suffix, 0), size - 1

    try:
        start = int(start_text)
        end = int(end_text) if end_text else size - 1
    except ValueError as exc:
        raise HTTPException(status_code=416, detail="invalid Range header") from exc

    if start < 0 or end < start or start >= size:
        raise HTTPException(status_code=416, detail="range not satisfiable")
    return start, min(end, size - 1)


def _content_disposition(filename: str, resource_id: int) -> str:
    """Build a safe attachment header with ASCII and UTF-8 filenames."""
    name = filename.strip() or str(resource_id)
    fallback = "".join(
        ch if 32 <= ord(ch) < 127 and ch not in '\\"' else "_"
        for ch in name
    ).strip() or str(resource_id)
    encoded = quote(name, safe="!#$&+-.^_`|~")
    return f'attachment; filename="{fallback}"; filename*=UTF-8\'\'{encoded}'


async def _get_backend(session: AsyncSession, account_id: int | None) -> tuple[TelegramStreamBackend, TelethonFileProvider]:
    client_provider = DatabaseTelegramClientProvider(
        session=session,
        runtime=get_runtime(),
        pool=get_pool(),
    )
    # Authenticate before returning StreamingResponse. Errors raised only
    # while iterating the response body cannot change its HTTP status safely.
    await client_provider.get_client(account_id)
    provider = TelethonFileProvider(client_provider)
    reader = TelegramChunkReader(provider)
    return TelegramStreamBackend(ResourceResolver(session), reader), provider


@router.get("/resources/{resource_id}/download")
async def download_resource(
    resource_id: int,
    range_header: str | None = Header(default=None, alias="Range"),
    session: AsyncSession = Depends(get_db_session),
):
    resolver = ResourceResolver(session)

    try:
        location = await resolver.resolve_telegram(resource_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    size = location.size
    if size <= 0:
        raise HTTPException(status_code=409, detail="resource size is unknown")

    try:
        byte_range = _parse_range(range_header, size)
    except HTTPException as exc:
        if exc.status_code == 416:
            exc.headers = {"Content-Range": f"bytes */{size}"}
        raise

    if byte_range is None:
        start, end = 0, size - 1
        status_code = 200
    else:
        start, end = byte_range
        status_code = 206

    length = end - start + 1
    try:
        backend, provider = await _get_backend(session, location.account_id)
        await provider.validate_message(
            chat_id=location.chat_id,
            message_id=location.message_id,
            account_id=location.account_id,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TelegramClientAuthorizationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    stream = backend.stream(resource_id, start=start, limit=length)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
        "Content-Disposition": _content_disposition(location.filename, resource_id),
    }
    if status_code == 206:
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"

    return StreamingResponse(
        stream,
        status_code=status_code,
        media_type=location.mime_type,
        headers=headers,
    )
