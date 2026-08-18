import os
import time
import asyncio

from database import get_connection


# ============================================================
# SQLite 扫描写入锁
# 多 Telegram 账号共用一个 files.db
# 防止同时 UPDATE/INSERT 导致 database locked
# ============================================================
db_lock = asyncio.Lock()



# ============================================================
# Telegram 文件扫描器
# 设计：
# 不创建 TelegramClient
# 不负责 connect/disconnect
# 使用 main.py 中唯一 TelegramClient
# 防止多个 Telethon Client
# 打开 session 导致 sqlite lock
# ============================================================
TG_STORAGE_CHAT_ID = int(

    os.getenv(

        "TG_STORAGE_CHAT_ID",

        "0"

    )

)

# 扫描间隔
# 默认5分钟
SCAN_INTERVAL = int(
    os.getenv(
        "SCAN_INTERVAL",
        "300"
    )
)


# ============================================================
# 单次扫描
# ============================================================
async def scan_dialogs(client, account_id):

    async with db_lock:
        return await _scan_dialogs(client, account_id)


async def _scan_dialogs(client, account_id):

    print(

        "[SCAN] start telegram scan",

        flush=True

    )
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            telegram_chat_id,
            name,
            scan_interval,
            last_message_id,
            last_scan_time,
            sync_mode,
            scan_status
        FROM telegram_sources
        WHERE account_id=?
        AND enabled=1
        """,
        (
            account_id,
        )
    )

    source_rows = cursor.fetchall()

    sources = {
        row["telegram_chat_id"]: {
            "id": row["id"],
            "name": row["name"],
            "scan_interval": row["scan_interval"],
            "last_message_id": row["last_message_id"],
            "last_scan_time": row["last_scan_time"],
            "sync_mode": row["sync_mode"],
            "scan_status": row["scan_status"]
        }
        for row in source_rows
    }

    source_chat_ids = set(sources.keys())

    print(
        "[SCAN] sources:",
        sources,
        flush=True
    )

    count = 0


    async for dialog in client.iter_dialogs():
        # ----------------------------------------------------
        # 只扫描指定TG存储位置
        # ----------------------------------------------------
        if dialog.id not in source_chat_ids:

            continue

        print(

            "[SCAN] dialog:",
            dialog.name,
            "id:",
            dialog.id,
            flush=True
        )

        source = sources.get(dialog.id)

        if not source:

            continue


        cursor.execute(
            """
            UPDATE telegram_sources
            SET scan_status='scanning',
                updated_at=strftime('%s','now')
            WHERE id=?
            """,
            (
                source["id"],
            )
        )


        # ----------------------------------------------------
        # full模式才进行历史校验
        # ----------------------------------------------------
        if source["sync_mode"] == "full":
    
            cursor.execute(
                """
                UPDATE files
                SET scan_status='checking',
                    is_available=0
                WHERE account_id=?
                AND telegram_chat_id=?
                """,
                (
                    account_id,
                    dialog.id,
                )
            )



        last_message_id = source["last_message_id"] or 0

        current_max_message_id = last_message_id

        print(
            "[SCAN] last message:",
            last_message_id,
            flush=True
        )

        # ----------------------------------------------------
        # 增量扫描
        # ----------------------------------------------------
        
        async for message in client.iter_messages(

            dialog.entity,

            min_id=last_message_id

        ):

            if not message.media:

                continue

            if not message.file:

                continue

            if message.id > current_max_message_id:

                current_max_message_id = message.id

            filename = message.file.name

            if not filename:

                filename = f"{message.id}.bin"

            print(

                "[SCAN] file:",

                message.id,

                filename,

                flush=True

            )

            cursor.execute(
                """
                UPDATE files
                SET status='active',
                    scan_status='verified',
                    is_available=1
                WHERE account_id=?
                AND telegram_chat_id=?
                AND message_id=?
                """,
                (
                    account_id,
                    dialog.id,
                    message.id,
                )
            )

            cursor.execute(
                """
                INSERT OR IGNORE INTO files
                (
                    filename,
                    size,
                    mime_type,
                    telegram_chat_id,
                    message_id,
                    upload_time,
                    account_id
                )
                
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    filename,
                    message.file.size,
                    message.file.mime_type,
                    dialog.id,
                    message.id,
                    int(
                        message.date.timestamp()
                    ),
                    account_id
                )
            )

            count += 1
        # ----------------------------------------------------
        # full模式才检查删除
        # ----------------------------------------------------


        if source["sync_mode"] == "full":

            cursor.execute(
                """
                UPDATE files
                SET status='deleted',
                    is_available=0
                WHERE account_id=?
                AND telegram_chat_id=?
                AND scan_status='checking'
                """,
                (
                    account_id,
                    dialog.id,
                )
            )


        cursor.execute(
            """
            UPDATE telegram_sources
            SET
                last_message_id=?,
                last_scan_time=strftime('%s','now'),
                scan_status='success',
                updated_at=strftime('%s','now')
            WHERE id=?
            """,
            (
                current_max_message_id,
                source["id"],
            )
        )


    conn.commit()

    conn.close()

    print(

        f"[SCAN] finished {count} files",

        flush=True

    )


# ============================================================
# 后台循环扫描
# main.py启动调用
# ============================================================
async def scanner_loop(client, account_id):

    print(

        "[SCAN] scanner loop started",

        flush=True

    )



    while True:

        try:

            await scan_dialogs(client, account_id)

        except Exception as e:

            print(

                "[SCAN] error:",

                repr(e),

                flush=True

            )

        print(

            f"[SCAN] sleep {SCAN_INTERVAL}s",

            flush=True

        )

        await asyncio.sleep(

            SCAN_INTERVAL

        )