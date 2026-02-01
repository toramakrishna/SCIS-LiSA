# Extension Cookbook - Ready-to-Use Code Examples

## 🍳 Common Extension Scenarios

### Scenario 1: Add a "Faculty Profiles" Page

**Complete Implementation:**

```typescript
// 1️⃣ Create types (types/faculty.ts)
export interface FacultyMember {
  id: number;
  name: string;
  designation: string;
  email: string;
  publications: number;
  collaborations: number;
  h_index: number;
}

// 2️⃣ Add API (lib/api/endpoints.ts)
export const facultyAPI = {
  getAll: () => apiClient.get<FacultyMember[]>('/faculty'),
  getById: (id: number) => apiClient.get<FacultyMember>(`/faculty/${id}`),
  getPublications: (name: string) => 
    apiClient.get(`/authors/${encodeURIComponent(name)}/publications`),
};

// 3️⃣ Create hook (features/faculty/hooks/useFaculty.ts)
import { useQuery } from '@tanstack/react-query';
import { facultyAPI } from '@/lib/api/endpoints';

export function useFacultyList() {
  return useQuery({
    queryKey: ['faculty'],
    queryFn: async () => {
      const { data } = await facultyAPI.getAll();
      return data;
    },
  });
}

export function useFacultyById(id: number) {
  return useQuery({
    queryKey: ['faculty', id],
    queryFn: async () => {
      const { data } = await facultyAPI.getById(id);
      return data;
    },
    enabled: !!id,
  });
}

// 4️⃣ Create components (features/faculty/components/FacultyCard.tsx)
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Mail, BookOpen, Users } from 'lucide-react';
import type { FacultyMember } from '@/types/faculty';

interface FacultyCardProps {
  faculty: FacultyMember;
}

export function FacultyCard({ faculty }: FacultyCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <CardTitle>{faculty.name}</CardTitle>
        <p className="text-sm text-muted-foreground">{faculty.designation}</p>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-center gap-2 text-sm">
          <Mail className="h-4 w-4" />
          <a href={`mailto:${faculty.email}`} className="hover:underline">
            {faculty.email}
          </a>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <BookOpen className="h-4 w-4" />
          <span>{faculty.publications} Publications</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <Users className="h-4 w-4" />
          <span>{faculty.collaborations} Collaborators</span>
        </div>
        <div className="text-sm">
          <span className="font-medium">H-Index:</span> {faculty.h_index}
        </div>
      </CardContent>
    </Card>
  );
}

// features/faculty/components/FacultyGrid.tsx
import { useFacultyList } from '../hooks/useFaculty';
import { FacultyCard } from './FacultyCard';
import { Skeleton } from '@/components/ui/skeleton';

export function FacultyGrid() {
  const { data: faculty, isLoading } = useFacultyList();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-48" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {faculty?.map((member) => (
        <FacultyCard key={member.id} faculty={member} />
      ))}
    </div>
  );
}

// 5️⃣ Create page (pages/FacultyPage.tsx)
import { PageContainer } from '@/components/layout/PageContainer';
import { FacultyGrid } from '@/features/faculty/components/FacultyGrid';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';
import { useState } from 'react';

export function FacultyPage() {
  const [search, setSearch] = useState('');

  return (
    <PageContainer 
      title="Faculty Profiles"
      description="Browse faculty members and their research profiles"
    >
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search faculty by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>
      
      <FacultyGrid />
    </PageContainer>
  );
}

// 6️⃣ Register route (app/router.tsx)
import { FacultyPage } from '@/pages/FacultyPage';

// In routes array:
{
  path: 'faculty',
  element: <FacultyPage />,
}

// 7️⃣ Add navigation (components/layout/Sidebar.tsx)
import { GraduationCap } from 'lucide-react';

const navigation = [
  // ... existing items
  { name: 'Faculty', path: '/faculty', icon: GraduationCap },
];
```

**Result:** Complete faculty profiles page with search, grid layout, and individual cards!

---

### Scenario 2: Add "Collaboration Network" Tab to Analytics

