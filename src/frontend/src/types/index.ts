// MCP API Types
export interface QueryRequest {
  question: string;
}

export interface QueryResponse {
  question: string;
  sql: string;
  explanation: string;
  data: any[];
  visualization: VisualizationConfig;
  row_count: number;
  confidence: number;
}

export interface VisualizationConfig {
  type: 'line_chart' | 'bar_chart' | 'pie_chart' | 'table' | 'network_graph' | 'multi_line_chart';
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
  venue: string;
  type: string;
  doi?: string;
  url?: string;
  citation_count: number;
}

export interface Author {
  id: number;
  name: string;
  dblp_pid?: string;
  h_index?: number;
  publication_count: number;
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
