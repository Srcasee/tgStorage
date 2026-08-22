# Known Bugs

Tracked during code review.

## Review corrections

- Previous review statements claiming no CI, no pytest foundation, or no migration workflow were incorrect.
- Repository contains GitHub Actions validation, pytest configuration, and Alembic migration infrastructure.
- Remaining concerns are coverage depth, quality gates, and consistency verification.

## P0

- ConcurrentChunkStream and ChunkScheduler interface mismatch.
- Telegram client creation path may bypass runtime/network plugin.
- Multi-account download acceleration is not integrated into the main download path.
- Account model lacks runtime download scheduling metrics (speed, active tasks, failures).
- Download API bypasses DownloadManager and directly builds Telegram streaming path.

## P1

- Chunk merger lacks full integrity validation.
- Resource resolver model limits multi-account download.
- Streaming lifecycle needs verification.
- Network plugin is not yet fully associated with account/network profiles.
- Network quality feedback is missing for dynamic selection.
- Search service provides database filtering but lacks product-level full-text search strategy.
- Large-scale indexing may require task queues, retry tracking, and persistent scan jobs.
- API layer contains download assembly responsibilities; DownloadService/DownloadManager boundary should be enforced.
- API contracts need formal documentation and stability rules.
- Admin frontend is currently closer to an API console than a complete management dashboard.
- Admin frontend lacks complete category management workflow.
- Admin frontend lacks Telegram runtime status and download metrics display.
- SQLite may become a scaling bottleneck for very large TG indexes.
- Deployment proxy runtime integration with NetworkPlugin requires verification.
- CI exists, but needs stronger quality gates such as linting and static checks.
- Regression coverage exists for admin, download contracts, headers, runtime validation, and indexer validation, but core acceleration paths still lack sufficient coverage.

## P2

- Admin frontend authentication integration requires verification.

## Architecture review notes

- TelegramAccount identity/session data should remain separate from runtime scheduling metrics.
- Resource identity design uses source and Telegram message identity boundaries.
- TelegramSource correctly scopes scanning by account and chat identity.
- Resource search API provides the core search-to-frontend path.
- Download API supports HTTP Range delivery.
- Admin API provides account, source, resource, and network management foundations.

## Additional files requiring review

- docker-compose.prod.yml
- docker-entrypoint.sh
- scripts/
- requirements
