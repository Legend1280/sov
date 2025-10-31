/**
 * APIService - Centralized API handler for Core backend
 * 
 * All API calls to Core should go through this service.
 * Provides:
 * - Unified error handling
 * - Request/response logging
 * - Type-safe API methods
 * - Base URL configuration
 */

const CORE_API_BASE = import.meta.env.VITE_CORE_API_URL || 'http://localhost:8001';
const DEXABOOKS_API_BASE = import.meta.env.VITE_DEXABOOKS_API_URL || 'http://localhost:8002';

export class APIService {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = CORE_API_BASE) {
    this.baseUrl = baseUrl;
  }

  setAuthToken(token: string | null) {
    this.authToken = token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }
    return headers;
  }
  private async fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...(options?.headers || {}),
        },
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`API Error [${url}]:`, error);
      throw error;
    }
  }

  // ==================== Generic HTTP Methods ====================

  async get<T = any>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    return this.fetchJSON<T>(url, { ...options, method: 'GET' });
  }

  async post<T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    return this.fetchJSON<T>(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    return this.fetchJSON<T>(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T = any>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    return this.fetchJSON<T>(url, { ...options, method: 'DELETE' });
  }

  async patch<T = any>(endpoint: string, data?: any, options?: RequestInit): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    return this.fetchJSON<T>(url, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  /**
   * Upload a file to the Core API
   */
  async uploadFile(file: File, endpoint: string = '/api/ingest'): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const headers: HeadersInit = {};
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Upload failed: ${response.statusText}`);
    }

    return await response.json();
  }

  // ==================== Core API ====================
  
  /**
   * Fetch ontology definition for a given object type
   */
  async getOntology(objectType: string): Promise<any> {
    return this.fetchJSON(`${CORE_API_BASE}/api/ontology/${objectType}`);
  }

  /**
   * Fetch provenance data for a given object ID
   */
  async getProvenance(objectId: string): Promise<any> {
    return this.fetchJSON(`${CORE_API_BASE}/api/provenance/${objectId}`);
  }

  /**
   * Fetch object data by ID
   */
  async getObject(objectId: string): Promise<any> {
    return this.fetchJSON(`${CORE_API_BASE}/api/objects/${objectId}`);
  }

  // ==================== DexaBooks API ====================
  
  /**
   * Fetch all transactions
   */
  async getTransactions(): Promise<any> {
    const data = await this.fetchJSON<any>(`${DEXABOOKS_API_BASE}/api/transactions`);
    return data.transactions || data;
  }

  /**
   * Fetch analytics summary
   */
  async getAnalyticsSummary(): Promise<any> {
    const data = await this.fetchJSON<any>(`${DEXABOOKS_API_BASE}/api/analytics/summary`);
    return data.summary || data;
  }

  /**
   * Fetch top expenses
   */
  async getTopExpenses(): Promise<any> {
    const data = await this.fetchJSON<any>(`${DEXABOOKS_API_BASE}/api/analytics/top-expenses`);
    return data.top_expenses || data;
  }

  /**
   * Fetch forecast data
   */
  async getForecast(): Promise<any> {
    return this.fetchJSON(`${DEXABOOKS_API_BASE}/api/forecast`);
  }

  // ==================== Generic Data Fetcher ====================
  
  /**
   * Generic data fetcher for module-defined endpoints
   * Used by ViewportManager to fetch data based on manifest config
   */
  async fetchData(endpoint: string): Promise<any> {
    // Determine base URL based on endpoint prefix
    let baseUrl = CORE_API_BASE;
    if (endpoint.includes('/dexabooks/')) {
      baseUrl = DEXABOOKS_API_BASE;
      endpoint = endpoint.replace('/dexabooks/', '/');
    }
    
    const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
    const data = await this.fetchJSON<any>(url);
    
    // Unwrap common response patterns
    if (data.transactions) return data.transactions;
    if (data.summary) return data.summary;
    if (data.top_categories) return data;
    
    return data;
  }
}

// Export singleton instance
export const apiService = new APIService();
export default apiService;
