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
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Lightbulb className="h-3 w-3" />
        <span>Suggested follow-up questions:</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            className="text-xs h-auto py-2 px-3 whitespace-normal text-left hover:bg-primary hover:text-primary-foreground transition-colors"
            onClick={() => onQuestionClick(question)}
          >
            {question}
          </Button>
        ))}
      </div>
    </div>
  );
}
