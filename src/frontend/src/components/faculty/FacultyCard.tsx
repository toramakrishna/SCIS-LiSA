import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PublicationItem } from './PublicationItem';
import { 
  ChevronDown, 
  ChevronUp, 
  Mail, 
  Phone, 
  BookOpen, 
  Award,
  ExternalLink,
  Maximize2,
  Database
} from 'lucide-react';
import type { Author, Publication } from '@/types';

interface FacultyCardProps {
  faculty: Author;
  onExpandPublications: (facultyId: number) => void;
  publications?: Publication[];
  isLoadingPublications?: boolean;
}

export function FacultyCard({ 
  faculty, 
  onExpandPublications,
  publications,
  isLoadingPublications 
}: FacultyCardProps) {
  const navigate = useNavigate();
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    if (!isExpanded && !publications) {
      onExpandPublications(faculty.id);
    }
    setIsExpanded(!isExpanded);
  };

  const handleVerificationChange = (publicationId: number, isVerified: boolean) => {
    // Update local state to reflect the change
    console.log(`Publication ${publicationId} ${isVerified ? 'accepted' : 'rejected'}`);
  };

  const getDesignationColor = (designation?: string) => {
    if (!designation) return 'default';
    if (designation.includes('Senior Professor') || designation.includes('Professor')) return 'default';
    if (designation.includes('Associate')) return 'secondary';
    return 'outline';
  };

  const photoUrl = faculty.photo_path 
    ? `/${faculty.photo_path}`
    : faculty.irins_photo_url 
    ? faculty.irins_photo_url
    : null;

  return (
    <Card className="group hover:shadow-xl hover:scale-[1.02] transition-all duration-300 border-l-4 border-l-blue-500 overflow-hidden bg-gradient-to-br from-white to-blue-50/30 dark:from-slate-900 dark:to-blue-950/20 hover:border-l-purple-500">
      <CardHeader className="pb-3 bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-blue-950/20 dark:to-purple-950/20">
        <div className="flex items-start gap-4">
          {/* Profile Photo */}
          {photoUrl && (
            <div className="flex-shrink-0">
              <div className="w-24 h-24 rounded-full overflow-hidden ring-4 ring-blue-200 dark:ring-blue-800 shadow-lg bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900">
                <img
                  src={photoUrl}
                  alt={faculty.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
            </div>
          )}
          
          <div className="flex-1 min-w-0">
            <h3 className="text-xl font-bold bg-gradient-to-r from-blue-700 to-purple-700 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent group-hover:from-purple-700 group-hover:to-pink-700 dark:group-hover:from-purple-400 dark:group-hover:to-pink-400 transition-all">
              {faculty.name}
            </h3>
            <div className="flex flex-wrap gap-2 mt-2">
              {faculty.designation && (
                <Badge variant={getDesignationColor(faculty.designation)}>
                  {faculty.designation}
                </Badge>
              )}
              {faculty.status === 'Former Faculty' && (
                <Badge variant="outline" className="border-amber-500 text-amber-700 dark:text-amber-400">
                  Former Faculty
                </Badge>
              )}
            </div>
            {faculty.h_index && (
              <div className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900 dark:to-pink-900 border border-purple-200 dark:border-purple-700">
                <Award className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                <span className="text-sm font-medium text-purple-700 dark:text-purple-300">H-Index: {faculty.h_index}</span>
              </div>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Contact Information */}
        <div className="flex flex-wrap gap-4 text-sm">
          {faculty.email && (
            <a 
              href={`mailto:${faculty.email}`}
              className="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors font-medium"
            >
              <Mail className="h-4 w-4" />
              <span>{faculty.email}</span>
            </a>
          )}
          {faculty.phone && (
            <div className="flex items-center gap-2 text-green-600 dark:text-green-400 font-medium">
              <Phone className="h-4 w-4" />
              <span>{faculty.phone}</span>
            </div>
          )}
        </div>

        {/* Education */}
        {faculty.education && (
          <div className="space-y-1 p-3 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 border border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-2 text-sm font-medium text-blue-700 dark:text-blue-400">
              <Award className="h-4 w-4" />
              <span>Education</span>
            </div>
            <p className="text-sm text-blue-900 dark:text-blue-200 pl-6">
              {faculty.education}
            </p>
          </div>
        )}

        {/* Research Interests / Areas of Interest */}
        {(faculty.areas_of_interest || faculty.research_interests) && (
          <div className="space-y-2 p-3 rounded-lg bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-950/30 dark:to-yellow-950/30 border border-orange-200 dark:border-orange-800">
            <div className="flex items-center gap-2 text-sm font-medium text-orange-700 dark:text-orange-400">
              <Award className="h-4 w-4" />
              <span>Research Interests</span>
            </div>
            <p className="text-sm text-orange-900 dark:text-orange-200 pl-6">
              {faculty.areas_of_interest || faculty.research_interests}
            </p>
          </div>
        )}

        {/* Homepage Link */}
        {faculty.homepage && (
          <a
            href={faculty.homepage}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors font-medium"
          >
            <ExternalLink className="h-4 w-4" />
            <span>Visit Homepage</span>
          </a>
        )}

        {/* DBLP Profile Link with Publications Count */}
        <div className="flex flex-wrap items-center gap-3">
          {faculty.dblp_pid && (
            <a
              href={`https://dblp.org/pid/${faculty.dblp_pid}.html`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors font-medium"
            >
              <Database className="h-4 w-4" />
              <span>View DBLP Profile</span>
            </a>
          )}
          {faculty.irins_url && (
            <a
              href={faculty.irins_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300 transition-colors font-medium"
            >
              <ExternalLink className="h-4 w-4" />
              <span>IRINS Profile</span>
            </a>
          )}
          {faculty.scopus_url && (
            <a
              href={faculty.scopus_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300 transition-colors font-medium"
            >
              <ExternalLink className="h-4 w-4" />
              <span>Scopus Profile</span>
            </a>
          )}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900 dark:to-indigo-900 border border-blue-200 dark:border-blue-700">
            <BookOpen className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            <span className="text-sm font-semibold text-blue-700 dark:text-blue-300">{faculty.publication_count || 0} Publications</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-2 mt-3">
          <Button
            variant="default"
            size="sm"
            onClick={() => navigate(`/faculty/${faculty.id}`)}
            className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-md"
          >
            <Maximize2 className="h-4 w-4 mr-2" />
            View Full Details
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleToggle}
            className="flex-1 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30"
          >
            <BookOpen className="h-4 w-4 mr-2" />
            {isExpanded ? 'Hide' : 'Preview'} Publications
            {isExpanded ? <ChevronUp className="h-4 w-4 ml-2" /> : <ChevronDown className="h-4 w-4 ml-2" />}
          </Button>
        </div>

        {/* Publications List */}
        {isExpanded && (
          <div className="mt-4 space-y-2 border-t pt-4 animate-in slide-in-from-top-2">
            {isLoadingPublications ? (
              <div className="text-center py-4 text-muted-foreground">
                Loading publications...
              </div>
            ) : publications && publications.length > 0 ? (
              <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                {publications.map((pub) => (
                  <PublicationItem
                    key={pub.id}
                    publication={pub}
                    facultyId={faculty.id}
                    onVerificationChange={handleVerificationChange}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-muted-foreground">
                No publications found
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
