# SCISLiSA Frontend

React + TypeScript frontend for the School of Computer and Information Sciences - Library and Scholarly Analytics platform.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will run at http://localhost:5173/

## 📁 Project Structure

```
src/
├── app/                    # Application setup
│   └── router.tsx         # React Router configuration
├── components/            # Shared UI components
│   ├── ui/               # shadcn/ui components (Button, Card, Input)
│   └── layout/           # Layout components (Header, Sidebar, MainLayout)
├── pages/                # Page components
│   ├── HomePage.tsx      # Landing page
│   ├── QueryPage.tsx     # Natural language query interface
│   └── AnalyticsPage.tsx # Analytics dashboard
├── features/             # Feature-specific modules
├── lib/                  # Utilities and configurations
│   ├── api/             # API client and endpoints
│   ├── stores/          # Zustand state stores
│   └── utils.ts         # Helper functions
└── types/               # TypeScript type definitions
```

## 🛠️ Tech Stack

- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Routing**: React Router v6
- **State Management**: Zustand + TanStack Query
- **UI Components**: shadcn/ui (Radix UI + Tailwind)
- **Styling**: Tailwind CSS
- **Charts**: Recharts + D3.js
- **API Client**: Axios
- **Forms**: React Hook Form + Zod

## 🎨 Features

✅ **Phase 1 Complete** (Setup & Foundation)
- Vite + React + TypeScript setup
- Tailwind CSS configuration with dark mode support
- React Router v6 with nested routes
- shadcn/ui component library
- API client configuration
- Layout components (Header, Sidebar, MainLayout)
- Initial pages (Home, Query, Analytics)

🚧 **Next Steps** (Phase 2)
- Query interface with natural language input
- Real-time query results display
- Visualization components (charts, graphs)
- WebSocket integration for live updates
- Advanced features (export, history, suggestions)

## 🔧 Adding New Pages

Adding a new page is easy - just 3 steps:

1. **Create the page component**:
```tsx
// src/pages/NewPage.tsx
export function NewPage() {
  return <div>New Page Content</div>;
}
```

2. **Register the route**:
```tsx
// src/app/router.tsx
import { NewPage } from '@/pages/NewPage';

// Add to children array:
{
  path: 'new',
  element: <NewPage />,
}
```

3. **Add navigation link**:
```tsx
// src/components/layout/Sidebar.tsx
const navigation = [
  // ... existing items
  { name: 'New', path: '/new', icon: IconName },
];
```

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) and [EXTENSION_COOKBOOK.md](EXTENSION_COOKBOOK.md) for more examples!

## 🌐 API Integration

The frontend connects to the backend MCP API at `http://localhost:8000/api/v1`:

```typescript
// Available endpoints:
mcpAPI.query(question)           // POST /mcp/query
mcpAPI.getExamples()             // GET /mcp/examples
mcpAPI.getSchema()               // GET /mcp/schema
mcpAPI.validateSQL(sql)          // POST /mcp/validate-sql
```

## 📚 Documentation

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Full development plan and architecture
- [Architecture Guide](ARCHITECTURE_GUIDE.md) - Visual architecture diagrams and patterns
- [Extension Cookbook](EXTENSION_COOKBOOK.md) - Ready-to-use code examples

## 🎯 Development Workflow

1. Start backend server: `cd src/backend && ./start_mcp.sh`
2. Start frontend server: `npm run dev`
3. Open http://localhost:5173/
4. Make changes and see hot reload in action!

## 🎨 Styling

Using Tailwind CSS with CSS variables for theming:

```tsx
// Light/Dark mode automatically handled
<div className="bg-background text-foreground">
  <Card className="border-border">
    <CardHeader>
      <CardTitle className="text-card-foreground">Title</CardTitle>
    </CardHeader>
  </Card>
</div>
```

## 🔍 TypeScript

All types are defined in `src/types/index.ts`. Import as needed:

```typescript
import type { QueryResponse, Publication, Faculty } from '@/types';
```

## 🤝 Contributing

1. Create feature branches from `backend` branch
2. Follow existing code structure and patterns
3. Use TypeScript strict mode
4. Test on both light and dark modes
5. Ensure responsive design works on mobile

---

Built with ❤️ for scholarly analytics
