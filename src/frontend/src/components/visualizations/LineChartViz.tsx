import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface LineChartVizProps {
  data: any[];
  config: {
    title?: string;
    x_axis?: string;
    y_axis?: string;
    lines?: Array<{ field: string; label: string; color?: string }>;
  };
}

const COLORS = [
  '#3b82f6', // blue
  '#10b981', // emerald
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // violet
  '#ec4899', // pink
];

export function LineChartViz({ data, config }: LineChartVizProps) {
  const { title, x_axis, y_axis, lines } = config;

  // Auto-detect x and y axis if not matching
  let xKey = x_axis;
  let yKey = y_axis;

  if (data.length > 0) {
    const keys = Object.keys(data[0]);
    
    // If x_axis doesn't exist, find first string or year-like column
    if (xKey && !(xKey in data[0])) {
      xKey = keys.find(k => 
        typeof data[0][k] === 'string' || 
        k.toLowerCase().includes('year') ||
        k.toLowerCase().includes('date')
      ) || keys[0];
    }
    
    // If y_axis doesn't exist, find first numeric column
    if (yKey && !(yKey in data[0])) {
      yKey = keys.find(k => typeof data[0][k] === 'number') || keys[1] || keys[0];
    }

    // Fallback defaults
    if (!xKey) xKey = keys[0];
    if (!yKey) yKey = keys.find(k => typeof data[0][k] === 'number') || keys[1];
  }

  // If multiple lines are specified, use them; otherwise use y_axis
  const lineFields = lines || (yKey ? [{ field: yKey, label: yKey }] : []);

  return (
    <Card className="border-l-4 border-l-green-500">
      <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30">
        <CardTitle className="text-green-700 dark:text-green-400">{title || 'Line Chart'}</CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <ResponsiveContainer width="100%" height={350}>
          <LineChart 
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey={xKey} 
              tick={{ fill: '#64748b', fontSize: 12 }}
            />
            <YAxis 
              tick={{ fill: '#64748b', fontSize: 12 }}
              label={{ value: yKey, angle: -90, position: 'insideLeft', style: { fill: '#64748b' } }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            {lineFields.map((line, index) => (
              <Line
                key={line.field}
                type="monotone"
                dataKey={line.field}
                name={line.label}
                stroke={line.color || COLORS[index % COLORS.length]}
                strokeWidth={3}
                dot={{ r: 4, strokeWidth: 2 }}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
