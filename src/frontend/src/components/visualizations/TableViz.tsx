import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface TableVizProps {
  data: any[];
  config: {
    title?: string;
    columns?: string[];
  };
}

export function TableViz({ data, config }: TableVizProps) {
  const { title, columns } = config;

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

  // Helper function to get badge styling based on publication type
  const getPublicationTypeBadge = (type: string): { bg: string; text: string; icon: string } => {
    const typeStyles: Record<string, any> = {
      'journal': {
        bg: 'bg-blue-100 dark:bg-blue-900/50',
        text: 'text-blue-700 dark:text-blue-300',
        icon: '📄'
      },
      'conference': {
        bg: 'bg-green-100 dark:bg-green-900/50',
        text: 'text-green-700 dark:text-green-300',
        icon: '🎤'
      },
      'book chapter': {
        bg: 'bg-purple-100 dark:bg-purple-900/50',
        text: 'text-purple-700 dark:text-purple-300',
        icon: '📚'
      },
      'book': {
        bg: 'bg-amber-100 dark:bg-amber-900/50',
        text: 'text-amber-700 dark:text-amber-300',
        icon: '📖'
      },
      'preprint': {
        bg: 'bg-gray-100 dark:bg-gray-900/50',
        text: 'text-gray-700 dark:text-gray-300',
        icon: '📝'
      }
    };
    const lowerType = type?.toLowerCase() || '';
    return typeStyles[lowerType] || typeStyles['journal'];
  };

  // Get columns from data if not specified
  const displayColumns = columns || (data.length > 0 ? Object.keys(data[0]) : []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm sm:text-base">{title || 'Data Table'}</CardTitle>
      </CardHeader>
      <CardContent className="px-2 sm:px-6">
        <div className="overflow-x-auto overflow-y-auto max-h-96 -mx-2 sm:mx-0">
          <table className="w-full text-xs sm:text-sm border-collapse min-w-[500px]">
            <thead className="sticky top-0 bg-muted">
              <tr>
                {displayColumns.map((col) => (
                  <th key={col} className="p-1.5 sm:p-2 text-left font-semibold border-b whitespace-nowrap">
                    {getDisplayColumnName(col)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx} className="border-b hover:bg-accent/50 transition-colors">
                  {displayColumns.map((col) => {
                    const value = row[col];
                    
                    // Special rendering for publication_type column with color badges
                    if (col === 'publication_type' || col === 'type') {
                      const style = getPublicationTypeBadge(String(value));
                      return (
                        <td key={col} className="p-1.5 sm:p-2">
                          <span className={`inline-flex items-center gap-1 ${style.bg} ${style.text} px-2 py-1 rounded-full text-xs font-semibold`}>
                            <span>{style.icon}</span>
                            <span>{String(value ?? '')}</span>
                          </span>
                        </td>
                      );
                    }
                    
                    // Default rendering
                    return (
                      <td key={col} className="p-1.5 sm:p-2">
                        {String(value ?? '')}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          {data.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No data to display
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
