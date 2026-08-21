"""Legacy Telegram scanner kept for reference only.

This is the pre-v2 scanner implementation. It enumerated Telegram dialogs and
then scanned configured chat IDs from that dialog list. It is intentionally not
imported by the active indexer.

Do not use this module for production scanning.
"""

import os
import asyncio

from database import get_connection


db_lock = asyncio.Lock()

TG_STORAGE_CHAT_ID = int(os.getenv("TG_STORAGE_CHAT_ID", "0"))
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL", "300"))


async def scan_dialogs(client, account_id):
    async with db_lock:
        return await _scan_dialogs(client, account_id)


async def _scan_dialogs(client, account_id):
    print("[SCAN-LEGACY] start telegram scan", flush=True)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, telegram_chat_id, name, scan_interval, last_message_id,
               last_scan_time, sync_mode, scan_status
        FROM telegram_sources
        WHERE account_id=? AND enabled=1
        """,
        (account_id,),
    )
    source_rows = cursor.fetchall()
    sources = {
        row["telegram_chat_id"]: {
            "id": row["id"], "name": row["name"],
            "scan_interval": row["scan_interval"],
            "last_message_id": row["last_message_id"],
            "last_scan_time": row["last_scan_time"],
            "sync_mode": row["sync_mode"], "scan_status": row["scan_status"],
        }
        for row in source_rows
    }
    source_chat_ids = set(sources.keys())

    count = 0
    async for dialog in client.iter_dialogs():
        if dialog.id not in source_chat_ids:
            continue
        source = sources.get(dialog.id)
        if not source:
            continue
        last_message_id = source["last_message_id"] or 0
        async for message in client.iter_messages(dialog.entity, min_id=last_message_id):
            if not message.media or not message.file:
                continue
            filename = message.file.name or f"{message.id}.bin"
            cursor.execute(
                """
                INSERT OR IGNORE INTO files
                (filename, size, mime_type, telegram_chat_id, message_id, upload_time, account_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    filename, message.file.size, message.file.mime_type,
                    dialog.id, message.id, int(message.date.timestamp()), account_id,
                ),
            )
            count += 1
    conn.commit()
    conn.close()
    print(f"[SCAN-LEGACY] finished {count} files", flush=True)


async def scanner_loop(client, account_id):
    while True:
        try:
            await scan_dialogs(client, account_id)
        except Exception as exc:
            print(f"[SCAN-LEGACY] error: {exc!r}", flush=True)
        await asyncio.sleep(SCAN_INTERVAL)
