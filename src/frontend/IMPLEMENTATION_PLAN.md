# Frontend Technology Stack & Implementation Plan

## 🎯 Recommended Technology Stack

Based on the requirements for an AI-powered interactive data insights assistant, here's the optimal technology stack:

### Core Framework & Language
**React 18+ with TypeScript**
- **Why React**: Component-based architecture, rich ecosystem, excellent for interactive UIs
- **Why TypeScript**: Type safety, better IDE support, catches errors early, self-documenting code
- **Build Tool**: Vite (ultra-fast HMR, optimized production builds)

### Routing & Navigation
**React Router v6**
- Declarative routing
- Nested routes for layouts
- Code splitting per route
- Easy to add new pages/tabs
- Built-in navigation hooks

### UI & Styling
**Tailwind CSS + shadcn/ui**
- **Tailwind CSS**: Utility-first, responsive design, consistent styling
- **shadcn/ui**: Beautiful, accessible components built on Radix UI
- **Lucide React**: Modern icon library
- **Framer Motion**: Smooth animations and transitions

### Data Visualization
**Recharts (Primary) + D3.js (Advanced)**
- **Recharts**: React-native charts, easy to use, covers 80% of use cases
- **D3.js**: For complex custom visualizations (network graphs)
- **react-chartjs-2**: Alternative option for specific chart types

### State Management
**Zustand + TanStack Query (React Query)**
- **Zustand**: Lightweight, simple global state (UI state, user preferences)
- **TanStack Query**: Server state management, caching, real-time updates
- **Context API**: For theme, auth contexts

### Real-time Communication
**Socket.IO Client**
- WebSocket support with fallbacks
- Room-based communication
- Automatic reconnection
- Event-based architecture

### HTTP Client
**Axios**
- REST API calls to FastAPI backend
- Request/response interceptors
- Better error handling than fetch

### Form Handling
**React Hook Form + Zod**
- **React Hook Form**: Performant, minimal re-renders
- **Zod**: Schema validation, TypeScript integration

### Utilities
**Additional Libraries:**
- **date-fns**: Date manipulation
- **clsx**: Conditional CSS classes
- **react-markdown**: Render explanations
- **file-saver**: Export functionality
- **react-hot-toast**: Notifications

---

## � Extensibility Architecture

### Adding a New Page/Tab (3 Simple Steps)

The architecture is designed for easy extension. Here's how to add a new feature page:

#### Step 1: Create the Page Component

**pages/FacultyNetworkPage.tsx**
```typescript
import { PageContainer } from '@/components/layout/PageContainer';
import { FacultyNetwork } from '@/features/faculty/components/FacultyNetwork';

export function FacultyNetworkPage() {
  return (
    <PageContainer
      title="Faculty Collaboration Network"
      description="Explore research collaborations between faculty members"
    >
      <FacultyNetwork />
    </PageContainer>
  );
}
```

#### Step 2: Add Route Definition

**app/router.tsx** - Add one line:
```typescript
{
  path: 'faculty-network',
  element: <FacultyNetworkPage />,
},
```

#### Step 3: Add Navigation Item

**components/layout/Sidebar.tsx** - Add to navigation array:
```typescript
{ name: 'Faculty Network', path: '/faculty-network', icon: Network },
```

**That's it!** Your new page is fully integrated with routing, navigation, and layout.

---

### Tab-Based Pages Pattern

For pages with multiple tabs (like Analytics Dashboard):

**pages/AnalyticsPage.tsx**
```typescript
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TrendAnalysis } from '@/features/analytics/components/TrendAnalysis';
import { VenueAnalysis } from '@/features/analytics/components/VenueAnalysis';
import { CollaborationAnalysis } from '@/features/analytics/components/CollaborationAnalysis';

export function AnalyticsPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Analytics Dashboard</h1>
      
      <Tabs defaultValue="trends">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="venues">Venues</TabsTrigger>
          <TabsTrigger value="collaborations">Collaborations</TabsTrigger>
          {/* 🎯 EXTENSIBILITY: Add new tabs here */}
          {/* <TabsTrigger value="citations">Citations</TabsTrigger> */}
        </TabsList>

        <TabsContent value="trends">
          <TrendAnalysis />
        </TabsContent>

        <TabsContent value="venues">
          <VenueAnalysis />
        </TabsContent>

        <TabsContent value="collaborations">
          <CollaborationAnalysis />
        </TabsContent>

        {/* 🎯 EXTENSIBILITY: Add new tab content here */}
        {/* <TabsContent value="citations">
          <CitationAnalysis />
        </TabsContent> */}
      </Tabs>
    </div>
  );
}
```

