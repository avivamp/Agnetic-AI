import { SearchRequest, SearchResponse, Product } from "./types";

export class AgenticAIClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private headers() {
    return {
      "Content-Type": "application/json",
      ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {})
    };
  }

  async search(req: SearchRequest): Promise<SearchResponse> {
    const res = await fetch(`${this.baseUrl}/search`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(req)
    });
    if (!res.ok) throw new Error(`Search failed: ${res.status}`);
    return res.json();
  }

  async getProduct(sku: string): Promise<Product> {
    const res = await fetch(`${this.baseUrl}/products/${sku}`, {
      headers: this.headers()
    });
    if (!res.ok) throw new Error(`Product fetch failed: ${res.status}`);
    return res.json();
  }

  async getDiagnostics(qid: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/diag/${qid}`, {
      headers: this.headers()
    });
    if (!res.ok) throw new Error(`Diagnostics fetch failed: ${res.status}`);
    return res.json();
  }
}