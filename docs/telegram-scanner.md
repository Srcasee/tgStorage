# Telegram Scanner

## 1. Purpose

The Scanner is a source-scoped Telegram message discovery component.

Its only job is to answer:

> Which valid file resources exist in this explicitly configured Telegram source?

It is not a Telegram dialog crawler and not a download engine.

## 2. Baseline at 7a15c75

`app/telegram/scanner.py` is a compatibility entry point. It imports `TelegramResourceIndexer` from `app.indexer.service`; the active scanning implementation therefore lives in the indexer service. The old dialog-enumerating implementation remains in `scanner_legacy.py` for reference/rollback.

The indexer validates the configured entity with `client.get_entity(source.chat_id)`, then calls `client.iter_messages(source.chat_id, ...)`. This is intentionally source-scoped. Incremental mode uses the source cursor as `min_id`; full mode is explicit and source-scoped. Deleted, empty and non-file messages are ignored.

## 3. Current domain contract

A source is structurally identified by:

```text
(account_id, chat_id)
```

A resource is structurally identified by:

```text
(source_id, telegram_chat_id, telegram_message_id)
```

`telegram_chat_id` is persisted on the Resource deliberately. It is not redundant metadata: it makes the Telegram ownership of a resource auditable and prevents a legacy record from being silently reinterpreted as belonging to a newly rebound source.

`TelegramSource.bound_chat_id` records the chat identity to which the source row was previously bound. If an administrator changes `chat_id`, the scanner invalidates resources from the old binding and resets the incremental cursor before scanning the new chat.

## 4. Required scanner contract

### Input

```text
TelegramSource
  account_id
  chat_id
  bound_chat_id
  chat_type
  enabled
  sync_mode
  last_scanned_message_id
```

### Output

For every valid file message:

```text
Resource
  source_id
  telegram_chat_id = source.chat_id
  telegram_message_id
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

## 5. Channel vs supergroup

Telegram can expose channels and supergroups through entities with identical human-readable titles.

The entity type and stable peer identity are authoritative. The `-100...` prefix alone must never be used to infer channel/group identity because channels can also use `-100...` peer IDs in Telethon.

Therefore:

```text
(title)              -> display metadata
(account_id, chat_id)-> source identity
(entity type)        -> chat type metadata
```

## 6. Incremental scanning

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

The cursor belongs to the source, never to the account globally.

## 7. Full reconciliation

Full mode is an explicit administrative operation for one configured source:

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

It must never mean "scan everything this Telegram account can see".

## 8. Legacy data safety

Rows created before `telegram_chat_id` was persisted do not contain enough trustworthy information to reconstruct their Telegram ownership. Migration must therefore mark them `unavailable` rather than guessing their chat from the current `TelegramSource` row.

A subsequent source-scoped scan creates new resources with the exact chat identity.

This rule is specifically intended to prevent the historical failure where files from a same-title Channel appeared under a Supergroup source.

## 9. Resource validity

Only live file messages with usable media/file metadata and known size enter the active resource set.

Deleted, service-only, media-less, file-less or invalid-size messages must not become active resources.

## 10. Cross-chat deduplication policy

Do not deduplicate across chats because filenames, titles, sizes, MIME types or message IDs match.

Content-hash deduplication may be added later as an optimization, but it must never change resource ownership or source visibility.

## 11. Account isolation

Each Scanner operation must obtain the Telegram client associated with the source's `account_id`.

The client provider/runtime is responsible for session lifecycle and authorization. Scanner must not silently switch to an unrelated account.

## 12. Proxy boundary

Scanner must not know whether Telegram connectivity uses direct networking or a proxy.

```text
Scanner
   |
   v
Telegram client abstraction
   |
   +--> direct
   +--> SOCKS5
   +--> SOCKS4
   +--> HTTP
   +--> future transports
```

Proxy is optional infrastructure and must remain hot-swappable.

## 13. Evolution roadmap

### Phase 1 — Domain contract

- explicit `(account_id, chat_id)` source identity;
- persistent `telegram_chat_id` on Resource;
- source-bound resource uniqueness;
- explicit source rebinding behavior;
- active/unavailable lifecycle;
- account binding.

### Phase 2 — Deterministic Scanner

- incremental scans;
- explicit full reconciliation;
- idempotent rescans;
- deletion handling;
- cursor correctness;
- channel/supergroup isolation;
- same-title source isolation.

### Phase 3 — Real Telegram E2E

Test at minimum:

```text
Account A
  |
  +--> Channel X
  |
  +--> Supergroup Y
```

with same-title, same-filename and same-message-ID cases, repeated cycles, deletion/unavailability and both proxy/direct transport.

### Phase 4 — Performance

Only after identity correctness is stable: batching, safe concurrency, retry/backoff, rate-limit handling and efficient entity resolution.

### Phase 5 — Download acceleration

Keep download optimization outside Scanner:

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
```

## 14. Regression checklist

- [ ] no arbitrary dialog enumeration;
- [ ] only `source.chat_id` is scanned;
- [ ] account binding is preserved;
- [ ] cursor is source-scoped;
- [ ] rescanning is idempotent;
- [ ] resource stores exact Telegram chat ID;
- [ ] source rebinding invalidates old resources;
- [ ] same filename across chats remains separate;
- [ ] same message ID across chats remains separate;
- [ ] legacy chat-less resources are not guessed into a source;
- [ ] unavailable resources are hidden from normal search;
- [ ] proxy choice does not alter scanner semantics;
- [ ] scanner does not download complete files.