**Adding a new tab:**
1. Create component in `features/analytics/components/`
2. Import and add `<TabsTrigger>` + `<TabsContent>`
3. Done!

---

### Feature Module Pattern

Each feature is self-contained and can be added independently:

```
features/
└── citations/              # 🆕 New feature
    ├── components/
    │   ├── CitationGraph.tsx
    │   ├── CitationStats.tsx
    │   └── TopCitedPapers.tsx
    ├── hooks/
    │   ├── useCitations.ts
    │   └── useCitationAnalytics.ts
    ├── types.ts
    └── api.ts              # Feature-specific API calls
```

**Benefits:**
- ✅ Self-contained features
- ✅ Easy to add/remove
- ✅ No conflicts with existing code
- ✅ Clear ownership and testing

---

### API Endpoint Extension

**lib/api/endpoints.ts**
```typescript
// Easy to add new API groups
export const mcpAPI = { /* ... */ };
export const publicationsAPI = { /* ... */ };
export const facultyAPI = { /* ... */ };

// 🎯 EXTENSIBILITY: Add new API groups
export const citationsAPI = {
  getCitations: (publicationId: string) =>
    apiClient.get(`/citations/${publicationId}`),
  
  getCitationTrends: () =>
    apiClient.get('/citations/trends'),
};
```

---

### Store Extension

**lib/stores/useCitationStore.ts**
```typescript
import { create } from 'zustand';

interface CitationState {
  citations: Citation[];
  selectedPaper: string | null;
  // ... state properties
  
  fetchCitations: (paperId: string) => void;
  // ... actions
}

export const useCitationStore = create<CitationState>((set) => ({
  // Implementation
}));
```

Each feature can have its own store - no conflicts!

---

### Visualization Extension

**components/visualizations/CitationNetworkViz.tsx**
```typescript
import { VisualizationConfig } from '@/types/visualization';

interface CitationNetworkVizProps {
  config: VisualizationConfig;
}

export function CitationNetworkViz({ config }: CitationNetworkVizProps) {
  // New visualization implementation
  return (
    <div className="w-full h-[500px]">
      {/* D3 or custom chart */}
    </div>
  );
}
```

**Update ChartRenderer.tsx:**
```typescript
import { CitationNetworkViz } from './CitationNetworkViz';

export function ChartRenderer({ config }: ChartRendererProps) {
  switch (config.type) {
    // ... existing cases
    case 'citation_network':
      return <CitationNetworkViz config={config} />;
    default:
      return <div>Unsupported visualization type</div>;
  }
}
```

---

### Extension Patterns Summary

| What to Add | Files to Modify | Complexity |
|-------------|----------------|------------|
| **New Page** | 1. Create page<br>2. Add route<br>3. Add nav item | ⭐ Easy |
| **New Tab** | 1. Create component<br>2. Add TabsTrigger + TabsContent | ⭐ Easy |
| **New Feature Module** | 1. Create feature folder<br>2. Add components/hooks | ⭐⭐ Medium |
| **New Visualization** | 1. Create viz component<br>2. Update ChartRenderer | ⭐⭐ Medium |
| **New API Endpoint** | 1. Add to endpoints.ts | ⭐ Easy |
| **New Store** | 1. Create store file | ⭐ Easy |

---

### Real-World Extension Examples

#### Example 1: Adding a "Publications Browser" Page

