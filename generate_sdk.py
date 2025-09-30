import os

OPENAPI_FILE = "contracts/openapi.yaml"
OUTPUT_DIR = "sdk/react-native"

def main():
    print("🔄 Using static OpenAPI spec:", OPENAPI_FILE)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Use openapi-generator-cli to build SDK
    print("🚀 Generating React Native SDK...")
    os.system(
        f"npx @openapitools/openapi-generator-cli generate "
        f"-i {OPENAPI_FILE} "
        f"-g javascript "
        f"-o {OUTPUT_DIR}"
    )

    print("✅ React Native SDK generated at", OUTPUT_DIR)

if __name__ == "__main__":
    main()
