import { SearchRequest, SearchResponse, Product } from "./types";
export declare class AgenticAIClient {
    private baseUrl;
    private apiKey?;
    constructor(baseUrl: string, apiKey?: string);
    private headers;
    search(req: SearchRequest): Promise<SearchResponse>;
    getProduct(sku: string): Promise<Product>;
    getDiagnostics(qid: string): Promise<any>;
}
