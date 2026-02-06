import type { VisualizationConfig } from '@/types';
import { LineChartViz } from './LineChartViz';
import { BarChartViz } from './BarChartViz';
import { PieChartViz } from './PieChartViz';
import { TableViz } from './TableViz';

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

  // Handle "none" visualization - don't show any chart, just let the explanation be shown
  if (config.type === 'none') {
    return null;
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No data to visualize
      </div>
    );
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
      // TODO: Implement network graph with D3.js
      return <TableViz data={data} config={{ ...config, title: config.title + ' (Network Graph - Coming Soon)' }} />;
    
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
