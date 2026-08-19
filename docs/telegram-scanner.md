# Telegram Scanner

## 1. Purpose

The Scanner is a source-scoped Telegram message discovery component.

Its only job is to answer:

> Which valid file resources exist in this explicitly configured Telegram source?

It is not a Telegram dialog crawler and not a download engine.

## 2. Baseline at 7a15c75

`app/telegram/scanner.py` is a compatibility entry point. It imports `TelegramResourceIndexer` from `app.indexer.service`; the active scanning implementation therefore lives in the indexer service. The file documents the intended boundaries and explicitly states that arbitrary historical dialogs must not be enumerated. fileciteturn696file0

The indexer validates the configured entity with `client.get_entity(source.chat_id)`, then calls `client.iter_messages(source.chat_id, ...)`. This is intentionally source-scoped. Incremental mode uses the source cursor as `min_id`; full mode is explicit and source-scoped. Deleted, empty and non-file messages are ignored. fileciteturn697file0

`TelegramSource` stores `account_id`, `chat_id`, `chat_type`, title, sync mode, enabled state and a per-source message cursor. fileciteturn698file0

## 3. Required scanner contract

### Input

```text
TelegramSource
  account_id
  chat_id
  chat_type
  enabled
  sync_mode
  last_scanned_message_id
```

### Output

For every valid file message:

```text
Resource
  source identity
  Telegram chat identity
  Telegram message identity
  file metadata
  recognition metadata
  category
  status=active
```

### Boundary

The Scanner must never expand:

```text
source.chat_id
```

into:

```text
all dialogs visible to account
```

That was one of the most important lessons from the previous E2E failures.

## 4. Channel vs supergroup

Telegram can expose both channels and supergroups through Telethon entities that may have human-readable titles that are identical.

Example conceptual case:

```text
Documents
  channel
  chat_id = X

My Documents
  supergroup
  chat_id = Y
```

Even if two sources have the same title, they are different sources.

For a supergroup, the Telegram ID is commonly represented by a negative `-100...` peer ID. A channel can also have a `-100...` peer ID in Telethon, so **the `-100` prefix alone must never be used to infer channel/group identity**. The entity type and stable peer identity are the authoritative information.

Therefore:

```text
(title)              -> display metadata
(chat_id + account)  -> source identity
(entity type)        -> chat type metadata
```

## 5. Incremental scanning

Default mode should be incremental.

```text
cursor = last_scanned_message_id

iter_messages(source.chat_id, min_id=cursor)
                 |
                 v
          valid file messages
                 |
                 v
          persist/update Resource
                 |
                 v
       cursor = highest observed ID
```

The cursor belongs to the source, not to an account globally.

Never share a cursor between two chats.

## 6. Full reconciliation

Full mode is an explicit administrative operation.

```text
configured source
      |
      v
read complete history of THAT source
      |
      +--> seen valid resources -> active
      |
      +--> previously indexed but absent -> unavailable
```

A full scan must never mean "scan everything this Telegram account can see".

## 7. Resource validity

A Telegram message should be indexed as an active resource only when it has the properties required by the application, including a usable file/media payload and known size.

Messages that are:

- deleted;
- service-only;
- media-less;
- file-less;
- missing usable size;

must not enter the normal active search set.

## 8. Identity and uniqueness

The fundamental identity is source-bound:

```text
(account_id, chat_id, telegram_message_id)
```

or, if `source_id` is itself guaranteed to represent exactly one `(account_id, chat_id)` binding:

```text
(source_id, telegram_message_id)
```

The implementation must not use filename/title as a uniqueness key.

Two different chats can legitimately contain the same filename and message ID.

## 9. Cross-chat deduplication policy

Do **not** deduplicate across chats merely because:

- filenames are equal;
- titles are equal;
- sizes are equal;
- MIME types are equal;
- message IDs happen to match.

Cross-chat content deduplication may become an optional future optimization based on a content hash, but it must never change source ownership or make a resource appear to belong to another chat.

## 10. Deleted/unavailable behavior

Scanner reconciliation should distinguish:

```text
resource exists in DB
        |
        +--> Telegram message still valid -> active
        |
        +--> Telegram message inaccessible/deleted -> unavailable
```

Normal search should filter on `status == active`, as the baseline search service already does. fileciteturn708file0

An unavailable resource may remain in the database for history/reconciliation, but should not be downloadable as if it were active.

## 11. Account isolation

Each Scanner operation must obtain the Telegram client associated with the source's `account_id`.

The database-backed provider selects the enabled account, connects its session through the Telegram runtime, verifies authorization and registers the client in the process-local pool. fileciteturn703file0

A future multi-account implementation must preserve:

```text
Source A -> Account A client
Source B -> Account B client
```

and must never silently fall back to an unrelated account when a source has an explicit account binding.

## 12. Proxy boundary

Scanner must not know whether Telegram connectivity uses direct networking or a proxy.

Preferred dependency direction:

```text
Scanner
   |
   v
Telegram client abstraction
   |
   +--> direct transport
   |
   +--> SOCKS5
   +--> SOCKS4
   +--> HTTP
   +--> future transports
```

Proxy configuration should be hot-swappable at the transport/client layer.

## 13. Scanner evolution roadmap

### Phase 1 — Domain contract

Before changing Scanner again:

- make Telegram source identity explicit;
- make Resource Telegram chat identity persistent;
- make resource identity source-bound;
- define active/unavailable lifecycle;
- preserve account binding.

### Phase 2 — Deterministic scanner

Implement and test:

- incremental source scan;
- explicit full reconciliation;
- deleted message handling;
- cursor advancement;
- idempotent rescans;
- channel/supergroup isolation;
- same-title source isolation.

### Phase 3 — Real Telegram E2E matrix

At minimum test:

```text
Account A
  |
  +--> Channel X
  |      +--> file message
  |
  +--> Supergroup Y
         +--> file message
```

Also test:

- same display title across different chats;
- same filename in different chats;
- same message ID across different chats;
- repeated scanner cycles;
- deleted/unavailable message;
- cursor restart;
- proxy enabled;
- proxy disabled.

### Phase 4 — Performance

Only after correctness is stable:

- batch tuning;
- concurrency where safe;
- retry/backoff;
- rate-limit handling;
- efficient entity resolution.

### Phase 5 — Download acceleration

Scanner remains unchanged while Download evolves independently:

```text
Resource
  |
  v
Download Scheduler
  |
  +--> chunking
  +--> concurrent range reads
  +--> retry
  +--> cache
  +--> account/client selection
```

This separation directly supports the requirement to mitigate Telegram download speed limitations without making Scanner a large subsystem.

## 14. Regression checklist

Before every Scanner refactor, verify:

- [ ] no arbitrary dialog enumeration;
- [ ] source chat is the only scanned chat;
- [ ] source identity does not depend on title;
- [ ] account binding is preserved;
- [ ] cursor is source-scoped;
- [ ] rescanning is idempotent;
- [ ] old resources do not migrate between chats;
- [ ] same filename across chats remains separate;
- [ ] deleted messages are not active;
- [ ] unavailable resources are hidden from normal search;
- [ ] proxy choice does not alter scanner semantics;
- [ ] scanner does not perform file downloads.