```typescript
// 1. Create page
// pages/PublicationsBrowserPage.tsx
export function PublicationsBrowserPage() {
  return (
    <PageContainer title="Publications Browser">
      <PublicationList />
      <PublicationFilters />
    </PageContainer>
  );
}

// 2. Add route (app/router.tsx)
{ path: 'publications', element: <PublicationsBrowserPage /> }

// 3. Add nav (components/layout/Sidebar.tsx)
{ name: 'Publications', path: '/publications', icon: BookOpen }
```

#### Example 2: Adding a "Reports" Tab to Analytics

```typescript
// 1. Create component
// features/analytics/components/ReportsAnalysis.tsx
export function ReportsAnalysis() {
  return <div>Reports content</div>;
}

// 2. Update AnalyticsPage.tsx
<TabsTrigger value="reports">Reports</TabsTrigger>
<TabsContent value="reports">
  <ReportsAnalysis />
</TabsContent>
```

#### Example 3: Adding a "Scholar Profiles" Feature

```
features/
└── scholar/                    # New feature module
    ├── pages/
    │   └── ScholarProfilePage.tsx
    ├── components/
    │   ├── ScholarCard.tsx
    │   ├── ScholarStats.tsx
    │   └── PublicationTimeline.tsx
    ├── hooks/
    │   └── useScholar.ts
    └── api.ts
```

---

## �📋 Detailed Implementation Plan

### Phase 1: Project Setup & Foundation (Days 1-2)

#### 1.1 Initialize Project
```bash
npm create vite@latest scislisa-frontend -- --template react-ts
cd scislisa-frontend
npm install
```

#### 1.2 Install Core Dependencies
```bash
# Routing
npm install react-router-dom

# UI & Styling
npm install tailwindcss postcss autoprefixer
npm install @radix-ui/react-* (dropdown, dialog, tabs, etc.)
npm install class-variance-authority clsx tailwind-merge
npm install lucide-react framer-motion

# State Management & Data Fetching
npm install zustand
npm install @tanstack/react-query
npm install axios

# Real-time Communication
npm install socket.io-client

# Forms & Validation
npm install react-hook-form zod @hookform/resolvers

# Visualization
npm install recharts
npm install d3 @types/d3

# Utilities
npm install date-fns
npm install react-markdown
npm install react-hot-toast
npm install file-saver @types/file-saver
```

#### 1.3 Project Structure
```
src/
├── app/                          # App-level setup
│   ├── App.tsx
│   ├── main.tsx
│   └── router.tsx                # Route definitions
├── pages/                        # Page components (routes)
│   ├── HomePage.tsx
│   ├── QueryPage.tsx
│   ├── AnalyticsPage.tsx
│   ├── HistoryPage.tsx
│   ├── SettingsPage.tsx
│   └── HelpPage.tsx
├── components/                   # Reusable components
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── tabs.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── MainLayout.tsx
│   │   └── PageContainer.tsx
│   ├── chat/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── QueryInput.tsx
│   │   └── SuggestedQueries.tsx
│   └── visualizations/
│       ├── ChartRenderer.tsx
│       ├── LineChartViz.tsx
│       ├── BarChartViz.tsx
│       ├── PieChartViz.tsx
│       ├── TableViz.tsx
│       └── NetworkGraphViz.tsx
├── features/                     # Feature modules
│   ├── query/
│   │   ├── hooks/
│   │   │   ├── useQuery.ts
│   │   │   └── useQueryHistory.ts
│   │   ├── components/
│   │   │   ├── QueryPanel.tsx
│   │   │   └── QueryResults.tsx
│   │   └── types.ts
│   ├── analytics/
│   │   ├── components/
│   │   │   ├── AnalyticsDashboard.tsx
│   │   │   ├── InsightCard.tsx
│   │   │   └── TrendChart.tsx
│   │   └── hooks/
│   │       └── useAnalytics.ts
│   ├── publications/
│   │   ├── components/
│   │   │   ├── PublicationList.tsx
│   │   │   └── PublicationCard.tsx
│   │   └── hooks/
│   │       └── usePublications.ts
│   ├── faculty/
│   │   ├── components/
│   │   │   ├── FacultyProfile.tsx
│   │   │   └── CollaborationNetwork.tsx
│   │   └── hooks/
│   │       └── useFaculty.ts
│   └── export/
│       ├── components/
│       │   └── ExportDialog.tsx
│       └── utils/
│           └── exportUtils.ts
├── lib/                          # Utilities & configurations
│   ├── api/
│   │   ├── client.ts             # Axios instance
│   │   ├── endpoints.ts          # API endpoints
│   │   └── websocket.ts          # Socket.IO setup
│   ├── hooks/
│   │   ├── useDebounce.ts
│   │   └── useLocalStorage.ts
│   ├── utils/
│   │   ├── cn.ts                 # classNames utility
│   │   ├── formatters.ts
│   │   └── validators.ts
│   └── stores/
│       ├── useQueryStore.ts
│       ├── useUIStore.ts
│       └── useNavigationStore.ts
├── types/                        # TypeScript types
│   ├── api.ts
│   ├── query.ts
│   ├── routes.ts
│   └── visualization.ts
└── styles/
    └── globals.css
```

