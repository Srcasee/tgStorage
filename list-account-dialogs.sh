#!/bin/sh
set -eu

ACCOUNT_NAME="${1:?usage: ./list-account-dialogs.sh <account_name>}"

export TG_ACCOUNT_NAME="${ACCOUNT_NAME}"

docker compose run --rm \
  -e TG_ACCOUNT_NAME="${ACCOUNT_NAME}" \
  telegram-drive \
  python3 /app/scripts/list-account-dialogs.py "${ACCOUNT_NAME}"
