#!/bin/sh
set -eu

ACCOUNT_NAME="${1:?用法: ./sync-telegram-sources.sh <account_name>}"

docker compose run --rm \
  -e TG_ACCOUNT_NAME="${ACCOUNT_NAME}" \
  telegram-drive \
  python3 scripts/sync_telegram_sources.py "${ACCOUNT_NAME}"
