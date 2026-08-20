#!/bin/sh
set -eu

ACCOUNT_NAME="${1:?用法: ./scan-telegram-source.sh <account_name>}"
LIMIT="${2:-200}"

echo "[SCAN] account : ${ACCOUNT_NAME}"
echo "[SCAN] limit   : ${LIMIT}"

docker compose run --rm \
  telegram-drive \
  python3 -m app.indexer.worker --account "${ACCOUNT_NAME}" --limit "${LIMIT}"