#### 1.4 Configuration Files
- `tailwind.config.js` - Tailwind setup
- `tsconfig.json` - TypeScript config
- `vite.config.ts` - Vite config
- `.env` - Environment variables

#### 1.5 Router Setup

**app/router.tsx**
```typescript
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { HomePage } from '@/pages/HomePage';
import { QueryPage } from '@/pages/QueryPage';
import { AnalyticsPage } from '@/pages/AnalyticsPage';
import { HistoryPage } from '@/pages/HistoryPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { HelpPage } from '@/pages/HelpPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/query" replace />,
      },
      {
        path: 'home',
        element: <HomePage />,
      },
      {
        path: 'query',
        element: <QueryPage />,
      },
      {
        path: 'analytics',
        element: <AnalyticsPage />,
      },
      {
        path: 'history',
        element: <HistoryPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
      },
      {
        path: 'help',
        element: <HelpPage />,
      },
      // 🎯 EXTENSIBILITY: Add new pages here
      // {
      //   path: 'new-feature',
      //   element: <NewFeaturePage />,
      // },
    ],
  },
]);
```

**app/App.tsx**
```typescript
import { RouterProvider } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/query-client';
import { router } from './router';
import { Toaster } from '@/components/ui/toaster';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <Toaster />
    </QueryClientProvider>
  );
}

export default App;
```

**components/layout/MainLayout.tsx**
```typescript
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function MainLayout() {
  return (
    <div className="h-screen flex flex-col">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Outlet /> {/* Child routes render here */}
        </main>
      </div>
    </div>
  );
}
```

**components/layout/Sidebar.tsx**
```typescript
import { NavLink } from 'react-router-dom';
import { 
  Home, MessageSquare, BarChart3, History, 
  Settings, HelpCircle, Plus 
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';

const navigation = [
  { name: 'Home', path: '/home', icon: Home },
  { name: 'Query', path: '/query', icon: MessageSquare },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'History', path: '/history', icon: History },
  { name: 'Settings', path: '/settings', icon: Settings },
  { name: 'Help', path: '/help', icon: HelpCircle },
  // 🎯 EXTENSIBILITY: Add new navigation items here
  // { name: 'New Feature', path: '/new-feature', icon: Plus },
];

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-muted/40">
      <nav className="flex flex-col gap-2 p-4">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                'hover:bg-accent hover:text-accent-foreground',
                isActive && 'bg-accent text-accent-foreground font-medium'
              )
            }
          >
            <item.icon className="h-5 w-5" />
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
```

---

### Phase 2: Core Components (Days 3-5)

#### 2.1 API Layer Setup

**lib/api/client.ts**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if needed
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    return Promise.reject(error);
  }
);
```

**lib/api/endpoints.ts**
```typescript
import { apiClient } from './client';

