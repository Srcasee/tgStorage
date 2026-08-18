import asyncio

from urllib.parse import quote

from fastapi import APIRouter, Header, Query
from fastapi.responses import StreamingResponse

from database import get_connection

from telegram.client import get_client
from telegram.downloader import TelegramDownloader
from files.stream_service import VideoStreamService
from common.response import api_success

from fastapi import Response


router = APIRouter(
    prefix="/files",
    tags=["files"]
)



# ============================================================
# 文件列表
# GET /files
# 支持:
# /files?page=1&size=50
# ============================================================


@router.get("")
def list_files(

    page: int = Query(
        1,
        ge=1
    ),

    size: int = Query(
        50,
        ge=1,
        le=200
    )

):


    conn = get_connection()

    cursor = conn.cursor()



    # 总数量

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM files
        WHERE is_available=1
        """
    )

    total = cursor.fetchone()[0]



    offset = (
        page - 1
    ) * size



    cursor.execute(

        """
        SELECT

            id,

            filename,

            size,

            mime_type,

            telegram_chat_id,

            message_id

        FROM files
        
        WHERE is_available=1

        ORDER BY id DESC

        LIMIT ?

        OFFSET ?

        """,

        (

            size,

            offset

        )

    )


    rows = cursor.fetchall()


    conn.close()



    items = []


    for row in rows:

        items.append(

            {

                "id": row[0],

                "filename": row[1],

                "size": row[2],

                "mime_type": row[3],

                "telegram_chat_id": row[4],

                "message_id": row[5]

            }

        )


    return api_success(
        {
            "total": total,
            "page": page,
            "size": size,
            "items": items
        }
    )


# ============================================================
# 文件搜索
# GET /files/search?q=关键词
# ============================================================


@router.get("/search")
def search_files(

    q: str = Query(
        "",
        min_length=1
    )

):


    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT

            id,

            filename,

            size,

            mime_type,

            telegram_chat_id,

            message_id


        FROM files


        WHERE filename LIKE ?


        ORDER BY id DESC


        LIMIT 100


        """,

        (

            f"%{q}%",

        )

    )


    rows = cursor.fetchall()


    conn.close()



    return [

        {

            "id": row[0],

            "filename": row[1],

            "size": row[2],

            "mime_type": row[3],

            "telegram_chat_id": row[4],

            "message_id": row[5]

        }

        for row in rows

    ]




# ============================================================
# 文件下载
# GET /files/{id}/download
# ============================================================



@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    range_header: str | None = Header(default=None, alias="Range")
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            filename,
            telegram_chat_id,
            message_id,
            size,
            mime_type,
            account_id,
            is_available
        FROM files
        WHERE id=?
        """,
        (
            file_id,
        )
    )

    row = cursor.fetchone()

    conn.close()


    if not row:

        return {
            "error": "file not found"
        }


    if row["is_available"] != 1:

        return {
            "error": "file unavailable"
        }


    filename = row["filename"]

    chat_id = row["telegram_chat_id"]

    message_id = row["message_id"]

    file_size = row["size"]

    mime = row["mime_type"] or "application/octet-stream"

    account_id = row["account_id"]


    print(
        "[DOWNLOAD]",
        filename,
        "range:",
        range,
        flush=True
    )


    tg_client = get_client(account_id)

    downloader = TelegramDownloader(
        tg_client
    )


    file_info = await downloader.get_file_info(
        chat_id,
        message_id
    )


    start = 0

    end = file_size - 1


    if range_header:

        range_value = range_header.replace(
            "bytes=",
            ""
        )

        parts = range_value.split("-")


        if parts[0]:

            start = int(parts[0])


        if len(parts) > 1 and parts[1]:

            end = int(parts[1])


    content_length = end - start + 1



    async def stream():

        downloaded = 0


        async for chunk in downloader.stream(
            file_info,
            offset=start
        ):


            if downloaded + len(chunk) > content_length:

                chunk = chunk[
                    :content_length-downloaded
                ]


            downloaded += len(chunk)


            yield chunk


            if downloaded >= content_length:

                break



    headers = {

        "Accept-Ranges":
            "bytes",

        "Content-Disposition":
            f"attachment; filename*=UTF-8''{quote(filename)}"

    }


    if range_header:

        headers.update(

            {

                "Content-Range":
                    f"bytes {start}-{end}/{file_size}",

                "Content-Length":
                    str(content_length)

            }

        )

        status_code = 206


    else:

        headers["Content-Length"] = str(file_size)

        status_code = 200



    return StreamingResponse(

        stream(),

        status_code=status_code,

        media_type=mime,

        headers=headers

    )


@router.head("/{file_id}/download")
async def download_head(
    file_id: int
):


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            size,
            mime_type
        FROM files
        WHERE id=?
        """,
        (
            file_id,
        )
    )


    row = cursor.fetchone()


    conn.close()



    if not row:

        return Response(
            status_code=404
        )



    return Response(

        headers={

            "Accept-Ranges":
                "bytes",

            "Content-Length":
                str(row[0]),

            "Content-Disposition":
                "inline"

        }

    )
    
    
    
