# Known Bugs

Tracked during code review.

## P0

- ConcurrentChunkStream and ChunkScheduler interface mismatch.
- Telegram client creation path may bypass runtime/network plugin.
- Multi-account download acceleration is not integrated.
- Account model lacks runtime download scheduling metrics (speed, active tasks, failures).
- Download API bypasses DownloadManager and directly builds Telegram streaming path, preventing the intended multi-account acceleration pipeline.

## P1

- Chunk merger lacks full integrity validation.
- Resource resolver model limits multi-account download.
- Streaming lifecycle needs verification.
- Network plugin is not yet associated with account/network profiles.
- Network quality feedback is missing for dynamic selection.
- Search service currently provides lightweight database filtering only; no full-text index, ranking, or advanced user search strategy.
- Indexer commits resources directly during scan flow; large-scale indexing may need task queues, retry tracking, and scan job persistence.
- API layer contains download assembly responsibilities; DownloadService/DownloadManager boundary should be enforced.
- API contracts need formal documentation for Resource, Download, and Admin DTO stability.

## Models review notes

- TelegramAccount currently stores identity/session/status only; acceleration-related runtime state should remain outside the ORM or be introduced deliberately.
- Resource identity design is correct: source_id + telegram_chat_id + telegram_message_id uniqueness is enforced.
- TelegramSource correctly scopes scanning by account and chat identity.

## Indexer and search review notes

- TelegramResourceIndexer correctly enforces source/chat identity boundaries and maintains incremental scan cursors.
- Resource metadata classification and category resolution are already connected.
- ResourceSearchService supports filename, extension, category, and resource type filtering, but does not yet provide a product-level search experience.

## API review notes

- Resource search API provides the core search-to-frontend path.
- Download API supports HTTP Range requests and partial content delivery.
- Admin API provides account, source, resource category, and network plugin management foundations.
- Admin API still requires verification against the final admin frontend requirements.
