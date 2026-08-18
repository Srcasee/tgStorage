import os


# ============================================================
# Telegram 配置
# ============================================================


class Settings:


    TG_API_ID = int(
        os.getenv(
            "TG_API_ID",
            "0"
        )
    )


    TG_API_HASH = os.getenv(
        "TG_API_HASH"
    )


    TG_PHONE = os.getenv(
        "TG_PHONE"
    )
    
    
    TG_SESSION_DIR = os.getenv(
    "TG_SESSION_DIR",
    "/data/accounts"
    )


    TG_SESSION = os.getenv(
        "TG_SESSION",
        "/data/accounts/default"
    )


    TG_CONNECT_TIMEOUT = int(
        os.getenv(
            "TG_CONNECT_TIMEOUT",
            "30"
        )
    )


    ENABLE_PROXY = (
        os.getenv(
            "ENABLE_PROXY",
            "false"
        ).lower()
        == "true"
    )


    PROXY_HOST = os.getenv(
        "PROXY_HOST",
        "proxy"
    )


    PROXY_PORT = int(
        os.getenv(
            "PROXY_PORT",
            "1080"
        )
    )


    PROXY_TYPE = os.getenv(
        "PROXY_TYPE",
        "socks5"
    )



    DOWNLOAD_CHUNK_SIZE = int(
        os.getenv(
            "DOWNLOAD_CHUNK_SIZE",
            "1048576"
        )
    )



settings = Settings()



# ============================================================
# Telethon代理参数
# ============================================================


proxy = None


if settings.ENABLE_PROXY:


    proxy = (
        settings.PROXY_TYPE,
        settings.PROXY_HOST,
        settings.PROXY_PORT,
        True
    )