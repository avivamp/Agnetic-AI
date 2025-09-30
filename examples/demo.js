import { AgenticAIClient } from "../dist";

async function runDemo() {
  const client = new AgenticAIClient("http://localhost:8000", "test-api-key");

  const searchRes = await client.search({ query: "whisky under 200 AED" });
  console.log("Results:", searchRes.results);

  if (searchRes.results.length > 0) {
    const product = await client.getProduct(searchRes.results[0].sku);
    console.log("Product Detail:", product);

    const diag = await client.getDiagnostics(searchRes.diagnostics.qid);
    console.log("Diagnostics:", diag);
  }
}

runDemo();