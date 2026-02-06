import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface BarChartVizProps {
  data: any[];
  config: {
    title?: string;
    x_axis?: string;
    y_axis?: string;
    columns?: string[];
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

export function BarChartViz({ data, config }: BarChartVizProps) {
  const { title, x_axis, y_axis, columns } = config;

  // Auto-detect x and y axis if not matching
  let xKey = x_axis;
  let yKey = y_axis;

  // If x_axis doesn't exist in data, try to find a text/name column
  if (data.length > 0 && xKey && !(xKey in data[0])) {
    const possibleXKeys = Object.keys(data[0]).filter(key => 
      typeof data[0][key] === 'string' || key.toLowerCase().includes('name')
    );
    if (possibleXKeys.length > 0) {
      xKey = possibleXKeys[0];
    }
  }

  // If y_axis doesn't exist in data, try to find a numeric column
  if (data.length > 0 && yKey && !(yKey in data[0])) {
    const possibleYKeys = Object.keys(data[0]).filter(key => 
      typeof data[0][key] === 'number'
    );
    if (possibleYKeys.length > 0) {
      yKey = possibleYKeys[0];
    }
  }

  // Fallback: use first string column as x, first number column as y
  if (!xKey || !yKey) {
    const keys = Object.keys(data[0]);
    if (!xKey) {
      xKey = keys.find(k => typeof data[0][k] === 'string') || keys[0];
    }
    if (!yKey) {
      yKey = keys.find(k => typeof data[0][k] === 'number') || keys[1] || keys[0];
    }
  }

  return (
    <Card className="border-l-4 border-l-blue-500">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30">
        <CardTitle className="text-sm sm:text-base text-blue-700 dark:text-blue-400">{title || 'Bar Chart'}</CardTitle>
      </CardHeader>
      <CardContent className="pt-4 sm:pt-6 px-2 sm:px-6">
        <ResponsiveContainer width="100%" height={300} className="sm:h-[350px]">
          <BarChart 
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 50 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey={xKey} 
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fill: '#64748b', fontSize: 10 }}
            />
            <YAxis 
              tick={{ fill: '#64748b', fontSize: 10 }}
              width={40}
              label={{ value: yKey, angle: -90, position: 'insideLeft', style: { fill: '#64748b', fontSize: 10 } }}
            />
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
              wrapperStyle={{ paddingTop: '10px', fontSize: '11px' }}
              iconSize={12}
            />
            <Bar 
              dataKey={yKey} 
              fill="#3b82f6"
              radius={[8, 8, 0, 0]}
              maxBarSize={100}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        
        {/* Summary Stats for single data point */}
        {data.length === 1 && (
          <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="text-center">
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Top Result</p>
              <p className="text-2xl font-bold text-blue-700 dark:text-blue-400">{data[0][xKey]}</p>
              <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mt-1">
                {data[0][yKey]} {yKey?.replace(/_/g, ' ')}
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
