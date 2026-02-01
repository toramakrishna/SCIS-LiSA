import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { QueryInput } from '@/components/query/QueryInput';
import { SuggestedQueries } from '@/components/query/SuggestedQueries';
import { FrequentlyAskedQuestions } from '@/components/query/FrequentlyAskedQuestions';
import { MessageBubble } from '@/components/query/MessageBubble';
import { useQueryStore } from '@/lib/stores/useQueryStore';
import { mcpAPI } from '@/lib/api/endpoints';
import { Trash2, AlertCircle, Loader2 } from 'lucide-react';
import { useEffect, useRef } from 'react';

export function QueryPage() {
  const {
    messages,
    isLoading,
    error,
    addUserMessage,
    addAssistantMessage,
    setLoading,
    setError,
    clearMessages,
  } = useQueryStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleQuery = async (query: string) => {
    try {
      // Clear error and set loading state BEFORE adding message
      setError(null);
      setLoading(true);
      
      // Add user message
      addUserMessage(query);

      // Call MCP API
      const response = await mcpAPI.query(query);
      
      // Add assistant response (this will set isLoading to false)
      addAssistantMessage(response.data);
    } catch (err: any) {
      console.error('Query error:', err);
      let errorMessage = 'Failed to process query';
      
      if (err.response) {
        // Server responded with error status
        errorMessage = `Server error (${err.response.status}): ${err.response.data?.detail || err.response.statusText}`;
      } else if (err.request) {
        // Request made but no response
        errorMessage = 'Cannot connect to backend server. Make sure the backend is running at http://localhost:8000';
      } else {
        // Error in request configuration
        errorMessage = err.message || 'Unknown error occurred';
      }
      
      // setError will automatically set isLoading to false
      setError(errorMessage);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">Natural Language Query</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2 font-medium">
            Ask questions about publications, authors, and research trends
          </p>
        </div>
        {messages.length > 0 && (
          <Button size="sm" onClick={clearMessages} className="bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white shadow-md">
            <Trash2 className="h-4 w-4 mr-2" />
            Clear History
          </Button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-l-4 border-l-red-500 bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-950/30 dark:to-pink-950/30">
          <CardContent className="p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-700 dark:text-red-400">Error</p>
              <p className="text-sm text-red-600 dark:text-red-300">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Frequently Asked Questions - Show only when no messages */}
      {messages.length === 0 && (
        <Card className="border-l-4 border-l-purple-500 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30">
          <CardHeader>
            <CardTitle className="text-purple-700 dark:text-purple-400">Frequently Asked Questions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="text-center py-4">
                <p className="text-purple-600 dark:text-purple-400 font-medium text-lg">
                  Start by asking a question or try one of the examples below
                </p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-2">
                  Click any question to see how different visualizations work
                </p>
              </div>
              <FrequentlyAskedQuestions onSelectQuery={handleQuery} />
              <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                <SuggestedQueries onSelectQuery={handleQuery} />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Conversation Area - Show only when there are messages */}
      {messages.length > 0 && (
        <Card className="border-l-4 border-l-purple-500 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30">
          <CardHeader>
            <CardTitle className="text-purple-700 dark:text-purple-400">Conversation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  type={message.type}
                  content={message.content}
                  timestamp={message.timestamp}
                  queryResponse={message.queryResponse}
                  onFollowUpClick={handleQuery}
                />
              ))}
              {isLoading && (
                <div className="flex items-center gap-3 p-5 bg-gradient-to-r from-indigo-100 to-blue-100 dark:from-indigo-900/50 dark:to-blue-900/50 rounded-lg border-l-4 border-l-blue-500 shadow-lg animate-pulse">
                  <Loader2 className="h-6 w-6 animate-spin text-blue-600 dark:text-blue-400" />
                  <div className="flex flex-col">
                    <span className="text-base text-blue-700 dark:text-blue-300 font-semibold">Processing your query...</span>
                    <span className="text-xs text-blue-600 dark:text-blue-400 mt-0.5">This may take a few moments</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Query Input - Always at the bottom */}
      <Card className="border-l-4 border-l-indigo-500 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-950/30 dark:to-blue-950/30">
        <CardContent className="p-4">
          <QueryInput onSubmit={handleQuery} isLoading={isLoading} />
        </CardContent>
      </Card>
    </div>
  );
}
