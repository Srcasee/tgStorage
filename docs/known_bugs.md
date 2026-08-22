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
- Admin frontend is currently an API validation console rather than a complete management dashboard.
- Admin frontend lacks category management UI for resource classification workflows.
- Admin frontend does not expose Telegram account runtime status, health, or download metrics.

## P2

- Admin frontend authentication flow is incomplete; frontend integration with admin authentication needs verification.

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

## Admin frontend review notes

- Frontend currently covers account creation, source creation, and resource listing validation flows.
- Account update/delete and source update/delete handlers exist in JavaScript but are not represented as complete UI workflows.
- Network plugin management exists at API level but has no complete frontend operations panel.
