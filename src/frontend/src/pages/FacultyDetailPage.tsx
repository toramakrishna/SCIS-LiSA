import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PublicationItem } from '@/components/faculty/PublicationItem';
import {
  ArrowLeft,
  Mail,
  Phone,
  Award,
  ExternalLink,
  BookOpen,
  Users,
  TrendingUp,
  Loader2,
  GraduationCap
} from 'lucide-react';
import type { Author, Publication } from '@/types';

export function FacultyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [faculty, setFaculty] = useState<Author | null>(null);
  const [publications, setPublications] = useState<Publication[]>([]);
  const [isLoadingFaculty, setIsLoadingFaculty] = useState(true);
  const [isLoadingPublications, setIsLoadingPublications] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    if (id) {
      loadFacultyDetails();
      loadPublications(1);
    }
  }, [id]);

  const loadFacultyDetails = async () => {
    setIsLoadingFaculty(true);
    try {
      // First try to get faculty details directly - if endpoint exists
      // Otherwise fall back to searching in the list
      try {
        const response = await fetch(`/api/v1/faculty/${id}`);
        if (response.ok) {
          const data = await response.json();
          setFaculty(data);
        } else {
          throw new Error('Direct fetch failed');
        }
      } catch {
        // Fallback: search in paginated list
        let found = false;
        let page = 1;
        
        while (!found) {
          const response = await fetch(`/api/v1/faculty/?page=${page}&page_size=100`);
          const data = await response.json();
          
          const facultyMember = data.items.find((f: Author) => f.id === parseInt(id!));
          
          if (facultyMember) {
            setFaculty(facultyMember);
            found = true;
          } else if (page >= data.pages) {
            // Reached last page, faculty not found
            console.error('Faculty member not found');
            break;
          } else {
            page++;
          }
        }
      }
    } catch (error) {
      console.error('Failed to load faculty details:', error);
    } finally {
      setIsLoadingFaculty(false);
    }
  };

  const loadPublications = async (page: number) => {
    setIsLoadingPublications(true);
    try {
      const response = await fetch(
        `/api/v1/faculty/${id}/publications?page=${page}&page_size=${pageSize}`
      );
      const data = await response.json();
      setPublications(data.items);
      // Calculate total pages from total and page_size
      const totalPages = Math.ceil(data.total / pageSize);
      setTotalPages(totalPages);
      setCurrentPage(page);
    } catch (error) {
      console.error('Failed to load publications:', error);
    } finally {
      setIsLoadingPublications(false);
    }
  };

  const loadCollaborators = async () => {
    if (!faculty) {
      console.log('Faculty not loaded yet, skipping collaborators');
      return;
    }
    
    setIsLoadingCollaborators(true);
    try {
      console.log('Loading collaborators for faculty:', faculty.name);
      
      // Get all publications by fetching all pages
      let allPublications: Publication[] = [];
      let totalPages = 1;
      
      // Fetch first page to get total pages
      const firstResponse = await fetch(
        `/api/v1/faculty/${id}/publications?page=1&page_size=100`
      );
      const firstData = await firstResponse.json();
      
      allPublications = firstData.items;
      totalPages = firstData.pages;
      
      // Fetch remaining pages
      for (let page = 2; page <= totalPages; page++) {
        const response = await fetch(
          `/api/v1/faculty/${id}/publications?page=${page}&page_size=100`
        );
        const data = await response.json();
        allPublications = [...allPublications, ...data.items];
      }
      
      console.log('Total publications fetched:', allPublications.length);
      
      // Count co-authors
      const coAuthorMap = new Map<string, number>();
      allPublications.forEach((pub: Publication) => {
        if (pub.authors && pub.authors.length > 0) {
          pub.authors.forEach((author: string) => {
            // Exclude the faculty member themselves
            if (author !== faculty.name) {
              coAuthorMap.set(author, (coAuthorMap.get(author) || 0) + 1);
            }
          });
        }
      });

      console.log('Total unique co-authors found:', coAuthorMap.size);

      // Sort by collaboration count
      const sortedCollaborators = Array.from(coAuthorMap.entries())
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10); // Top 10 collaborators

      console.log('Top 10 collaborators:', sortedCollaborators);
      setCollaborators(sortedCollaborators);
    } catch (error) {
      console.error('Failed to load collaborators:', error);
    } finally {
      setIsLoadingCollaborators(false);
    }
  };

  const handleVerificationChange = (publicationId: number, isVerified: boolean) => {
    console.log(`Publication ${publicationId} ${isVerified ? 'accepted' : 'rejected'}`);
  };

  const getDesignationColor = (designation?: string) => {
    if (!designation) return 'default';
    if (designation.includes('Senior Professor') || designation.includes('Professor')) return 'default';
    if (designation.includes('Associate')) return 'secondary';
    return 'outline';
  };

  const photoUrl = faculty?.photo_path 
    ? `/${faculty.photo_path}`
    : faculty?.irins_photo_url 
    ? faculty.irins_photo_url
    : null;

  if (isLoadingFaculty) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!faculty) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-lg text-slate-600 dark:text-slate-400 font-medium">Faculty member not found</p>
          <Button 
            onClick={() => navigate('/faculty')} 
            className="mt-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-md"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Faculty List
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-6">
        <Button 
          onClick={() => navigate('/faculty')}
          className="mb-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-md"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Faculty List
        </Button>
      </div>

      {/* Faculty Profile Card */}
      <Card className="mb-6 border-l-4 border-l-primary bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30">
        <CardHeader>
          <div className="flex items-start gap-6 flex-wrap">
            {/* Profile Photo */}
            {photoUrl && (
              <div className="flex-shrink-0">
                <div className="w-32 h-32 rounded-full overflow-hidden ring-4 ring-blue-300 dark:ring-blue-700 shadow-xl bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900">
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
            
            <div className="flex-1">
              <CardTitle className="text-3xl mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">{faculty.name}</CardTitle>
              <div className="flex flex-wrap gap-2 mb-3">
                {faculty.designation && (
                  <Badge variant={getDesignationColor(faculty.designation)} className="text-sm">
                    {faculty.designation}
                  </Badge>
                )}
                {faculty.status === 'Former Faculty' && (
                  <Badge variant="outline" className="border-amber-500 text-amber-700 dark:text-amber-400 text-sm">
                    Former Faculty
                  </Badge>
                )}
              </div>
              
              {/* Stats Row */}
              {faculty.h_index && (
                <div className="flex flex-wrap gap-4 mt-4">
                  <div className="text-center p-3 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg">
                    <div className="text-2xl font-bold">{faculty.h_index}</div>
                    <div className="text-xs opacity-90">H-Index</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Contact Information */}
          <div className="flex flex-wrap gap-6">
            {faculty.email && (
              <a 
                href={`mailto:${faculty.email}`}
                className="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors font-medium"
              >
                <Mail className="h-5 w-5" />
                <span>{faculty.email}</span>
              </a>
            )}
            {faculty.phone && (
              <div className="flex items-center gap-2 text-green-600 dark:text-green-400 font-medium">
                <Phone className="h-5 w-5" />
                <span>{faculty.phone}</span>
              </div>
            )}
            {faculty.homepage && (
              <a
                href={faculty.homepage}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors font-medium"
              >
                <ExternalLink className="h-5 w-5" />
                <span>Homepage</span>
              </a>
            )}
          </div>

          {/* Education */}
          {faculty.education && (
            <div className="space-y-2 p-4 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30 border border-blue-200 dark:border-blue-800">
              <div className="flex items-center gap-2 font-medium text-blue-700 dark:text-blue-400">
                <GraduationCap className="h-5 w-5" />
                <span>Education</span>
              </div>
              <p className="text-blue-900 dark:text-blue-200 pl-7">
                {faculty.education}
              </p>
            </div>
          )}

          {/* Research Interests / Areas of Interest */}
          {(faculty.areas_of_interest || faculty.research_interests) && (
            <div className="space-y-2 p-4 rounded-lg bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-950/30 dark:to-yellow-950/30 border border-orange-200 dark:border-orange-800">
              <div className="flex items-center gap-2 font-medium text-orange-700 dark:text-orange-400">
                <Award className="h-5 w-5" />
                <span>Research Interests</span>
              </div>
              <p className="text-orange-900 dark:text-orange-200 pl-7">
                {faculty.areas_of_interest || faculty.research_interests}
              </p>
            </div>
          )}
          
          {/* DBLP and IRINS Links with Publications Count */}
          <div className="flex flex-wrap items-center gap-4">
            {faculty.dblp_pid && (
              <a
                href={`https://dblp.org/pid/${faculty.dblp_pid}.html`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-100 to-blue-100 dark:from-indigo-900 dark:to-blue-900 border border-indigo-200 dark:border-indigo-700 text-indigo-700 dark:text-indigo-300 hover:from-indigo-200 hover:to-blue-200 dark:hover:from-indigo-800 dark:hover:to-blue-800 transition-all font-medium shadow-sm"
              >
                <ExternalLink className="h-5 w-5" />
                <span>View DBLP Profile</span>
              </a>
            )}
            {faculty.irins_url && (
              <a
                href={faculty.irins_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900 dark:to-emerald-900 border border-green-200 dark:border-green-700 text-green-700 dark:text-green-300 hover:from-green-200 hover:to-emerald-200 dark:hover:from-green-800 dark:hover:to-emerald-800 transition-all font-medium shadow-sm"
              >
                <ExternalLink className="h-5 w-5" />
                <span>View IRINS Profile</span>
              </a>
            )}
            {faculty.scopus_url && (
              <a
                href={faculty.scopus_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-orange-100 to-amber-100 dark:from-orange-900 dark:to-amber-900 border border-orange-200 dark:border-orange-700 text-orange-700 dark:text-orange-300 hover:from-orange-200 hover:to-amber-200 dark:hover:from-orange-800 dark:hover:to-amber-800 transition-all font-medium shadow-sm"
              >
                <ExternalLink className="h-5 w-5" />
                <span>View Scopus Profile</span>
              </a>
            )}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-100 to-cyan-100 dark:from-blue-900 dark:to-cyan-900 border border-blue-200 dark:border-blue-700 shadow-sm">
              <BookOpen className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              <span className="text-lg font-bold text-blue-700 dark:text-blue-300">{faculty.publication_count || 0}</span>
              <span className="text-sm font-medium text-blue-600 dark:text-blue-400">Publications</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <div>
        {/* Publications Section */}
        <div>
          <Card className="border-l-4 border-l-blue-500">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30">
              <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-400">
                <BookOpen className="h-5 w-5" />
                Publications
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingPublications ? (
                <div className="text-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                </div>
              ) : publications.length > 0 ? (
                <>
                  <div className="space-y-4">
                    {publications.map((pub) => (
                      <PublicationItem
                        key={pub.id}
                        publication={pub}
                        facultyId={faculty.id}
                        onVerificationChange={handleVerificationChange}
                      />
                    ))}
                  </div>
                  
                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-2 mt-6">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => loadPublications(currentPage - 1)}
                        disabled={currentPage === 1}
                      >
                        Previous
                      </Button>
                      <span className="text-sm text-muted-foreground">
                        Page {currentPage} of {totalPages}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => loadPublications(currentPage + 1)}
                        disabled={currentPage === totalPages}
                      >
                        Next
                      </Button>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No publications found
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
