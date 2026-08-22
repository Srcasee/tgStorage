# Known Bugs

Tracked during code review.

## P0

- ConcurrentChunkStream and ChunkScheduler interface mismatch.
- Telegram client creation path may bypass runtime/network plugin.
- Multi-account download acceleration is not integrated.

## P1

- Chunk merger lacks full integrity validation.
- Resource resolver model limits multi-account download.
- Streaming lifecycle needs verification.
