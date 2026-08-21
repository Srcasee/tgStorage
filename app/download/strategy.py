from enum import Enum


class DownloadStrategy(str, Enum):
    STREAM = "stream"
    CONCURRENT = "concurrent"


class DownloadStrategySelector:
    def __init__(self, concurrent_threshold: int = 64 * 1024 * 1024):
        self.concurrent_threshold = concurrent_threshold

    def select(self, file_size: int) -> DownloadStrategy:
        if file_size >= self.concurrent_threshold:
            return DownloadStrategy.CONCURRENT
        return DownloadStrategy.STREAM
