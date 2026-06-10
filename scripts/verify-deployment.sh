#!/usr/bin/env sh
# Usage: ./scripts/verify-deployment.sh https://rednote-api.onrender.com
set -eu

API_BASE="${1:-http://localhost:8000}"

echo "Checking health: ${API_BASE}/health"
curl -fsS "${API_BASE}/health"
echo ""

echo "Creating session..."
curl -fsS -X POST "${API_BASE}/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{"title":"肖申克的救赎","year":1994}'
echo ""

echo "Deployment smoke check passed."
