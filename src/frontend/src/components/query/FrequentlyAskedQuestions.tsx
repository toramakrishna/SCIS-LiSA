import { Card } from '@/components/ui/card';
import { EXAMPLE_QUERIES, CHART_TYPE_COLORS } from '@/lib/constants/exampleQueries';
import { BarChart3, TrendingUp, PieChart, Table, MessageSquare, Network, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FrequentlyAskedQuestionsProps {
  onSelectQuery: (query: string) => void;
}

const CHART_ICONS = {
  bar: BarChart3,
  line: TrendingUp,
  pie: PieChart,
  table: Table,
  network: Network,
  scatter: Activity,
  none: MessageSquare
};

export function FrequentlyAskedQuestions({ onSelectQuery }: FrequentlyAskedQuestionsProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="text-lg">💡</span>
        <span>Frequently Asked Questions - Explore Different Visualizations</span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {EXAMPLE_QUERIES.map((example, index) => {
          const Icon = CHART_ICONS[example.chartType] || MessageSquare;
          
          return (
            <Card
              key={index}
              onClick={() => onSelectQuery(example.question)}
              className="p-4 cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-[1.02] border-l-4 border-l-transparent hover:border-l-indigo-500 bg-gradient-to-r from-white to-slate-50 dark:from-slate-800 dark:to-slate-800/50"
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 line-clamp-2">
                      {example.question}
                    </h3>
                  </div>
                  {Icon && <Icon className="h-5 w-5 text-slate-400 dark:text-slate-500 shrink-0" />}
                </div>
                
                <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-1">
                  {example.description}
                </p>
                
                <div className="flex items-center gap-2">
                  <span className={cn(
                    'text-xs px-2 py-1 rounded-md font-medium',
                    CHART_TYPE_COLORS[example.chartType]
                  )}>
                    {example.chartType.charAt(0).toUpperCase() + example.chartType.slice(1)} Chart
                  </span>
                  <span className="text-xs px-2 py-1 rounded-md bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300">
                    {example.category}
                  </span>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
