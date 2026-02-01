import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function QueryPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Natural Language Query</h1>
        <p className="text-muted-foreground mt-2">
          Ask questions about publications, authors, and research trends
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Query Interface</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            Query interface coming soon...
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
