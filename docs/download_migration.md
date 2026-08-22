# Download Migration Plan

## Naming decision

The rewritten subsystem keeps the existing module name:

```
app/download
```

No `download_v2` directory will be introduced.

The old execution chain will be replaced in place.

## Migration phases

### Phase 1: Remove obsolete execution implementations

Delete:

- `manager.py`
- `merger.py`
- `concurrent_stream.py`

Reason:

- no stable external dependency found;
- responsibilities will be replaced by DownloadService, Scheduler and Assembler.

### Phase 2: Replace execution core

Rewrite:

- `download_engine.py`
- `download_runtime.py`
- `chunk_scheduler.py`
- `account_selector.py`

Target responsibilities:

```
DownloadService
    |
DownloadTask
    |
Execution Runtime
    |
Scheduler
    |
Backend Provider
```

## Network boundary

All Telegram accounts share the same network policy.

```
System Network Plugin
        |
Telegram Runtime
        |
All Telegram Accounts
```

No account-level proxy binding is designed.

## Preserve

Keep and evolve:

- chunk.py
- range.py
- chunk_manager.py
- providers.py
- resource_resolver.py
- factory.py
- cache related adapters

## Safety rule

Delete old execution files only after replacement interfaces are available.
