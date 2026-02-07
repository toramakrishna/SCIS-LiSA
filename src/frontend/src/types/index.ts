// MCP API Types
export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface QueryRequest {
  question: string;
  model?: string;
  conversation_history?: Message[];
}

export interface QueryResponse {
  question: string;
  sql: string;
  explanation: string;
  note?: string;
  data: any[];
  visualization: VisualizationConfig;
  row_count: number;
  confidence: number;
  suggested_questions?: string[];
}

export interface VisualizationConfig {
  type: 'line_chart' | 'bar_chart' | 'pie_chart' | 'table' | 'network_graph' | 'multi_line_chart' | 'none';
  title: string;
  x_axis?: string;
  y_axis?: string;
  value_field?: string;
  label_field?: string;
  lines?: LineConfig[];
}

export interface LineConfig {
  field: string;
  label: string;
  color?: string;
}

export interface ExampleQuery {
  question: string;
  category: string;
}

// Database Types
export interface Publication {
  id: number;
  title: string;
  year: number;
  venue?: string;
  journal?: string;
  booktitle?: string;
  publication_type?: string;
  type?: string;
  volume?: string;
  number?: string;
  pages?: string;
  publisher?: string;
  editor?: string;
  series?: string;
  doi?: string;
  url?: string;
  ee?: string;
  dblp_key?: string;
  citation_count?: number;
  authors?: string[];  // Array of author names for DBLP format
  is_verified?: boolean | null;  // Verification status
}

export interface Author {
  id: number;
  name: string;
  dblp_pid?: string;
  h_index?: number | null;
  scopus_author_id?: string | null;
  scopus_url?: string | null;
  publication_count: number;
  total_publications?: number;
  designation?: string;
  email?: string;
  phone?: string;
  department?: string;
  research_interests?: string | null;
  homepage?: string | null;
  profile_page?: string | null;
  education?: string | null;
  areas_of_interest?: string | null;
  status?: string | null;
  is_faculty?: boolean;
  dblp_names?: string[];
  dblp_urls?: string[];
  irins_profile?: string | null;
  irins_url?: string | null;
  irins_photo_url?: string | null;
  photo_path?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface Faculty {
  id: number;
  name: string;
  designation: string;
  email?: string;
  publications: number;
  collaborations: number;
  h_index?: number;
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages?: number;
  has_next?: boolean;
  has_prev?: boolean;
}

export type FacultyListResponse = PaginatedResponse<Author>;
export type PublicationListResponse = PaginatedResponse<Publication>;
