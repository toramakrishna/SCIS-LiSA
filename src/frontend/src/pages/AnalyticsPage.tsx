import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-yellow-600 bg-clip-text text-transparent">Analytics Dashboard</h1>
        <p className="text-slate-600 dark:text-slate-400 mt-2 font-medium">
          Visualize trends, citations, and research impact
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="border-l-4 border-l-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 hover:shadow-xl transition-shadow">
          <CardHeader>
            <CardTitle className="text-blue-700 dark:text-blue-400">Publication Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center h-64 text-blue-600 dark:text-blue-400 font-medium">
              Chart coming soon...
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30 hover:shadow-xl transition-shadow">
          <CardHeader>
            <CardTitle className="text-purple-700 dark:text-purple-400">Top Authors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center h-64 text-purple-600 dark:text-purple-400 font-medium">
              Chart coming soon...
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
