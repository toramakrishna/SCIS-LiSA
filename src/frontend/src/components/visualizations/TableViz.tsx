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
                  <th key={col} className="p-1.5 sm:p-2 text-left font-medium border-b whitespace-nowrap">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx} className="border-b hover:bg-accent">
                  {displayColumns.map((col) => (
                    <td key={col} className="p-1.5 sm:p-2">
                      {String(row[col] ?? '')}
                    </td>
                  ))}
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
