import os
import asyncio


from urllib.parse import quote

from telethon import TelegramClient

from fastapi import FastAPI

from fastapi.responses import StreamingResponse

from files.api import router as files_router

from telegram.client import get_default_client

from telegram.scanner import scanner_loop

from fastapi.responses import FileResponse

from telegram.client import get_clients

from database import get_connection

# ============================================================
# Scanner
# 后台文件扫描任务
# 注意:
# 不创建 TelegramClient
# 使用下面唯一 client
# 防止 session sqlite lock
# ============================================================

from telegram.scanner import scan_dialogs


# ============================================================
# 环境变量读取
# ============================================================
# ============================================================
# Telegram API
# ============================================================

TG_API_ID = int(

    os.getenv(

        "TG_API_ID",

        "0"

    )

)



TG_API_HASH = os.getenv(

    "TG_API_HASH"

)





# Telegram账号
#
# 仅用于首次 login.py 登录
#
# 生产模式不会调用验证码


TG_PHONE = os.getenv(

    "TG_PHONE"

)





# ============================================================
# Session配置
# ============================================================



# Session存储路径
#
# 使用/data目录
#
# 对应docker:
#
# ./data:/data
#
# 容器删除不会丢失登录状态


TG_SESSION = os.getenv(

    "TG_SESSION",

    "/data/telegram_session"

)







# ============================================================
# Telegram代理配置
# ============================================================



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







# ============================================================
# Telegram连接参数
# ============================================================



TG_CONNECT_TIMEOUT = int(

    os.getenv(

        "TG_CONNECT_TIMEOUT",

        "60"

    )

)







# ============================================================
# 下载参数
# ============================================================



DOWNLOAD_CHUNK_SIZE = int(

    os.getenv(

        "DOWNLOAD_CHUNK_SIZE",

        "1048576"

    )

)








# ============================================================
# 创建Telegram Client
#
# 全项目唯一实例
#
# scanner
# downloader
# API
#
# 全部共享这个client
#
# ============================================================




proxy = None





if ENABLE_PROXY:



    proxy = {


        "proxy_type": PROXY_TYPE,


        "addr": PROXY_HOST,


        "port": PROXY_PORT,


        "rdns": True

    }





    print(

        "[TG] Proxy enabled:",

        PROXY_HOST,

        PROXY_PORT,

        flush=True

    )





else:



    print(

        "[TG] Proxy disabled",

        flush=True

    )




# ============================================================
# FastAPI
# ============================================================



app = FastAPI()

app.include_router(
    files_router
)




# ============================================================
# 后台任务
#
# scanner_task:
#
# 保存后台扫描协程
#
# shutdown 时取消
#
# ============================================================

scanner_task = None




# ============================================================
# 首页
# ============================================================



@app.get("/")
async def home():

    return FileResponse(
        "/app/web/index.html"
    )
    
    
@app.get("/web")
async def web():

    return FileResponse(
        "/app/web/index.html"
    )
    
    
# ============================================================
# 下载接口
# ============================================================





# ============================================================
# Startup
# 生产模式：
# 1.连接Telegram
# 2.读取已有session
# 3.验证授权
# 4.启动后台扫描任务
# 不发送验证码
# ============================================================

@app.on_event("startup")
async def startup():

    global scanner_task

    print(
        "正在连接 Telegram...",
        flush=True
    )

    # ========================================================
    # 获取所有 Telegram 账号
    # ========================================================

    from telegram.client import get_clients

    clients = get_clients()

    if not clients:

        raise RuntimeError(
            "No Telegram sessions found"
        )

    # ========================================================
    # 连接并验证所有账号
    # ========================================================

    for name, tg_client in clients.items():

        print(
            f"[TG] connecting: {name}",
            flush=True
        )

        await tg_client.connect()

        authorized = await tg_client.is_user_authorized()

        if not authorized:

            print(
                f"[TG] session not authorized: {name}",
                flush=True
            )

            await tg_client.disconnect()

            continue

        me = await tg_client.get_me()

        print(
            f"[TG] authorized: "
            f"{name} / "
            f"{me.username or me.first_name or me.id}",
            flush=True
        )

    # ========================================================
    # 后台扫描
    # ========================================================

    async def run_scanners():

        tasks = []

        for name, tg_client in clients.items():
            
            conn = get_connection()

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id
                FROM accounts
                WHERE session=?
                """,
                (
                    name,
                )
            )

            row = cursor.fetchone()

            conn.close()

            if not row:

                print(
                    f"[SCAN] account not found: {name}",
                    flush=True
                )

                continue

            account_id = row[0]
            
            print(
                f"[SCAN] bind account: {name} -> {account_id}",
                flush=True
            )

            if not tg_client.is_connected():

                continue

            if not await tg_client.is_user_authorized():

                continue

            async def run_one(
                account_id,
                account_name,
                account_client
            ):

                try:

                    print(
                        f"[SCAN] starting: {account_name}",
                        flush=True
                    )

                    await scanner_loop(
                        account_client,
                        account_id
                    )

                except asyncio.CancelledError:

                    raise

                except Exception as e:

                    print(
                        f"[SCAN] "
                        f"{account_name} crashed:",
                        repr(e),
                        flush=True
                    )

            tasks.append(
                asyncio.create_task(
                    run_one(
                        account_id,
                        name,
                        tg_client
                    )
                )
            )

        if tasks:

            await asyncio.gather(
                *tasks
            )

    scanner_task = asyncio.create_task(
        run_scanners()
    )

    print(
        "[SCAN] background scanner started",
        flush=True
    )



    
    
# ============================================================
# Shutdown
#
# 停止后台任务
# 关闭Telegram连接
#
# ============================================================



@app.on_event("shutdown")

async def shutdown():


    global scanner_task




    print(

        "Telegram关闭",

        flush=True

    )





    # ========================================================
    # 停止扫描任务
    # ========================================================


    if scanner_task:


        scanner_task.cancel()



        try:


            await scanner_task



        except asyncio.CancelledError:


            pass






    # ========================================================
    # 关闭Telegram连接
    # ========================================================



    clients = get_clients()

    for name, tg_client in clients.items():

        if tg_client.is_connected():

            await tg_client.disconnect()

            print(
                f"[TG] disconnected: {name}",
                flush=True
            )