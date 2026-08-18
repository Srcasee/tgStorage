import asyncio

from cache.video import VideoCache, CHUNK_SIZE


# 一个 (file_id, chunk_index) 只允许存在一个共享的缓存填充任务。
#
# 浏览器播放 MP4 时会同时产生多个 Range 请求，而且 Chrome 会主动
# 取消旧 Range、重新发起新的 Range。
#
# 因此 Telegram chunk 下载不能绑定某一个 HTTP 请求的生命周期。
_CHUNK_TASKS = {}

_CHUNK_TASKS_LOCK = asyncio.Lock()


# 后台预取任务
#
# 防止同一个 file/chunk 被重复预取
_PREFETCH_TASKS = set()


# 限制同时进行的 Telegram chunk 下载数量，避免浏览器一次发出大量
# Range 请求时，同时建立几十个 Telegram 下载。
_DOWNLOAD_SEMAPHORE = asyncio.Semaphore(4)


class VideoStreamService:

    def __init__(
        self,
        downloader
    ):
        self.downloader = downloader
        self.cache = VideoCache()


    async def _fill_chunk(
        self,
        file_id,
        file_info,
        chunk_index
    ):

        async with _DOWNLOAD_SEMAPHORE:

            # 等待下载槽期间，其他请求可能已经把 chunk 写入缓存。
            cached = self.cache.read(
                file_id,
                chunk_index
            )

            if cached:
                return cached


            offset = (
                chunk_index
                *
                CHUNK_SIZE
            )


            data = bytearray()


            try:

                async for chunk in self.downloader.stream(
                    file_info,
                    offset=offset
                ):

                    remain = (
                        CHUNK_SIZE
                        -
                        len(data)
                    )


                    if remain <= 0:

                        break


                    data.extend(
                        chunk[:remain]
                    )


                    if len(data) >= CHUNK_SIZE:

                        break


            except asyncio.CancelledError:

                print(
                    "[VIDEO CACHE TASK] cancelled",
                    file_id,
                    chunk_index,
                    flush=True
                )

                raise


            result = bytes(data)


            print(
                "[VIDEO CACHE]",
                "file=",
                file_id,
                "chunk=",
                chunk_index,
                "size=",
                len(result),
                flush=True
            )


            if result:

                self.cache.write(
                    file_id,
                    chunk_index,
                    result
                )


                print(
                    "[VIDEO CACHE WRITE]",
                    file_id,
                    chunk_index,
                    len(result),
                    flush=True
                )


            return result


    async def _get_or_create_task(
        self,
        file_id,
        file_info,
        chunk_index
    ):

        key = (
            file_id,
            chunk_index
        )


        async with _CHUNK_TASKS_LOCK:

            task = _CHUNK_TASKS.get(
                key
            )


            if (
                task is None
                or task.done()
            ):

                task = asyncio.create_task(
                    self._fill_chunk(
                        file_id,
                        file_info,
                        chunk_index
                    )
                )


                _CHUNK_TASKS[key] = task


                def cleanup(
                    done_task,
                    task_key=key
                ):

                    current = _CHUNK_TASKS.get(
                        task_key
                    )


                    if current is done_task:

                        _CHUNK_TASKS.pop(
                            task_key,
                            None
                        )


                task.add_done_callback(
                    cleanup
                )


            return task


    async def _prefetch_chunks(
        self,
        file_id,
        file_info,
        chunk_index
    ):

        for index in (
            chunk_index + 1,
            chunk_index + 2
        ):

            key = (
                file_id,
                index
            )


            if key in _PREFETCH_TASKS:
                continue


            if self.cache.exists(
                file_id,
                index
            ):
                continue


            _PREFETCH_TASKS.add(
                key
            )


            async def run(
                idx=index,
                task_key=key
            ):

                try:

                    await self.get_chunk(
                        file_id,
                        file_info,
                        idx
                    )

                finally:

                    _PREFETCH_TASKS.discard(
                        task_key
                    )


            asyncio.create_task(
                run()
            )



    async def get_chunk(
        self,
        file_id,
        file_info,
        chunk_index
    ):

        cached = self.cache.read(
            file_id,
            chunk_index
        )


        if cached:

            return cached


        task = await self._get_or_create_task(
            file_id,
            file_info,
            chunk_index
        )


        # 非常关键：
        #
        # HTTP Range 请求被 Chrome 取消时，只取消当前 HTTP 请求的等待，
        # 不取消共享的 Telegram chunk 下载任务。
        #
        # 这样后续 Range 请求可以直接复用正在进行的下载任务，完成后
        # 写入 VideoCache。
        result = await asyncio.shield(
            task
        )


        asyncio.create_task(
            self._prefetch_chunks(
                file_id,
                file_info,
                chunk_index
            )
        )


        return result
