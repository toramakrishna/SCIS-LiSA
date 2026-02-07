import { Lightbulb } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SuggestedFollowUpsProps {
  questions: string[];
  onQuestionClick: (question: string) => void;
}

export function SuggestedFollowUps({ questions, onQuestionClick }: SuggestedFollowUpsProps) {
  if (!questions || questions.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2 sm:space-y-3">
      <div className="flex items-center gap-2 text-xs sm:text-sm font-semibold">
        <div className="p-1 rounded-md bg-gradient-to-br from-amber-500 to-orange-500 shadow-sm">
          <Lightbulb className="h-3 w-3 sm:h-3.5 sm:w-3.5 text-white" />
        </div>
        <span className="text-slate-700 dark:text-slate-300">Suggested follow-up questions:</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            className="text-xs h-auto py-2 px-3 whitespace-normal text-left bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30 border-2 border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300 hover:from-purple-100 hover:to-pink-100 dark:hover:from-purple-900/50 dark:hover:to-pink-900/50 hover:border-purple-300 dark:hover:border-purple-700 hover:shadow-md transition-all font-medium"
            onClick={() => onQuestionClick(question)}
          >
            {question}
          </Button>
        ))}
      </div>
    </div>
  );
}
