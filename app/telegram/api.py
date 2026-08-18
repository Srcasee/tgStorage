from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import get_connection
from telegram.client import get_client


router = APIRouter(
    prefix="/api/telegram",
    tags=["telegram"]
)


# ============================================================
# Telegram账号列表
# ============================================================

@router.get("/accounts")
def list_accounts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            username,
            session,
            enabled
        FROM accounts
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    return [
        dict(row)
        for row in rows
    ]



# ============================================================
# 查看Telegram dialogs
# ============================================================

@router.get("/accounts/{account_id}/dialogs")
async def list_dialogs(account_id: int):

    try:
        client = get_client(account_id)

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


    await client.connect()

    try:

        if not await client.is_user_authorized():
            raise HTTPException(
                status_code=401,
                detail="telegram session not authorized"
            )


        result = []


        async for dialog in client.iter_dialogs(limit=200):

            result.append(
                {
                    "id": dialog.id,
                    "name": dialog.name
                }
            )


        return result


    finally:

        await client.disconnect()



# ============================================================
# 添加扫描源
# ============================================================

class SourceCreate(BaseModel):

    account_id: int

    telegram_chat_id: int

    name: str



@router.post("/sources")
def add_source(data: SourceCreate):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO telegram_sources
        (
            account_id,
            telegram_chat_id,
            name,
            enabled
        )
        VALUES
        (?, ?, ?, 1)
        """,
        (
            data.account_id,
            data.telegram_chat_id,
            data.name
        )
    )


    conn.commit()
    conn.close()


    return {
        "status":"ok"
    }
