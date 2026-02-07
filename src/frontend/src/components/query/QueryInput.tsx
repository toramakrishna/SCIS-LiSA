import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { EXAMPLE_QUERIES, CHART_TYPE_COLORS } from '@/lib/constants/exampleQueries';

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
}

export function QueryInput({
  onSubmit,
  isLoading = false,
  placeholder = 'Ask a question about publications, authors, or research trends...',
  className,
}: QueryInputProps) {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState(EXAMPLE_QUERIES);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const justSelectedRef = useRef(false);

  // Auto-focus input after response is received
  useEffect(() => {
    if (!isLoading && inputRef.current) {
      // Small delay to ensure DOM is updated
      const timer = setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    justSelectedRef.current = false; // Reset flag when user manually types

    if (value.trim().length >= 2) {
      const filtered = EXAMPLE_QUERIES.filter(
        (example) =>
          example.question.toLowerCase().includes(value.toLowerCase()) ||
          example.category.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setFilteredSuggestions(EXAMPLE_QUERIES);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    justSelectedRef.current = true; // Set flag to prevent reopening
    setQuery(suggestion);
    setShowSuggestions(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
      setQuery('');
      setShowSuggestions(false);
      justSelectedRef.current = false;
    }
  };

  const handleInputFocus = () => {
    // Don't show suggestions if user just selected from dropdown
    if (!justSelectedRef.current && query.trim().length >= 2) {
      setShowSuggestions(filteredSuggestions.length > 0);
    }
  };

  return (
    <div className="relative">
      <form onSubmit={handleSubmit} className={cn('flex gap-2', className)}>
        <div className="relative flex-1">
          <Input
            ref={inputRef}
            value={query}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            placeholder={placeholder}
            disabled={isLoading}
            className="flex-1"
          />
          {showSuggestions && filteredSuggestions.length > 0 && (
            <div
              ref={suggestionsRef}
              className="absolute z-50 w-full bottom-full mb-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg max-h-[400px] overflow-y-auto"
            >
              <div className="p-2 border-b border-slate-200 dark:border-slate-700 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/30 dark:to-purple-950/30">
                <div className="flex items-center gap-2 text-xs font-medium text-indigo-700 dark:text-indigo-400">
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>Example Questions - Try Different Charts</span>
                </div>
              </div>
              {filteredSuggestions.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleSuggestionClick(example.question)}
                  className="w-full text-left px-3 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors border-b border-slate-100 dark:border-slate-700/50 last:border-b-0"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-slate-900 dark:text-slate-100 mb-1">
                        {example.question}
                      </div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        {example.description}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className={cn(
                        'text-xs px-2 py-0.5 rounded-full font-medium',
                        CHART_TYPE_COLORS[example.chartType]
                      )}>
                        {example.chartType}
                      </span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
        <Button type="submit" disabled={!query.trim() || isLoading} className="min-w-[80px] sm:min-w-[120px]">
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-1 sm:mr-2 animate-spin" />
              <span className="hidden sm:inline">Processing</span>
            </>
          ) : (
            <>
              <Send className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Send</span>
            </>
          )}
        </Button>
      </form>
    </div>
  );
}
