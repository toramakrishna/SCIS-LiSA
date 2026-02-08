# Architecture Extension Guide - Visual Reference

## 🏗️ Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    React Application                        │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │              React Router                             │  │ │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │  │ │
│  │  │  │   Home   │ │  Query   │ │Analytics │ │  [NEW]  │ │  │ │
│  │  │  │   Page   │ │   Page   │ │   Page   │ │  Page   │ │  │ │
│  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬────┘ │  │ │
│  │  └───────┼────────────┼────────────┼──────────────┼─────┘  │ │
│  │          │            │            │              │         │ │
│  │  ┌───────▼────────────▼────────────▼──────────────▼─────┐  │ │
│  │  │              Shared Components                        │  │ │
│  │  │  • ChatInterface  • Visualizations  • Layouts         │  │ │
│  │  └───────────────────────────────────────────────────────┘  │ │
│  │                                                             │ │
│  │  ┌───────────────────────────────────────────────────────┐ │ │
│  │  │                  State Management                      │ │ │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │ │ │
│  │  │  │  Query   │ │    UI    │ │   Auth   │ │  [NEW]  │ │ │ │
│  │  │  │  Store   │ │  Store   │ │  Store   │ │  Store  │ │ │ │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘ │ │ │
│  │  └───────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌───────────────────────────────────────────────────────┐ │ │
│  │  │              API Layer (Axios)                         │ │ │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │ │ │
│  │  │  │   MCP    │ │   Pubs   │ │  Faculty │ │  [NEW]  │ │ │ │
│  │  │  │   API    │ │   API    │ │   API    │ │   API   │ │ │ │
│  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬────┘ │ │ │
│  │  └───────┼────────────┼────────────┼──────────────┼─────┘ │ │
│  │          │            │            │              │         │ │
│  │  ┌───────▼────────────▼────────────▼──────────────▼─────┐ │ │
│  │  │              WebSocket Client                          │ │ │
│  │  └───────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP/WebSocket
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │   MCP    │ │   Pubs   │ │  Faculty │ │   [NEW]          │  │
│  │ Endpoint │ │ Endpoint │ │ Endpoint │ │   Endpoint       │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────────────┘  │
│       └────────────┴────────────┴──────────────┘                │
│                          │                                       │
│                ┌─────────▼──────────┐                           │
│                │   PostgreSQL DB    │                           │
│                └────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Extension Points

### 1️⃣ Adding a New Page

```
pages/
├── HomePage.tsx           ← Existing
├── QueryPage.tsx          ← Existing
├── AnalyticsPage.tsx      ← Existing
└── NewFeaturePage.tsx     ← ✨ ADD HERE

        ↓

app/router.tsx
{ path: 'new-feature', element: <NewFeaturePage /> }  ← ✨ ADD ROUTE

        ↓

components/layout/Sidebar.tsx
{ name: 'New Feature', path: '/new-feature', icon: Icon }  ← ✨ ADD NAV
```

### 2️⃣ Adding Tabs to a Page

```
AnalyticsPage
├── Tab: Trends         ← Existing
├── Tab: Venues         ← Existing
├── Tab: Collaborations ← Existing
└── Tab: [New Tab]      ← ✨ ADD HERE

Just add:
<TabsTrigger value="new-tab">New Tab</TabsTrigger>
<TabsContent value="new-tab"><NewComponent /></TabsContent>
```

### 3️⃣ Adding a Feature Module

```
features/
├── query/              ← Existing
├── analytics/          ← Existing
├── export/             ← Existing
└── new-feature/        ← ✨ CREATE NEW MODULE
    ├── components/
    ├── hooks/
    ├── types.ts
    └── api.ts

Self-contained and isolated!
```

### 4️⃣ Adding an API Endpoint Group

```typescript
lib/api/endpoints.ts

export const mcpAPI = { ... };        ← Existing
export const publicationsAPI = { ... }; ← Existing

export const newFeatureAPI = {        ← ✨ ADD NEW GROUP
  getData: () => apiClient.get('/new-feature/data'),
  postData: (data) => apiClient.post('/new-feature', data),
};
```

### 5️⃣ Adding a Visualization Type

