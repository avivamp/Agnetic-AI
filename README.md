# Agentic AI SDK

A lightweight SDK to integrate Agentic AI product search into any shopping app.

## Features
- Search products with natural language queries
- Get product details
- Fetch query diagnostics

## Usage
```ts
import { AgenticAIClient } from "agentic-ai-sdk";

const client = new AgenticAIClient("http://localhost:8000", "your-api-key");

async function run() {
  const res = await client.search({ query: "whisky under 200 AED" });
  console.log(res.results);
}
```
