#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting tgStorage..."
exec "$@"