```typescript
components/visualizations/

├── LineChartViz.tsx     ← Existing
├── BarChartViz.tsx      ← Existing
├── PieChartViz.tsx      ← Existing
└── NewChartViz.tsx      ← ✨ ADD NEW CHART

        ↓

ChartRenderer.tsx
case 'new_chart':        ← ✨ ADD CASE
  return <NewChartViz config={config} />;
```

## 🔄 Data Flow

### Query Flow
```
User Input
    ↓
QueryInput Component
    ↓
useQuery Hook
    ↓
MCP API Call
    ↓
Backend Processing (Ollama)
    ↓
SQL Generation
    ↓
Database Query
    ↓
Results + Visualization Config
    ↓
ChartRenderer
    ↓
Display to User
```

### State Management Flow
```
Component Action
    ↓
Zustand Store Update
    ↓
State Change
    ↓
React Re-render
    ↓
UI Update
```

### WebSocket Flow
```
Backend Event
    ↓
WebSocket Message
    ↓
Socket.IO Client
    ↓
Event Handler
    ↓
Store Update
    ↓
Component Update
```

## 📦 Component Hierarchy

```
App
└── RouterProvider
    └── MainLayout
        ├── Header
        │   ├── Logo
        │   ├── Search
        │   └── UserMenu
        ├── Sidebar
        │   └── Navigation
        │       ├── NavItem (Home)
        │       ├── NavItem (Query)
        │       ├── NavItem (Analytics)
        │       └── NavItem ([New])  ← ✨ EXTENSIBLE
        └── Outlet (Page Content)
            ├── QueryPage
            │   ├── ChatInterface
            │   │   ├── MessageBubble
            │   │   ├── QueryInput
            │   │   └── SuggestedQueries
            │   └── QueryResults
            │       └── ChartRenderer
            ├── AnalyticsPage
            │   └── Tabs
            │       ├── TrendAnalysis  ← Tab 1
            │       ├── VenueAnalysis  ← Tab 2
            │       └── [NewAnalysis]  ← ✨ ADD TAB
            └── [NewPage]              ← ✨ ADD PAGE
```

## 🎨 Styling Architecture

```
Tailwind CSS (Utility Classes)
    ↓
shadcn/ui Components (Base Components)
    ↓
Custom Components (Feature-specific)
    ↓
Pages (Composed UI)
```

**Benefits:**
- ✅ Consistent design system
- ✅ Easy to customize
- ✅ Type-safe component props
- ✅ Accessible by default

## 🔐 State Management Strategy

```
UI State (Zustand)
├── Theme
├── Sidebar collapsed
├── Active tab
└── Modal states

Server State (TanStack Query)
├── Publications data
├── Analytics data
├── Query results
└── [New API data]  ← ✨ EXTENSIBLE

Persistent State (localStorage)
├── Query history
├── User preferences
└── Recent searches
```

## 🚀 Build & Deploy Flow

```
Development
    ↓
npm run dev (Vite)
    ↓
Hot Module Replacement
    ↓
Fast Iteration

Production
    ↓
npm run build
    ↓
Optimized Bundle
    ↓
Static Assets
    ↓
Deploy (Vercel/Netlify/Docker)
```

## 📊 Feature Integration Checklist

When adding a new feature, ensure:

- [ ] **Types defined** in `types/`
- [ ] **API methods** in `lib/api/endpoints.ts`
- [ ] **Custom hooks** in `features/[name]/hooks/`
- [ ] **Components** in `features/[name]/components/`
- [ ] **Page** in `pages/` (if needed)
- [ ] **Route** in `app/router.tsx`
- [ ] **Navigation** in `Sidebar.tsx`
- [ ] **Store** in `lib/stores/` (if needed)
- [ ] **Tests** for critical paths
- [ ] **Documentation** updated

## 🎯 Best Practices for Extensions

1. **Feature Modules**: Keep features self-contained
2. **Shared Components**: Reuse UI components
3. **Type Safety**: Define types for all data
4. **Error Handling**: Use error boundaries
5. **Loading States**: Show loading indicators
6. **Accessibility**: Follow WCAG guidelines
7. **Performance**: Lazy load when possible
8. **Testing**: Test new features
9. **Documentation**: Document new APIs
10. **Code Review**: Review before merging

---

This architecture is designed for **maximum extensibility** while maintaining **clean separation of concerns**!