export const mcpAPI = {
  query: (question: string, model?: string) =>
    apiClient.post('/mcp/query', { question, model }),
  
  getExamples: () =>
    apiClient.get('/mcp/examples'),
  
  getSchema: () =>
    apiClient.get('/mcp/schema'),
  
  validateSQL: (sql: string) =>
    apiClient.post('/mcp/validate-sql', null, { params: { sql } }),
};

export const publicationsAPI = {
  getStats: () => apiClient.get('/publications/stats'),
  search: (query: string) => apiClient.get('/publications/search', { params: { q: query } }),
};
```

**lib/api/websocket.ts**
```typescript
import { io, Socket } from 'socket.io-client';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

class WebSocketService {
  private socket: Socket | null = null;

  connect() {
    this.socket = io(WS_URL, {
      transports: ['websocket'],
      autoConnect: true,
    });

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('❌ WebSocket disconnected');
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  emit(event: string, data: any) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }
}

export const wsService = new WebSocketService();
```

#### 2.2 Type Definitions

**types/query.ts**
```typescript
export interface QueryRequest {
  question: string;
  model?: string;
}

export interface QueryResponse {
  question: string;
  sql: string | null;
  explanation: string;
  data: any[];
  visualization: VisualizationConfig;
  row_count: number;
  confidence?: number;
  error?: string;
}

export interface VisualizationConfig {
  type: 'line_chart' | 'bar_chart' | 'pie_chart' | 'table' | 'network_graph' | 'multi_line_chart' | 'error';
  data: any[];
  columns?: string[];
  x_axis?: string;
  y_axis?: string;
  series?: string;
  label?: string;
  value?: string;
  title?: string;
  node1?: string;
  node2?: string;
  edge_weight?: string;
}

export interface QueryHistoryItem {
  id: string;
  timestamp: Date;
  question: string;
  response: QueryResponse;
}
```

#### 2.3 State Management

**lib/stores/useQueryStore.ts**
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { QueryHistoryItem, QueryResponse } from '@/types/query';

interface QueryState {
  currentQuery: string;
  currentResponse: QueryResponse | null;
  history: QueryHistoryItem[];
  isLoading: boolean;
  
  setCurrentQuery: (query: string) => void;
  setCurrentResponse: (response: QueryResponse) => void;
  addToHistory: (item: QueryHistoryItem) => void;
  clearHistory: () => void;
  setLoading: (loading: boolean) => void;
}

export const useQueryStore = create<QueryState>()(
  persist(
    (set) => ({
      currentQuery: '',
      currentResponse: null,
      history: [],
      isLoading: false,
      
      setCurrentQuery: (query) => set({ currentQuery: query }),
      setCurrentResponse: (response) => set({ currentResponse: response }),
      addToHistory: (item) => set((state) => ({ 
        history: [item, ...state.history].slice(0, 50) // Keep last 50
      })),
      clearHistory: () => set({ history: [] }),
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'query-storage',
      partialize: (state) => ({ history: state.history }),
    }
  )
);
```

---

### Phase 3: Chat Interface (Days 6-8)

#### 3.1 Query Input Component

**components/chat/QueryInput.tsx**
```typescript
import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export function QueryInput({ onSubmit, isLoading }: QueryInputProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query);
      setQuery('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <Textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question about publications..."
        className="pr-12 min-h-[100px]"
        disabled={isLoading}
      />
      <Button
        type="submit"
        size="icon"
        className="absolute bottom-2 right-2"
        disabled={!query.trim() || isLoading}
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Send className="h-4 w-4" />
        )}
      </Button>
    </form>
  );
}
```

#### 3.2 Message Display

