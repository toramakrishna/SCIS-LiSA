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
  Loader2
} from 'lucide-react';
import type { Author, Publication } from '@/types';
import axios from 'axios';

export function FacultyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [faculty, setFaculty] = useState<Author | null>(null);
  const [publications, setPublications] = useState<Publication[]>([]);
  const [collaborators, setCollaborators] = useState<Array<{ name: string; count: number }>>([]);
  const [isLoadingFaculty, setIsLoadingFaculty] = useState(true);
  const [isLoadingPublications, setIsLoadingPublications] = useState(true);
  const [isLoadingCollaborators, setIsLoadingCollaborators] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    if (id) {
      loadFacultyDetails();
      loadPublications(1);
    }
  }, [id]);

  useEffect(() => {
    if (faculty) {
      loadCollaborators();
    }
  }, [faculty]);

  const loadFacultyDetails = async () => {
    setIsLoadingFaculty(true);
    try {
      // First try to get faculty details directly - if endpoint exists
      // Otherwise fall back to searching in the list
      try {
        const directResponse = await axios.get(`http://localhost:8000/api/v1/faculty/${id}`);
        setFaculty(directResponse.data);
      } catch {
        // Fallback: search in paginated list
        let found = false;
        let page = 1;
        
        while (!found) {
          const response = await axios.get(`http://localhost:8000/api/v1/faculty/`, {
            params: { page, page_size: 100 }
          });
          
          const facultyMember = response.data.items.find((f: Author) => f.id === parseInt(id!));
          
          if (facultyMember) {
            setFaculty(facultyMember);
            found = true;
          } else if (page >= response.data.pages) {
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
      const response = await axios.get(
        `http://localhost:8000/api/v1/faculty/${id}/publications`,
        {
          params: {
            page,
            page_size: pageSize
          }
        }
      );
      setPublications(response.data.items);
      setTotalPages(response.data.pages);
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
      const firstResponse = await axios.get(
        `http://localhost:8000/api/v1/faculty/${id}/publications`,
        {
          params: {
            page: 1,
            page_size: 100
          }
        }
      );
      
      allPublications = firstResponse.data.items;
      totalPages = firstResponse.data.pages;
      
      // Fetch remaining pages
      for (let page = 2; page <= totalPages; page++) {
        const response = await axios.get(
          `http://localhost:8000/api/v1/faculty/${id}/publications`,
          {
            params: {
              page,
              page_size: 100
            }
          }
        );
        allPublications = [...allPublications, ...response.data.items];
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
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex-1">
              <CardTitle className="text-3xl mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">{faculty.name}</CardTitle>
              {faculty.designation && (
                <Badge variant={getDesignationColor(faculty.designation)} className="text-sm">
                  {faculty.designation}
                </Badge>
              )}
            </div>
            <div className="flex gap-6">
              <div className="text-center p-4 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg">
                <div className="text-3xl font-bold">{faculty.publication_count || 0}</div>
                <div className="text-sm opacity-90">Publications</div>
              </div>
              {faculty.h_index && (
                <div className="text-center p-4 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg">
                  <div className="text-3xl font-bold">{faculty.h_index}</div>
                  <div className="text-sm opacity-90">H-Index</div>
                </div>
              )}
              <div className="text-center p-4 rounded-lg bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg">
                <div className="text-3xl font-bold">{collaborators.length}</div>
                <div className="text-sm opacity-90">Collaborators</div>
              </div>
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

          {/* Research Interests */}
          {faculty.research_interests && (
            <div className="space-y-2 p-4 rounded-lg bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-950/30 dark:to-yellow-950/30 border border-orange-200 dark:border-orange-800">
              <div className="flex items-center gap-2 font-medium text-orange-700 dark:text-orange-400">
                <Award className="h-5 w-5" />
                <span>Research Interests</span>
              </div>
              <p className="text-orange-900 dark:text-orange-200 pl-7">
                {faculty.research_interests}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Publications Section - Takes 2/3 width */}
        <div className="lg:col-span-2">
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

        {/* Collaborators Section - Takes 1/3 width */}
        <div className="lg:col-span-1">
          <Card className="sticky top-4 border-l-4 border-l-green-500">
            <CardHeader className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30">
              <CardTitle className="flex items-center gap-2 text-green-700 dark:text-green-400">
                <Users className="h-5 w-5" />
                Top Collaborators
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingCollaborators ? (
                <div className="text-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin mx-auto text-primary" />
                </div>
              ) : collaborators.length > 0 ? (
                <div className="space-y-3">
                  {collaborators.map((collab, index) => (
                    <div 
                      key={index}
                      className="flex items-center justify-between p-3 rounded-lg hover:bg-gradient-to-r hover:from-green-50 hover:to-emerald-50 dark:hover:from-green-950/30 dark:hover:to-emerald-950/30 transition-all border border-transparent hover:border-green-200 dark:hover:border-green-800"
                    >
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <div className="flex items-center justify-center w-7 h-7 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 text-white text-xs font-bold flex-shrink-0 shadow">
                          {index + 1}
                        </div>
                        <span className="text-sm truncate font-medium">{collab.name}</span>
                      </div>
                      <Badge variant="secondary" className="ml-2 flex-shrink-0 bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900 dark:to-emerald-900 text-green-700 dark:text-green-300 border-green-300 dark:border-green-700">
                        <TrendingUp className="h-3 w-3 mr-1" />
                        {collab.count}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground text-sm">
                  No collaborators found
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
