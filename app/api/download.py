from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.download.providers import ResourceLocation
from app.download.service import DownloadService
from app.download.backend.telegram_backend import TelegramBackend
from app.download.resource_resolver import ResourceResolver
from app.telegram.client_provider import DatabaseTelegramClientProvider
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
    try:
        start = int(start_text)
        end = int(end_text) if end_text else size - 1
    except ValueError as exc:
        raise HTTPException(status_code=416, detail="invalid Range header") from exc
    if start < 0 or end < start or start >= size:
        raise HTTPException(status_code=416, detail="range not satisfiable")
    return start, min(end, size - 1)


def _content_disposition(filename: str, resource_id: int) -> str:
    name = filename.strip() or str(resource_id)
    fallback = "".join(ch if 32 <= ord(ch) < 127 else "_" for ch in name)
    encoded = quote(name, safe="!#$&+-.^_`|~")
    return f'attachment; filename="{fallback}"; filename*=UTF-8\'\'{encoded}'


async def _backend(session: AsyncSession) -> DownloadService:
    provider = DatabaseTelegramClientProvider(
        session=session,
        runtime=get_runtime(),
        pool=get_pool(),
    )
    return DownloadService(TelegramBackend(provider, lambda account: provider.get_account(account)))


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

    size = location.size
    byte_range = _parse_range(range_header, size)
    start, end = byte_range or (0, size - 1)

    service = await _backend(session)
    resource = ResourceLocation(
        resource_id=str(resource_id),
        backend="telegram",
        metadata={
            "chat_id": location.chat_id,
            "message_id": location.message_id,
            "account_id": location.account_id,
        },
    )

    stream = service.stream(resource, offset=start, limit=end - start + 1)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Content-Disposition": _content_disposition(location.filename, resource_id),
    }
    status_code = 206 if byte_range else 200
    if byte_range:
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"

    return StreamingResponse(
        stream,
        status_code=status_code,
        media_type=location.mime_type,
        headers=headers,
    )
