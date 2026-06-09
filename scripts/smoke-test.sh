#!/usr/bin/env bash
set -euo pipefail

API_URL="${1:-${NEXT_PUBLIC_API_URL:-http://localhost:8000}}"
API_URL="${API_URL%/}"

echo "Checking ${API_URL}/api/health"
curl -fsS "${API_URL}/api/health"
echo

echo "Checking ${API_URL}/api/smoke"
curl -fsS "${API_URL}/api/smoke"
echo

echo "Smoke tests passed."
