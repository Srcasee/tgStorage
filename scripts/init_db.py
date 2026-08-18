import sqlite3
import os


DB_PATH = "/opt/telegram-drive/data/files.db"


os.makedirs("/opt/telegram-drive/data", exist_ok=True)


conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()


# 文件表
cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
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

    created_at INTEGER DEFAULT (strftime('%s','now'))
)
""")


# 分类表
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    parent_id INTEGER DEFAULT 0

)
""")


# 分享链接表
cursor.execute("""
CREATE TABLE IF NOT EXISTS shares (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    file_id INTEGER NOT NULL,

    token TEXT UNIQUE,

    expire_time INTEGER,

    created_at INTEGER DEFAULT (strftime('%s','now'))

)
""")


conn.commit()

conn.close()


print("Database initialized:", DB_PATH)
