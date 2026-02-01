import { NavLink } from 'react-router-dom';
import { Home, Search, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Home', path: '/', icon: Home },
  { name: 'Query', path: '/query', icon: Search },
  { name: 'Analytics', path: '/analytics', icon: TrendingUp },
];

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-background">
      <nav className="flex flex-col gap-2 p-4">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )
              }
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
