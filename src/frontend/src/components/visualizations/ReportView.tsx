import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, FileText } from 'lucide-react';
import { useState } from 'react';

interface ReportViewProps {
  data: Record<string, unknown>[];
  config: {
    title: string;
    type: string;
  };
  reportFormat?: string;
}

export function ReportView({ data, config, reportFormat }: ReportViewProps) {
  const [copied, setCopied] = useState(false);

  // Format data as text report
  const formatAsReport = (): string => {
    // Safe check for data availability
    if (!data || !Array.isArray(data) || data.length === 0) {
      return 'No data available for report.';
    }

    const title = config?.title || 'Report';
    let report = `${title}\n`;
    report += '='.repeat(title.length) + '\n\n';

    // If custom report_format is provided, use it
    if (reportFormat) {
      data.forEach((item, index) => {
        report += `${index + 1}. `;
        let formatted = reportFormat;
        // Replace {{field}} placeholders with actual values
        Object.keys(item).forEach(key => {
          const value = item[key] ?? '';
          formatted = formatted.replace(new RegExp(`\\{\\{${key}\\}\\}`, 'g'), String(value));
        });
        report += formatted + '\n\n';
      });
    } else {
      // Default formatting: show all fields in paragraph style
      data.forEach((item, index) => {
        report += `${index + 1}. `;
        const entries = Object.entries(item);
        
        entries.forEach(([key, value], idx) => {
          const formattedKey = key
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
          
          if (idx === 0) {
            // First field (usually title) on same line as number
            report += `${value}\n`;
          } else {
            // Other fields indented
            report += `   ${formattedKey}: ${value ?? 'N/A'}\n`;
          }
        });
        
        report += '\n'; // Extra line between records
      });
    }

    report += `\n---\nTotal Records: ${data.length}\n`;
    report += `Generated: ${new Date().toLocaleString()}\n`;

    return report;
  };

  const downloadReport = () => {
    const reportText = formatAsReport();
    const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report_${new Date().getTime()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = async () => {
    const reportText = formatAsReport();
    try {
      await navigator.clipboard.writeText(reportText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Early return if no data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <Card className="shadow-md border-2 border-amber-200 dark:border-amber-800">
        <CardContent className="p-6">
          <p className="text-center text-amber-700 dark:text-amber-300">
            No data available for report.
          </p>
        </CardContent>
      </Card>
    );
  }

  const reportText = formatAsReport();

  return (
    <Card className="shadow-md border-2 border-emerald-200 dark:border-emerald-800">
      <CardHeader className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/40 border-b">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
            <CardTitle className="text-lg font-bold text-emerald-900 dark:text-emerald-100">
              {config?.title || 'Report'}
            </CardTitle>
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={copyToClipboard}
              className="bg-white dark:bg-slate-800"
            >
              {copied ? '✓ Copied' : 'Copy'}
            </Button>
            <Button
              size="sm"
              onClick={downloadReport}
              className="bg-emerald-600 hover:bg-emerald-700 text-white"
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
          <pre className="text-sm font-mono whitespace-pre-wrap break-words text-slate-800 dark:text-slate-200">
            {reportText}
          </pre>
        </div>
        <div className="mt-4 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
          <FileText className="h-3 w-3" />
          <span>Report format - Ready to download or copy for official documentation</span>
        </div>
      </CardContent>
    </Card>
  );
}