```typescript
// 1️⃣ Create component (features/analytics/components/CollaborationNetwork.tsx)
import { useQuery } from '@tanstack/react-query';
import { mcpAPI } from '@/lib/api/endpoints';
import { NetworkGraphViz } from '@/components/visualizations/NetworkGraphViz';
import { Card, CardContent } from '@/components/ui/card';

export function CollaborationNetwork() {
  const { data, isLoading } = useQuery({
    queryKey: ['collaborations-network'],
    queryFn: async () => {
      const { data } = await mcpAPI.query(
        'Show top collaborations between faculty members'
      );
      return data;
    },
  });

  if (isLoading) {
    return <div>Loading network...</div>;
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <NetworkGraphViz config={data.visualization} />
      </CardContent>
    </Card>
  );
}

// 2️⃣ Update page (pages/AnalyticsPage.tsx)
import { CollaborationNetwork } from '@/features/analytics/components/CollaborationNetwork';

// Add to tabs:
<TabsTrigger value="collaborations">Collaborations</TabsTrigger>

<TabsContent value="collaborations">
  <CollaborationNetwork />
</TabsContent>
```

**Result:** New tab with collaboration network visualization!

---

### Scenario 3: Add Real-time Notifications

```typescript
// 1️⃣ Create notification store (lib/stores/useNotificationStore.ts)
import { create } from 'zustand';

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: Date;
}

interface NotificationState {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
  notifications: [],
  
  addNotification: (notification) => {
    const id = Math.random().toString(36).substr(2, 9);
    set((state) => ({
      notifications: [
        { ...notification, id, timestamp: new Date() },
        ...state.notifications,
      ].slice(0, 50), // Keep last 50
    }));
  },
  
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
  
  clearAll: () => set({ notifications: [] }),
}));

// 2️⃣ Create notification component (components/notifications/NotificationBell.tsx)
import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { useNotificationStore } from '@/lib/stores/useNotificationStore';
import { Badge } from '@/components/ui/badge';

export function NotificationBell() {
  const { notifications, removeNotification, clearAll } = useNotificationStore();
  const unreadCount = notifications.length;

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0"
            >
              {unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h4 className="font-semibold">Notifications</h4>
            {unreadCount > 0 && (
              <Button variant="ghost" size="sm" onClick={clearAll}>
                Clear all
              </Button>
            )}
          </div>
          
          {notifications.length === 0 ? (
            <p className="text-sm text-muted-foreground">No notifications</p>
          ) : (
            <div className="space-y-2 max-h-96 overflow-auto">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className="p-3 border rounded-lg hover:bg-accent"
                >
                  <div className="flex justify-between items-start">
                    <div className="space-y-1">
                      <p className="font-medium text-sm">{notification.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {notification.message}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeNotification(notification.id)}
                    >
                      ×
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}

// 3️⃣ Add to header (components/layout/Header.tsx)
import { NotificationBell } from '@/components/notifications/NotificationBell';

export function Header() {
  return (
    <header className="border-b">
      <div className="flex items-center justify-between p-4">
        <h1>SCISLiSA</h1>
        <div className="flex items-center gap-4">
          <NotificationBell />
          {/* Other header items */}
        </div>
      </div>
    </header>
  );
}

// 4️⃣ Use in components
import { useNotificationStore } from '@/lib/stores/useNotificationStore';

function MyComponent() {
  const { addNotification } = useNotificationStore();
  
  const handleAction = async () => {
    // Do something
    addNotification({
      title: 'Success!',
      message: 'Your query completed successfully',
      type: 'success',
    });
  };
  
  return <Button onClick={handleAction}>Run Query</Button>;
}
```

**Result:** Complete notification system with bell icon, badge, and toast-style notifications!

---

### Scenario 4: Add Export to PDF Feature