**components/chat/MessageBubble.tsx**
```typescript
import { QueryResponse } from '@/types/query';
import { Card } from '@/components/ui/card';
import { ChartRenderer } from '@/components/visualizations/ChartRenderer';
import ReactMarkdown from 'react-markdown';

interface MessageBubbleProps {
  query: string;
  response: QueryResponse;
}

export function MessageBubble({ query, response }: MessageBubbleProps) {
  return (
    <div className="space-y-4">
      {/* User Query */}
      <div className="flex justify-end">
        <Card className="max-w-[80%] p-4 bg-primary text-primary-foreground">
          <p>{query}</p>
        </Card>
      </div>

      {/* AI Response */}
      <div className="flex justify-start">
        <Card className="max-w-[90%] p-6 space-y-4">
          {/* Explanation */}
          <div className="prose prose-sm">
            <ReactMarkdown>{response.explanation}</ReactMarkdown>
          </div>

          {/* Visualization */}
          {response.data && response.data.length > 0 && (
            <ChartRenderer config={response.visualization} />
          )}

          {/* SQL Query (collapsible) */}
          {response.sql && (
            <details className="text-xs">
              <summary className="cursor-pointer text-muted-foreground">
                View SQL Query
              </summary>
              <pre className="mt-2 p-2 bg-muted rounded overflow-x-auto">
                <code>{response.sql}</code>
              </pre>
            </details>
          )}

          {/* Metadata */}
          <div className="flex gap-4 text-xs text-muted-foreground">
            <span>{response.row_count} results</span>
            {response.confidence && (
              <span>Confidence: {(response.confidence * 100).toFixed(0)}%</span>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
```

#### 3.3 Suggested Queries

**components/chat/SuggestedQueries.tsx**
```typescript
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';

const SUGGESTED_QUERIES = [
  "Show publication trends over the last 10 years",
  "Who are the top 10 most productive faculty members?",
  "What are the most popular publication venues?",
  "Show collaborations between faculty members",
  "What types of publications do we have?",
];

interface SuggestedQueriesProps {
  onSelect: (query: string) => void;
}

export function SuggestedQueries({ onSelect }: SuggestedQueriesProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Sparkles className="h-4 w-4" />
        <span>Try asking:</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {SUGGESTED_QUERIES.map((query, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onSelect(query)}
            className="text-xs"
          >
            {query}
          </Button>
        ))}
      </div>
    </div>
  );
}
```

---

### Phase 4: Visualization Components (Days 9-12)

#### 4.1 Chart Renderer (Router)

**components/visualizations/ChartRenderer.tsx**
```typescript
import { VisualizationConfig } from '@/types/query';
import { LineChartViz } from './LineChartViz';
import { BarChartViz } from './BarChartViz';
import { PieChartViz } from './PieChartViz';
import { TableViz } from './TableViz';
import { NetworkGraphViz } from './NetworkGraphViz';

interface ChartRendererProps {
  config: VisualizationConfig;
}

export function ChartRenderer({ config }: ChartRendererProps) {
  switch (config.type) {
    case 'line_chart':
      return <LineChartViz config={config} />;
    case 'bar_chart':
      return <BarChartViz config={config} />;
    case 'pie_chart':
      return <PieChartViz config={config} />;
    case 'table':
      return <TableViz config={config} />;
    case 'network_graph':
      return <NetworkGraphViz config={config} />;
    case 'multi_line_chart':
      return <LineChartViz config={config} isMultiLine />;
    default:
      return <div>Unsupported visualization type</div>;
  }
}
```

#### 4.2 Individual Chart Components

Each chart component will:
- Use Recharts for rendering
- Support responsive sizing
- Include export functionality
- Show tooltips and legends
- Support theming

---

### Phase 5: Advanced Features (Days 13-15)

#### 5.1 Export Functionality
- Export charts as PNG/SVG
- Export data as CSV/JSON
- Export full report as PDF

#### 5.2 Query History
- Sidebar with recent queries
- Search through history
- Re-run previous queries
- Delete history items

#### 5.3 Next Question Suggestions
- AI-powered suggestions based on current query
- Context-aware recommendations
- Quick access buttons

---

### Phase 6: Polish & Testing (Days 16-18)

#### 6.1 UI/UX Enhancements
- Loading states and skeletons
- Error boundaries
- Toast notifications
- Smooth transitions
- Dark mode support

#### 6.2 Performance Optimization
- Code splitting
- Lazy loading
- Memoization
- Virtual scrolling for large datasets

#### 6.3 Testing
- Unit tests (Vitest)
- Component tests (React Testing Library)
- E2E tests (Playwright)
- Accessibility testing

