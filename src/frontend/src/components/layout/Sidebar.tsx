import { NavLink } from 'react-router-dom';
import { Home, Search, TrendingUp, Users } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Home', path: '/', icon: Home, gradient: 'from-blue-500 to-indigo-600', color: 'text-blue-600' },
  { name: 'Query', path: '/query', icon: Search, gradient: 'from-purple-500 to-pink-600', color: 'text-purple-600' },
  { name: 'Faculty', path: '/faculty', icon: Users, gradient: 'from-green-500 to-emerald-600', color: 'text-green-600' },
  { name: 'Analytics', path: '/analytics', icon: TrendingUp, gradient: 'from-orange-500 to-yellow-600', color: 'text-orange-600' },
];

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-gradient-to-b from-slate-50 to-blue-50 dark:from-slate-900 dark:to-blue-950/30">
      <nav className="flex flex-col gap-2 p-4">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200',
                  isActive
                    ? `bg-gradient-to-r ${item.gradient} text-white shadow-md scale-[1.02]`
                    : `${item.color} dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 hover:scale-[1.02] hover:shadow-sm`
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
