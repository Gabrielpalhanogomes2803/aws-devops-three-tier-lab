#!/usr/bin/env bash
set -euo pipefail
# Execute em host com acesso HTTP ao Front-end. Não testa autorização, HA ou TLS público.
BASE_URL="${1:-http://localhost}"
printf 'Checking %s\n' "$BASE_URL"
curl --fail --show-error --silent --max-time 10 "$BASE_URL/api/health"
printf '\n'
curl --fail --show-error --silent --max-time 10 "$BASE_URL/api/tasks?test=1"
printf '\n'
