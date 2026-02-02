# 🚀 SCISLiSA Frontend - Quick Start Guide

## Current Status

✅ **Phase 1 Complete** - Foundation is ready!
- Frontend running at: http://localhost:5173/
- Backend API at: http://localhost:8000/api/v1
- All core setup complete, ready for feature development

## What You Can Do Right Now

### 1. View the Application
The frontend is already running. Open: http://localhost:5173/

**Available Pages:**
- **Home** (`/`) - Landing page with features and stats
- **Query** (`/query`) - Natural language query interface (placeholder)
- **Analytics** (`/analytics`) - Analytics dashboard (placeholder)

### 2. Test Navigation
Click through the sidebar navigation:
- Active route is highlighted in blue
- Smooth transitions between pages
- Responsive layout works on all screen sizes

### 3. Verify Backend Connection
The API client is configured to connect to `http://localhost:8000/api/v1`

**Test API in browser console:**
```javascript
// Open browser console (F12) and try:
fetch('http://localhost:8000/api/v1/mcp/examples')
  .then(r => r.json())
  .then(console.log)
```

## Development Commands

```bash
# Frontend is already running, but if you need to restart:
cd /Users/othadem/go/src/github.com/drtoramakrishna/SCISLiSA/src/frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## File Structure Overview

```
src/
├── app/router.tsx           # ← Routes configuration
├── pages/                   # ← Add new pages here
│   ├── HomePage.tsx
│   ├── QueryPage.tsx
│   └── AnalyticsPage.tsx
├── components/
│   ├── ui/                  # ← shadcn/ui components
│   └── layout/              # ← Header, Sidebar, MainLayout
├── lib/
│   ├── api/                 # ← API client & endpoints
│   └── utils.ts
└── types/                   # ← TypeScript types
```

## Adding Your First Feature

### Example: Add a "Publications" Page

**1. Create page component:**
```bash
# Create file: src/pages/PublicationsPage.tsx
```

```tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function PublicationsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Publications</h1>
      <Card>
        <CardHeader>
          <CardTitle>All Publications</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Your content here */}
        </CardContent>
      </Card>
    </div>
  );
}
```

**2. Add route (in `src/app/router.tsx`):**
```tsx
import { PublicationsPage } from '@/pages/PublicationsPage';

// In children array:
{
  path: 'publications',
  element: <PublicationsPage />,
}
```

**3. Add navigation link (in `src/components/layout/Sidebar.tsx`):**
```tsx
import { BookOpen } from 'lucide-react';

const navigation = [
  // ... existing items
  { name: 'Publications', path: '/publications', icon: BookOpen },
];
```

**Done!** Your new page is live at http://localhost:5173/publications 🎉

## Making API Calls

### Using TanStack Query

```tsx
import { useQuery } from '@tanstack/react-query';
import { mcpAPI } from '@/lib/api/endpoints';

function MyComponent() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['examples'],
    queryFn: async () => {
      const response = await mcpAPI.getExamples();
      return response.data;
    },
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>{JSON.stringify(data, null, 2)}</div>;
}
```

### Direct API Call

```tsx
import { mcpAPI } from '@/lib/api/endpoints';

async function handleQuery() {
  try {
    const response = await mcpAPI.query('Show top 10 faculty');
    console.log(response.data);
  } catch (error) {
    console.error('API Error:', error);
  }
}
```

## Styling with Tailwind

```tsx
// Basic layout
<div className="flex gap-4 p-6">
  <Card className="flex-1">
    <CardHeader>
      <CardTitle>Title</CardTitle>
    </CardHeader>
  </Card>
</div>

// Responsive design
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Content */}
</div>

// Dark mode ready (automatic with CSS variables)
<div className="bg-background text-foreground">
  <p className="text-muted-foreground">Secondary text</p>
</div>
```

## Common Tasks

### Add a New UI Component
```tsx
// Create in: src/components/ui/MyComponent.tsx
import { cn } from '@/lib/utils';

export function MyComponent({ className }: { className?: string }) {
  return (
    <div className={cn('base-styles', className)}>
      {/* Component content */}
    </div>
  );
}
```

### Create a Custom Hook
```tsx
// Create in: src/lib/hooks/useMyHook.ts
import { useState, useEffect } from 'react';

export function useMyHook() {
  const [value, setValue] = useState(null);
  
  useEffect(() => {
    // Your logic
  }, []);
  
  return { value, setValue };
}
```

### Add Global State (Zustand)
```tsx
// Create in: src/lib/stores/useMyStore.ts
import { create } from 'zustand';

interface MyState {
  count: number;
  increment: () => void;
}

export const useMyStore = create<MyState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));

// Use in components:
const { count, increment } = useMyStore();
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
npm run dev
```

### Backend Not Responding
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/mcp/examples

# If not, start it:
cd /Users/othadem/go/src/github.com/drtoramakrishna/SCISLiSA/src/backend
./start_mcp.sh
```

### TypeScript Errors
```bash
# Check for errors
npx tsc --noEmit

# The build will also show errors
npm run build
```

## Next Phase Preview

**Phase 2 will add:**
- 🔍 Query Input with autocomplete
- 💬 Chat-style conversation interface
- 📊 Chart components (Line, Bar, Pie, Table)
- 📈 Dynamic visualization rendering
- 🔄 Real-time updates via WebSocket
- 💾 Query history
- 📤 Export functionality

## Resources

- 📖 [Full Implementation Plan](IMPLEMENTATION_PLAN.md)
- 🏗️ [Architecture Guide](ARCHITECTURE_GUIDE.md)
- 📚 [Extension Cookbook](EXTENSION_COOKBOOK.md)
- ✅ [Phase 1 Summary](PHASE_1_SUMMARY.md)
- 📘 [Frontend README](FRONTEND_README.md)

## Need Help?

Check these files for examples:
- **Adding pages**: See [EXTENSION_COOKBOOK.md](EXTENSION_COOKBOOK.md) Scenario 1
- **Adding tabs**: See [EXTENSION_COOKBOOK.md](EXTENSION_COOKBOOK.md) Scenario 2
- **API integration**: See `src/lib/api/endpoints.ts`
- **Component patterns**: See existing pages in `src/pages/`

---

**You're all set!** The foundation is solid. Start building features! 🚀
