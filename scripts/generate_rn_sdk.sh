#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
SPEC="$ROOT/contracts/openapi.yaml"
OUT="$ROOT/sdk-react-native"

if ! command -v openapi-generator-cli >/dev/null 2>&1; then
  echo "Please install openapi-generator-cli first: npm i -g @openapitools/openapi-generator-cli"
  exit 1
fi

rm -rf "$OUT"
openapi-generator-cli generate -i "$SPEC" -g typescript-fetch -o "$OUT"

# Add package.json for RN publish/install
cat > "$OUT/package.json" <<'JSON'
{
  "name": "@aeroshop/agentic-ai-sdk",
  "version": "0.1.0",
  "main": "index.js",
  "types": "index.d.ts",
  "private": false,
  "description": "Agentic AI React Native SDK",
  "author": "AeroShop",
  "license": "MIT"
}
JSON

# Re-export a simple client for nicer DX
cat > "$OUT/index.ts" <<'TS'
export * from "./apis";
export * from "./models";
TS

echo "✅ React Native SDK generated at: $OUT"
