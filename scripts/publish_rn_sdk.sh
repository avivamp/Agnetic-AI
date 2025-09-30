#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/sdk-react-native"

if [ ! -f "$OUT/package.json" ]; then
  echo "SDK not found. Run ./scripts/generate_rn_sdk.sh first."
  exit 1
fi

cd "$OUT"
# Build types (tsc not required for typescript-fetch output, but if you add custom code do: npx tsc)
npm publish --access public
