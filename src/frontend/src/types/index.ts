// MCP API Types
export interface QueryRequest {
  question: string;
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
  h_index?: number;
  publication_count: number;
  designation?: string;
  email?: string;
  phone?: string;
  research_interests?: string;
  homepage?: string;
  is_faculty?: boolean;
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
