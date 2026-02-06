import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, X, ExternalLink, Loader2 } from 'lucide-react';
import type { Publication } from '@/types';

interface PublicationItemProps {
  publication: Publication;
  facultyId: number;
  onVerificationChange: (publicationId: number, isVerified: boolean) => void;
}

export function PublicationItem({ publication, facultyId, onVerificationChange }: PublicationItemProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<boolean | null>(
    publication.is_verified ?? null
  );

  const handleVerify = async (isVerified: boolean) => {
    setIsUpdating(true);
    try {
      const response = await fetch(
        `/api/v1/faculty/${facultyId}/publications/${publication.id}/verify?is_verified=${isVerified}&verified_by=system`,
        { method: 'POST' }
      );
      
      if (response.ok) {
        setVerificationStatus(isVerified);
        onVerificationChange(publication.id, isVerified);
      } else {
        console.error('Failed to verify publication:', await response.text());
      }
    } catch (error) {
      console.error('Failed to verify publication:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  // Format publication in DBLP style with 3 lines
  const formatAuthors = () => {
    if (publication.authors && publication.authors.length > 0) {
      return publication.authors.join(', ') + ':';
    }
    return '';
  };

  const formatTitle = () => {
    return publication.title + '.';
  };

  const formatVenue = () => {
    const parts = [];
    
    // Venue (journal or booktitle)
    const venue = publication.journal || publication.booktitle;
    if (venue) {
      parts.push(venue);
    }
    
    // Volume/Number
    if (publication.volume) {
      let volNum = publication.volume;
      if (publication.number) {
        volNum += `(${publication.number})`;
      }
      volNum += ':';
      parts.push(volNum);
    }
    
    // Pages
    if (publication.pages) {
      parts.push(publication.pages);
    }
    
    // Year
    if (publication.year) {
      parts.push(`(${publication.year})`);
    }
    
    return parts.join(' ');
  };

  const getVerificationBadge = () => {
    if (verificationStatus === null) {
      return <Badge variant="outline" className="text-xs">Pending Review</Badge>;
    } else if (verificationStatus) {
      return <Badge variant="default" className="text-xs bg-green-600">Verified</Badge>;
    } else {
      return <Badge variant="destructive" className="text-xs">Rejected</Badge>;
    }
  };

  return (
    <div className="p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors border border-border">
      <div className="space-y-2">
        {/* DBLP Format - 3 lines with color coding */}
        <div className="text-sm leading-relaxed font-mono">
          {/* Line 1: Authors - Blue color for emphasis */}
          <div className="mb-1 text-blue-700 dark:text-blue-400 font-medium">{formatAuthors()}</div>
          {/* Line 2: Title - Dark color, slightly bold */}
          <div className="mb-1 text-foreground font-semibold">{formatTitle()}</div>
          {/* Line 3: Venue details - Muted gray color */}
          <div className="text-slate-600 dark:text-slate-400">{formatVenue()}</div>
        </div>
        
        {/* Metadata Row */}
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            {/* Type Badge */}
            {publication.publication_type && (
              <Badge variant="outline" className="text-xs">
                {publication.publication_type}
              </Badge>
            )}
            
            {/* Verification Status */}
            {getVerificationBadge()}
            
            {/* External Links */}
            {publication.url && (
              <a
                href={publication.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-primary hover:underline inline-flex items-center gap-1"
              >
                <ExternalLink className="h-3 w-3" />
                View
              </a>
            )}
            {publication.doi && (
              <a
                href={`https://doi.org/${publication.doi}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-primary hover:underline inline-flex items-center gap-1"
              >
                DOI
              </a>
            )}
          </div>
          
          {/* Accept/Reject Buttons */}
          {verificationStatus === null && (
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                className="h-7 text-xs hover:bg-green-50 hover:text-green-700 hover:border-green-300"
                onClick={() => handleVerify(true)}
                disabled={isUpdating}
              >
                {isUpdating ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <>
                    <Check className="h-3 w-3 mr-1" />
                    Accept
                  </>
                )}
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="h-7 text-xs hover:bg-red-50 hover:text-red-700 hover:border-red-300"
                onClick={() => handleVerify(false)}
                disabled={isUpdating}
              >
                {isUpdating ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <>
                    <X className="h-3 w-3 mr-1" />
                    Reject
                  </>
                )}
              </Button>
            </div>
          )}
          
          {/* Show undo button if already verified/rejected */}
          {verificationStatus !== null && (
            <Button
              size="sm"
              variant="ghost"
              className="h-7 text-xs"
              onClick={() => setVerificationStatus(null)}
              disabled={isUpdating}
            >
              Undo
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
