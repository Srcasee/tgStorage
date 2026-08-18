import asyncio

from dataclasses import dataclass


@dataclass
class TelegramFileInfo:
    chat_id: int
    message_id: int
    filename: str
    size: int | None
    mime_type: str
    media: object


class TelegramDownloader:


    def __init__(
        self,
        client,
        chunk_size=4 * 1024 * 1024
    ):

        self.client = client
        self.chunk_size = chunk_size



    async def get_file_info(
        self,
        chat_id: int,
        message_id: int
    ) -> TelegramFileInfo:


        message = await self.client.get_messages(
            int(chat_id),
            ids=int(message_id)
        )


        if not message:

            raise RuntimeError(
                "telegram message not found"
            )


        if not message.media:

            raise RuntimeError(
                "telegram message has no media"
            )


        filename = None

        try:

            filename = message.file.name

        except Exception:

            pass


        if not filename:

            filename = f"{message_id}.bin"



        size = None

        try:

            size = message.file.size

        except Exception:

            pass



        mime_type = "application/octet-stream"


        try:

            if message.file.mime_type:

                mime_type = message.file.mime_type

        except Exception:

            pass



        return TelegramFileInfo(

            chat_id=int(chat_id),

            message_id=int(message_id),

            filename=filename,

            size=size,

            mime_type=mime_type,

            media=message.media

        )



    async def stream(

        self,

        file_info: TelegramFileInfo,

        offset: int = 0

    ):

        iterator = self.client.iter_download(

            file_info.media,

            offset=offset,

            chunk_size=self.chunk_size,

            request_size=self.chunk_size

        )

        try:

            async for chunk in iterator:

                yield chunk

        except asyncio.CancelledError:

            print(
                "[TELEGRAM STREAM] cancelled",
                "message=",
                file_info.message_id,
                "offset=",
                offset
            )

            raise

        finally:

            close = getattr(
                iterator,
                "aclose",
                None
            )

            if close:

                try:

                    result = close()

                    if hasattr(
                        result,
                        "__await__"
                    ):

                        await result

                except Exception as exc:

                    print(
                        "[TELEGRAM STREAM] close error",
                        repr(exc)
                    )
