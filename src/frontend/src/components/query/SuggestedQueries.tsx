import { Card, CardContent } from '@/components/ui/card';
import { Lightbulb } from 'lucide-react';

interface SuggestedQueriesProps {
  onSelectQuery: (query: string) => void;
}

const exampleQueries = [
  'Show top 10 faculty by publication count',
  'What are the publication trends over the last 5 years?',
  'List the most cited publications',
  'Show collaborations between faculty members',
  'Which venues have the most publications?',
  'Show faculty with h-index greater than 10',
];

export function SuggestedQueries({ onSelectQuery }: SuggestedQueriesProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Lightbulb className="h-4 w-4" />
        <span>Suggested queries to get started:</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {exampleQueries.map((query, index) => (
          <Card
            key={index}
            className="cursor-pointer hover:bg-accent transition-colors"
            onClick={() => onSelectQuery(query)}
          >
            <CardContent className="p-3">
              <p className="text-sm">{query}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
