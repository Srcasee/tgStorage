"""Authentication dependencies for protected application endpoints."""

from fastapi import Header, HTTPException, status

from app.core.config import settings


async def require_admin_api_key(
    x_admin_api_key: str | None = Header(default=None),
) -> None:
    """Protect administrative APIs with a simple deployment-level API key.

    This is the first security layer. A full user/role system can replace it
    later without changing admin route structure.
    """
    expected = getattr(settings, "admin_api_key", None)
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin authentication is not configured",
        )

    if x_admin_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid admin api key",
        )