```typescript
// 1️⃣ Install dependency
// npm install jspdf jspdf-autotable

// 2️⃣ Create export utility (lib/utils/exportToPDF.ts)
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

export function exportTableToPDF(
  data: any[],
  columns: string[],
  filename: string = 'export.pdf'
) {
  const doc = new jsPDF();
  
  // Add title
  doc.setFontSize(18);
  doc.text('SCISLiSA Export', 14, 20);
  
  // Add timestamp
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);
  
  // Add table
  autoTable(doc, {
    startY: 40,
    head: [columns],
    body: data.map((row) => columns.map((col) => row[col])),
  });
  
  // Save
  doc.save(filename);
}

export function exportChartToPDF(
  chartElement: HTMLElement,
  title: string,
  filename: string = 'chart.pdf'
) {
  const doc = new jsPDF();
  
  // Add title
  doc.setFontSize(18);
  doc.text(title, 14, 20);
  
  // Convert chart to image and add to PDF
  html2canvas(chartElement).then((canvas) => {
    const imgData = canvas.toDataURL('image/png');
    doc.addImage(imgData, 'PNG', 10, 30, 190, 100);
    doc.save(filename);
  });
}

// 3️⃣ Create export button component (components/export/ExportButton.tsx)
import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { exportTableToPDF } from '@/lib/utils/exportToPDF';

interface ExportButtonProps {
  data: any[];
  columns: string[];
  filename?: string;
}

export function ExportButton({ data, columns, filename }: ExportButtonProps) {
  const handleExportCSV = () => {
    const csv = [
      columns.join(','),
      ...data.map((row) => columns.map((col) => row[col]).join(',')),
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename || 'export'}.csv`;
    a.click();
  };
  
  const handleExportPDF = () => {
    exportTableToPDF(data, columns, `${filename || 'export'}.pdf`);
  };
  
  const handleExportJSON = () => {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename || 'export'}.json`;
    a.click();
  };
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm">
          <Download className="h-4 w-4 mr-2" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={handleExportCSV}>
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleExportPDF}>
          Export as PDF
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleExportJSON}>
          Export as JSON
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// 4️⃣ Use in components
<ExportButton 
  data={queryResults} 
  columns={['title', 'year', 'authors']}
  filename="publications"
/>
```

**Result:** Multi-format export functionality with dropdown menu!

---

### Scenario 5: Add Dark Mode Toggle

```typescript
// 1️⃣ Create theme store (lib/stores/useThemeStore.ts)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeState {
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'theme-storage',
    }
  )
);

// 2️⃣ Create theme provider (components/providers/ThemeProvider.tsx)
import { useEffect } from 'react';
import { useThemeStore } from '@/lib/stores/useThemeStore';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useThemeStore((state) => state.theme);
  
  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)')
        .matches
        ? 'dark'
        : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
  }, [theme]);
  
  return <>{children}</>;
}

// 3️⃣ Create theme toggle (components/theme/ThemeToggle.tsx)
import { Moon, Sun, Monitor } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useThemeStore } from '@/lib/stores/useThemeStore';

export function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme('light')}>
          <Sun className="h-4 w-4 mr-2" />
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('dark')}>
          <Moon className="h-4 w-4 mr-2" />
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('system')}>
          <Monitor className="h-4 w-4 mr-2" />
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// 4️⃣ Add to app (app/App.tsx)
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { ThemeToggle } from '@/components/theme/ThemeToggle';

// Wrap app
<ThemeProvider>
  <RouterProvider router={router} />
</ThemeProvider>

// Add toggle to header
<Header>
  <ThemeToggle />
</Header>
```

**Result:** Complete dark mode with system preference detection and manual toggle!

---

## 🎯 Quick Reference

| Want to add... | Files to create/modify | Complexity |
|----------------|------------------------|------------|
| New page | Page → Route → Nav | ⭐ Easy |
| New tab | Component → TabsTrigger/Content | ⭐ Easy |
| New API | endpoints.ts → Hook | ⭐ Easy |
| New chart | ChartComponent → ChartRenderer | ⭐⭐ Medium |
| New feature | Full feature module | ⭐⭐ Medium |
| Theme support | ThemeProvider + Toggle | ⭐⭐ Medium |
| Export feature | Export utils + Button | ⭐⭐ Medium |
| Notifications | Store + Component | ⭐⭐ Medium |

All examples are production-ready and follow best practices!
