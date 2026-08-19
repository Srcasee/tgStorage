# tgStorage v2 architecture

Phase 0 introduces the new layered architecture.

Layers:
- core: runtime configuration and infrastructure
- models: database entities
- storage: storage backends (Telegram first)
- metadata: resource analysis and classification
- plugins: optional extensions

This directory is introduced without removing v1 code.
