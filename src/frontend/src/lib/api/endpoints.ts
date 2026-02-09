import axios from 'axios';
import type { QueryRequest, QueryResponse, Faculty, Publication, PaginatedResponse } from '@/types';

// Create axios instance with base configuration
// Always use relative URLs - Vite proxy will handle forwarding to the backend
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds - increased for LLM query processing
});

// Add request interceptor to ensure trailing slashes
// This prevents 307 redirects that cause CORS issues in Codespaces
api.interceptors.request.use((config) => {
  // Add trailing slash only to root collection endpoints (e.g., /faculty, /publications)
  // Don't add to paths with sub-resources (e.g., /faculty/123, /analytics/overview)
  if (config.url && !config.url.endsWith('/')) {
    // Split off query string to analyze path only
    const urlPath = config.url.split('?')[0];
    
    // Check if it's a root collection endpoint (single path segment)
    // e.g., /faculty YES, /faculty/123 NO, /analytics/overview NO
    const isRootCollection = /^\/[^/]+$/.test(urlPath);
    
    if (isRootCollection) {
      config.url += '/';
    }
  }
  return config;
});

// MCP Analytics API
export const mcpAPI = {
  // Natural language query
  query: async (
    question: string, 
    conversationHistory?: Array<{role: string; content: string}>,
    isPredefinedQuery: boolean = false
  ): Promise<QueryResponse> => {
    const payload: QueryRequest = { 
      question,
      conversation_history: conversationHistory,
      is_predefined_query: isPredefinedQuery
    };
    const response = await api.post<QueryResponse>('/mcp/query', payload);
    return response.data;
  },

  // Faculty endpoints
  faculty: {
    list: async (params?: {
      page?: number;
      page_size?: number;
      designation?: string;
      sort_by?: string;
    }): Promise<PaginatedResponse<Faculty>> => {
      const response = await api.get<PaginatedResponse<Faculty>>('/faculty', { params });
      return response.data;
    },

    get: async (id: number): Promise<Faculty> => {
      const response = await api.get<Faculty>(`/faculty/${id}`);
      return response.data;
    },

    publications: async (id: number, params?: {
      page?: number;
      page_size?: number;
      year?: number;
      publication_type?: string;
    }): Promise<PaginatedResponse<Publication>> => {
      const response = await api.get<PaginatedResponse<Publication>>(
        `/faculty/${id}/publications`,
        { params }
      );
      return response.data;
    },

    stats: async (id: number) => {
      const response = await api.get(`/faculty/${id}/stats`);
      return response.data;
    },
  },

  // Analytics endpoints
  analytics: {
    stats: async () => {
      const response = await api.get('/analytics/overview');
      return response.data;
    },

    yearlyTrends: async (params?: {
      start_year?: number;
      end_year?: number;
    }) => {
      const response = await api.get('/analytics/yearly-trends', { params });
      return response.data;
    },

    topAuthors: async (params?: {
      limit?: number;
      faculty_only?: boolean;
    }) => {
      const response = await api.get('/analytics/top-authors', { params });
      return response.data;
    },

    topVenues: async (params?: { limit?: number }) => {
      const response = await api.get('/analytics/top-venues', { params });
      return response.data;
    },

    collaborationNetwork: async (params?: {
      faculty_id?: number;
      min_publications?: number;
    }) => {
      const response = await api.get('/analytics/collaboration-network', { params });
      return response.data;
    },
  },

  // Publications endpoints
  publications: {
    list: async (params?: {
      page?: number;
      page_size?: number;
      year?: number;
      publication_type?: string;
      search?: string;
    }): Promise<PaginatedResponse<Publication>> => {
      const response = await api.get<PaginatedResponse<Publication>>('/publications', { params });
      return response.data;
    },

    get: async (id: number): Promise<Publication> => {
      const response = await api.get<Publication>(`/publications/${id}`);
      return response.data;
    },

    search: async (query: string, params?: {
      page?: number;
      page_size?: number;
    }): Promise<PaginatedResponse<Publication>> => {
      const response = await api.get<PaginatedResponse<Publication>>('/publications/search', {
        params: { q: query, ...params },
      });
      return response.data;
    },
  },

  // Authors endpoints
  authors: {
    list: async (params?: {
      page?: number;
      page_size?: number;
      search?: string;
      faculty_only?: boolean;
    }) => {
      const response = await api.get('/authors', { params });
      return response.data;
    },

    get: async (id: number) => {
      const response = await api.get(`/authors/${id}`);
      return response.data;
    },

    publications: async (id: number, params?: {
      page?: number;
      page_size?: number;
    }) => {
      const response = await api.get(`/authors/${id}/publications`, { params });
      return response.data;
    },
  },

  // Venues endpoints
  venues: {
    list: async (params?: {
      page?: number;
      page_size?: number;
      venue_type?: string;
    }) => {
      const response = await api.get('/venues', { params });
      return response.data;
    },

    get: async (id: number) => {
      const response = await api.get(`/venues/${id}`);
      return response.data;
    },

    publications: async (id: number, params?: {
      page?: number;
      page_size?: number;
    }) => {
      const response = await api.get(`/venues/${id}/publications`, { params });
      return response.data;
    },
  },
};

// Export axios instance for direct use if needed
export { api };
