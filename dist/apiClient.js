"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgenticAIClient = void 0;
class AgenticAIClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }
    headers() {
        return {
            "Content-Type": "application/json",
            ...(this.apiKey ? { Authorization: `Bearer ${this.apiKey}` } : {})
        };
    }
    async search(req) {
        const res = await fetch(`${this.baseUrl}/search`, {
            method: "POST",
            headers: this.headers(),
            body: JSON.stringify(req)
        });
        if (!res.ok)
            throw new Error(`Search failed: ${res.status}`);
        return res.json();
    }
    async getProduct(sku) {
        const res = await fetch(`${this.baseUrl}/products/${sku}`, {
            headers: this.headers()
        });
        if (!res.ok)
            throw new Error(`Product fetch failed: ${res.status}`);
        return res.json();
    }
    async getDiagnostics(qid) {
        const res = await fetch(`${this.baseUrl}/diag/${qid}`, {
            headers: this.headers()
        });
        if (!res.ok)
            throw new Error(`Diagnostics fetch failed: ${res.status}`);
        return res.json();
    }
}
exports.AgenticAIClient = AgenticAIClient;
