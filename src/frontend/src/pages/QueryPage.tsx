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
      
      // Build conversation history from existing messages
      // Include only the last few messages to avoid overwhelming the LLM
      const conversationHistory = messages.slice(-6).map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.type === 'user' 
          ? msg.content 
          : msg.queryResponse?.sql 
            ? `${msg.queryResponse.sql} [VISUALIZATION: ${msg.queryResponse.visualization.type}]`  // Include visualization type
            : msg.content
      }));
      
      // Add user message
      addUserMessage(query);

      // Call MCP API with conversation history
      const response = await mcpAPI.query(query, conversationHistory);
      
      // Add assistant response with explanation as content and full response as metadata
      addAssistantMessage({
        content: response.explanation || "Query executed successfully",
        queryResponse: response
      });
    } catch (err: any) {
      console.error('Query error:', err);
      let errorMessage = 'Failed to process query';
      
      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        // Request timeout
        errorMessage = '⏱️ Query took too long to process (timeout after 60 seconds). The query might be too complex or the AI model is overloaded. Please try: (1) Simplifying your question, (2) Asking for less data with LIMIT, or (3) Trying again in a moment.';
      } else if (err.response) {
        // Server responded with error status
        errorMessage = `Server error (${err.response.status}): ${err.response.data?.detail || err.response.statusText}`;
      } else if (err.request) {
        // Request made but no response received
        errorMessage = '🔌 Cannot connect to backend server. Make sure the backend is running at http://localhost:8000 and that the Ollama service is available.';
      } else {
        // Error in request configuration
        errorMessage = err.message || 'Unknown error occurred';
      }
      
      // setError will automatically set isLoading to false
      setError(errorMessage);
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">Natural Language Query</h1>
          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-2 font-medium">
            Ask questions about publications, authors, and research trends
          </p>
        </div>
        {messages.length > 0 && (
          <Button size="sm" onClick={clearMessages} className="bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white shadow-md w-full sm:w-auto">
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
            <CardTitle className="text-sm sm:text-base text-purple-700 dark:text-purple-400">Frequently Asked Questions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 sm:space-y-6">
              <div className="text-center py-3 sm:py-4">
                <p className="text-purple-600 dark:text-purple-400 font-medium text-base sm:text-lg">
                  Start by asking a question or try one of the examples below
                </p>
                <p className="text-slate-500 dark:text-slate-400 text-xs sm:text-sm mt-2">
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
            <CardTitle className="text-sm sm:text-base text-purple-700 dark:text-purple-400">Conversation</CardTitle>
          </CardHeader>
          <CardContent className="px-3 sm:px-6">
            <div className="space-y-3 sm:space-y-4 max-h-[500px] sm:max-h-[600px] overflow-y-auto overflow-x-hidden">
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
                <div className="flex items-center gap-2 sm:gap-3 p-3 sm:p-5 bg-gradient-to-r from-indigo-100 to-blue-100 dark:from-indigo-900/50 dark:to-blue-900/50 rounded-lg border-l-4 border-l-blue-500 shadow-lg animate-pulse">
                  <Loader2 className="h-5 w-5 sm:h-6 sm:w-6 animate-spin text-blue-600 dark:text-blue-400" />
                  <div className="flex flex-col">
                    <span className="text-sm sm:text-base text-blue-700 dark:text-blue-300 font-semibold">Processing your query...</span>
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