# ============================================================
# 视频播放
# 支持:
# - HTTP Range
# - 206 Partial Content
# - 浏览器在线播放
# - 拖动进度条
# ============================================================



@router.get("/{file_id}/stream")
@router.head("/{file_id}/stream")
async def stream_file(
    file_id: int,
    range_header: str | None = Header(None, alias="Range")
):

    print('[RANGE REQUEST]', range_header)



    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            telegram_chat_id,

            message_id,

            filename,

            mime_type,

            size,

            account_id

        FROM files

        WHERE id=?

        """,
        (
            file_id,
        )
    )


    row = cursor.fetchone()


    conn.close()



    if not row:

        return {
            "error": "file not found"
        }



    chat_id = row["telegram_chat_id"]

    message_id = row["message_id"]

    filename = row["filename"]

    mime = row["mime_type"] or "application/octet-stream"

    size = row["size"]

    account_id = row["account_id"]



    tg_client = get_client(account_id)


    downloader = TelegramDownloader(
        tg_client
    )


    file_info = await downloader.get_file_info(
        chat_id,
        message_id
    )



    start = 0

    end = size - 1



    if range_header:


        value = range_header.replace(
            "bytes=",
            ""
        )


        parts = value.split("-")


        if parts[0]:

            start = int(parts[0])


        if len(parts) > 1 and parts[1]:

            end = int(parts[1])



    # ========================================================
    # Video Range Window
    #
    # Keep HTTP range size aligned with cache chunk size.
    # Prevent Range: bytes=0- from exposing the whole file.
    # ========================================================

    from cache.video import CHUNK_SIZE


    if (
        end - start + 1 > CHUNK_SIZE
    ):

        end = min(
            start + CHUNK_SIZE - 1,
            size - 1
        )


    length = end - start + 1



    stream_service = VideoStreamService(
        downloader
    )


    async def generator():

        chunk_size = 4 * 1024 * 1024

        first_chunk = start // chunk_size

        last_chunk = end // chunk_size

        try:

            for index in range(
                first_chunk,
                last_chunk + 1
            ):

                data = await stream_service.get_chunk(
                    file_id,
                    file_info,
                    index
                )

                if not data:
                    break


                chunk_start = index * chunk_size

                chunk_end = chunk_start + len(data) - 1


                offset_start = max(
                    0,
                    start - chunk_start
                )

                offset_end = min(
                    len(data),
                    end - chunk_start + 1
                )


                if offset_start < offset_end:

                    output = data[
                        offset_start:
                        offset_end
                    ]

                    yield output

        except asyncio.CancelledError:

            print(
                "[VIDEO STREAM] client disconnected",
                "file=",
                file_id,
                "range=",
                f"{start}-{end}",
                flush=True
            )

            raise




    headers = {

        "Accept-Ranges":

            "bytes",


        "Content-Length":

            str(length),


        "Content-Disposition":

            "inline",
            
            
        "Content-Type":
            
            mime

    }



    if range_header:

        headers["Content-Range"] = (
            f"bytes {start}-{end}/{size}"
        )



    status = 206 if range_header else 200



    return StreamingResponse(

        generator(),

        status_code=status,

        media_type=mime,

        headers=headers

    )
