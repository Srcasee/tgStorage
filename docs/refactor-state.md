# tgStorage Refactor State

> Baseline: `7a15c75` on `architecture-consolidation`.
> Current work continues from this baseline.

## Current product boundary

The core path is:

```text
Telegram source -> Telegram runtime/scanner -> resource recognition/indexer
-> SQLite -> FastAPI API -> Web -> search/download
```

Admin controls which accounts/sources are exposed and how resources are categorized. Preview, playback and sharing are extensions. Proxy is optional infrastructure and must remain replaceable. Download optimization is a separate concern from scanning.

## Current refactor phase

**Phase 1: stabilize Telegram domain identity.**

The first code-level step is to make Telegram resource identity explicit and auditable before further Scanner optimization.

Implemented in the current branch:

- `TelegramSource` declares a unique `(account_id, chat_id)` identity.
- `TelegramSource.bound_chat_id` records the chat a source row is currently bound to.
- `Resource.telegram_chat_id` persists the exact Telegram chat identity.
- Resource uniqueness is expressed as `(source_id, telegram_chat_id, telegram_message_id)`.
- Legacy resources without a trustworthy chat identity are treated as unavailable by migration rather than guessed into the current source chat.
- Rebinding a source invalidates its previous resources and resets the incremental cursor.
- Scanner writes the exact source `chat_id` to every newly indexed resource.
- `is_indexable_message()` is the single small predicate for live file messages.
- Regression coverage verifies identity, chat persistence and source rebinding.

## Why this phase exists

Real Telegram E2E testing previously demonstrated that same-title Channel and Supergroup resources could be mixed, and that legacy records could be incorrectly reused after source changes. The correct fix is not title heuristics. Telegram chat identity must remain structural from Scanner through persistence and download.

## Rules

1. Scanner receives one configured source and never enumerates arbitrary dialogs.
2. Titles, usernames and filenames are metadata, never identity.
3. A Telegram message ID is only meaningful within its chat/source context.
4. Legacy records with unknown chat identity must not be guessed into a new source.
5. User search exposes only active resources.
6. Scanner discovers/indexes; Download streams.
7. Proxy remains an infrastructure adapter.
8. Keep the application modular but monolithic; avoid premature distributed infrastructure.

## Next phase

After Phase 1 passes local regression tests, validate with real Telegram Channel + Supergroup E2E cases, including repeated scans and source rebinding. Only then proceed to Scanner performance and download acceleration.
