# Architecture Decisions

## Decision records

This file records important technical decisions.

## ADR-001 Resource identity

A Telegram resource identity must include:

- account identity
- Telegram chat identity
- Telegram message id

Filename alone is not a unique identity.

## ADR-002 Proxy design

Proxy is an optional transport plugin. Core business code must not depend on proxy implementation.

## ADR-003 Download acceleration

Future acceleration should be implemented through Download Manager, account scheduling and workers instead of coupling API directly to Telegram clients.
