import os

from telethon import TelegramClient

from config import settings, proxy


clients = {}


def sync_sessions():

    from database import get_connection


    session_dir = settings.TG_SESSION_DIR

    if not os.path.exists(session_dir):
        return


    files = os.listdir(session_dir)


    sessions = []

    for f in files:

        if f.endswith(".session"):

            sessions.append(
                f[:-8]
            )


    conn = get_connection()
    cursor = conn.cursor()


    for session in sessions:

        cursor.execute(
            """
            SELECT id
            FROM accounts
            WHERE session=?
            """,
            (
                session,
            )
        )

        row = cursor.fetchone()


        if not row:

            cursor.execute(
                """
                INSERT INTO accounts(
                    name,
                    session,
                    enabled
                )
                VALUES(
                    ?,
                    ?,
                    1
                )
                """,
                (
                    session,
                    session
                )
            )

            print(
                "[ACCOUNT] auto added:",
                session,
                flush=True
            )


    conn.commit()
    conn.close()



def get_clients():

    global clients


    if clients:
        return clients


    sync_sessions()


    session_dir = settings.TG_SESSION_DIR


    if not os.path.exists(session_dir):
        return clients


    for file in os.listdir(session_dir):

        if not file.endswith(".session"):
            continue


        name = file[:-8]


        session = os.path.join(
            session_dir,
            name
        )


        clients[name] = TelegramClient(
            session,
            settings.TG_API_ID,
            settings.TG_API_HASH,
            proxy=proxy
        )


    return clients
    
    
# 兼容旧代码
client = None


def get_default_client():

    global client


    if client:
        return client


    all_clients = get_clients()


    if not all_clients:
        raise RuntimeError(
            "No telegram session found"
        )


    # 默认第一个账号
    client = list(
        all_clients.values()
    )[0]


    return client
    
    

def get_client(account_id: int):

    from database import get_connection


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            session
        FROM accounts
        WHERE id=?
        AND enabled=1
        """,
        (
            account_id,
        )
    )


    row = cursor.fetchone()


    conn.close()


    if not row:

        raise RuntimeError(
            f"Telegram account {account_id} not found"
        )


    session_name = row[0]


    all_clients = get_clients()


    if session_name not in all_clients:

        raise RuntimeError(
            f"Session {session_name} not loaded"
        )


    return all_clients[session_name]