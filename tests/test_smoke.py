from pathlib import Path



def test_application_imports_and_exposes_mvp_routes():
    from app.main import app

    # FastAPI may keep nested include_router entries as internal router
    # objects in app.routes. OpenAPI is the stable flattened view of the
    # public HTTP contract and does not require application startup.
    routes = set(app.openapi()["paths"])
    assert "/" in routes
    assert "/web" in routes
    assert "/api/v2/resources/search" in routes
    assert "/api/v2/resources/{resource_id}/download" in routes


def test_models_expose_expected_tables():
    from app.models import Base

    assert {
        "telegram_accounts",
        "telegram_sources",
        "resources",
        "categories",
        "network_plugins",
    }.issubset(Base.metadata.tables)


def test_alembic_cli_files_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "alembic.ini").is_file()
    assert (root / "alembic" / "env.py").is_file()
    assert (root / "alembic" / "versions" / "0001_initial_schema.py").is_file()


async def test_startup_skips_scanner_when_disabled(monkeypatch):
    import app.main as main

    main.index_worker_enabled = False

    def fail_start():
        raise AssertionError("scanner must not start when disabled")

    monkeypatch.setattr(main.index_worker, "start", fail_start)
    await main.startup()
