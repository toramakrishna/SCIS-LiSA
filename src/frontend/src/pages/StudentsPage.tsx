import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { GraduationCap, Search, Loader2, ChevronDown, ChevronRight, Plus } from 'lucide-react';

interface Student {
  id: number;
  registration_number: string;
  name: string;
  semester?: number;
  program?: string;
  school_name?: string;
  programme_type?: string;
  email?: string;
  phone?: string;
}

interface School {
  school: string;
  count: number;
}

interface ProgramGroup {
  program: string;
  students: Student[];
  isExpanded: boolean;
}

export function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [schools, setSchools] = useState<School[]>([]);
  const [programGroups, setProgramGroups] = useState<ProgramGroup[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSchool, setSelectedSchool] = useState('');
  const [totalStudents, setTotalStudents] = useState(0);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [availablePrograms, setAvailablePrograms] = useState<string[]>([]);
  const [newStudent, setNewStudent] = useState({
    registration_number: '',
    name: '',
    semester: '',
    program: '',
    school_name: 'School of Computer and Information\nSciences'
  });

  useEffect(() => {
    loadSchools();
  }, []);

  useEffect(() => {
    if (selectedSchool) {
      loadStudents();
    }
  }, [selectedSchool, searchQuery]);

  useEffect(() => {
    if (isAddDialogOpen && newStudent.school_name) {
      loadProgramsForSchool(newStudent.school_name);
    }
  }, [newStudent.school_name, isAddDialogOpen]);

  const loadSchools = async () => {
    try {
      const response = await fetch('/api/v1/students/stats/summary');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSchools(data.by_school || []);
      
      // Set default school to "School of Computer and Information Sciences"
      const defaultSchool = data.by_school.find((s: School) => 
        s.school.includes('Computer and Information')
      );
      if (defaultSchool) {
        setSelectedSchool(defaultSchool.school);
      }
    } catch (err) {
      console.error('Error loading schools:', err);
      setError(err instanceof Error ? err.message : 'Failed to load schools');
    }
  };

  const loadProgramsForSchool = async (schoolName: string) => {
    try {
      const params = new URLSearchParams({
        page: '1',
        page_size: '5000',
        school: schoolName
      });
      const response = await fetch(`/api/v1/students/?${params}`);
      if (response.ok) {
        const data = await response.json();
        const uniquePrograms = Array.from(new Set(
          data.items
            .map((s: Student) => s.program)
            .filter((p: string | undefined) => p && p.trim())
        )) as string[];
        setAvailablePrograms(uniquePrograms.sort());
      }
    } catch (err) {
      console.error('Error loading programs:', err);
      setAvailablePrograms([]);
    }
  };

  const loadStudents = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        page: '1',
        page_size: '5000', // Load all students for the school (increased backend limit to 5000)
        sort_by: 'registration_number'
      });
      
      if (selectedSchool) {
        params.append('school', selectedSchool);
      }
      
      if (searchQuery.trim()) {
        params.append('search', searchQuery.trim());
      }
      
      const response = await fetch(`/api/v1/students/?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setStudents(data.items);
      setTotalStudents(data.total);
      
      // Group students by program
      groupStudentsByProgram(data.items);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Network error occurred';
      setError(errorMessage);
      console.error('Error loading students:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const groupStudentsByProgram = (studentsList: Student[]) => {
    // Group students by program
    const programMap = new Map<string, Student[]>();
    
    studentsList.forEach(student => {
      const program = student.program || 'Other';
      if (!programMap.has(program)) {
        programMap.set(program, []);
      }
      programMap.get(program)!.push(student);
    });
    
    // Convert to array and sort programs (PhD first, then alphabetically)
    const groups: ProgramGroup[] = Array.from(programMap.entries())
      .map(([program, students]) => ({
        program,
        students: students.sort((a, b) => a.registration_number.localeCompare(b.registration_number)),
        // Expand all groups when searching, otherwise only PhD programs
        isExpanded: searchQuery.trim() !== '' || program.toLowerCase().includes('phd') || program.toLowerCase().includes('ph.d')
      }))
      .sort((a, b) => {
        // PhD programs first
        const aIsPhD = a.program.toLowerCase().includes('phd') || a.program.toLowerCase().includes('ph.d');
        const bIsPhD = b.program.toLowerCase().includes('phd') || b.program.toLowerCase().includes('ph.d');
        
        if (aIsPhD && !bIsPhD) return -1;
        if (!aIsPhD && bIsPhD) return 1;
        
        // Then sort alphabetically
        return a.program.localeCompare(b.program);
      });
    
    setProgramGroups(groups);
  };

  const toggleProgramExpansion = (programIndex: number) => {
    setProgramGroups(prevGroups =>
      prevGroups.map((group, index) => {
        if (index === programIndex) {
          // Toggle the clicked program
          return { ...group, isExpanded: !group.isExpanded };
        } else {
          // Collapse all other programs
          return { ...group, isExpanded: false };
        }
      })
    );
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
  };

  const handleAddStudent = async () => {
    // Validate required fields
    if (!newStudent.registration_number || !newStudent.name) {
      alert('Registration number and name are required');
      return;
    }

    setIsSaving(true);
    try {
      const payload: any = {
        registration_number: newStudent.registration_number,
        name: newStudent.name,
        semester: newStudent.semester ? parseInt(newStudent.semester) : null,
        program: newStudent.program || null,
        school_name: newStudent.school_name || null,
        programme_type: null,
        email: null,
        phone: null,
      };

      const response = await fetch('/api/v1/students/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add student');
      }

      // Success - reset form and close dialog
      setNewStudent({
        registration_number: '',
        name: '',
        semester: '',
        program: '',
        school_name: 'School of Computer and Information\nSciences'
      });
      setIsAddDialogOpen(false);
      
      // Reload students list
      await loadStudents();
      await loadSchools();
      alert('Student added successfully!');
    } catch (error: any) {
      console.error('Error adding student:', error);
      alert(error.message || 'Failed to add student');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-yellow-600 bg-clip-text text-transparent">
            Students Directory
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2 font-medium">
            Browse students by school and program ({totalStudents.toLocaleString()} students)
          </p>
        </div>
        
        {/* Add Student Button with Dialog */}
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-orange-600 hover:bg-orange-700">
              <Plus className="h-4 w-4 mr-2" />
              Add Student
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Add New Student</DialogTitle>
              <DialogDescription>
                Enter student details below. Registration number and name are required.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="reg_no">Registration Number *</Label>
                  <Input
                    id="reg_no"
                    value={newStudent.registration_number}
                    onChange={(e) => setNewStudent(prev => ({ ...prev, registration_number: e.target.value }))}
                    placeholder="e.g., 24MCMC01"
                    required
                    className="h-10"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name *</Label>
                  <Input
                    id="name"
                    value={newStudent.name}
                    onChange={(e) => setNewStudent(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., John Doe"
                    required
                    className="h-10"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="school">School Name</Label>
                <Select 
                  value={newStudent.school_name} 
                  onValueChange={(value) => setNewStudent(prev => ({ ...prev, school_name: value, program: '' }))}
                >
                  <SelectTrigger className="h-10">
                    <SelectValue placeholder="Select school" />
                  </SelectTrigger>
                  <SelectContent>
                    {schools.map((school) => (
                      <SelectItem key={school.school} value={school.school}>
                        {school.school.replace(/\n/g, ' ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="program">Program</Label>
                  <Select 
                    value={newStudent.program} 
                    onValueChange={(value) => setNewStudent(prev => ({ ...prev, program: value }))}
                    disabled={!newStudent.school_name || availablePrograms.length === 0}
                  >
                    <SelectTrigger className="h-10">
                      <SelectValue placeholder="Select program" />
                    </SelectTrigger>
                    <SelectContent>
                      {availablePrograms.map((program) => (
                        <SelectItem key={program} value={program}>
                          {program}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="semester">Semester</Label>
                  <Select 
                    value={newStudent.semester} 
                    onValueChange={(value) => setNewStudent(prev => ({ ...prev, semester: value }))}
                  >
                    <SelectTrigger className="h-10">
                      <SelectValue placeholder="Select semester" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14].map((sem) => (
                        <SelectItem key={sem} value={sem.toString()}>
                          Semester {sem}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsAddDialogOpen(false)}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button
                onClick={handleAddStudent}
                disabled={isSaving}
                className="bg-orange-600 hover:bg-orange-700"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Adding...
                  </>
                ) : (
                  'Add Student'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            {/* School Filter */}
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                Filter by School
              </label>
              <Select value={selectedSchool} onValueChange={setSelectedSchool}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a school" />
                </SelectTrigger>
                <SelectContent>
                  {schools.map((school) => (
                    <SelectItem key={school.school} value={school.school}>
                      {school.school.replace(/\n/g, ' ')} ({school.count} students)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Search Bar */}
            <form onSubmit={handleSearch} className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  type="text"
                  placeholder="Search by name or registration number..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button type="submit" className="bg-orange-600 hover:bg-orange-700">
                Search
              </Button>
              {searchQuery && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setSearchQuery('')}
                >
                  Clear
                </Button>
              )}
            </form>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="h-12 w-12 text-orange-500 animate-spin mb-4" />
              <p className="text-slate-600 dark:text-slate-400">Loading students...</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <Card className="border-l-4 border-l-red-500">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <h3 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-2">
                Error Loading Students
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">{error}</p>
              <Button onClick={loadStudents} className="mt-4">
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {!isLoading && !error && students.length === 0 && (
        <Card className="border-l-4 border-l-orange-500">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <GraduationCap className="h-16 w-16 text-orange-400 mb-4" />
              <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300 mb-2">
                {searchQuery ? 'No Students Found' : 'No Student Data Available'}
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md">
                {searchQuery
                  ? `No students match your search "${searchQuery}". Try a different search term.`
                  : 'No students found for the selected school.'}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Students by Program (Collapsible Tables) */}
      {!isLoading && !error && programGroups.length > 0 && (
        <div className="space-y-4">
          {programGroups.map((group, index) => (
            <Card key={group.program} className="border-l-4 border-l-orange-500">
              <CardHeader 
                className="cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                onClick={() => toggleProgramExpansion(index)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {group.isExpanded ? (
                      <ChevronDown className="h-5 w-5 text-orange-600" />
                    ) : (
                      <ChevronRight className="h-5 w-5 text-orange-600" />
                    )}
                    <CardTitle className="text-orange-700 dark:text-orange-400">
                      {group.program}
                    </CardTitle>
                  </div>
                  <span className="text-sm text-slate-500 dark:text-slate-400">
                    {group.students.length} student{group.students.length !== 1 ? 's' : ''}
                  </span>
                </div>
              </CardHeader>
              
              {group.isExpanded && (
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-[150px]">Reg No</TableHead>
                          <TableHead>Name</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {group.students.map((student) => (
                          <TableRow key={student.id}>
                            <TableCell className="font-mono text-sm">
                              {student.registration_number}
                            </TableCell>
                            <TableCell className="font-medium">
                              {student.name}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

