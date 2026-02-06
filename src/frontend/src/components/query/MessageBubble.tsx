import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { User, Bot, Code2, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { QueryResponse } from '@/types';
import { ChartRenderer } from '@/components/visualizations/ChartRenderer';
import { SuggestedFollowUps } from './SuggestedFollowUps';

interface MessageBubbleProps {
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  queryResponse?: QueryResponse;
  onFollowUpClick?: (question: string) => void;
}

export function MessageBubble({
  type,
  content,
  timestamp,
  queryResponse,
  onFollowUpClick,
}: MessageBubbleProps) {
  const isUser = type === 'user';
  const [showSQL, setShowSQL] = useState(false);
  const [copied, setCopied] = useState(false);

  const formatSQL = (sql: string): string => {
    // Add line breaks before major SQL keywords for better readability
    return sql
      .replace(/\s+/g, ' ') // Normalize whitespace first
      .replace(/\b(SELECT|FROM|WHERE|JOIN|LEFT JOIN|RIGHT JOIN|INNER JOIN|OUTER JOIN|GROUP BY|ORDER BY|HAVING|LIMIT|OFFSET|UNION|INTERSECT|EXCEPT|WITH|AS)\b/gi, '\n$1')
      .replace(/\bAND\b/gi, '\n  AND')
      .replace(/\bOR\b/gi, '\n  OR')
      .replace(/\bON\b/gi, '\n  ON')
      .trim();
  };

  const handleCopySQL = async () => {
    if (queryResponse?.sql) {
      try {
        await navigator.clipboard.writeText(queryResponse.sql);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy SQL:', err);
      }
    }
  };

  return (
    <div className={cn('flex gap-2 sm:gap-3', isUser && 'flex-row-reverse')}>
      <div
        className={cn(
          'flex h-7 w-7 sm:h-8 sm:w-8 shrink-0 items-center justify-center rounded-full',
          isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'
        )}
      >
        {isUser ? <User className="h-3.5 w-3.5 sm:h-4 sm:w-4" /> : <Bot className="h-3.5 w-3.5 sm:h-4 sm:w-4" />}
      </div>

      <div className={cn('flex-1 space-y-2 min-w-0', isUser && 'flex flex-col items-end')}>
        <Card className={cn(isUser && 'bg-primary text-primary-foreground')}>
          <CardContent className="p-2 sm:p-3">
            <p className="text-xs sm:text-sm whitespace-pre-wrap break-words">{content}</p>
          </CardContent>
        </Card>

        {queryResponse && (
          <div className="space-y-2 w-full">
            {/* Note/Assumptions - Display if present */}
            {queryResponse.note && (
              <div className="p-2 sm:p-3 bg-amber-50 dark:bg-amber-950/30 border-l-4 border-l-amber-500 rounded-lg">
                <div className="flex items-start gap-2">
                  <div className="flex items-center justify-center w-4 h-4 sm:w-5 sm:h-5 rounded-full bg-amber-500 text-white text-xs font-bold flex-shrink-0 mt-0.5">
                    i
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold text-amber-700 dark:text-amber-400 mb-1">Note</p>
                    <p className="text-xs text-amber-600 dark:text-amber-300 break-words">{queryResponse.note}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Visualization - Now appears FIRST */}
            <ChartRenderer 
              data={queryResponse.data} 
              config={queryResponse.visualization} 
            />

            {/* Suggested Follow-up Questions */}
            {queryResponse.suggested_questions && queryResponse.suggested_questions.length > 0 && (
              <SuggestedFollowUps
                questions={queryResponse.suggested_questions}
                onQuestionClick={onFollowUpClick || (() => {})}
              />
            )}

            {/* SQL Query - Collapsible, appears LAST */}
            <div className="border rounded-lg bg-slate-50 dark:bg-slate-900/50">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSQL(!showSQL)}
                className="w-full flex items-center justify-between p-2 sm:p-3 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg"
              >
                <div className="flex items-center gap-1.5 sm:gap-2 min-w-0 flex-1">
                  <Code2 className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-slate-600 dark:text-slate-400 shrink-0" />
                  <span className="text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300">
                    View SQL Query
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400 hidden sm:inline">
                    {queryResponse.row_count} rows {queryResponse.confidence ? `• ${Math.round(queryResponse.confidence * 100)}% confidence` : ''}
                  </span>
                </div>
                {showSQL ? (
                  <ChevronUp className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-slate-600 dark:text-slate-400 shrink-0" />
                ) : (
                  <ChevronDown className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-slate-600 dark:text-slate-400 shrink-0" />
                )}
              </Button>
              
              {showSQL && (
                <div className="px-2 sm:px-3 pb-2 sm:pb-3">
                  <div className="relative">
                    <pre className="text-xs bg-slate-100 dark:bg-slate-800 p-2 sm:p-3 pr-10 sm:pr-12 rounded-md overflow-x-auto border border-slate-200 dark:border-slate-700">
                      <code className="text-slate-800 dark:text-slate-200 whitespace-pre">{queryResponse.sql ? formatSQL(queryResponse.sql) : 'No SQL generated'}</code>
                    </pre>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleCopySQL}
                      className="absolute top-2 right-2 h-8 w-8 p-0 hover:bg-slate-200 dark:hover:bg-slate-700"
                      title={copied ? "Copied!" : "Copy SQL"}
                    >
                      {copied ? (
                        <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
                      ) : (
                        <Copy className="h-4 w-4 text-slate-600 dark:text-slate-400" />
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <span className="text-xs text-muted-foreground px-1">
          {timestamp.toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
}
