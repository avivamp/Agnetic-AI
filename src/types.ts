export interface Product {
  sku: string;
  name: string;
  price: number;
  currency: string;
  thumbnail?: string;
  score?: number;
  description?: string;
}

export interface SearchRequest {
  query: string;
  locale?: string;
  currency?: string;
  filters?: Record<string, any>;
  paging?: { page: number; size: number };
}

export interface SearchResponse {
  results: Product[];
  diagnostics: any;
}