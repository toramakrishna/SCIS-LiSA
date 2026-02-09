/**
 * Example queries for demonstrating different visualization types
 */

export interface ExampleQuery {
  question: string;
  description: string;
  chartType: 'bar' | 'line' | 'pie' | 'table' | 'network' | 'scatter' | 'none';
  category: string;
}

export const EXAMPLE_QUERIES: ExampleQuery[] = [
  {
    question: "Show publication trends over the last 10 years",
    description: "View yearly publication counts as a line chart",
    chartType: "line",
    category: "Trends"
  },
  {
    question: "Who are the top 10 faculty members by publication count?",
    description: "Compare faculty productivity with a bar chart",
    chartType: "bar",
    category: "Faculty"
  },
  {
    question: "What is the distribution of publications by type?",
    description: "See publication types breakdown as a pie chart",
    chartType: "pie",
    category: "Analysis"
  },
  {
    question: "List all publications from 2023",
    description: "View detailed publication data in a table",
    chartType: "table",
    category: "Publications"
  },
  {
    question: "Show collaboration network between faculty members",
    description: "Visualize co-authorship relationships as a network graph",
    chartType: "network",
    category: "Collaboration"
  },
  {
    question: "What are the top conferences where faculty publish?",
    description: "View most popular venues as a bar chart",
    chartType: "bar",
    category: "Venues"
  },
  {
    question: "Show publication counts by faculty member",
    description: "Compare individual faculty productivity",
    chartType: "bar",
    category: "Faculty"
  },
  {
    question: "What is the h-index distribution of faculty?",
    description: "Analyze research impact metrics",
    chartType: "bar",
    category: "Analytics"
  }
];

/**
 * Color schemes for different chart types
 */
export const CHART_TYPE_COLORS: Record<string, string> = {
  bar: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  line: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  pie: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  table: "bg-slate-100 text-slate-700 dark:bg-slate-700/30 dark:text-slate-400",
  network: "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400",
  scatter: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  none: "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400"
};
