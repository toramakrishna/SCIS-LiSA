import type { VisualizationConfig } from '@/types';
import { LineChartViz } from './LineChartViz';
import { BarChartViz } from './BarChartViz';
import { PieChartViz } from './PieChartViz';
import { TableViz } from './TableViz';
import { NetworkGraphViz } from './NetworkGraphViz';

interface ChartRendererProps {
  data: any[];
  config: VisualizationConfig;
}

export function ChartRenderer({ data, config }: ChartRendererProps) {
  // Handle undefined or missing config
  if (!config) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No visualization configuration available
      </div>
    );
  }

  // Handle "empty" visualization type - when query returns no results
  if (config.type === 'empty') {
    return (
      <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-900 text-amber-600 dark:text-amber-400 flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-amber-800 dark:text-amber-300 mb-1">
              No Results Found
            </h3>
            <p className="text-sm text-amber-700 dark:text-amber-400">
              {config.message || 'The query returned no results. Try adjusting your search criteria or check the spelling of names.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Helper function to map database column names to meaningful display names
  const getDisplayColumnName = (key: string): string => {
    const columnMap: Record<string, string> = {
      'title': 'Title',
      'authors': 'Authors',
      'publication_type': 'Type',
      'year': 'Year',
      'venue': 'Venue',
      'journal': 'Journal',
      'booktitle': 'Conference/Book',
      'author_name': 'Author',
      'name': 'Name',
      'h_index': 'H-Index',
      'citation_count': 'Citations',
      'publication_count': 'Publications',
      'is_faculty': 'Faculty Member',
      'affiliation': 'Affiliation',
      'doi': 'DOI',
      'url': 'URL',
      'abstract': 'Abstract',
      'keywords': 'Keywords',
      'count': 'Count',
      'total': 'Total',
    };
    return columnMap[key] || key.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  // Helper function to get color scheme based on publication type
  const getPublicationTypeStyle = (type: string): { 
    bg: string; border: string; text: string; badge: string; badgeBg: string; icon: string 
  } => {
    const typeStyles: Record<string, any> = {
      'journal': {
        bg: 'from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30',
        border: 'border-blue-300 dark:border-blue-700',
        text: 'text-blue-900 dark:text-blue-100',
        badge: 'text-blue-700 dark:text-blue-300',
        badgeBg: 'bg-blue-100 dark:bg-blue-900/50',
        icon: '📄'
      },
      'conference': {
        bg: 'from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30',
        border: 'border-green-300 dark:border-green-700',
        text: 'text-green-900 dark:text-green-100',
        badge: 'text-green-700 dark:text-green-300',
        badgeBg: 'bg-green-100 dark:bg-green-900/50',
        icon: '🎤'
      },
      'book chapter': {
        bg: 'from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30',
        border: 'border-purple-300 dark:border-purple-700',
        text: 'text-purple-900 dark:text-purple-100',
        badge: 'text-purple-700 dark:text-purple-300',
        badgeBg: 'bg-purple-100 dark:bg-purple-900/50',
        icon: '📚'
      },
      'book': {
        bg: 'from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30',
        border: 'border-amber-300 dark:border-amber-700',
        text: 'text-amber-900 dark:text-amber-100',
        badge: 'text-amber-700 dark:text-amber-300',
        badgeBg: 'bg-amber-100 dark:bg-amber-900/50',
        icon: '📖'
      },
      'preprint': {
        bg: 'from-gray-50 to-slate-50 dark:from-gray-950/30 dark:to-slate-950/30',
        border: 'border-gray-300 dark:border-gray-700',
        text: 'text-gray-900 dark:text-gray-100',
        badge: 'text-gray-700 dark:text-gray-300',
        badgeBg: 'bg-gray-100 dark:bg-gray-900/50',
        icon: '📝'
      }
    };
    const lowerType = type?.toLowerCase() || '';
    return typeStyles[lowerType] || typeStyles['journal']; // default to journal style
  };

  // Handle "none" visualization - show data in a nice text format if available
  if (config.type === 'none') {
    // If there's data, show it in a formatted way
    if (data && data.length > 0) {
      return (
        <div className="space-y-4">
          {data.map((row, idx) => {
            // Get publication type for color styling
            const pubType = row.publication_type || row.type || 'journal';
            const style = getPublicationTypeStyle(String(pubType));
            
            return (
              <div 
                key={idx} 
                className={`bg-gradient-to-br ${style.bg} border-2 ${style.border} rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200`}
              >
                {/* Publication Type Badge */}
                {(row.publication_type || row.type) && (
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xl">{style.icon}</span>
                    <span className={`${style.badgeBg} ${style.badge} px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide`}>
                      {String(row.publication_type || row.type)}
                    </span>
                  </div>
                )}
                
                {/* Data Fields */}
                <div className="space-y-2">
                  {Object.entries(row).map(([key, value]) => {
                    // Skip if already shown as badge
                    if (key === 'publication_type' || key === 'type') return null;
                    
                    const displayName = getDisplayColumnName(key);
                    const displayValue = value === null || value === undefined ? 'N/A' : String(value);
                    
                    return (
                      <div key={key} className="flex items-start gap-3">
                        <span className={`text-sm font-bold ${style.text} min-w-[140px] opacity-80`}>
                          {displayName}:
                        </span>
                        <span className={`text-sm ${style.text} font-medium flex-1`}>
                          {displayValue}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      );
    }
    // No data and visualization is "none" - let the explanation be shown
    return null;
  }

  // If no data for other visualization types, don't show anything
  // The natural language explanation will be the main content
  if (!data || data.length === 0) {
    return null;
  }

  switch (config.type) {
    case 'line':
    case 'line_chart':
    case 'multi_line_chart':
      return <LineChartViz data={data} config={config} />;
    
    case 'bar':
    case 'bar_chart':
      return <BarChartViz data={data} config={config} />;
    
    case 'pie':
    case 'pie_chart':
      return <PieChartViz data={data} config={config} />;
    
    case 'table':
      return <TableViz data={data} config={config} />;
    
    case 'network_graph':
      return <NetworkGraphViz data={data} config={config} />;
    
    case 'error':
      return (
        <div className="text-center py-8 text-red-600">
          Error generating visualization
        </div>
      );
    
    default:
      // Fallback to table view
      console.warn('Unknown visualization type:', config.type);
      return <TableViz data={data} config={config} />;
  }
}
