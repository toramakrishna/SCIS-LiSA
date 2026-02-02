import { createBrowserRouter } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { HomePage } from '@/pages/HomePage';
import { QueryPage } from '@/pages/QueryPage';
import { AnalyticsPage } from '@/pages/AnalyticsPage';
import { FacultyPage } from '@/pages/FacultyPage';
import { FacultyDetailPage } from '@/pages/FacultyDetailPage';
import { AdminPage } from '@/pages/AdminPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'query',
        element: <QueryPage />,
      },
      {
        path: 'faculty',
        element: <FacultyPage />,
      },
      {
        path: 'faculty/:id',
        element: <FacultyDetailPage />,
      },
      {
        path: 'analytics',
        element: <AnalyticsPage />,
      },
      {
        path: 'admin',
        element: <AdminPage />,
      },
    ],
  },
]);
