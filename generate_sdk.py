import os
import json
import requests

OPENAPI_URL = "http://localhost:8000/openapi.json"
OUTPUT_DIR = "sdk/react-native"

def main():
    print("🔄 Fetching OpenAPI spec from backend...")
    response = requests.get(OPENAPI_URL)
    spec = response.json()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save OpenAPI spec for reference
    with open(os.path.join(OUTPUT_DIR, "openapi.json"), "w") as f:
        json.dump(spec, f, indent=2)

    # Here we use openapi-generator-cli (installed via npm or docker)
    print("🚀 Generating React Native SDK...")
    os.system(
        f"npx @openapitools/openapi-generator-cli generate "
        f"-i {OUTPUT_DIR}/openapi.json "
        f"-g javascript "
        f"-o {OUTPUT_DIR}"
    )

    print("✅ React Native SDK generated at", OUTPUT_DIR)

if __name__ == "__main__":
    main()
