import os


def test_env_variable_priority(monkeypatch):
    monkeypatch.setenv("TG_API_ID", "999")
    monkeypatch.setenv("TG_API_HASH", "env-hash")

    from app.core.config import Settings

    settings = Settings()

    assert settings.telegram_api_id == 999
    assert settings.telegram_api_hash == "env-hash"


def test_proxy_configuration(monkeypatch):
    monkeypatch.setenv("ENABLE_PROXY", "true")
    monkeypatch.setenv("PROXY_TYPE", "socks5")
    monkeypatch.setenv("PROXY_HOST", "127.0.0.1")
    monkeypatch.setenv("PROXY_PORT", "1080")

    from app.core.config import Settings

    settings = Settings()

    assert settings.proxy.enabled is True
    assert settings.proxy.proxy_type == "socks5"
    assert settings.proxy.host == "127.0.0.1"
    assert settings.proxy.port == 1080
