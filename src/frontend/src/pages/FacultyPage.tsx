import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { FacultyCard } from '@/components/faculty/FacultyCard';
import { 
  RefreshCw, 
  Search, 
  Users,
  Filter,
  SortAsc,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { mcpAPI } from '@/lib/api/endpoints';
import type { Author, Publication } from '@/types';

interface FacultyWithPublications extends Author {
  publications?: Publication[];
  isLoadingPublications?: boolean;
}

export function FacultyPage() {
  const [faculty, setFaculty] = useState<FacultyWithPublications[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [totalCount, setTotalCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const loadFaculty = async (refresh = false) => {
    try {
      if (refresh) setIsRefreshing(true);
      else setIsLoading(true);
      setError(null);

      const response = await mcpAPI.faculty.list();

      setFaculty(response.items || []);
      setTotalCount(response.total || 0);
    } catch (error: any) {
      console.error('Failed to load faculty:', error);
      const errorMsg = error?.message || 'Cannot connect to backend server. Make sure the backend is running at http://localhost:8000';
      setError(errorMsg);
      setFaculty([]);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const loadFacultyPublications = async (facultyId: number) => {
    // Set loading state for this faculty
    setFaculty(prev => prev.map(f => 
      f.id === facultyId 
        ? { ...f, isLoadingPublications: true } 
        : f
    ));

    try {
      const response = await mcpAPI.faculty.publications(facultyId);

      setFaculty(prev => prev.map(f =>
        f.id === facultyId
          ? { ...f, publications: response.items || [], isLoadingPublications: false }
          : f
      ));
    } catch (error) {
      console.error('Failed to load publications:', error);
      setFaculty(prev => prev.map(f =>
        f.id === facultyId
          ? { ...f, isLoadingPublications: false }
          : f
      ));
    }
  };

  useEffect(() => {
    loadFaculty();
  }, [sortBy]);

  const filteredFaculty = faculty.filter(f =>
    f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (f.designation && f.designation.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (f.research_interests && f.research_interests.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const sortOptions = [
    { value: 'name', label: 'Name' },
    { value: 'publication_count', label: 'Publications' },
    { value: 'h_index', label: 'H-Index' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              <Users className="h-8 w-8 text-blue-600" />
              Faculty Directory
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2 font-medium">
              Browse our distinguished faculty members and their research contributions
            </p>
          </div>
          <Button
            onClick={() => loadFaculty(true)}
            disabled={isRefreshing}
            size="sm"
            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 shadow-md text-white"
          >
            {isRefreshing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Refreshing...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </>
            )}
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="border-l-4 border-l-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg">
                <Users className="h-6 w-6 text-white" />
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-700 dark:text-blue-400">{totalCount}</div>
                <div className="text-sm text-blue-600 dark:text-blue-300 font-medium">Total Faculty</div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-purple-500 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg">
                <Filter className="h-6 w-6 text-white" />
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-700 dark:text-purple-400">{filteredFaculty.length}</div>
                <div className="text-sm text-purple-600 dark:text-purple-300 font-medium">Filtered Results</div>
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-green-500 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30">
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg">
                <SortAsc className="h-6 w-6 text-white" />
              </div>
              <div>
                <div className="text-sm font-medium text-green-700 dark:text-green-400">Sort by</div>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="text-sm bg-transparent border-none focus:outline-none cursor-pointer text-green-600 dark:text-green-300 font-medium"
                >
                  {sortOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <Card className="border-l-4 border-l-indigo-500 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-950/30 dark:to-blue-950/30">
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-indigo-500" />
              <Input
                type="text"
                placeholder="Search by name, designation, or research interests..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 border-indigo-200 dark:border-indigo-800 focus:border-indigo-400 dark:focus:border-indigo-600"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Faculty Grid */}
      {error && (
        <Card className="border-l-4 border-l-red-500 bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-950/30 dark:to-pink-950/30">
          <CardContent className="p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-red-700 dark:text-red-400">Error Loading Faculty</p>
              <p className="text-sm text-red-600 dark:text-red-300 mt-1">{error}</p>
              <Button 
                onClick={() => loadFaculty()} 
                size="sm" 
                className="mt-3 bg-red-600 hover:bg-red-700 text-white"
              >
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      ) : filteredFaculty.length === 0 ? (
        <Card className="border-l-4 border-l-slate-300">
          <CardContent className="p-12 text-center">
            <Users className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2 text-slate-700 dark:text-slate-300">No faculty found</h3>
            <p className="text-slate-500 dark:text-slate-400">
              Try adjusting your search criteria
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {filteredFaculty.map((member) => (
            <FacultyCard
              key={member.id}
              faculty={member}
              onExpandPublications={loadFacultyPublications}
              publications={member.publications}
              isLoadingPublications={member.isLoadingPublications}
            />
          ))}
        </div>
      )}
    </div>
  );
}
