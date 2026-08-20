#!/bin/sh
set -eu

ACCOUNT_NAME="${1:?用法: ./login-account.sh <session_name>}"
PHONE="${2:?用法: ./login-account.sh <session_name> <phone>}"

SESSION_DIR="${TG_SESSION_DIR:-./data/accounts}"
SESSION_PATH="${SESSION_DIR}/${ACCOUNT_NAME}"

mkdir -p "${SESSION_DIR}"

echo "[LOGIN] account : ${ACCOUNT_NAME}"
echo "[LOGIN] session : ${SESSION_PATH}"
echo "[LOGIN] phone   : ${PHONE}"

docker compose run --rm \
  -e TG_PHONE="${PHONE}" \
  -e TG_SESSION="${SESSION_PATH}" \
  telegram-drive \
  python3 /app/telegram/login.py