---

## 📊 Timeline Summary

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| 1. Setup & Foundation | 2 days | Project structure, dependencies, configs |
| 2. Core Components | 3 days | API layer, types, state management |
| 3. Chat Interface | 3 days | Query input, message display, suggestions |
| 4. Visualizations | 4 days | All chart types, table, export |
| 5. Advanced Features | 3 days | History, suggestions, export |
| 6. Polish & Testing | 3 days | UX, performance, tests |
| **Total** | **18 days** | **Production-ready application** |

---

## 🚀 Getting Started Checklist

- [ ] Initialize Vite + React + TypeScript project
- [ ] Install all dependencies
- [ ] Set up Tailwind CSS
- [ ] Configure shadcn/ui
- [ ] Create folder structure
- [ ] Set up API client
- [ ] Define TypeScript types
- [ ] Create state stores
- [ ] Build chat interface
- [ ] Implement visualizations
- [ ] Add export functionality
- [ ] Test with backend API
- [ ] Deploy to production

---

## 📦 Next Steps

1. **Review and approve technology stack**
2. **Set up development environment**
3. **Begin Phase 1 implementation**
4. **Establish CI/CD pipeline**
5. **Plan deployment strategy**

This plan provides a complete roadmap for building a production-ready, AI-powered data insights assistant frontend!

---

## 🎯 Quick Extension Reference

### Checklist for Adding New Features

**New Main Page:**
- [ ] Create page component in `pages/`
- [ ] Add route in `app/router.tsx`
- [ ] Add navigation item in `Sidebar.tsx`
- [ ] Create feature components in `features/[feature-name]/`
- [ ] Add API endpoints if needed
- [ ] Update types in `types/`

**New Tab in Existing Page:**
- [ ] Create tab component in `features/[feature]/components/`
- [ ] Add `<TabsTrigger>` and `<TabsContent>` in page
- [ ] Add state/hooks if needed

**New Chart Type:**
- [ ] Create visualization component in `components/visualizations/`
- [ ] Update `ChartRenderer.tsx` switch statement
- [ ] Add type to `VisualizationConfig`
- [ ] Export data utility functions

**New API Integration:**
- [ ] Add API methods to `lib/api/endpoints.ts`
- [ ] Create types in `types/api.ts`
- [ ] Create custom hook with TanStack Query
- [ ] Add to relevant feature module

---

## 🚀 Extension Examples with Code

### Complete Example: Adding "Citation Analysis" Feature

**1. Create Types** (`types/citation.ts`):
```typescript
export interface Citation {
  id: string;
  title: string;
  citedBy: number;
  year: number;
}

export interface CitationNetwork {
  nodes: { id: string; label: string; value: number }[];
  edges: { source: string; target: string; weight: number }[];
}
```

**2. Create API** (`lib/api/endpoints.ts`):
```typescript
export const citationsAPI = {
  getCitationStats: () => apiClient.get('/citations/stats'),
  getCitationNetwork: () => apiClient.get('/citations/network'),
  getTopCited: (limit: number) => 
    apiClient.get('/citations/top', { params: { limit } }),
};
```

**3. Create Hook** (`features/citations/hooks/useCitations.ts`):
```typescript
import { useQuery } from '@tanstack/react-query';
import { citationsAPI } from '@/lib/api/endpoints';

export function useCitationStats() {
  return useQuery({
    queryKey: ['citation-stats'],
    queryFn: () => citationsAPI.getCitationStats(),
  });
}

export function useTopCited(limit = 10) {
  return useQuery({
    queryKey: ['top-cited', limit],
    queryFn: () => citationsAPI.getTopCited(limit),
  });
}
```

**4. Create Components** (`features/citations/components/`):
```typescript
// CitationStats.tsx
export function CitationStats() {
  const { data, isLoading } = useCitationStats();
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Citation Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Display stats */}
      </CardContent>
    </Card>
  );
}

// TopCitedPapers.tsx
export function TopCitedPapers() {
  const { data, isLoading } = useTopCited(10);
  
  return (
    <div className="space-y-4">
      {data?.map(paper => (
        <PaperCard key={paper.id} paper={paper} />
      ))}
    </div>
  );
}
```

