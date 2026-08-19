# tgStorage Architecture

## 1. Product architecture

```text
                         TELEGRAM
                            |
             +--------------+--------------+
             |                             |
       Telegram Account A            Telegram Account B
             |                             |
             +--------------+--------------+
                            |
                            v
                +------------------------+
                | Telegram Client Layer  |
                | Telethon + Transport   |
                +-----------+------------+
                            |
                    explicit source only
                            |
                            v
                +------------------------+
                |      Scanner Layer     |
                | source-scoped discovery|
                | incremental cursor     |
                +-----------+------------+
                            |
                            v
                +------------------------+
                | Recognition / Indexer  |
                | filename/MIME/type/tags|
                | category resolution    |
                +-----------+------------+
                            |
                            v
                +------------------------+
                |       Resource DB      |
                | source + TG identity   |
                | metadata + lifecycle   |
                +-----------+------------+
                            |
                            v
                 +-----------------------+
                 |       FastAPI API      |
                 +-----------+-----------+
                             |
              +--------------+---------------+
              |                              |
              v                              v
      +---------------+              +----------------+
      | User Web UI   |              | Admin Web UI   |
      | Search        |              | Accounts       |
      | Download      |              | Sources        |
      +-------+-------+              | Categories     |
              |                      +----------------+
              v
      +---------------+
      | Download Layer|
      | Range/stream  |
      | Telegram read |
      +---------------+
```

## 2. Layer responsibilities

### Telegram Client Layer

Responsibilities:

- create/reuse Telethon clients per configured account;
- manage session lifecycle;
- authorization checks;
- select direct or proxied transport;
- expose a small client interface to Scanner and Download layers.

Non-responsibilities:

- resource classification;
- user search;
- Web rendering;
- category policy.

### Scanner Layer

Responsibilities:

- scan only administrator-configured sources;
- validate the configured Telegram entity;
- read messages within the source's scan boundary;
- maintain per-source cursor;
- ignore non-resource/service/deleted messages;
- hand valid Telegram messages to the indexer.

Non-responsibilities:

- downloading complete files;
- cross-source deduplication by filename/title;
- arbitrary Telegram dialog discovery;
- Web/API behavior.

### Recognition / Indexer Layer

Responsibilities:

- transform Telegram file metadata into application `Resource` metadata;
- infer extension/resource type/tags;
- resolve categories;
- persist resource lifecycle state.

The analyzer/classifier should remain lightweight. Avoid separate heavy indexing infrastructure until actual scale requires it.

### Resource DB

The resource record is the bridge between Telegram and the application.

Conceptually:

```text
Resource
  account/source identity
  Telegram chat identity
  Telegram message identity
  filename
  extension
  MIME type
  resource type
  tags
  size
  category
  lifecycle status
```

A Telegram message ID without its chat/source identity is not a globally safe identity.

### API Layer

The API is the primary application boundary.

Core API capabilities:

```text
GET /api/v2/resources/search
GET /api/v2/resources/{id}/download
```

Future admin endpoints should be added under the same modular API rather than creating a second service.

### Download Layer

The download path is deliberately separate from Scanner.

```text
Resource ID
   |
   v
Resource Resolver
   |
   v
Telegram account/chat/message
   |
   v
Telegram reader
   |
   +--> Range
   +--> chunking
   +--> retry
   +--> future acceleration/cache
   |
   v
HTTP StreamingResponse
```

This separation is important for requirement #4: Telegram download performance can be optimized without making Scanner complex.

## 3. Proxy architecture

Proxy is an optional transport plugin.

```text
                 Telegram Client Factory
                         |
              +----------+----------+
              |                     |
              v                     v
        Direct Transport      Proxy Transport
                                  |
                    +-------------+-------------+
                    |             |             |
                  SOCKS5        SOCKS4         HTTP
```

The rest of the application should depend on the Telegram client abstraction, not on proxy environment variables.

Future transports can be added without changing Scanner/Indexer/API code.

## 4. Admin architecture

Admin control is policy, not discovery.

```text
Admin Web
   |
   v
Admin API
   |
   +--> Telegram accounts
   +--> Telegram sources
   +--> source enabled/disabled
   +--> sync mode
   +--> categories
   +--> resource visibility
```

The Scanner consumes this policy. It does not invent policy.

## 5. Core identity model

The architectural invariant is:

```text
Telegram account
      +
Telegram chat
      +
Telegram message ID
      |
      v
one source-bound resource identity
```

Human-readable names are metadata only:

```text
chat title     != identity
filename       != identity
username       != identity
```

This is particularly important when a channel and a supergroup have the same visible title.

## 6. Resource lifecycle

```text
Telegram message discovered
          |
          v
       ACTIVE
          |
     message inaccessible
          |
          v
    UNAVAILABLE
          |
   message becomes valid
          |
          v
       ACTIVE
```

`UNAVAILABLE` is a lifecycle state, not a reason to silently expose the record in normal search.

## 7. Storage choice

SQLite remains the default database while the application is small and single-node.

PostgreSQL is a future compatibility target, not a prerequisite for the architecture.

Avoid introducing distributed storage solely for architectural fashion.

## 8. Extension points

These are deliberately outside the initial critical path:

- image preview;
- video playback improvements;
- share links;
- thumbnails;
- favorites;
- richer tags;
- download acceleration/cache;
- PostgreSQL.

They should attach to existing Resource/API/Download boundaries instead of reshaping them.

## 9. Anti-goals

The following are explicitly out of scope for the core architecture unless a concrete requirement appears:

- arbitrary Telegram history archiving;
- automatic scanning of every visible Telegram dialog;
- Telegram chat management platform;
- microservices;
- event streaming infrastructure;
- mandatory proxy;
- mandatory external search engine;
- mandatory object storage;
- media transcoding pipeline.
