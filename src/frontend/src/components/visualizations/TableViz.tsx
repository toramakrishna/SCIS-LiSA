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
        <CardTitle>{title || 'Data Table'}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-auto max-h-96">
          <table className="w-full text-sm border-collapse">
            <thead className="sticky top-0 bg-muted">
              <tr>
                {displayColumns.map((col) => (
                  <th key={col} className="p-2 text-left font-medium border-b">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx} className="border-b hover:bg-accent">
                  {displayColumns.map((col) => (
                    <td key={col} className="p-2">
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
