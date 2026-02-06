import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';

export function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      {/* Mobile: Horizontal navigation at top, Desktop: Vertical sidebar on left */}
      <div className="flex flex-col md:flex-row flex-1">
        <Sidebar />
        <main className="flex-1 p-4 md:p-6 overflow-auto">
          <div className="container max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}
