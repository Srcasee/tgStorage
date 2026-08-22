# Known Bugs

Tracked during code review.

## Review corrections

- CI, pytest and Alembic infrastructure exist.
- Current concern is not absence of infrastructure, but completeness and consistency.

## P0

- ConcurrentChunkStream and ChunkScheduler interface mismatch.
- Telegram client creation path may bypass runtime/network plugin.
- Download acceleration path is not connected as a single production pipeline.

## P1

- Chunk merger lacks integrity validation.
- DownloadManager, DownloadEngine and ChunkScheduler responsibilities are fragmented.
- AccountSelector only checks enabled state and lacks runtime scheduling metrics.
- ResourceResolver is coupled to Telegram location instead of a generic resource location abstraction.
- Network plugin is not fully associated with account/network profiles.
- Core chunk acceleration path lacks regression tests.
- Provider interface still exposes Telegram-specific identifiers and needs backend abstraction.
- merger.py and chunk_merger.py have overlapping responsibilities.

## Download subsystem architecture notes

Current components exist:

- ChunkManager
- ChunkScheduler
- ChunkMerger
- ConcurrentStream
- DownloadEngine
- DownloadRuntime
- AccountSelector
- ResourceResolver
- Provider factory
- Message cache adapter

However, these components do not yet form a stable production pipeline.

Additional findings:

- ChunkManager is a reusable range planning component and should be retained.
- ChunkMerger restores ordering but lacks content integrity verification.
- DownloadRuntime currently acts mainly as a wrapper and needs redesign around DownloadTask lifecycle.
- Provider abstraction is valuable and should remain, but backend selection should be generalized.
- Telegram-specific execution details should move behind backend providers.

Confirmed direction:

- Do not continue incremental patching of the current download subsystem indefinitely.
- Future download v2 should replace the old execution pipeline.
- Keep useful abstractions, but redesign scheduling, worker, account selection and backend boundaries.

## Supplemental review completed

Reviewed:

- tests
- deployment files
- scripts
- requirements
- app/download core modules

Remaining:

- Finish app/download KEEP / REWRITE / DELETE classification.
- Design download v2 architecture.
