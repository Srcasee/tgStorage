import sqlite3
import os


DB_PATH = os.getenv(
    "DATABASE_PATH",
    "/data/files.db"
)


def get_connection():

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "PRAGMA journal_mode=WAL;"
    )

    cursor.execute(
        "PRAGMA busy_timeout=30000;"
    )

    return conn



def init_database():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS files
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT NOT NULL,

            size INTEGER DEFAULT 0,

            mime_type TEXT,

            telegram_chat_id INTEGER NOT NULL,

            message_id INTEGER NOT NULL,

            topic_id INTEGER,

            telegram_file_id TEXT,

            upload_time INTEGER,

            category_id INTEGER,

            created_at INTEGER DEFAULT (strftime('%s','now')),

            last_message_id INTEGER DEFAULT 0,

            account_id INTEGER,

            status TEXT DEFAULT 'active',

            is_available INTEGER DEFAULT 1,

            scan_status TEXT DEFAULT 'idle'
        )
        """
    )


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            session TEXT UNIQUE,

            enabled INTEGER DEFAULT 1
        )
        """
    )


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS telegram_sources
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            telegram_chat_id INTEGER,

            last_message_id INTEGER DEFAULT 0,

            last_scan_time INTEGER,

            scan_interval INTEGER DEFAULT 600,

            sync_mode TEXT DEFAULT 'incremental',

            scan_status TEXT DEFAULT 'idle'
        )
        """
    )


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categories
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE
        )
        """
    )


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS shares
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            file_id INTEGER,

            token TEXT UNIQUE,

            created_at INTEGER DEFAULT (strftime('%s','now'))
        )
        """
    )


    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_file_unique
        ON files(account_id,telegram_chat_id,message_id)
        """
    )


    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_files_account
        ON files(account_id)
        """
    )


    conn.commit()

    conn.close()


    print(
        "[DB] database initialized",
        flush=True
    )