**5. Create Page** (`pages/CitationsPage.tsx`):
```typescript
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CitationStats } from '@/features/citations/components/CitationStats';
import { TopCitedPapers } from '@/features/citations/components/TopCitedPapers';
import { CitationNetwork } from '@/features/citations/components/CitationNetwork';

export function CitationsPage() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Citation Analysis</h1>
      
      <Tabs defaultValue="stats">
        <TabsList>
          <TabsTrigger value="stats">Statistics</TabsTrigger>
          <TabsTrigger value="top">Top Cited</TabsTrigger>
          <TabsTrigger value="network">Network</TabsTrigger>
        </TabsList>

        <TabsContent value="stats">
          <CitationStats />
        </TabsContent>

        <TabsContent value="top">
          <TopCitedPapers />
        </TabsContent>

        <TabsContent value="network">
          <CitationNetwork />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

**6. Register Route** (`app/router.tsx`):
```typescript
{
  path: 'citations',
  element: <CitationsPage />,
}
```

**7. Add Navigation** (`components/layout/Sidebar.tsx`):
```typescript
import { Quote } from 'lucide-react';

const navigation = [
  // ... existing items
  { name: 'Citations', path: '/citations', icon: Quote },
];
```

**Done!** You now have a complete Citation Analysis feature with:
- ✅ Dedicated page
- ✅ Multiple tabs
- ✅ API integration
- ✅ Custom hooks
- ✅ Type safety
- ✅ Navigation

---

## 🎨 UI Component Extension

### Adding a Custom Dashboard Widget

```typescript
// components/widgets/CustomWidget.tsx
interface WidgetProps {
  title: string;
  data: any[];
  onExport?: () => void;
}

export function CustomWidget({ title, data, onExport }: WidgetProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{title}</CardTitle>
        {onExport && (
          <Button size="sm" variant="outline" onClick={onExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {/* Widget content */}
      </CardContent>
    </Card>
  );
}

// Use in any page:
<CustomWidget 
  title="My Custom Analysis"
  data={analysisData}
  onExport={handleExport}
/>
```

---

## 📦 Module Federation (Advanced)

For very large applications, you can use Module Federation to load features dynamically:

```typescript
// vite.config.ts
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'host-app',
      remotes: {
        citationModule: 'http://localhost:3001/assets/remoteEntry.js',
      },
      shared: ['react', 'react-dom', 'react-router-dom'],
    }),
  ],
});
```

This allows you to:
- Load features on-demand
- Deploy features independently
- Build micro-frontends
- Scale team development

---

## 🔄 State Synchronization Patterns

### Cross-Feature Communication

```typescript
// lib/stores/useEventBus.ts
import { create } from 'zustand';

type EventListener = (data: any) => void;

interface EventBusState {
  listeners: Record<string, EventListener[]>;
  emit: (event: string, data: any) => void;
  on: (event: string, callback: EventListener) => void;
  off: (event: string, callback: EventListener) => void;
}

export const useEventBus = create<EventBusState>((set, get) => ({
  listeners: {},
  
  emit: (event, data) => {
    const listeners = get().listeners[event] || [];
    listeners.forEach(callback => callback(data));
  },
  
  on: (event, callback) => {
    set(state => ({
      listeners: {
        ...state.listeners,
        [event]: [...(state.listeners[event] || []), callback],
      },
    }));
  },
  
  off: (event, callback) => {
    set(state => ({
      listeners: {
        ...state.listeners,
        [event]: (state.listeners[event] || []).filter(cb => cb !== callback),
      },
    }));
  },
}));

// Usage:
const { emit, on } = useEventBus();

// Feature A emits
emit('publication-selected', { id: '123' });

// Feature B listens
useEffect(() => {
  on('publication-selected', (data) => {
    // Handle event
  });
}, []);
```

This architecture ensures your application remains maintainable and scalable as you add more features!
