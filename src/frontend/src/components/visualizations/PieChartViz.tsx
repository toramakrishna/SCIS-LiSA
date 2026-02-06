import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface PieChartVizProps {
  data: any[];
  config: {
    title?: string;
    label_field?: string;
    value_field?: string;
  };
}

const COLORS = [
  '#3b82f6', // blue
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#10b981', // emerald
  '#f59e0b', // amber
  '#06b6d4', // cyan
  '#ef4444', // red
  '#6366f1', // indigo
];

export function PieChartViz({ data, config }: PieChartVizProps) {
  const { title, label_field, value_field } = config;

  // Auto-detect label and value fields
  let labelKey = label_field;
  let valueKey = value_field;

  if (data.length > 0) {
    const keys = Object.keys(data[0]);
    
    if (!labelKey) {
      labelKey = keys.find(k => typeof data[0][k] === 'string') || keys[0];
    }
    if (!valueKey) {
      valueKey = keys.find(k => typeof data[0][k] === 'number') || keys[1] || keys[0];
    }
  }

  // Transform data for pie chart
  const pieData = data.map((item) => ({
    name: item[labelKey || 'name'],
    value: item[valueKey || 'value'],
  }));

  return (
    <Card className="border-l-4 border-l-purple-500">
      <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30">
        <CardTitle className="text-sm sm:text-base text-purple-700 dark:text-purple-400">{title || 'Pie Chart'}</CardTitle>
      </CardHeader>
      <CardContent className="pt-4 sm:pt-6 px-2 sm:px-6">
        <ResponsiveContainer width="100%" height={300} className="sm:h-[350px]">
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((_entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                fontSize: '12px'
              }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '11px' }}
              iconSize={12}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
