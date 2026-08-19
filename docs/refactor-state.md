# tgStorage Refactor State

> Baseline: `7a15c75` on `architecture-consolidation`.
> This document is the context anchor for future refactor work.

## 1. Project positioning

`tgStorage` is a lightweight personal resource system whose primary value is turning Telegram resources into a searchable and downloadable storage catalog.

The canonical product path is:

```text
Telegram Storage Sources
        |
        v
Telegram Client / Scanner
        |
        v
Resource Recognition / Indexer
        |
        v
API
        |
        +------------------+
        |                  |
        v                  v
Web Frontend        Admin Web Backend
        |
        v
Search / Download
```

The system is **not** intended to become a general Telegram management platform, a message archive, or a large distributed storage platform.

## 2. Non-negotiable requirements

1. **Core path:** Telegram source -> API -> resource recognition/indexing -> Web -> user search/download.
2. **Admin control:** administrators control which Telegram accounts/sources are exposed and how resources are categorized.
3. **Proxy:** proxy is optional infrastructure, must remain hot-swappable, and must support multiple network types.
4. **Download performance:** the download path should be optimized independently so Telegram transfer limitations can be mitigated as far as technically/legal/practical constraints allow.

## 3. Baseline architecture at 7a15c75

### Telegram side

- `TelegramAccount` stores configured Telegram accounts/session references.
- `TelegramSource` represents an explicitly configured chat source.
- `TelegramClientRuntime` owns process-local Telethon clients.
- `DatabaseTelegramClientProvider` obtains an enabled account client and verifies authorization.
- `TelegramIndexWorker` periodically scans enabled sources.
- `TelegramResourceIndexer` indexes valid file messages from one configured source.

The active scanner entry point deliberately does not enumerate arbitrary dialogs. `app/telegram/scanner.py` is a compatibility entry point and points to the indexer service; the pre-v2 implementation is preserved in `scanner_legacy.py` for reference/rollback. See `app/telegram/scanner.py` and `app/indexer/service.py`. fileciteturn696file0 fileciteturn697file0

### Resource side

`Resource` is the normalized application-level resource record. At 7a15c75 it contains source/message identity, filename, extension, MIME type, resource type, tags, size, category and status. fileciteturn699file0

The important design rule is that Telegram identity belongs to the resource/source boundary; filename/title is metadata, never identity.

### API/Web side

The FastAPI application mounts the v2 API and serves a minimal Web frontend. The startup lifecycle starts the Telegram index worker only when Telegram credentials are configured. fileciteturn704file0

The v2 router currently exposes resource search and download. fileciteturn705file0

Resource search only returns resources with `status == "active"`, and supports text/category/type filters. fileciteturn706file0 fileciteturn708file0

The download endpoint resolves a Telegram resource, validates the remote message, supports HTTP Range requests, and streams data through a Telegram-backed reader/backend. fileciteturn707file0

The current Web UI is intentionally minimal: search resources and download them. Video preview, image preview and sharing are extension points rather than core requirements. fileciteturn709file0

## 4. Refactor progress

### Completed before this state

- V1.0 established the product concept: Telegram as object-storage backend, multi-account scanning, SQLite indexing, FastAPI download/streaming, Range support and Docker deployment. fileciteturn695file0
- The v2 direction introduced explicit Telegram sources instead of implicit historical dialog discovery.
- Per-source incremental cursor support was introduced.
- Source identity was moved toward `(account_id, chat_id)` instead of chat title.
- Legacy scanner logic was preserved in `scanner_legacy.py`.
- Resource recognition/indexing was separated from API and download code.
- Async Telegram client lifecycle/provider boundaries were introduced.
- Automated tests were added around scanner boundaries and indexing behavior.

### Reverted/abandoned direction

Later experimental changes attempted to solve cross-chat identity and historical resource issues through increasingly complex resource/source rebinding rules. Real Telegram E2E testing exposed incorrect behavior around same-title channel/group cases and cross-chat duplicate resources.

Those changes are intentionally **not** the current baseline.

The project is reset to `7a15c75` as the architectural reference point so the next refactor can be designed from stable boundaries rather than accumulated patches.

## 5. Known baseline limitations

The baseline is not considered feature-complete. In particular:

- Telegram source binding still needs a carefully designed, real-Telegram-validated identity model.
- Resource records need a reliable Telegram chat identity field all the way through persistence, search and download.
- Scanner behavior must be tested against both channels and supergroups with identical/similar titles.
- Deleted/inaccessible Telegram messages must be represented without polluting the active search set.
- Proxy configuration exists as an environment-backed concern but should be formalized as a replaceable transport adapter before more Telegram features are added.
- Download acceleration should be designed after source/resource identity is stable.
- Admin Web functionality is still a future layer; do not prematurely complicate the core API.

## 6. Architecture rules for future work

### Rule A: scanner scope is explicit

A scanner run operates on one configured `TelegramSource`. It must never discover additional chats merely because the authenticated Telegram account can see them.

### Rule B: chat identity is structural

Never identify a Telegram source using `title`, username, display name or other human-readable metadata. The source identity must use stable Telegram/account identifiers.

### Rule C: resource identity is source-bound

A Telegram message ID is only meaningful inside its Telegram chat/source context. Any uniqueness rule must preserve that boundary.

### Rule D: search sees only active resources

Historical/unavailable records may remain for audit/reconciliation, but ordinary user search/download must not expose them.

### Rule E: Scanner does not download

Scanner discovers and indexes. Downloading belongs to the download layer.

### Rule F: proxy is infrastructure

Business logic must not be littered with proxy conditionals. Telegram transport should be selected through a small provider/adapter boundary.

### Rule G: keep the system monolithic and modular

A clean modular FastAPI application is preferred over premature microservices or distributed infrastructure.

Do not add Redis, Kafka, Elasticsearch, Celery, object-storage clusters, CDN infrastructure or similar systems unless an actual requirement demonstrates that SQLite + application services cannot satisfy the need.

## 7. Current milestone

**Milestone: stabilize the domain model before the next Scanner rewrite.**

The immediate objective is not to add features. It is to make the following invariant true:

```text
(account, Telegram chat, Telegram message)
             |
             v
        one Resource
             |
             +--> active/unavailable lifecycle
             +--> searchable metadata
             +--> downloadable Telegram location
```

Only after that invariant is demonstrated with real channel + supergroup E2E tests should Scanner optimization and download acceleration continue.
