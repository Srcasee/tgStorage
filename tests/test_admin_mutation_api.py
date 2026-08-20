"""Phase 2-C admin mutation API database E2E tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.core.database import get_session
from app.models import Resource, Category, TelegramAccount, TelegramSource


@pytest.mark.asyncio
async def test_admin_account_and_source_mutation_e2e(override_database):
    app.dependency_overrides[get_session] = override_database
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            account = await client.post(
                "/admin/accounts",
                json={"name": "test-account", "session_path": "/tmp/test.session", "enabled": True},
            )
            assert account.status_code == 200
            account_id = account.json()["id"]

            source = await client.post(
                "/admin/sources",
                json={
                    "account_id": account_id,
                    "chat_id": -100123456,
                    "chat_type": "channel",
                    "title": "test-source",
                },
            )
            assert source.status_code == 200
            assert source.json()["id"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_resource_category_mutation_relation_e2e(override_database, test_session_factory):
    app.dependency_overrides[get_session] = override_database
    try:
        async with test_session_factory() as session:
            account = TelegramAccount(
                name="resource-test-account",
                session_path="/tmp/resource-test.session",
                enabled=True,
            )
            session.add(account)
            await session.commit()
            await session.refresh(account)

            source = TelegramSource(
                account_id=account.id,
                chat_id=-100999999,
                chat_type="channel",
                title="resource-test-source",
            )
            category = Category(name="test-category")
            session.add_all([source, category])
            await session.commit()
            await session.refresh(source)
            await session.refresh(category)

            resource = Resource(
                source_id=source.id,
                filename="test.mkv",
                category_id=None,
            )
            session.add(resource)
            await session.commit()
            await session.refresh(resource)

            resource_id = resource.id
            category_id = category.id

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(
                f"/admin/resources/{resource_id}",
                json={"category_id": category_id},
            )
            assert response.status_code == 200
            assert response.json()["category_id"] == category_id

        async with test_session_factory() as session:
            result = await session.execute(
                select(Resource).where(Resource.id == resource_id)
            )
            updated_resource = result.scalar_one()
            assert updated_resource.category_id == category_id
    finally:
        app.dependency_overrides.clear()
